# relocating.py — RelocatingState: drift toward remembered-comfortable ground.
#
# Phase B of the biochem/affinity addendum (§B4). When a non-urgent entity is stressed
# by its current region and remembers somewhere more comfortable, IdleState routes it
# here with a path toward that region's center. Named distinctly (not MOVING) because
# legibility is a hard requirement — the observation panel must show *why* it moved.
#
# Movement mirrors MovingState, but the interrupt differs: relocation carries no
# target_source, so it re-checks *any* urgent need and yields to IDLE (survival always
# outranks comfort). On arrival it clears the relocate target and returns to IDLE.
from __future__ import annotations
import math
from Mechanics.needs.need import NeedZone
from Mechanics.needs.needs_system import get_priority_need
import settings


class RelocatingState:
    name = "RELOCATING"

    def enter(self, controller) -> None:
        pass

    def _finish(self, controller) -> None:
        controller.relocate_target_region = None
        controller.path = []
        controller.path_index = 0
        controller._set_state("IDLE")

    def update(self, controller, dt: float) -> None:
        # Survival outranks comfort: abandon the drift if any need turns urgent.
        priority = get_priority_need(controller.needs)
        if priority is not None and priority.zone in (NeedZone.WARNING, NeedZone.CRITICAL):
            self._finish(controller)
            return

        if not controller.path or controller.path_index >= len(controller.path):
            self._finish(controller)
            return

        # Yield the goal tile if another entity now occupies it.
        next_tile = controller.path[controller.path_index]
        is_goal = (controller.path_index == len(controller.path) - 1)
        if is_goal and next_tile in controller._occupied:
            self._finish(controller)
            return

        target_col, target_row = next_tile
        tx, ty = controller.tile_map.grid_to_world_center(target_col, target_row)
        dx, dy = tx - controller.npc.x, ty - controller.npc.y
        dist = math.hypot(dx, dy)
        step = settings.NPC_SPEED * dt

        if dist <= step:
            controller.npc.x = tx
            controller.npc.y = ty
            controller.path_index += 1
        else:
            controller.npc.x += (dx / dist) * step
            controller.npc.y += (dy / dist) * step
