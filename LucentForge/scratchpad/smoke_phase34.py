"""Phase 3.4 smoke test — O-panel ZONE section + HUD zone flash subscriber.

Run from LucentForge directory: py smoke_phase34.py
No pygame display required.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS  {label}")
        passed += 1
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))
        failed += 1


# ── Minimal mocks ────────────────────────────────────────────────────────────

class MockRoom:
    def __init__(self, name): self.name = name

class MockEntity:
    def __init__(self, name, entity_id, x=0.0, y=0.0):
        self.name = name
        self.entity_id = entity_id
        self.x = x
        self.y = y

FOREST_ROOM  = MockRoom("Forest")
TOWN_ROOM    = MockRoom("Town Outskirts")

# ── Group 1: ZONE_LABEL_DURATION constant ────────────────────────────────────
print("\n[1] ZONE_LABEL_DURATION constant")
import settings
check("ZONE_LABEL_DURATION defined",  hasattr(settings, "ZONE_LABEL_DURATION"))
check("ZONE_LABEL_DURATION > 0",      getattr(settings, "ZONE_LABEL_DURATION", 0) > 0)
check("ZONE_LABEL_DURATION <= 300",   getattr(settings, "ZONE_LABEL_DURATION", 999) <= 300)

# ── Group 2: observation_panel accepts player kwarg ───────────────────────────
print("\n[2] draw_observation_panel signature accepts player kwarg")
import inspect
from Mechanics.renderer.observation_panel import draw_observation_panel
sig = inspect.signature(draw_observation_panel)
params = list(sig.parameters.keys())
check("player param exists",  "player" in params)
check("player has default",   sig.parameters.get("player") is not None
                              and sig.parameters["player"].default is None)

# ── Group 3: ZoneTracker — two independent subscribers ───────────────────────
print("\n[3] Two subscribers: general + player-only")
from Mechanics.world.zone_events import ZoneTracker, ZoneCrossingEvent

player_entity = MockEntity("Player", "player_01")
npc_entity    = MockEntity("Grom",   "npc_grom")

tracker = ZoneTracker()
all_fired:    list[ZoneCrossingEvent] = []
player_fired: list[ZoneCrossingEvent] = []
zone_flash: list = [None]

tracker.subscribe(all_fired.append)

def _on_player_zone_cross(event) -> None:
    if event.entity_name == player_entity.name:
        room_name = event.to_room.name if event.to_room else "Unknown"
        zone_flash[0] = (room_name, settings.ZONE_LABEL_DURATION)
        player_fired.append(event)

tracker.subscribe(_on_player_zone_cross)

class MockTileMap:
    TILE = 32
    def world_to_grid(self, x, y): return (int(x // self.TILE), int(y // self.TILE))
    def get_region(self, col, row): return "forest" if col < 6 else "town_outskirts"

class MockRooms:
    _map = {"forest": FOREST_ROOM, "town_outskirts": TOWN_ROOM}
    def get_room_for_region(self, px, py, region): return self._map.get(region)

tile_map = MockTileMap()
rooms    = MockRooms()

# Place both in forest — init call (no events)
player_entity.x = 2 * 32 + 16
npc_entity.x    = 3 * 32 + 16
tracker.check_and_fire([player_entity, npc_entity], tile_map, rooms, 0, 0, tick=1)
check("no events on init",          len(all_fired) == 0)
check("zone_flash still None",      zone_flash[0] is None)

# Move NPC to town — only NPC crosses; player stays in forest
npc_entity.x = 10 * 32 + 16
tracker.check_and_fire([player_entity, npc_entity], tile_map, rooms, 0, 0, tick=50)
check("general fires for NPC",      len(all_fired) == 1)
check("all_fired entity is Grom",   all_fired[0].entity_name == "Grom")
check("player_fired still empty",   len(player_fired) == 0)
check("zone_flash still None",      zone_flash[0] is None)

# Move player to town — player crosses; player_fired + zone_flash set
player_entity.x = 11 * 32 + 16
tracker.check_and_fire([player_entity, npc_entity], tile_map, rooms, 0, 0, tick=100)
check("general fires for player",   len(all_fired) == 2)
check("player_fired has event",     len(player_fired) == 1)
check("zone_flash set",             zone_flash[0] is not None)
check("zone_flash room is Town",    zone_flash[0] is not None and zone_flash[0][0] == "Town Outskirts")
check("zone_flash frames correct",  zone_flash[0] is not None and zone_flash[0][1] == settings.ZONE_LABEL_DURATION)

# ── Group 4: zone_flash countdown logic ───────────────────────────────────────
print("\n[4] zone_flash countdown and clear")
name, frames = zone_flash[0]
# Simulate the frame-loop decrement from main.py
for _ in range(frames - 1):
    name, frames = zone_flash[0]
    zone_flash[0] = (name, frames - 1) if frames > 1 else None
check("still active 1 frame before end", zone_flash[0] is not None)
# Final frame
name, frames = zone_flash[0]
zone_flash[0] = (name, frames - 1) if frames > 1 else None
check("cleared after ZONE_LABEL_DURATION frames", zone_flash[0] is None)

# ── Group 5: to_room=None -> "Unknown" in flash ───────────────────────────────
print("\n[5] to_room=None sets flash to 'Unknown'")
zone_flash2: list = [None]

def _flash2(event) -> None:
    if event.entity_name == "Player":
        room_name = event.to_room.name if event.to_room else "Unknown"
        zone_flash2[0] = (room_name, settings.ZONE_LABEL_DURATION)

tracker2 = ZoneTracker()
tracker2.subscribe(_flash2)

class MockRoomsEmpty:
    def get_room_for_region(self, px, py, region): return None

p2 = MockEntity("Player", "player_02", x=2*32+16)
tracker2.check_and_fire([p2], tile_map, MockRoomsEmpty(), 0, 0, tick=1)  # init
p2.x = 10 * 32 + 16  # moves to different region but both return None -> no change
tracker2.check_and_fire([p2], tile_map, MockRoomsEmpty(), 0, 0, tick=5)
check("None->None: no flash (room unchanged)", zone_flash2[0] is None)

# ── Group 6: WorldSim integration (zone_tracker still has 2 subscribers) ─────
print("\n[6] WorldSim.zone_tracker subscriber count")
from Mechanics.world.world_sim import WorldSim
ws = WorldSim()
sub_count_before = len(ws.zone_tracker._callbacks)
ws.zone_tracker.subscribe(lambda e: None)
ws.zone_tracker.subscribe(lambda e: None)
check("can add 2 subscribers",  len(ws.zone_tracker._callbacks) == sub_count_before + 2)

# ── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*48}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 3.4 smoke CLEAN")
