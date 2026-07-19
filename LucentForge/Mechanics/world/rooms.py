"""rooms.py — Room data layer: RoomType, RoomDefinition, RoomRegistry.

Stage 3, Phase 3.1. Loads rooms.json; no DB dependency, no gameplay change.
Region tags from tile_map._assign_regions() are the bridge between the two systems.
"""
from __future__ import annotations
import enum
import json
from dataclasses import dataclass

from Mechanics.entities.affinity import Affinity


class RoomType(enum.Enum):
    WILDERNESS       = "WILDERNESS"
    SETTLEMENT       = "SETTLEMENT"
    GOBLIN_TERRITORY = "GOBLIN_TERRITORY"
    BRIDGE           = "BRIDGE"
    FARM             = "FARM"
    STORAGE          = "STORAGE"
    RIVER            = "RIVER"


@dataclass(frozen=True)
class RoomDefinition:
    id:          str
    name:        str
    room_type:   RoomType
    description: str
    panel_x:     int
    panel_y:     int
    tile_bounds: tuple[int, int, int, int]  # col_min, row_min, col_max, row_max
    region_tag:  str                         # matches tile_map.get_region() output
    # Environment affinity field (§M5): None = elementally neutral. Intensity 0..1
    # scales the like-affinity casting bonus (consumed by affinity combat in 4.6).
    affinity:           Affinity | None = None
    affinity_intensity: float = 0.0


class RoomRegistry:
    """Loads RoomDefinition objects from rooms.json and provides tile-based queries.

    Three lookup strategies:
    - get_by_id()          — O(1) by room ID string
    - get_room_for_region() — O(1) by tile_map region tag (preferred in ZoneTracker)
    - get_room_for_tile()  — bounding-box approximation; check smallest rooms first
    """

    def __init__(self) -> None:
        self._rooms: list[RoomDefinition] = []
        self._by_id: dict[str, RoomDefinition] = {}
        self._by_panel: dict[tuple[int, int], list[RoomDefinition]] = {}
        # (panel_x, panel_y, region_tag) → RoomDefinition
        self._by_region: dict[tuple[int, int, str], RoomDefinition] = {}

    @classmethod
    def from_json(cls, path: str) -> "RoomRegistry":
        registry = cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            room = RoomDefinition(
                id=entry["id"],
                name=entry["name"],
                room_type=RoomType(entry["room_type"]),
                description=entry["description"],
                panel_x=entry["panel_x"],
                panel_y=entry["panel_y"],
                tile_bounds=tuple(entry["tile_bounds"]),
                region_tag=entry["region_tag"],
                affinity=(Affinity(entry["affinity"]) if entry.get("affinity") else None),
                affinity_intensity=entry.get("affinity_intensity", 0.0),
            )
            registry._rooms.append(room)
            registry._by_id[room.id] = room
            registry._by_panel.setdefault((room.panel_x, room.panel_y), []).append(room)
            registry._by_region[(room.panel_x, room.panel_y, room.region_tag)] = room
        return registry

    # --- Public API ---

    def get_by_id(self, room_id: str) -> RoomDefinition | None:
        return self._by_id.get(room_id)

    def get_rooms_for_panel(self, panel_x: int, panel_y: int) -> list[RoomDefinition]:
        return self._by_panel.get((panel_x, panel_y), [])

    def get_room_for_tile(self, panel_x: int, panel_y: int,
                          col: int, row: int) -> RoomDefinition | None:
        """Return the room containing (col, row) using a tile_bounds bounding-box check.

        Checks smallest rooms first so specific overlay zones (goblin_camp, storage, etc.)
        win over broad base regions. Accurate for rectangular zones; approximate for the
        winding river and bridge which share overlapping bounding boxes.

        Prefer get_room_for_region() in ZoneTracker where the tile_map region tag is known.
        """
        candidates = self.get_rooms_for_panel(panel_x, panel_y)
        ordered = sorted(
            candidates,
            key=lambda r: (r.tile_bounds[2] - r.tile_bounds[0] + 1)
                        * (r.tile_bounds[3] - r.tile_bounds[1] + 1),
        )
        for room in ordered:
            cmin, rmin, cmax, rmax = room.tile_bounds
            if cmin <= col <= cmax and rmin <= row <= rmax:
                return room
        return None

    def get_room_for_region(self, panel_x: int, panel_y: int,
                             region_tag: str) -> RoomDefinition | None:
        """Return room by tile_map region tag. O(1); use this in ZoneTracker."""
        return self._by_region.get((panel_x, panel_y, region_tag))

    def center_tile(self, room_id: str) -> tuple[int, int] | None:
        """Center (col, row) of a room's tile_bounds — the relocate aim point (Phase B).

        The caller pathfinds toward it (and to the nearest free tile if the exact center
        is blocked), so an approximate center is fine for the winding river/bridge.
        """
        room = self._by_id.get(room_id)
        if room is None:
            return None
        cmin, rmin, cmax, rmax = room.tile_bounds
        return ((cmin + cmax) // 2, (rmin + rmax) // 2)
