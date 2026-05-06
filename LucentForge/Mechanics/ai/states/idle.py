# idle.py — IdleState: think/decide which need to pursue
from __future__ import annotations
import math
from Mechanics.needs.need import NeedZone
from Mechanics.needs.needs_system import get_priority_need
from Mechanics.needs.source_selector import select_source
from Mechanics.world.pathfinder import bfs_path
import settings


class IdleState:
    name = "IDLE"

    def __init__(self):
        self._wait_timer: float = 0.0  # H5: cooldown when no viable source found

    def enter(self, controller) -> None:
        pass

    def update(self, controller, dt: float) -> None:
        # H5: wait cooldown after failing to find a source
        if self._wait_timer > 0:
            self._wait_timer -= dt
            return

        priority_need = get_priority_need(controller.needs)

        # Behavior strategy override (Heartbeat-4: goblins patrol/raid)
        override = controller.behavior.decide(controller, priority_need)
        if override and override in ("PATROLLING", "RAIDING"):
            controller._set_state(override)
            return

        if priority_need is None:
            return

        # Pre-sleep prep: handle other urgent needs before sleeping
        if (priority_need.need_id == "sleep"
                and priority_need.zone == NeedZone.WARNING):
            blocking = next(
                (n for n in controller.needs
                 if n.need_id != "sleep"
                 and n.zone in (NeedZone.WARNING, NeedZone.CRITICAL)),
                None
            )
            if blocking:
                print(f"[PRE-SLEEP] {controller.npc.name}: {blocking.label} is {blocking.zone.value} -- handling before sleep")
                priority_need = blocking

        source = select_source(priority_need.need_id, controller.sources,
                              controller.npc.x, controller.npc.y,
                              controller.memory, controller.brain.traits,
                              contested=controller.contested_sources)
        if source is None:
            self._wait_timer = 3.0  # H5: wait 3s before retrying
            return

        # H5: don't path to a depleted source — wait for regen instead
        if source.is_finite and source.stock <= 0:
            self._wait_timer = 5.0  # longer wait — source needs time to regen
            return

        if source.distance_from(controller.npc.x, controller.npc.y) < settings.TILE_SIZE * 0.6:
            # Capture decision context even for immediate satisfaction (H3)
            controller._decision_start_pos = (controller.npc.x, controller.npc.y)
            controller._decision_need_zone = priority_need.zone
            controller._was_interrupted = False
            controller._start_satisfying(source)
            return

        start = controller.tile_map.world_to_grid(controller.npc.x, controller.npc.y)
        if source.tiles:
            free = [t for t in source.tiles if t not in controller._occupied]
            goal = min(free, key=lambda t: math.hypot(t[0] - start[0], t[1] - start[1]),
                       ) if free else (source.grid_col, source.grid_row)
        else:
            goal = (source.grid_col, source.grid_row)
        path = bfs_path(controller.tile_map.is_blocked, start, goal,
                        controller.tile_map.cols, controller.tile_map.rows)
        if path:
            controller.path = path
            controller.path_index = 0
            controller.target_source = source
            # Capture decision context for outcome interpretation (H3)
            controller._decision_start_pos = (controller.npc.x, controller.npc.y)
            controller._decision_need_zone = priority_need.zone
            controller._was_interrupted = False
            controller._set_state("MOVING")
            log_key = f"{priority_need.need_id}:{source.label}"
            if controller._last_need_log != log_key:
                print(f"[NEED] {controller.npc.name} -> {source.label} "
                      f"({priority_need.label} {priority_need.current_value:.1f})")
                controller._last_need_log = log_key
