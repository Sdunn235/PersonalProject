# combat.py — Backward-compatible facade
# Logic has been decomposed into:
#   action_selector.py, ability_resolver.py, damage_resolver.py,
#   turn_end.py, turn_processor.py, turn_result.py, fighter.py
from __future__ import annotations
from Mechanics.combat.fighter import Fighter, InvStack, build_fighter
from Mechanics.combat.damage_resolver import DamageResolver
from Mechanics.combat.turn_processor import TurnProcessor

_processor = TurnProcessor()
_damage = DamageResolver()


def take_turn(att: Fighter, defn: Fighter, rng,
              forced_ability: dict | None = None) -> dict:
    """Execute one combat turn. Delegates to TurnProcessor."""
    return _processor.process(att, defn, rng, forced_ability=forced_ability)


def hit_check(att: Fighter, defn: Fighter, rng) -> bool:
    return _damage.hit_check(att, defn, rng)


def damage_roll(att: Fighter, defn: Fighter, rng) -> tuple[int, bool]:
    return _damage.damage_roll(att, defn, rng)
