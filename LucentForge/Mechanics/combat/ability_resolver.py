# ability_resolver.py — Cost checking and ability dispatch
from __future__ import annotations
from Mechanics.combat import rules
from Mechanics.combat.casting import spell_pool_and_cost


class AbilityResolver:
    """Validates ability costs and resolves heal abilities."""

    def validate_and_pay(self, att, ability: dict) -> dict:
        """Check if fighter can afford the ability. Pay costs or fallback to basic.

        Stamina (cost_cycles) is unchanged; magic cost now routes to the right pool
        (§M4): Bit-spells spend `att.bits`, Byte-spells spend `att.mp` (Byte pool).
        """
        cost_sp = int(ability.get("cost_cycles", 0))
        pool, cost_mag = spell_pool_and_cost(ability)
        have_mag = att.bits if pool == "bit" else att.mp
        if cost_sp > att.cycles or cost_mag > have_mag:
            return {"id": "_basic", "name": "Basic", "kind": "attack",
                    "power": 1.0, "cost_cycles": 0}
        att.cycles -= cost_sp
        if pool == "bit":
            att.bits -= cost_mag
        else:
            att.mp -= cost_mag
        return ability

    def resolve_heal(self, att, ability: dict) -> int:
        """Apply a heal ability and return HP healed."""
        amount = int(ability.get("amount", 0)) or int(att.max_hp * ability.get("amount_pct", 0))
        before = att.hp
        att.hp = min(att.hp + amount, att.max_hp)
        healed = att.hp - before
        att.heals_used += 1
        att.cooldowns["heal"] = rules.HEAL_COOLDOWN_ROUNDS
        return healed
