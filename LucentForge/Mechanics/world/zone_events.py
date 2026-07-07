from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from Mechanics.world.rooms import RoomDefinition, RoomRegistry
    from Mechanics.world.tile_map import TileMap


@dataclass
class ZoneCrossingEvent:
    entity_name: str
    from_room:   "RoomDefinition | None"
    to_room:     "RoomDefinition | None"
    tick:        int


class ZoneTracker:
    """Observer hub for spatial room transitions.

    Edge-triggered: fires on room change, not every tick.
    Tracks player + all NPCs by entity.name.

    Usage:
        tracker.subscribe(my_callback)
        events = tracker.check_and_fire(entities, tile_map, rooms, 0, 0, tick)
    """

    def __init__(self) -> None:
        self._current_rooms: dict[str, "RoomDefinition | None"] = {}
        self._callbacks: list[Callable[[ZoneCrossingEvent], None]] = []

    def subscribe(self, callback: Callable[[ZoneCrossingEvent], None]) -> None:
        self._callbacks.append(callback)

    def check_and_fire(
        self,
        entities: list,
        tile_map: "TileMap",
        rooms: "RoomRegistry",
        panel_x: int,
        panel_y: int,
        tick: int,
    ) -> list[ZoneCrossingEvent]:
        """Check each entity's current room; fire callbacks on change.

        Returns list of events fired this call.
        First call per entity: initializes cache silently (no event).
        """
        events: list[ZoneCrossingEvent] = []
        for entity in entities:
            col, row = tile_map.world_to_grid(entity.x, entity.y)
            region = tile_map.get_region(col, row)
            current = rooms.get_room_for_region(panel_x, panel_y, region)

            if entity.name not in self._current_rooms:
                self._current_rooms[entity.name] = current
                continue

            cached = self._current_rooms[entity.name]
            if current is cached:
                continue

            event = ZoneCrossingEvent(
                entity_name=entity.name,
                from_room=cached,
                to_room=current,
                tick=tick,
            )
            self._current_rooms[entity.name] = current
            events.append(event)
            for cb in self._callbacks:
                cb(event)

        return events
