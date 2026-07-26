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

    def _try_relocate(self, controller) -> bool:
        """Drift toward the best remembered-comfortable region, if warranted (Phase B).

        Returns True and enters RELOCATING when: sustained stress is high, the entity
        isn't already content (comfort's dampening role), a positive-comfort region is
        remembered that beats the current spot by a margin, it isn't already there, and a
        walkable path exists. Otherwise False (no state change → parity with pre-Phase-B).
        """
        if controller.rooms is None:
            return False
        stress = controller.brain.chemicals.get("stress")
        if stress < settings.COMFORT_RELOCATE_STRESS_THRESHOLD:
            return False
        # Comfort's dampening/settling role (§B4): a content entity stays put.
        if controller.affinity_comfort >= settings.COMFORT_CONTENT_THRESHOLD:
            return False
        best = controller.memory.best_region()
        if best is None:
            return False
        best_id, best_pref = best
        if best_pref - controller.affinity_comfort < settings.COMFORT_RELOCATE_MARGIN:
            return False
        current = controller._current_room()
        if current is not None and current.id == best_id:
            return False  # already on the most comfortable remembered ground
        path = self._relocate_path(controller, best_id)
        if not path:
            return False

        controller.path = path
        controller.path_index = 0
        controller.target_source = None
        controller.relocate_target_region = best_id
        controller._set_state("RELOCATING")
        room = controller.rooms.get_by_id(best_id)
        print(f"[COMFORT] {controller.npc.name} stressed ({stress:.2f}) -> drifting to "
              f"{room.name if room else best_id} (remembered comfort {best_pref:+.2f})")
        return True

    def _relocate_path(self, controller, room_id):
        """BFS to the nearest reachable, unoccupied tile inside the target region."""
        room = controller.rooms.get_by_id(room_id)
        if room is None:
            return None
        start = controller.tile_map.world_to_grid(controller.npc.x, controller.npc.y)
        cmin, rmin, cmax, rmax = room.tile_bounds
        candidates = [
            (c, r)
            for c in range(cmin, cmax + 1)
            for r in range(rmin, rmax + 1)
            if not controller.tile_map.is_blocked(c, r)
            and (c, r) not in controller._occupied
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda t: math.hypot(t[0] - start[0], t[1] - start[1]))
        for goal in candidates[:8]:  # a few nearest reachable tiles
            path = bfs_path(controller.tile_map.is_blocked, start, goal,
                            controller.tile_map.cols, controller.tile_map.rows)
            if path:
                return path
        return None

    def update(self, controller, dt: float) -> None:
        # H5: wait cooldown after failing to find a source
        if self._wait_timer > 0:
            self._wait_timer -= dt
            return

        priority_need = get_priority_need(controller.needs)

        # Behavior strategy override (Heartbeat-4: goblins patrol/raid)
        override = controller.behavior.decide(controller, priority_need)
        if override == "RAIDING":
            controller._set_state("RAIDING")
            return

        # Comfort-relocate (biochem/affinity addendum §B4, Phase B): a non-urgent,
        # stressed entity that remembers more comfortable ground drifts toward it.
        # Outranks patrol/idle-wander, but never an active raid or an urgent survival
        # need — priority_need is None here means nothing is urgent.
        if priority_need is None and self._try_relocate(controller):
            return

        if override == "PATROLLING":
            controller._set_state("PATROLLING")
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
                from Mechanics.observation.event_log import EVENTS
                EVENTS.append("NEED", f"{controller.npc.name} needs {priority_need.label} "
                                      f"-> {source.label}")
