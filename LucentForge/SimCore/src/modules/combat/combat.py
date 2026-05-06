from dataclasses import dataclass, field
from .stats import Stats
from . import status as S
from . import rules
from .derive import BaseStats, FlatMods, Effect, derive_stats
# --- Inventory stack ----------------------------------------------------------
@dataclass
class InvStack:
    item: dict
    qty: int = 1
# --- Fighter class -------------------------------------------------------------
@dataclass
class Fighter:
    name: str
    hp: int
    stats: Stats
    weapon: dict | None = None
    # Multiple abilities supported
    abilities: list[dict] | None = None
    # Track max hp for capping heals
    max_hp: int = 0
    # inventory (list of stacks)
    bag: list[InvStack] = field(default_factory=list)
    # per-element multipliers (damage taken)
    resistances: dict = field(default_factory=lambda: {"neutral": 1.0})

    # per-turn regen amount
    cycle_regen: int = rules.CYCLE_REGEN_PER_TURN 

    # sources for deriving current stats
    base: BaseStats = field(default_factory=BaseStats)
    gear_mods: list[FlatMods] = field(default_factory=list)
    effects: list[Effect] = field(default_factory=list)


    #  Ability economy & cooldowns
    cycles: int = rules.CYCLE_MAX_DEFAULT
    max_cycles: int = rules.CYCLE_MAX_DEFAULT
    cooldowns: dict = field(default_factory=dict)
    heals_used: int = 0

    ability: dict | None = None  # scratch

    def __post_init__(self):
        if self.max_hp <= 0:
            self.max_hp = self.hp
    
    def refresh_stats(self):
        self.stats = derive_stats(self.base, self.gear_mods, self.effects, mode=self.stats.clamp_mode)

    def tick_cooldowns(self):
        for k in list(self.cooldowns.keys()):
            self.cooldowns[k] = max(0, self.cooldowns[k]-1)
            if self.cooldowns[k] == 0:
                del self.cooldowns[k]
# --- Hit chance ----------------------------------------------------------------
def hit_check(att: Fighter, defn: Fighter, rng) -> bool:
    dex_diff = (att.stats.DEX - defn.stats.DEX)
    hit_pct = rules.HIT_BASE + dex_diff * rules.HIT_PER_DEX_DIFF
    if hit_pct < rules.HIT_MIN: hit_pct = rules.HIT_MIN
    if hit_pct > rules.HIT_MAX: hit_pct = rules.HIT_MAX
    return rng.chance(hit_pct)
# --- Damage calculation --------------------------------------------------------
def damage_roll(att: Fighter, defn: Fighter, rng) -> tuple[int, bool]:
    base = att.stats.STR
    wep = att.weapon["atk"] if att.weapon else 0
    power = att.ability.get("power", 1.0) if att.ability else 1.0
    raw = int((base + wep) * power)

    # Variance ±10%
    spread = max(1, raw // 10)
    raw += rng.range_int(-spread, spread)

    # Crit
    crit_bonus = (att.weapon.get("crit_bonus", 0) if att.weapon else 0)
    crit_chance = min(60.0, att.stats.LCK + crit_bonus)
    was_crit = rng.chance(crit_chance)
    if was_crit:
        raw = int(raw * 1.5)

    # NEW: Element multiplier BEFORE DEF
    elem = att.ability.get("element", "neutral") if att.ability else "neutral"
    mult = float(defn.resistances.get(elem, 1.0))
    raw = int(raw * mult)

    # Mitigation (flat) + clamp
    mitigated = max(1, raw - defn.stats.DEF)
    return rules.apply_damage_cap(mitigated), was_crit
# --- Status effects -----------------------------------------------------------
def apply_poison(f: Fighter):
    if f.stats.status.has(S.POISON):
        tick = max(1, int(round(f.hp * 0.02)))
        f.hp = max(0, f.hp - tick)
# --- Inventory helpers --------------------------------------------------------
def _consume_one(st: InvStack) -> None:
    st.qty -= 1
# --- Find first item in bag matching key ---------------------------------------
def _first_item_in_bag(f: Fighter, key: str) -> "InvStack | None":
    for st in f.bag:
        if st.qty > 0 and st.item.get(key, 0) > 0:
            return st
    return None
# --- Ability helpers ----------------------------------------------------------
def _can_pay(att: Fighter, ability: dict) -> bool:
    cost = int(ability.get("cost_cycles", 0))
    return att.cycles >= cost
# --- Action decision helpers ---------------------------------------------------
def _should_heal(current_hp, max_hp, heal_amount, is_enemy=False):
    if is_enemy:
        threshold = rules.ENEMY_ITEM_HEAL_THRESHOLD
        eff      = rules.ENEMY_HEAL_MIN_EFFICIENCY
    else:
        threshold = rules.ITEM_HEAL_THRESHOLD
        eff      = rules.HEAL_MIN_EFFICIENCY

    missing = max_hp - current_hp
    if current_hp > int(max_hp * threshold):
        return False
    return missing >= int(heal_amount * eff)
#--- AI: Choose best healing item ------------------------------------------------
def _best_heal_stack(f: Fighter) -> InvStack | None:
    """Pick the most potent healing consumable we have."""
    heals = [
        st for st in f.bag
        if st.qty > 0 and st.item.get("type") == "consumable" and st.item.get("heal", 0) > 0
    ]
    if not heals:
        return None
    return max(heals, key=lambda st: st.item["heal"])

def _heal_choice(att, is_enemy):
    # Gather options
    best_item = None
    best_item_amt = 0
    for st in att.bag:
        if st.qty > 0 and st.item.get("heal", 0) > 0:
            amt = int(st.item["heal"])
            if amt > best_item_amt:
                best_item_amt, best_item = amt, st

    best_ability = None
    best_ability_amt = 0
    if att.abilities:
        for a in att.abilities:
            if a.get("kind") == "heal" and _can_pay(att, a):
                amt = int(a.get("amount", 0))
                if amt > best_ability_amt:
                    best_ability_amt, best_ability = amt, a

    # Decide if we should heal at all (using the best available amt)
    best_amt = max(best_item_amt, best_ability_amt)
    if best_amt <= 0: 
        return None  # no heal available

    # gate via thresholds/efficiency
    if not _should_heal(att.hp, att.max_hp, best_amt, is_enemy=is_enemy):
        return None

    # Prefer ability if it heals more (or equal and we want to save items)
    if best_ability and best_ability_amt >= best_item_amt:
        return {"type":"ability", "ability": best_ability}
    if best_item:
        return {"type":"use_item","stack": best_item}
    return None

def _first_item_in_bag(f: Fighter, key: str):
    for st in f.bag:
        if st.qty > 0 and st.item.get(key, 0) > 0:
            return st
    return None

def _min_unpayable_cost(att: Fighter):
    costs = []
    if att.abilities:
        for a in att.abilities:
            if a.get("kind") in ("attack","heal"):
                c = int(a.get("cost_cycles", 0))
                if c > att.cycles:
                    costs.append(c)
    return min(costs) if costs else None

def _ether_if_it_enables_attack(att: Fighter):
    ether = _first_item_in_bag(att, "restore_cycles")
    if not ether:
        return None
    restore = int(ether.item.get("restore_cycles",0))
    needed = _min_unpayable_cost(att)
    if needed is None:
        return None  # nothing to unlock
    # only Ether if it would let us pay something AND we’re reasonably low
    if att.cycles + restore >= needed and att.cycles <= max(10, needed // 2):
        return ether
    return None

# --- Action selection ---------------------------------------------------------
def choose_action(att: Fighter, defn: Fighter, rng):
    """
    Returns a dict describing the chosen action:
      {"type":"use_item","stack":InvStack}  OR
      {"type":"ability","ability":{...}}    OR
      {"type":"ability","ability":{"id":"_basic","power":1.0,"kind":"attack"}}
    """

    is_enemy = getattr(att, "is_enemy", False)

    # respect cooldown & max-heals
    heal_locked = att.cooldowns.get("heal", 0) > 0
    heal_capped = att.heals_used >= rules.HEAL_MAX_PER_BATTLE

    # 1) Heal (smart pick)
    if not heal_locked and not heal_capped:
        hc = _heal_choice(att, is_enemy)
        if hc:
            return hc
        
    # 2) Attacks we can pay
    if att.abilities:
        attacks = [a for a in att.abilities if a.get("kind","attack") == "attack" and _can_pay(att, a)]
        if attacks:
            return {"type":"ability", "ability": max(attacks, key=lambda a:a.get("power",1.0))}

    # 3) If we can’t pay anything, consider Ether (smart, see next)
    ether = _ether_if_it_enables_attack(att)
    if ether:
        return {"type":"use_item","stack": ether}

    # 4) Fallback
    return {"type":"ability","ability":{"id":"_basic","name":"Basic","kind":"attack","power":1.0,"cost_cycles":0}}

# --- Execute a turn -----------------------------------------------------------
def take_turn(att: Fighter, defn: Fighter, rng):
    # tick durations/cooldowns at the start of our turn
    att.tick_cooldowns()
    action = choose_action(att, defn, rng)

    # USE ITEM
    # USE ITEM (heal or ether)
    if action["type"] == "use_item":
        st: InvStack = action["stack"]
        healed = 0
        restored = 0

        if st.item.get("heal", 0) > 0:
            before = att.hp
            att.hp = min(att.hp + int(st.item.get("heal",0)), att.max_hp)
            healed = att.hp - before
            att.heals_used += 1
            att.cooldowns["heal"] = rules.HEAL_COOLDOWN_ROUNDS

        if st.item.get("restore_cycles", 0) > 0:
            before = att.cycles
            att.cycles = min(att.cycles + int(st.item["restore_cycles"]), att.max_cycles)
            restored = att.cycles - before

        _consume_one(st)
        if st.qty <= 0:
            try: att.bag.remove(st)
            except ValueError: pass

        apply_poison(att); apply_poison(defn)
        # end-of-turn regen
        att.cycles = min(att.max_cycles, att.cycles + att.cycle_regen)
        return {"type":"use_item","item":st.item["id"],"amount":healed, "cycles_restored": restored}

    # ABILITY (heal or attack)
    ability = action["ability"]
    # Spend cost (if any); if can’t pay (race condition), fallback to basic
    cost = int(ability.get("cost_cycles", 0))
    if cost > att.cycles:
        ability = {"id":"_basic","name":"Basic","kind":"attack","power":1.0,"cost_cycles":0}
        cost = 0
    att.cycles -= cost

    if ability.get("kind") == "heal":
        amount = int(ability.get("amount", 0))
        before = att.hp
        att.hp = min(att.hp + amount, att.max_hp)
        healed = att.hp - before
        att.heals_used += 1
        att.cooldowns["heal"] = rules.HEAL_COOLDOWN_ROUNDS
        apply_poison(att); apply_poison(defn)
        att.cycles = min(att.max_cycles, att.cycles + att.cycle_regen)
        return {"type":"heal","amount":healed,"ability":ability.get("id","")}

    # Attack path
    if not hit_check(att, defn, rng):
        apply_poison(att); apply_poison(defn)
        att.cycles = min(att.max_cycles, att.cycles + att.cycle_regen)
        return {"type":"miss","amount":0,"ability": ability.get("id",""),"element": ability.get("element","neutral")}

    att.ability = ability
    dmg, was_crit = damage_roll(att, defn, rng)
    defn.hp = max(0, defn.hp - dmg)
    apply_poison(att); apply_poison(defn)
    att.cycles = min(att.max_cycles, att.cycles + att.cycle_regen)
    return {"type":"hit","amount":dmg,"crit": was_crit,"ability":ability.get("id",""),"element": ability.get("element","neutral")}

    # Set the ability used for damage calc
    # att.ability = ability
    # dmg, was_crit = damage_roll(att, defn, rng)
    # defn.hp = max(0, defn.hp - dmg)
    # apply_poison(att); apply_poison(defn)
    # return {
    #     "type":"hit",
    #     "amount":dmg,
    #     "crit": was_crit,
    #     "ability": ability.get("id",""),
    #     "element": ability.get("element","neutral"),
    # }
