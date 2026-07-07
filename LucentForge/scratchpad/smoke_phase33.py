"""Phase 3.3 smoke test — ZoneCrossingEvent + ZoneTracker.

Run from LucentForge directory: py smoke_phase33.py
Uses mock tile_map / rooms objects — no pygame display required.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS  {label}")
        passed += 1
    else:
        print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))
        failed += 1


# ── Minimal mocks ────────────────────────────────────────────────────────────

class MockEntity:
    def __init__(self, name, col, row, tile_size=32):
        self.name = name
        self.x = col * tile_size + tile_size // 2
        self.y = row * tile_size + tile_size // 2


class MockRoom:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"<Room {self.name}>"


FOREST_ROOM  = MockRoom("Forest")
TOWN_ROOM    = MockRoom("Town Outskirts")
GOBLIN_ROOM  = MockRoom("Goblin Camp")

REGION_MAP = {
    "forest":         FOREST_ROOM,
    "town_outskirts": TOWN_ROOM,
    "goblin_camp":    GOBLIN_ROOM,
}


class MockTileMap:
    TILE = 32

    def world_to_grid(self, x, y):
        return (int(x // self.TILE), int(y // self.TILE))

    def get_region(self, col, row):
        if col < 6:
            return "forest"
        if col >= 14:
            return "goblin_camp"
        return "town_outskirts"


class MockRooms:
    def get_room_for_region(self, panel_x, panel_y, region):
        return REGION_MAP.get(region)


tile_map = MockTileMap()
rooms    = MockRooms()


# ── Group 1: ZoneCrossingEvent dataclass ─────────────────────────────────────
print("\n[1] ZoneCrossingEvent")
from Mechanics.world.zone_events import ZoneCrossingEvent, ZoneTracker

evt = ZoneCrossingEvent("Grom", FOREST_ROOM, TOWN_ROOM, tick=1200)
check("entity_name", evt.entity_name == "Grom")
check("from_room",   evt.from_room is FOREST_ROOM)
check("to_room",     evt.to_room is TOWN_ROOM)
check("tick",        evt.tick == 1200)

# ── Group 2: first call — no event (cache init only) ─────────────────────────
print("\n[2] First call initializes cache silently")
tracker = ZoneTracker()
fired = []
tracker.subscribe(fired.append)

grom = MockEntity("Grom", col=2, row=10)  # forest region
events = tracker.check_and_fire([grom], tile_map, rooms, 0, 0, tick=1)
check("no events on first call", len(events) == 0)
check("cache seeded",            "Grom" in tracker._current_rooms)
check("cached room is Forest",   tracker._current_rooms["Grom"] is FOREST_ROOM)
check("no callback fired",       len(fired) == 0)

# ── Group 3: same room — no event ────────────────────────────────────────────
print("\n[3] Same room — no event")
grom.x = 3 * 32 + 16  # still forest (col 3)
events = tracker.check_and_fire([grom], tile_map, rooms, 0, 0, tick=10)
check("no events (still forest)", len(events) == 0)
check("no callback fired",        len(fired) == 0)

# ── Group 4: room change — event fires ───────────────────────────────────────
print("\n[4] Room change fires exactly one event")
grom.x = 10 * 32 + 16  # town_outskirts (col 10)
events = tracker.check_and_fire([grom], tile_map, rooms, 0, 0, tick=100)
check("one event fired",             len(events) == 1)
check("callback fired once",         len(fired) == 1)
check("from_room is Forest",         events[0].from_room is FOREST_ROOM)
check("to_room is Town",             events[0].to_room is TOWN_ROOM)
check("entity_name is Grom",         events[0].entity_name == "Grom")
check("tick is 100",                 events[0].tick == 100)
check("cache updated to Town",       tracker._current_rooms["Grom"] is TOWN_ROOM)

# ── Group 5: crossing again does not re-fire (edge-triggered) ─────────────────
print("\n[5] No re-fire while in same room")
grom.x = 11 * 32 + 16  # still town_outskirts (col 11)
events = tracker.check_and_fire([grom], tile_map, rooms, 0, 0, tick=110)
check("no events (same room)", len(events) == 0)
check("callback count still 1", len(fired) == 1)

# ── Group 6: second crossing fires again ─────────────────────────────────────
print("\n[6] Second crossing fires new event")
grom.x = 15 * 32 + 16  # goblin_camp (col 15)
events = tracker.check_and_fire([grom], tile_map, rooms, 0, 0, tick=200)
check("one event fired",          len(events) == 1)
check("callback count now 2",     len(fired) == 2)
check("from_room is Town",        events[0].from_room is TOWN_ROOM)
check("to_room is GoblinCamp",    events[0].to_room is GOBLIN_ROOM)
check("tick 200",                 events[0].tick == 200)

# ── Group 7: multiple entities tracked independently ─────────────────────────
print("\n[7] Multiple entities — independent tracking")
tracker2 = ZoneTracker()
fired2 = []
tracker2.subscribe(fired2.append)

alder  = MockEntity("Alder",  col=2,  row=5)   # forest
player = MockEntity("Player", col=10, row=8)   # town_outskirts

# First call — init both
tracker2.check_and_fire([alder, player], tile_map, rooms, 0, 0, tick=1)
check("no events on init", len(fired2) == 0)

# Alder moves to town; player stays in town
alder.x = 10 * 32 + 16
events = tracker2.check_and_fire([alder, player], tile_map, rooms, 0, 0, tick=50)
check("one event (Alder only)", len(events) == 1)
check("Alder crossed",          events[0].entity_name == "Alder")
check("player not in events",   all(e.entity_name != "Player" for e in events))

# ── Group 8: None room (unmapped region) ─────────────────────────────────────
print("\n[8] None room (unmapped region) — no crash")
class MockRoomsEmpty:
    def get_room_for_region(self, panel_x, panel_y, region):
        return None

tracker3 = ZoneTracker()
fired3 = []
tracker3.subscribe(fired3.append)
entity3 = MockEntity("Xray", col=2, row=2)
tracker3.check_and_fire([entity3], tile_map, MockRoomsEmpty(), 0, 0, tick=1)
entity3.x = 10 * 32 + 16
events = tracker3.check_and_fire([entity3], tile_map, MockRoomsEmpty(), 0, 0, tick=5)
# from_room=None, to_room=None — no event since both None (same room = no change)
check("both None = no event (still None->None)", len(events) == 0)

# ── Group 9: WorldSim owns zone_tracker ──────────────────────────────────────
print("\n[9] WorldSim.zone_tracker wiring")
# Import WorldSim without pygame display (it doesn't need one at import time)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
from Mechanics.world.world_sim import WorldSim
ws = WorldSim()
check("zone_tracker attribute exists", hasattr(ws, "zone_tracker"))
check("zone_tracker is ZoneTracker",   isinstance(ws.zone_tracker, ZoneTracker))
sub_fired = []
ws.zone_tracker.subscribe(sub_fired.append)
check("subscribe works on world_sim.zone_tracker", True)

# ── Group 10: log_spatial_zone callback format ────────────────────────────────
print("\n[10] log_spatial_zone output format")
import io, contextlib
from Mechanics.ai.npc_logger import log_spatial_zone
evt2 = ZoneCrossingEvent("Grom", FOREST_ROOM, TOWN_ROOM, tick=1200)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    log_spatial_zone(evt2)
line = buf.getvalue().strip()
check("[ZONE] prefix",       line.startswith("[ZONE]"))
check("entity name present", "Grom" in line)
check("room name present",   "Town Outskirts" in line)
check("tick present",        "1200" in line)

# to_room=None case
evt3 = ZoneCrossingEvent("Grom", TOWN_ROOM, None, tick=999)
buf2 = io.StringIO()
with contextlib.redirect_stdout(buf2):
    log_spatial_zone(evt3)
line2 = buf2.getvalue().strip()
check("to_room=None -> 'Unknown'", "Unknown" in line2)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*48}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 3.3 smoke CLEAN")
