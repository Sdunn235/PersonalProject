# run_panel_data_tests.py — panels are DATA (Arc B, BACKLOG LF-010 step 1).
#
# The starting panel used to be built by code (TileMap's Heartbeat-2 procedural builder). Arc B's map
# loader needs every panel to be a data file, so new panels are content, not code. These checks pin:
#   1. panels.json points Panel(0,0) at a map file that exists and reads as 18 rows x 18 tiles;
#   2. the data panel is IDENTICAL to the old procedural one (characterization: tiles, blocking,
#      regions, rock/tree art, need sources, rendered pixels) — the move changes nothing in play;
#   3. the game loads Panel(0,0) from data (the procedural builder is not called at runtime).
#
#   py scratchpad/run_panel_data_tests.py
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness.headless import quiet  # noqa: E402  (sets SDL dummy drivers + sys.path)

import pygame  # noqa: E402
import settings  # noqa: E402
from Mechanics.world.tile_map import TileMap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


print("=" * 64)
print("Panel data tests - Panel(0,0) as data, identical to the procedural map")
print("=" * 64)
pygame.init()
if pygame.display.get_surface() is None:
    pygame.display.set_mode((1, 1))

panels = json.load(open(os.path.join(ROOT, "Mechanics", "data", "panels.json"), encoding="utf-8"))
p00 = next((p for p in panels if p["panel_x"] == 0 and p["panel_y"] == 0), None)
map_rel = (p00 or {}).get("map")
map_path = os.path.join(ROOT, "Mechanics", "data", map_rel) if map_rel else None
check("panels.json gives Panel(0,0) a map file", bool(map_rel))
check("the map file exists", bool(map_path) and os.path.isfile(map_path), str(map_path))
if not (map_path and os.path.isfile(map_path)):
    print("=" * 64)
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)

data = json.load(open(map_path, encoding="utf-8"))
check(f"map is {settings.ROWS} rows x {settings.COLS} tiles",
      len(data["tiles"]) == settings.ROWS and all(len(r) == settings.COLS for r in data["tiles"]))
check("every tile char is in the tile legend",
      all(ch in data["tile_legend"] for r in data["tiles"] for ch in r))
check("every region char is in the region legend",
      all(ch in data["region_legend"] for r in data["regions"] for ch in r))

with quiet():
    golden = TileMap()
    golden.build_procedural_panel_0_0()       # the old code path, kept only as this test's golden
    loaded = TileMap()
    loaded.load_real_map()                    # what the game calls

check("tiles identical", loaded.grid == golden.grid)
check("blocking identical", loaded.blocked == golden.blocked)
check("regions identical", loaded.regions == golden.regions)
check("rock-vs-tree art identical", loaded._RIVER_ROCKS_SET == golden._RIVER_ROCKS_SET)


def sources(tm):
    return sorted((s.label, s.need_id, s.world_x, s.world_y) for s in tm.get_need_sources())


check("need sources identical", sources(loaded) == sources(golden))
a = pygame.Surface((settings.WINDOW_W, settings.WINDOW_H))
b = pygame.Surface((settings.WINDOW_W, settings.WINDOW_H))
with quiet():
    golden.draw(a)
    loaded.draw(b)
check("rendered map pixels identical",
      pygame.image.tobytes(a, "RGB") == pygame.image.tobytes(b, "RGB"))

# The runtime path must not depend on the procedural builder any more.
orig = TileMap.build_procedural_panel_0_0
TileMap.build_procedural_panel_0_0 = lambda self: (_ for _ in ()).throw(AssertionError("procedural called"))
try:
    with quiet():
        TileMap().load_real_map()
    check("the game loads Panel(0,0) from data (procedural builder not called)", True)
except AssertionError:
    check("the game loads Panel(0,0) from data (procedural builder not called)", False)
finally:
    TileMap.build_procedural_panel_0_0 = orig

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Panel data tests CLEAN")
