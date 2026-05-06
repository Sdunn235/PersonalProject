# turn_processor.py — Orchestrator replacing the monolithic take_turn()
from __future__ import annotations
from Mechanics.combat.action_selector import ActionSelector
from Mechanics.combat.ability_resolver import AbilityResolver
from Mechanics.combat.damage_resolver import DamageResolver
from Mechanics.combat.turn_end import TurnEndHandler
from Mechanics.combat.turn_result import TurnResult
from Mechanics.combat import rules


class TurnProcessor:
    """Single-responsibility orchestrator for one combat turn."""

    def __init__(self):
        self.selector = ActionSelector()
        self.ability_resolver = AbilityResolver()
        self.damage_resolver = DamageResolver()
        self.turn_end = TurnEndHandler()

    def process(self, att, defn, rng,
                forced_ability: dict | None = None) -> dict:
        """Execute one turn. Returns a result dict (backward compatible)."""
        att.tick_cooldowns()

        if forced_ability is not None:
            action = {"type": "ability", "ability": forced_ability}
        else:
            action = self.selector.choose(att, defn, rng)

        if action["type"] == "use_item":
            result = self._handle_item(att, action)
            self.turn_end.apply(att, defn)
            return result.to_dict()

        ability = self.ability_resolver.validate_and_pay(att, action["ability"])

        if ability.get("kind") == "heal":
            healed = self.ability_resolver.resolve_heal(att, ability)
            self.turn_end.apply(att, defn)
            return TurnResult(
                type="heal", amount=healed,
                ability=ability.get("id", ""),
                ability_name=ability.get("name", ""),
            ).to_dict()

        if not self.damage_resolver.hit_check(att, defn, rng):
            self.turn_end.apply(att, defn)
            return TurnResult(
                type="miss", amount=0,
                ability=ability.get("id", ""),
                ability_name=ability.get("name", ""),
                element=ability.get("element", "neutral"),
            ).to_dict()

        att.ability = ability
        dmg, was_crit = self.damage_resolver.damage_roll(att, defn, rng)
        defn.hp = max(0, defn.hp - dmg)
        self.turn_end.apply(att, defn)
        return TurnResult(
            type="hit", amount=dmg, crit=was_crit,
            ability=ability.get("id", ""),
            ability_name=ability.get("name", ""),
            element=ability.get("element", "neutral"),
        ).to_dict()

    def _handle_item(self, att, action: dict) -> TurnResult:
        st = action["stack"]
        healed = 0
        if st.item.get("heal", 0) > 0:
            before = att.hp
            att.hp = min(att.hp + int(st.item["heal"]), att.max_hp)
            healed = att.hp - before
            att.heals_used += 1
            att.cooldowns["heal"] = rules.HEAL_COOLDOWN_ROUNDS
        st.qty -= 1
        if st.qty <= 0:
            try:
                att.bag.remove(st)
            except ValueError:
                pass
        return TurnResult(type="use_item", amount=healed,
                          item=st.item.get("id", "?"))
