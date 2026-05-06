# raiding.py — RaidingState: goblin raids on civilized sources (Heartbeat-4)
#
# RAIDING behavior: path to a civilized food source, occupy it (blocking),
# then retreat after a duration or if needs become critical.
# CROSSING behavior: same but unlocks deeper targets (FARM, BED area).
from __future__ import annotations
import random
import settings
from Mechanics.needs.needs_system import get_priority_need
from Mechanics.world.pathfinder import bfs_path
from Mechanics.world.goblin_threat import ThreatStage


class RaidingState:
    name = "RAIDING"

    def __init__(self):
        self._target_source = None
        self._path: list[tuple[int, int]] = []
        self._path_index: int = 0
        self._occupy_timer: float = 0.0
        self._phase: str = "MOVING"  # MOVING -> OCCUPYING -> RETREATING

    def enter(self, controller) -> None:
        self._phase = "MOVING"
        self._occupy_timer = 0.0
        self._target_source = self._pick_raid_target(controller)

        if self._target_source is None:
            controller._set_state("IDLE")
            return

        start = controller.tile_map.world_to_grid(
            controller.npc.x, controller.npc.y)

        # Path to the target source
        if self._target_source.tiles:
            free = [t for t in self._target_source.tiles
                    if t not in controller._occupied]
            goal = min(free,
                       key=lambda t: abs(t[0] - start[0]) + abs(t[1] - start[1]),
                       ) if free else (self._target_source.grid_col,
                                       self._target_source.grid_row)
        else:
            goal = (self._target_source.grid_col,
                    self._target_source.grid_row)

        path = bfs_path(controller.tile_map.is_blocked, start, goal,
                        controller.tile_map.cols, controller.tile_map.rows)
        if not path:
            controller._set_state("IDLE")
            return

        self._path = path
        self._path_index = 0

        print(f"[GOBLIN] {controller.npc.name}: RAIDING -> "
              f"{self._target_source.label} "
              f"(threat={controller.behavior.threat.threat_level:.1f})")

    def _pick_raid_target(self, controller):
        """Pick a civilized source to raid based on threat stage."""
        stage = controller.behavior.threat.stage

        # Filter sources by threat stage
        if stage == ThreatStage.RAIDING:
            # Only target FOOD (nearest wild-side food source)
            target_labels = {"FOOD"}
        else:
            # CROSSING: deeper targets available
            target_labels = {"FOOD", "FARM"}

        candidates = [s for s in controller.sources
                      if s.label in target_labels]
        if not candidates:
            return None

        # Pick randomly (could be weighted by distance later)
        return random.choice(candidates)

    def update(self, controller, dt: float) -> None:
        # Always check for critical needs — goblins retreat when desperate
        priority = get_priority_need(controller.needs)
        if priority is not None and priority.zone.value == "critical":
            print(f"[GOBLIN] {controller.npc.name}: retreating — "
                  f"{priority.label} is critical")
            controller._set_state("IDLE")
            return

        # Check if threat dropped back to PASSIVE — retreat
        if hasattr(controller.behavior, 'threat'):
            if controller.behavior.threat.stage == ThreatStage.PASSIVE:
                controller._set_state("IDLE")
                return

        if self._phase == "MOVING":
            self._do_move(controller, dt)
        elif self._phase == "OCCUPYING":
            self._do_occupy(controller, dt)

    def _do_move(self, controller, dt: float) -> None:
        """Follow path toward raid target."""
        if self._path_index >= len(self._path):
            # Arrived at target
            self._phase = "OCCUPYING"
            self._occupy_timer = settings.GOBLIN_RAID_DURATION
            if self._target_source:
                print(f"[RAID] {controller.npc.name} reached "
                      f"{self._target_source.label} — blocking")
            return

        target_col, target_row = self._path[self._path_index]
        tx = target_col * settings.TILE_SIZE + settings.TILE_SIZE // 2
        ty = target_row * settings.TILE_SIZE + settings.TILE_SIZE // 2
        dx = tx - controller.npc.x
        dy = ty - controller.npc.y
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < 2.0:
            self._path_index += 1
        else:
            speed = settings.NPC_SPEED * dt
            controller.npc.x += (dx / dist) * speed
            controller.npc.y += (dy / dist) * speed

    def _do_occupy(self, controller, dt: float) -> None:
        """Stand on source tile, blocking other NPCs. Consumes stock (H5)."""
        self._occupy_timer -= dt

        # H5: goblins consume source stock while occupying (raiding = stealing food)
        if self._target_source is not None and self._target_source.is_finite:
            raid_consume = (self._target_source.satisfaction_amount
                           * dt / self._target_source.interaction_time)
            consumed = self._target_source.consume(raid_consume)
            if consumed > 0:
                # Raiding partially feeds the goblin (0.5x efficiency)
                hunger = next((n for n in controller.needs
                               if n.need_id == "hunger"), None)
                if hunger:
                    hunger.current_value = min(100.0,
                                               hunger.current_value + consumed * 0.5)

        if self._occupy_timer <= 0:
            stock_info = ""
            if self._target_source is not None and self._target_source.is_finite:
                stock_info = (f" (stock={self._target_source.stock:.0f}"
                              f"/{self._target_source.capacity:.0f})")
            print(f"[GOBLIN] {controller.npc.name}: raid complete, "
                  f"retreating{stock_info}")
            controller._set_state("IDLE")
