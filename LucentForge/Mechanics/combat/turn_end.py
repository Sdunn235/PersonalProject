# turn_end.py — End-of-turn effects: poison ticks, cycle/MP regen
from __future__ import annotations
from Mechanics.combat import rules


class TurnEndHandler:
    """Applies end-of-turn effects to both fighters."""

    def apply(self, att, defn) -> None:
        """Poison ticks + resource regen for both fighters."""
        _apply_poison(att)
        _apply_poison(defn)
        att.cycles = min(att.max_cycles, att.cycles + att.cycle_regen)
        att.mp     = min(att.max_mp,     att.mp     + rules.MP_REGEN_PER_TURN)


def _apply_poison(f) -> None:
    from Mechanics.entities import status as S
    if f.stats.status.has(S.POISON):
        f.hp = max(0, f.hp - max(1, int(f.hp * rules.POISON_TICK_PCT)))
