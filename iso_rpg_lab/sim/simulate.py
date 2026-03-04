import argparse
from statistics import mean, pstdev
from gameplay import rules
from gameplay.loader import load_all
from gameplay.stats import Stats, StatusFlags
from gameplay.combat import Fighter, InvStack, take_turn  # NOTE: InvStack imported here
from gameplay.rng import RNG32
from gameplay.derive import BaseStats, FlatMods

def _flat_from_item(it):
    return FlatMods(
        STR=it.get("str",0), DEX=it.get("dex",0), MAG=it.get("mag",0),
        WIS=it.get("wis",0), LCK=it.get("lck",0), DEF=it.get("def",0), RES=it.get("res",0)
    )

def make_player(db):
    P = db["players"]["hero"] # only one for now

    base = P.get("base", {})
    base_stats = BaseStats(**{k:int(v) for k,v in base.items()})

    stats = Stats(STR=base_stats.STR, MAG=base_stats.MAG, LCK=base_stats.LCK,
                  DEF=0, RES=0, DEX=base_stats.DEX, clamp_mode="clamp", status=StatusFlags(0))

    # equipment
    eq = P.get("equipment", {})
    weapon = db["items"].get(eq.get("weapon")) if eq.get("weapon") else None
    gear_mods = []
    for sid in (eq.get("armor"), eq.get("acc")):
        if sid and sid in db["items"]:
            gear_mods.append(_flat_from_item(db["items"][sid]))

    # bag
    bag = []
    for st in P.get("bag", []):
        it = db["items"].get(st["id"])
        if it: bag.append(InvStack(item=it, qty=int(st.get("qty",1))))

    # abilities
    abilities = [db["abilities"][aid] for aid in P.get("abilities", []) if aid in db["abilities"]]

    # resistances
    resist = P.get("resistances", {"neutral":1.0})

    f = Fighter(P.get("name","Hero"), hp=int(P.get("hp",200)), max_hp=int(P.get("hp",200)),
                stats=stats, weapon=weapon, abilities=abilities, bag=bag,
                resistances=resist, base=base_stats, gear_mods=gear_mods)
    # cycles
    cy = P.get("cycles", {})
    f.max_cycles  = int(cy.get("max", f.max_cycles))
    f.cycles      = int(cy.get("start", f.cycles))
    f.cycle_regen = int(cy.get("regen", f.cycle_regen))

    f.refresh_stats()
    return f

def make_enemy(db, enemy_id: str):
    e = db["enemies"][enemy_id]
    stats = Stats(STR=e["str"], MAG=e["mag"], LCK=e["lck"],
                  DEF=e["defense"], RES=e["resist"], DEX=e.get("dex", 5))
    abilities = [db["abilities"][aid] for aid in e.get("abilities", []) if aid in db["abilities"]]
    resistances = e.get("resistances", {"neutral": 1.0})

    # --- bag ---
    bag = []
    for st in e.get("bag", []):
        item = db["items"].get(st["id"])
        if item:
            bag.append(InvStack(item=item, qty=int(st.get("qty",1))))

    # --- gear ---
    weapon = None
    equip = e.get("equipment", {})
    wid = equip.get("weapon")
    if wid: weapon = db["items"].get(wid)

    # flat gear mods (armor/accessory to derived layer)
    from gameplay.derive import FlatMods
    gear_mods = []
    def _flat_from_item(it):
        return FlatMods(
            STR=it.get("str",0), DEX=it.get("dex",0), MAG=it.get("mag",0),
            WIS=it.get("wis",0), LCK=it.get("lck",0), DEF=it.get("def",0), RES=it.get("res",0)
        )
    for sid in (equip.get("armor"), equip.get("acc")):
        if sid and sid in db["items"]:
            gear_mods.append(_flat_from_item(db["items"][sid]))

    f = Fighter(e["name"], hp=e["hp"], max_hp=e["hp"], stats=stats,
                abilities=abilities, resistances=resistances,
                bag=bag, weapon=weapon, gear_mods=gear_mods)
    f.is_enemy = True
    cy = e.get("cycles", {})
    f.max_cycles = int(cy.get("max", f.max_cycles))
    f.cycles     = int(cy.get("start", f.cycles))
    f.cycle_regen = int(cy.get("regen", getattr(f, "cycle_regen", rules.CYCLE_REGEN_PER_TURN)))
    f.refresh_stats()  # apply gear mods at spawn
    return f

def _bump(map_obj, key, inc=1):
    map_obj[key] = map_obj.get(key, 0) + inc

def _blank_side():
    return {
        "hits":0,             # number of successful hits
        "miss":0,              # number of missed attacks
        "crits":0,             # number of critical hits
        "dmg_dealt":0,        # total damage dealt
        "dmg_taken":0,        # total damage taken
        "heals_used":0,       # number of healing actions used
        "healed_amount":0,    # total amount healed
        "items_used":{},      # item_id -> count
        "abilities_used":{},  # ability_id -> count
        "elements_used":{},   # element -> count
        "attacks_used":0,     # number of attack actions (hit+miss)
        "cycles_spent":0,     # number of cycles spent
        "cycles_restored":0,  # number of cycles restored
        "heals_blocked_cd":0, # number of heals blocked by cooldown
        "heals_blocked_cap":0, # number of heals blocked by cap
        "basics_used":0, 
        "ethers_used":0
    }

def make_allies(db, n=1):
    return [make_player(db) for _ in range(n)]

def make_enemies(db, ids):
    return [make_enemy(db, eid) for eid in ids]

def alive(units): return [u for u in units if u.hp > 0]

def target_lowest_hp(units):
    units = [u for u in units if u.hp > 0]
    return min(units, key=lambda u: u.hp) if units else None

def act_round_party(allies, enemies, rng):
    # refresh derived stats at the start of each round
    for u in alive(allies) + alive(enemies):
        u.refresh_stats()
    events = []
    for unit, side in initiative_order(allies, enemies):
        opp = enemies if side == "ally" else allies
        tgt = target_lowest_hp(opp)
        if not tgt: break
        ev = take_turn(unit, tgt, rng)
        events.append((side, ev))
        if not alive(opp): break
    return events

def initiative_order(allies, enemies):
    # alive units from both sides, sort by DEX desc; allies win ties
    units = [(u, "ally") for u in alive(allies)] + [(u, "enemy") for u in alive(enemies)]
    units.sort(key=lambda t: (t[0].stats.DEX, 1 if t[1]=="ally" else 0), reverse=True)
    return units  # list of tuples (unit, side)

def act_round_party(allies, enemies, rng):
    # Returns a list of events in order
    events = []
    for unit, side in initiative_order(allies, enemies):
        opp = enemies if side == "ally" else allies
        tgt = target_lowest_hp(opp)
        if not tgt: break
        ev = take_turn(unit, tgt, rng)
        events.append((side, ev))
        # early-out if team wiped
        if not alive(opp): break
    return events

def _bump(map_obj, key, inc=1):
    map_obj[key] = map_obj.get(key, 0) + inc

def battle(allies_t, enemies_t, seed=1234, collect=None):
    rng = RNG32(seed)
    import copy
    allies = [copy.deepcopy(a) for a in allies_t]
    enemies = [copy.deepcopy(e) for e in enemies_t]

    rounds = 0
    sides = {"hero": _blank_side(), "enemy": _blank_side()}

    while alive(allies) and alive(enemies) and rounds < 999:
        for side, evt in act_round_party(allies, enemies, rng):
            actor = "hero" if side == "ally" else "enemy"
            target = "enemy" if side == "ally" else "hero"
            _tally_event(evt, sides, actor, target)
        rounds += 1

    winner = "Hero" if alive(allies) and not alive(enemies) else ("Enemy" if alive(enemies) and not alive(allies) else "Stalemate")

    if collect is not None:
        for side_name in ("hero","enemy"):
            S, C = sides[side_name], collect[side_name]
            for k in ("hits","miss","crits","dmg_dealt","dmg_taken","heals_used","healed_amount","attacks_used","basics_used","ethers_used"):
                C[k] += S[k]
            for k,v in S["items_used"].items():     _bump(C["items_used"], k, v)
            for k,v in S["abilities_used"].items(): _bump(C["abilities_used"], k, v)
            for k,v in S["elements_used"].items():  _bump(C["elements_used"], k, v)

    # survivors (optional metric)
    survivors_ally = len(alive(allies))
    survivors_enemy = len(alive(enemies))
    return {"winner": winner, "rounds": rounds, "ally_survivors": survivors_ally, "enemy_survivors": survivors_enemy}

def _tally_event(evt, sides, actor, target):
    A = sides[actor]; T = sides[target]
    t = evt["type"]

    if t in ("hit","miss"):
        ab = evt.get("ability","")
        if ab: _bump(A["abilities_used"], ab)
        el = evt.get("element","neutral")
        _bump(A["elements_used"], el)

        if t == "hit":
            A["hits"] += 1; A["attacks_used"] += 1
            A["dmg_dealt"] += evt.get("amount",0); T["dmg_taken"] += evt.get("amount",0)
            if evt.get("crit"): A["crits"] += 1
        else:
            A["miss"] += 1; A["attacks_used"] += 1

        if ab == "_basic":   # NEW
            A["basics_used"] += 1

    elif t == "heal":
        A["heals_used"] += 1
        A["healed_amount"] += evt.get("amount",0)
        ab = evt.get("ability","")
        if ab: _bump(A["abilities_used"], ab)

    elif t == "use_item":
        it = evt.get("item","")
        if it: _bump(A["items_used"], it)
        if it == "ether_small":   # NEW
            A["ethers_used"] += 1
        healed = evt.get("amount",0)
        if healed:
            A["heals_used"] += 1
            A["healed_amount"] += healed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--enemy", default="slime_green")
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--heal", action="store_true", help="Hero uses healing ability instead of attack")
    parser.add_argument("--ally_count", type=int, default=1)
    parser.add_argument("--enemies", type=str, default=None, help="Comma-separated enemy IDs, e.g. 'bandit,bandit,slime_green'")

    args = parser.parse_args()

    db = load_all()
    # Enumerate everything that *could* be used
    all_abilities = ["_basic"] + list(db["abilities"].keys())
    all_items = [k for k,v in db["items"].items() if v.get("type") == "consumable"]
    all_elements  = sorted({a.get("element", "neutral") for a in db["abilities"].values()} | {"neutral"})
    # Build parties
    ally_party   = make_allies(db, n=args.ally_count)
    enemy_ids    = args.enemies.split(",") if args.enemies else [args.enemy]
    enemy_party  = make_enemies(db, enemy_ids)

    def _blank_side_prefilled():
        return {
            "hits":0, "miss":0, "crits":0,
            "dmg_dealt":0, "dmg_taken":0,
            "heals_used":0, "healed_amount":0,
            "items_used":{k:0 for k in all_items},
            "abilities_used":{k:0 for k in all_abilities},
            "elements_used":{k:0 for k in all_elements},
            "attacks_used":0,
            "basics_used":0, 
            "ethers_used":0
        }

    totals = {"hero": _blank_side_prefilled(), "enemy": _blank_side_prefilled()}
    results = [battle(ally_party, enemy_party, seed=args.seed+i, collect=totals) for i in range(args.runs)]
    wins = sum(1 for r in results if r["winner"] == "Hero")
    ally_survivors_avg  = sum(r["ally_survivors"]  for r in results) / args.runs
    enemy_survivors_avg = sum(r["enemy_survivors"] for r in results) / args.runs
    print(f"Win rate: {wins/args.runs*100:.1f}% | Avg ally survivors: {ally_survivors_avg:.2f} | Avg enemy survivors: {enemy_survivors_avg:.2f}")

    # Aggregates
    for side in ("hero","enemy"):
        S = totals[side]
        swings = S["hits"] + S["miss"]
        hit_rate = (S["hits"]/swings*100) if swings else 0
        avg_dmg_per_hit = (S["dmg_dealt"]/S["hits"]) if S["hits"] else 0
        avg_attacks_per_fight = S["attacks_used"] / args.runs
        avg_heals_per_fight   = S["heals_used"]   / args.runs
        avg_healed_per_fight  = S["healed_amount"]/ args.runs

        print(f"[{side.upper()}] hit% {hit_rate:.1f} | crit% {(S['crits']/max(1,S['hits'])*100):.1f} "
            f"| avg dmg/hit {avg_dmg_per_hit:.1f} | avg attacks/fight {avg_attacks_per_fight:.2f} "
            f"| avg heals/fight {avg_heals_per_fight:.2f} (avg healed {avg_healed_per_fight:.1f}) "
            f"| dmg dealt {S['dmg_dealt']} | dmg taken {S['dmg_taken']}"
            f"| basics_used {S['basics_used']} | ethers_used {S['ethers_used']}")

    def _print_full_counts(title, dct, order=None):
        print(title)
        keys = order if order is not None else sorted(dct.keys())
        for k in keys:
            print(f"  {k}: {dct[k]}")
        if not keys:
            print("  (none)")
        print("")

    # ... after printing [HERO] ... and [ENEMY] summary lines:
    print("\n=== DETAILED COUNTS ===")

    print("\n-- HERO --")
    _print_full_counts("Abilities used (counts):", totals["hero"]["abilities_used"], all_abilities)
    _print_full_counts("Items used (counts):",     totals["hero"]["items_used"],     all_items)
    _print_full_counts("Elements used (counts):",  totals["hero"]["elements_used"],  all_elements)

    print("-- ENEMY --")
    _print_full_counts("Abilities used (counts):", totals["enemy"]["abilities_used"], all_abilities)
    _print_full_counts("Items used (counts):",     totals["enemy"]["items_used"],     all_items)
    _print_full_counts("Elements used (counts):",  totals["enemy"]["elements_used"],  all_elements)

if __name__ == "__main__":
    main()
