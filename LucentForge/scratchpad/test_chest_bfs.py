"""test_chest_bfs.py — Phase 2.7 BFS sanity check: chest positions don't sever routes.

Builds the procedural tile map, stamps the 3 chest tiles as CHEST (blocked),
then asserts BFS can still connect every NPC-relevant source tile pair.

Usage: py scratchpad/test_chest_bfs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# noinspection PyPackageRequirements
import pygame
pygame.init()
pygame.display.set_mode((1, 1))  # minimal surface needed for TileMap

import settings
from Mechanics.world.tile_map import TileMap, CHEST, WALL, RIVER
from Mechanics.world.pathfinder import bfs_path

CHEST_POSITIONS = [
    (11, 8),   # town_supply_chest
    (2,  4),   # forest_cache
    (2,  14),  # goblin_hoard
]

# Key NPC movement tiles (col, row) drawn from known free-floor areas
SOURCE_ANCHORS = [
    (2,  2),    # goblin camp area
    (8,  2),    # north-center
    (15, 8),    # storage / east side
    (8,  16),   # south-center
    (4,  10),   # mid-left
]


def _build_map() -> TileMap:
    tm = TileMap()
    tm.load_real_map()
    return tm


def test_chest_positions_are_valid_floor():
    """Chest positions must be floor (not wall or river) before placement."""
    tm = _build_map()
    failures = []
    for col, row in CHEST_POSITIONS:
        t = tm.grid[row][col]
        if t in (WALL, RIVER):
            failures.append((col, row, t))
    if failures:
        for col, row, t in failures:
            print(f"  FAIL: Chest at ({col},{row}) is tile type {t} — must be floor!")
        return False
    print(f"  All {len(CHEST_POSITIONS)} chest positions are valid floor tiles.")
    return True


def test_bfs_after_chest_placement():
    """After stamping chests as blocked, source anchors must still be mutually reachable."""
    tm = _build_map()
    for col, row in CHEST_POSITIONS:
        tm._set(col, row, CHEST)

    blocked_fn = tm.is_blocked
    anchors = [(c, r) for c, r in SOURCE_ANCHORS if not blocked_fn(c, r)]
    if len(anchors) < 2:
        print("  SKIP: fewer than 2 unblocked anchors — check SOURCE_ANCHORS list")
        return True

    print(f"  Testing {len(anchors)} anchor points ...")
    failures = []
    for i, start in enumerate(anchors):
        for goal in anchors[i + 1:]:
            path = bfs_path(blocked_fn, start, goal, tm.cols, tm.rows)
            if not path:
                failures.append((start, goal))

    if failures:
        for s, g in failures:
            print(f"  FAIL: No path {s} → {g} after chest placement")
        return False
    pairs = len(anchors) * (len(anchors) - 1) // 2
    print(f"  All {pairs} anchor pairs reachable after chest placement.")
    return True


if __name__ == "__main__":
    print("=== Phase 2.7 BFS Connectivity Smoke Tests ===\n")
    results = [
        test_chest_positions_are_valid_floor(),
        test_bfs_after_chest_placement(),
    ]
    passed = sum(results)
    total = len(results)
    print(f"\n{passed}/{total} tests passed.")
    pygame.quit()
    sys.exit(0 if passed == total else 1)
