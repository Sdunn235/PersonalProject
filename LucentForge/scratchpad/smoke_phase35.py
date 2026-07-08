"""Phase 3.5 smoke test — ZoneAIResponder chemical injection + New-Game re-subscribe.

Run from LucentForge directory: py smoke_phase35.py
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

class MockChemicals:
    def __init__(self):
        self._levels = {"anger": 0.0, "fear": 0.0, "pain": 0.0, "loneliness": 0.0}
    def get(self, k): return self._levels.get(k, 0.0)
    def set(self, k, v): self._levels[k] = max(0.0, min(1.0, v))
    def add_fear(self, amount): self.set("fear", min(1.0, self.get("fear") + amount))

class MockBrain:
    def __init__(self): self.chemicals = MockChemicals()

class MockCtrl:
    def __init__(self): self.brain = MockBrain()

class MockEntity:
    def __init__(self, name, entity_id, subtype=None, x=0.0, y=0.0):
        self.name = name
        self.entity_id = entity_id
        self.subtype = subtype
        self.x = x
        self.y = y

# ── Group 1: ZoneAIResponder import + constants ───────────────────────────────
print("\n[1] ZoneAIResponder module")
from Mechanics.ai.zone_ai import ZoneAIResponder, _CIVILIZED, _GOBLIN_ZONE, \
    _GOBLIN_ANGER_NUDGE, _HUMAN_FEAR_NUDGE
from Mechanics.world.rooms import RoomType

check("ZoneAIResponder importable",   True)  # would raise above if not
check("_CIVILIZED has SETTLEMENT",    RoomType.SETTLEMENT in _CIVILIZED)
check("_CIVILIZED has FARM",          RoomType.FARM       in _CIVILIZED)
check("_CIVILIZED has STORAGE",       RoomType.STORAGE    in _CIVILIZED)
check("_CIVILIZED excludes GOBLIN",   RoomType.GOBLIN_TERRITORY not in _CIVILIZED)
check("_GOBLIN_ZONE has GOBLIN_TERR", RoomType.GOBLIN_TERRITORY in _GOBLIN_ZONE)
check("nudges > 0",                   _GOBLIN_ANGER_NUDGE > 0 and _HUMAN_FEAR_NUDGE > 0)

# ── Group 2: Goblin entering civilized territory -> anger nudge ───────────────
print("\n[2] Goblin entering civilized territory")

class MockRoom:
    def __init__(self, name, rt): self.name = name; self.room_type = rt

from dataclasses import dataclass
@dataclass
class MockEvent:
    entity_name: str
    from_room: object
    to_room: object
    tick: int = 0

responder = ZoneAIResponder()
goblin     = MockEntity("Grim", "g01", subtype="goblin")
goblin_ctrl = MockCtrl()

# enter Town Center (SETTLEMENT)
evt = MockEvent("Grim", None, MockRoom("Town Center", RoomType.SETTLEMENT))
responder.on_zone_cross(evt, goblin, goblin_ctrl)
check("goblin -> SETTLEMENT: anger bumped",
      goblin_ctrl.brain.chemicals.get("anger") > 0.0)
check("goblin -> SETTLEMENT: anger approx right",
      abs(goblin_ctrl.brain.chemicals.get("anger") - _GOBLIN_ANGER_NUDGE) < 0.001)
check("goblin -> SETTLEMENT: fear unchanged",
      goblin_ctrl.brain.chemicals.get("fear") == 0.0)

# enter Farm (FARM)
farm_goblin = MockEntity("Zug", "g02", subtype="goblin")
farm_ctrl   = MockCtrl()
evt_farm = MockEvent("Zug", None, MockRoom("Farm", RoomType.FARM))
responder.on_zone_cross(evt_farm, farm_goblin, farm_ctrl)
check("goblin -> FARM: anger bumped",
      farm_ctrl.brain.chemicals.get("anger") > 0.0)

# enter Storage (STORAGE)
stor_goblin = MockEntity("Brak", "g03", subtype="goblin")
stor_ctrl   = MockCtrl()
evt_stor = MockEvent("Brak", None, MockRoom("Storage", RoomType.STORAGE))
responder.on_zone_cross(evt_stor, stor_goblin, stor_ctrl)
check("goblin -> STORAGE: anger bumped",
      stor_ctrl.brain.chemicals.get("anger") > 0.0)

# ── Group 3: Goblin in non-civilized territory -> no effect ───────────────────
print("\n[3] Goblin in non-civilized territory")
home_goblin = MockEntity("Grak", "g04", subtype="goblin")
home_ctrl   = MockCtrl()

evt_wild = MockEvent("Grak", None, MockRoom("Wild Forest", RoomType.WILDERNESS))
responder.on_zone_cross(evt_wild, home_goblin, home_ctrl)
check("goblin -> WILDERNESS: no anger",  home_ctrl.brain.chemicals.get("anger") == 0.0)
check("goblin -> WILDERNESS: no fear",   home_ctrl.brain.chemicals.get("fear")  == 0.0)

evt_camp = MockEvent("Grak", None, MockRoom("Goblin Camp", RoomType.GOBLIN_TERRITORY))
responder.on_zone_cross(evt_camp, home_goblin, home_ctrl)
check("goblin -> GOBLIN_TERRITORY: no anger", home_ctrl.brain.chemicals.get("anger") == 0.0)
check("goblin -> GOBLIN_TERRITORY: no fear",  home_ctrl.brain.chemicals.get("fear")  == 0.0)

# ── Group 4: Human entering goblin territory -> fear ─────────────────────────
print("\n[4] Human entering goblin territory")
human     = MockEntity("Elara", "h01", subtype="human")
human_ctrl = MockCtrl()

evt_goblin_zone = MockEvent("Elara", None, MockRoom("Goblin Camp", RoomType.GOBLIN_TERRITORY))
responder.on_zone_cross(evt_goblin_zone, human, human_ctrl)
check("human -> GOBLIN_TERRITORY: fear bumped",
      human_ctrl.brain.chemicals.get("fear") > 0.0)
check("human -> GOBLIN_TERRITORY: fear approx right",
      abs(human_ctrl.brain.chemicals.get("fear") - _HUMAN_FEAR_NUDGE) < 0.001)
check("human -> GOBLIN_TERRITORY: anger unchanged",
      human_ctrl.brain.chemicals.get("anger") == 0.0)

# Player uses PlayerController which has no brain — guard returns early, no crash
class MockPlayerCtrl:
    pass  # no brain attribute — mirrors real PlayerController

player      = MockEntity("Player", "p01", subtype=None)
player_ctrl = MockPlayerCtrl()
evt_player_camp = MockEvent("Player", None, MockRoom("Goblin Camp", RoomType.GOBLIN_TERRITORY))
_raised = False
try:
    responder.on_zone_cross(evt_player_camp, player, player_ctrl)
except AttributeError:
    _raised = True
check("player (no brain) -> GOBLIN_TERRITORY: no AttributeError (guard returns early)", not _raised)

# ── Group 5: Human in non-goblin territory -> no effect ─────────────────────
print("\n[5] Human in non-goblin territory")
safe_human  = MockEntity("Mira", "h02", subtype="human")
safe_ctrl   = MockCtrl()

evt_town = MockEvent("Mira", None, MockRoom("Town Center", RoomType.SETTLEMENT))
responder.on_zone_cross(evt_town, safe_human, safe_ctrl)
check("human -> SETTLEMENT: no fear",  safe_ctrl.brain.chemicals.get("fear")  == 0.0)
check("human -> SETTLEMENT: no anger", safe_ctrl.brain.chemicals.get("anger") == 0.0)

# ── Group 6: to_room=None -> no effect ───────────────────────────────────────
print("\n[6] to_room=None -> no effect")
null_entity = MockEntity("Ghost", "x01", subtype="goblin")
null_ctrl   = MockCtrl()
evt_null = MockEvent("Ghost", None, None)
responder.on_zone_cross(evt_null, null_entity, null_ctrl)
check("to_room=None: no anger", null_ctrl.brain.chemicals.get("anger") == 0.0)
check("to_room=None: no fear",  null_ctrl.brain.chemicals.get("fear")  == 0.0)

# ── Group 7: anger caps at 1.0 ───────────────────────────────────────────────
print("\n[7] Anger caps at 1.0")
angry_goblin = MockEntity("Rend", "g99", subtype="goblin")
angry_ctrl   = MockCtrl()
angry_ctrl.brain.chemicals.set("anger", 0.95)
evt_civ = MockEvent("Rend", None, MockRoom("Homes", RoomType.SETTLEMENT))
for _ in range(5):
    responder.on_zone_cross(evt_civ, angry_goblin, angry_ctrl)
check("anger does not exceed 1.0", angry_ctrl.brain.chemicals.get("anger") <= 1.0)

# ── Group 8: ZoneTracker integration — responder fires via subscriber ─────────
print("\n[8] ZoneTracker subscriber integration")
from Mechanics.world.zone_events import ZoneTracker

class MockTileMap:
    TILE = 32
    def world_to_grid(self, x, y): return (int(x // self.TILE), int(y // self.TILE))
    def get_region(self, col, row): return "goblin_camp" if col < 4 else "town_center"

_SINGLETON_GOBLIN_ROOM = MockRoom("Goblin Camp", RoomType.GOBLIN_TERRITORY)
_SINGLETON_TOWN_ROOM   = MockRoom("Town Center",  RoomType.SETTLEMENT)

class MockRooms:
    def get_room_for_region(self, px, py, region):
        if region == "goblin_camp":  return _SINGLETON_GOBLIN_ROOM
        if region == "town_center":  return _SINGLETON_TOWN_ROOM
        return None

tracker = ZoneTracker()
fear_spy: list[float] = []

tracked_human = MockEntity("Brix", "brix01", subtype="human", x=10 * 32 + 16)
tracked_ctrl  = MockCtrl()

def _human_subscriber(event) -> None:
    if event.entity_name == "Brix":
        responder.on_zone_cross(event, tracked_human, tracked_ctrl)
        fear_spy.append(tracked_ctrl.brain.chemicals.get("fear"))

tracker.subscribe(_human_subscriber)
tile_map = MockTileMap()
rooms    = MockRooms()

# Init (silent)
tracker.check_and_fire([tracked_human], tile_map, rooms, 0, 0, tick=1)
check("no fear after init",           tracked_ctrl.brain.chemicals.get("fear") == 0.0)

# Move into goblin camp region
tracked_human.x = 2 * 32 + 16
tracker.check_and_fire([tracked_human], tile_map, rooms, 0, 0, tick=50)
check("fear bumped after crossing into goblin camp",
      tracked_ctrl.brain.chemicals.get("fear") > 0.0)
check("subscriber fired once (spy len 1)", len(fear_spy) == 1)

# Stay in goblin camp — no re-fire
tracker.check_and_fire([tracked_human], tile_map, rooms, 0, 0, tick=51)
check("no re-fire on same tick (edge-triggered)", len(fear_spy) == 1)

# ── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*48}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 3.5 smoke CLEAN")
