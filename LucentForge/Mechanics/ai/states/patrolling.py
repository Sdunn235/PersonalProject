# patrolling.py — PatrollingState: goblin camp patrol (Heartbeat-4)
#
# PASSIVE behavior: pick random tiles in goblin_camp, wander between them.
# Occasionally lurk near the south bridge to project fear.
# Transitions back to IDLE when hunger becomes urgent or threat stage changes.
from __future__ import annotations
import random
import settings
from Mechanics.needs.needs_system import get_priority_need
from Mechanics.world.pathfinder import bfs_path


# Goblin camp region tiles (cols 2-3, rows 13-14) + nearby forest tiles
_CAMP_TILES = [(c, r) for c in range(1, 4) for r in range(12, 16)]
# South bridge area for lurking patrols
_BRIDGE_LURK_TILES = [(3, 11), (3, 12), (4, 12)]


class PatrollingState:
    name = "PATROLLING"

    def __init__(self):
        self._patrol_target: tuple[int, int] | None = None
        self._path: list[tuple[int, int]] = []
        self._path_index: int = 0
        self._pause_timer: float = 0.0
        self._lurk_chance: float = 0.2  # 20% chance to lurk near bridge

    def enter(self, controller) -> None:
        self._patrol_target = None
        self._path = []
        self._path_index = 0
        self._pause_timer = 0.0
        print(f"[GOBLIN] {controller.npc.name}: PATROLLING "
              f"(threat={controller.behavior.threat.threat_level:.1f})")

    def _pick_target(self, controller) -> tuple[int, int] | None:
        """Pick a random patrol destination in or near goblin camp."""
        current = controller.tile_map.world_to_grid(
            controller.npc.x, controller.npc.y)

        # Occasional bridge lurk
        if random.random() < self._lurk_chance:
            candidates = [t for t in _BRIDGE_LURK_TILES
                          if not controller.tile_map.is_blocked(*t)
                          and t not in controller._occupied]
            if candidates:
                return random.choice(candidates)

        # Normal camp patrol
        candidates = [t for t in _CAMP_TILES
                      if not controller.tile_map.is_blocked(*t)
                      and t != current
                      and t not in controller._occupied]
        if candidates:
            return random.choice(candidates)
        return None

    def update(self, controller, dt: float) -> None:
        # Check if we should leave patrol: urgent need or threat escalated
        priority = get_priority_need(controller.needs)
        if priority is not None and priority.is_urgent:
            controller._set_state("IDLE")
            return

        # Check if threat stage changed from PASSIVE
        if hasattr(controller.behavior, 'threat'):
            from Mechanics.world.goblin_threat import ThreatStage
            if controller.behavior.threat.stage != ThreatStage.PASSIVE:
                controller._set_state("IDLE")
                return

        # Pausing at a patrol point
        if self._pause_timer > 0:
            self._pause_timer -= dt
            return

        # Need a new target
        if not self._path or self._path_index >= len(self._path):
            target = self._pick_target(controller)
            if target is None:
                self._pause_timer = settings.GOBLIN_PATROL_PAUSE
                return

            start = controller.tile_map.world_to_grid(
                controller.npc.x, controller.npc.y)
            path = bfs_path(controller.tile_map.is_blocked, start, target,
                            controller.tile_map.cols, controller.tile_map.rows)
            if not path:
                self._pause_timer = settings.GOBLIN_PATROL_PAUSE
                return

            self._patrol_target = target
            self._path = path
            self._path_index = 0

        # Follow path
        if self._path_index < len(self._path):
            target_col, target_row = self._path[self._path_index]
            tx = target_col * settings.TILE_SIZE + settings.TILE_SIZE // 2
            ty = target_row * settings.TILE_SIZE + settings.TILE_SIZE // 2
            dx = tx - controller.npc.x
            dy = ty - controller.npc.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < 2.0:
                self._path_index += 1
                if self._path_index >= len(self._path):
                    self._pause_timer = settings.GOBLIN_PATROL_PAUSE
            else:
                speed = settings.NPC_SPEED * dt
                controller.npc.x += (dx / dist) * speed
                controller.npc.y += (dy / dist) * speed
