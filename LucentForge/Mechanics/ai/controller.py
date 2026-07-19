# controller.py — Slim NPC AI controller using state pattern
from __future__ import annotations
import settings
from Mechanics.needs.need import Need
from Mechanics.needs.needs_system import update_needs
from Mechanics.needs.need_source import NeedSource
from Mechanics.biochem.brain import Brain
from Mechanics.biochem.emitter import AffinityComfortEmitter
from Mechanics.world.tile_map import TileMap
from Mechanics.ai.memory import Memory
from Mechanics.ai.npc_logger import NeedZoneLogger
from Mechanics.ai.behavior import BehaviorStrategy, HumanBehavior
from Mechanics.ai.states.idle import IdleState
from Mechanics.ai.states.moving import MovingState
from Mechanics.ai.states.satisfying import SatisfyingState
from Mechanics.ai.states.patrolling import PatrollingState
from Mechanics.ai.states.raiding import RaidingState
from Mechanics.ai.states.relocating import RelocatingState


class NPCController:
    def __init__(self, npc, needs: list[Need], brain: Brain,
                 sources: list[NeedSource], tile_map: TileMap,
                 behavior: BehaviorStrategy | None = None,
                 rooms=None):
        self.npc = npc
        self.needs = needs
        self.brain = brain
        self.sources = sources
        self.tile_map = tile_map

        # Affinity comfort emitter (biochem/affinity addendum §B4). `rooms` is a
        # RoomRegistry used to resolve the entity's current region each tick. When
        # None (or entity/region neutral), the emitter is a no-op.
        self.rooms = rooms
        self._affinity_emitter = AffinityComfortEmitter()
        self.affinity_comfort: float = 0.0  # last comfort score, for observability
        # Learned-comfort relocate (Phase B): best remembered region + active relocate
        # target, both surfaced in the observation panel / run-logger for legibility.
        self.best_region: tuple[str, float] | None = None
        self.relocate_target_region: str | None = None

        self.target_source: NeedSource | None = None
        self.path: list[tuple[int, int]] = []
        self.path_index: int = 0

        self.memory: Memory = Memory()

        self._tick: int = 0
        self._occupied: set[tuple[int, int]] = set()
        self._logger = NeedZoneLogger(needs, npc_name=npc.name)
        self._last_need_log: str | None = None

        # Decision-tracking for outcome interpretation (Heartbeat-3)
        self._decision_start_pos: tuple[float, float] = (0.0, 0.0)
        self._decision_need_zone = None  # NeedZone at decision time
        self._was_interrupted: bool = False

        self.behavior: BehaviorStrategy = behavior or HumanBehavior()
        self.contested_sources: set[str] = set()  # H4: goblin-occupied source labels

        # State objects
        self._states = {
            "IDLE": IdleState(),
            "MOVING": MovingState(),
            "SATISFYING": SatisfyingState(),
            "PATROLLING": PatrollingState(),
            "RAIDING": RaidingState(),
            "RELOCATING": RelocatingState(),
        }
        self._current_state = self._states["IDLE"]
        self.state: str = "IDLE"

    def _current_room(self):
        """Resolve the RoomDefinition the NPC currently occupies (or None if neutral/
        unavailable). Uses tile_map region tags → RoomRegistry, same path as ZoneTracker."""
        if self.rooms is None:
            return None
        col, row = self.tile_map.world_to_grid(self.npc.x, self.npc.y)
        region = self.tile_map.get_region(col, row)
        panel_x = getattr(self.npc, "panel_x", 0)
        panel_y = getattr(self.npc, "panel_y", 0)
        return self.rooms.get_room_for_region(panel_x, panel_y, region)

    def _set_state(self, name: str) -> None:
        self.state = name
        self._current_state = self._states[name]
        self._current_state.enter(self)

    def _start_satisfying(self, source: NeedSource) -> None:
        self.target_source = source
        self._set_state("SATISFYING")
        print(f"[ARRIVE] {self.npc.name} reached {source.label} -- satisfying {source.need_id}")

    def update(self, dt: float,
               occupied_tiles: set[tuple[int, int]] | None = None) -> None:
        self._tick += 1
        self._occupied = occupied_tiles or set()

        # 1. Tick needs
        is_sleeping = (self.state == "SATISFYING" and
                       self.target_source is not None and
                       self.target_source.need_id == "sleep")
        update_needs(self.needs, is_sleeping=is_sleeping)

        # 2. Update biochem + trait decay
        self.brain.tick(self.needs)
        self.brain.traits.decay_toward_neutral()

        # 2b. Affinity comfort emitter — sample current region, write comfort/stress,
        #     and learn this region's comfort (EMA) so lived experience shapes relocation.
        room = self._current_room()
        self.affinity_comfort = self._affinity_emitter.emit(
            self.brain.chemicals, self.npc, room)
        if room is not None:
            self.memory.record_region_comfort(room.id, self.affinity_comfort, self._tick)
        self.best_region = self.memory.best_region()

        # 3. Log zone transitions
        self._logger.check_zone_changes(self.needs)

        # 4. State machine
        self._current_state.update(self, dt)

        # 5. Periodic console log — disabled, HUD covers this now
        # if self._tick % settings.LOG_INTERVAL == 0:
        #     self._logger.log_needs(self.needs, self.npc, self.state, self._tick)
