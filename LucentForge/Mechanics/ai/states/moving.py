# moving.py — MovingState: pathfinding + critical-need interrupts
from __future__ import annotations
import math
from Mechanics.needs.need import NeedZone
from Mechanics.needs.needs_system import get_priority_need
import settings


class MovingState:
    name = "MOVING"

    def enter(self, controller) -> None:
        pass

    def update(self, controller, dt: float) -> None:
        if not controller.path or controller.path_index >= len(controller.path):
            if controller.target_source:
                controller._start_satisfying(controller.target_source)
            else:
                controller._set_state("IDLE")
            return

        # Check if a CRITICAL need overrides current target
        current_priority = get_priority_need(controller.needs)
        if (current_priority and controller.target_source and
                current_priority.zone == NeedZone.CRITICAL and
                current_priority.need_id != controller.target_source.need_id):
            print(f"[CRITICAL] {controller.npc.name}: {current_priority.label} is critical -- re-routing!")
            controller._was_interrupted = True
            controller._set_state("IDLE")
            return

        # Only block on the goal tile
        next_tile = controller.path[controller.path_index]
        is_goal = (controller.path_index == len(controller.path) - 1)
        if is_goal and next_tile in controller._occupied:
            controller._set_state("IDLE")
            controller.path = []
            controller.path_index = 0
            return

        target_col, target_row = controller.path[controller.path_index]
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
