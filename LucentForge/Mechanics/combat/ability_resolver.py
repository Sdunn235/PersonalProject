# ability_resolver.py — Cost checking and ability dispatch
from __future__ import annotations
from Mechanics.combat import rules


class AbilityResolver:
    """Validates ability costs and resolves heal abilities."""

    def validate_and_pay(self, att, ability: dict) -> dict:
        """Check if fighter can afford the ability. Pay costs or fallback to basic."""
        cost_sp = int(ability.get("cost_cycles", 0))
        cost_mp = int(ability.get("cost_mp", 0))
        if cost_sp > att.cycles or cost_mp > att.mp:
            return {"id": "_basic", "name": "Basic", "kind": "attack",
                    "power": 1.0, "cost_cycles": 0, "cost_mp": 0}
        att.cycles -= cost_sp
        att.mp -= cost_mp
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
