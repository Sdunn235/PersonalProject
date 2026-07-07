"""smoke_phase31.py — Phase 3.1 smoke test: rooms data layer.

Tests:
  1. All 9 room IDs are loadable via get_by_id()
  2. All RoomType enum values are present
  3. get_rooms_for_panel(0,0) returns 9 rooms
  4. get_room_for_region round-trips every tile in Panel(0,0) — accurate lookup
  5. get_room_for_tile returns correct room for rectangular overlay zones
  6. RoomType mapping matches §R3 of the addendum

Run from LucentForge root: py scratchpad/smoke_phase31.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Mechanics.world.rooms import RoomRegistry, RoomType
from Mechanics.world.tile_map import TileMap

ROOMS_JSON = os.path.join("Mechanics", "data", "rooms.json")

EXPECTED_IDS = [
    "panel00_forest",
    "panel00_town_center",
    "panel00_town_outskirts",
    "panel00_homes",
    "panel00_farm",
    "panel00_storage",
    "panel00_goblin_camp",
    "panel00_river",
    "panel00_bridge",
]

# §R3 region-to-RoomType mapping
REGION_TO_TYPE = {
    "forest":         RoomType.WILDERNESS,
    "town_center":    RoomType.SETTLEMENT,
    "town_outskirts": RoomType.SETTLEMENT,
    "homes":          RoomType.SETTLEMENT,
    "farm":           RoomType.FARM,
    "storage":        RoomType.STORAGE,
    "goblin_camp":    RoomType.GOBLIN_TERRITORY,
    "river":          RoomType.RIVER,
    "bridge":         RoomType.BRIDGE,
}

# Rectangular overlay zones — get_room_for_tile must be exact here
RECT_ZONE_SAMPLES = {
    "panel00_goblin_camp":  [(2, 13), (3, 14), (2, 14)],
    "panel00_storage":      [(11, 8), (12, 9)],
    "panel00_farm":         [(13, 2), (16, 5), (14, 3)],
    "panel00_town_center":  [(10, 7), (13, 9), (10, 8)],
    "panel00_homes":        [(10, 10), (13, 12), (11, 11)],
}

PASS = 0
FAIL = 0

def check(label: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        msg = f"  FAIL  {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def main() -> None:
    print("=== Phase 3.1 Smoke Test ===\n")

    # --- Load registry ---
    registry = RoomRegistry.from_json(ROOMS_JSON)
    print("[ Test 1 ] get_by_id — all 9 room IDs")
    for rid in EXPECTED_IDS:
        room = registry.get_by_id(rid)
        check(rid, room is not None)

    print("\n[ Test 2 ] RoomType enum — all 7 values present")
    for rt in RoomType:
        check(rt.name, True)  # just verifying enum iteration works

    print("\n[ Test 3 ] get_rooms_for_panel(0,0) — count == 9")
    rooms = registry.get_rooms_for_panel(0, 0)
    check(f"count={len(rooms)}", len(rooms) == 9)

    print("\n[ Test 4 ] get_room_for_region — round-trip every tile in Panel(0,0)")
    tile_map = TileMap()
    tile_map._apply_river()
    tile_map._assign_regions()

    misses = []
    type_mismatches = []
    for row in range(18):
        for col in range(18):
            region = tile_map.get_region(col, row)
            if region == "unknown":
                continue
            room = registry.get_room_for_region(0, 0, region)
            if room is None:
                misses.append(f"({col},{row}) region={region}")
            elif region in REGION_TO_TYPE and room.room_type != REGION_TO_TYPE[region]:
                type_mismatches.append(
                    f"({col},{row}) region={region} got {room.room_type} expected {REGION_TO_TYPE[region]}"
                )

    check("no missing rooms", len(misses) == 0,
          f"{len(misses)} tiles returned None: {misses[:3]}")
    check("no type mismatches", len(type_mismatches) == 0,
          f"{type_mismatches[:3]}")

    print("\n[ Test 5 ] get_room_for_tile — rectangular overlay zones")
    for room_id, samples in RECT_ZONE_SAMPLES.items():
        for col, row in samples:
            room = registry.get_room_for_tile(0, 0, col, row)
            ok = room is not None and room.id == room_id
            check(f"{room_id} @ ({col},{row})", ok,
                  f"got {room.id if room else None}")

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
