# action_selector.py — Choose what a fighter does on their turn
from __future__ import annotations
from Mechanics.combat import rules


def _can_pay(att, ability: dict) -> bool:
    sp_ok = att.cycles >= int(ability.get("cost_cycles", 0))
    mp_ok = att.mp >= int(ability.get("cost_mp", 0))
    return sp_ok and mp_ok


def _should_heal(hp, max_hp, heal_amount, is_enemy=False):
    threshold = rules.ENEMY_ITEM_HEAL_THRESHOLD if is_enemy else rules.ITEM_HEAL_THRESHOLD
    eff       = rules.ENEMY_HEAL_MIN_EFFICIENCY if is_enemy else rules.HEAL_MIN_EFFICIENCY
    if hp > int(max_hp * threshold):
        return False
    return (max_hp - hp) >= int(heal_amount * eff)


class ActionSelector:
    """Decides what action a fighter takes: use item, ability, spell, or basic attack."""

    def choose(self, att, defn, rng) -> dict:
        is_enemy    = att.is_enemy
        heal_locked = att.cooldowns.get("heal", 0) > 0
        heal_capped = att.heals_used >= rules.HEAL_MAX_PER_BATTLE

        if not heal_locked and not heal_capped:
            best_item = None
            best_item_amt = 0
            for st in att.bag:
                if st.qty > 0 and st.item.get("heal", 0) > 0:
                    amt = int(st.item["heal"])
                    if amt > best_item_amt:
                        best_item_amt, best_item = amt, st
            if best_item and _should_heal(att.hp, att.max_hp, best_item_amt, is_enemy):
                return {"type": "use_item", "stack": best_item}

        attacks = []
        if att.abilities:
            attacks += [a for a in att.abilities
                        if a.get("kind", "attack") == "attack" and _can_pay(att, a)]
        if att.spells:
            attacks += [s for s in att.spells
                        if s.get("kind", "attack") == "attack" and _can_pay(att, s)]
        if attacks:
            return {"type": "ability",
                    "ability": max(attacks, key=lambda a: a.get("power", 1.0))}

        return {"type": "ability",
                "ability": {"id": "_basic", "name": "Basic", "kind": "attack",
                            "power": 1.0, "cost_cycles": 0}}
