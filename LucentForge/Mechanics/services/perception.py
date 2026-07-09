# perception.py — passive Intuition trap sense (§12.2 / §M8).
#
# Real Intuition (Stage 4.1) finally powers the §12.2 perceive-trap check. This is
# a passive "danger sense": as the player nears a trapped container, a keen-enough
# Intuition reveals it in advance (world marker + log hint), so the attribute build
# means noticing more of the world's hazards.
from __future__ import annotations
import settings
from Mechanics.services.outcome import attribute_term


def perceive_traps(player, chest_reg: dict) -> list[str]:
    """Reveal nearby traps the player's Intuition is keen enough to notice.

    Deterministic threshold form of the §12.2 perceive-trap check — a passive
    sense, not a per-frame die roll:

        TRAP_PERCEIVE_BASE + attribute_term(Intuition) >= trap perceive DC

    Only trapped, unopened, not-yet-perceived chests within TRAP_PERCEIVE_RADIUS
    (Manhattan) are considered. Mutates `chest.trap_perceived`. Returns hint
    messages for chests newly perceived this call (empty if none).
    """
    pcol = int(player.x // settings.TILE_SIZE)
    prow = int(player.y // settings.TILE_SIZE)
    score = settings.TRAP_PERCEIVE_BASE + attribute_term(player.attributes, "intuition")

    hints: list[str] = []
    for chest in chest_reg.values():
        if not chest.is_trapped or chest.is_opened or chest.trap_perceived:
            continue
        if abs(chest.col - pcol) + abs(chest.row - prow) > settings.TRAP_PERCEIVE_RADIUS:
            continue
        dc = chest.perceive_dc or settings.TRAP_PERCEIVE_DC
        if score >= dc:
            chest.trap_perceived = True
            hints.append(
                f"[PERCEIVE] {player.name}'s instincts flag a trap on the chest "
                f"at ({chest.col},{chest.row})."
            )
    return hints
