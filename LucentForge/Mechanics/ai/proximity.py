# proximity.py — Goblin proximity fear system (Heartbeat-4)
#
# Each frame, goblins on the civilized side of the river inject fear
# into nearby non-goblin NPCs. This uses the existing biochem layer —
# fear multiplies need urgency through the fearfulness trait, making
# NPCs flee or reprioritize.
from __future__ import annotations
import math
import settings


def update_proximity_fear(npc_list: list, defeated: set[str]) -> set[str]:
    """Check goblin proximity to other NPCs and inject fear.

    Args:
        npc_list: List of (entity, controller, sprite) tuples.
        defeated: Set of defeated entity IDs to skip.

    Returns:
        Set of source labels that are currently contested (goblin standing
        on a source tile).
    """
    radius_px = settings.GOBLIN_FEAR_RADIUS * settings.TILE_SIZE
    fear_amount = settings.GOBLIN_FEAR_AMOUNT
    contested: set[str] = set()

    # Collect living goblins and their grid positions
    goblins = []
    for entity, ctrl, _ in npc_list:
        if (entity.entity_id not in defeated
                and entity.subtype == "goblin"):
            goblins.append((entity, ctrl))

    if not goblins:
        return contested

    # Collect non-goblin NPCs
    others = []
    for entity, ctrl, _ in npc_list:
        if (entity.entity_id not in defeated
                and entity.subtype != "goblin"):
            others.append((entity, ctrl))

    # Check each goblin
    for gob_entity, gob_ctrl in goblins:
        # Check if goblin is on a source tile → contested
        gob_grid = (int(gob_entity.x // settings.TILE_SIZE),
                     int(gob_entity.y // settings.TILE_SIZE))
        for src in gob_ctrl.sources:
            if src.tiles and gob_grid in src.tiles:
                contested.add(src.label)
            elif (src.grid_col, src.grid_row) == gob_grid:
                contested.add(src.label)

        # Inject fear into nearby non-goblin NPCs
        for other_entity, other_ctrl in others:
            dx = gob_entity.x - other_entity.x
            dy = gob_entity.y - other_entity.y
            dist = math.hypot(dx, dy)

            if dist < radius_px:
                other_ctrl.brain.chemicals.add_fear(fear_amount)
                # Record threat memory for the source the NPC was heading to
                if (other_ctrl.target_source is not None
                        and other_ctrl.state in ("MOVING", "SATISFYING")):
                    other_ctrl.memory.record_threat(
                        other_ctrl.target_source.label,
                        other_ctrl._tick)
