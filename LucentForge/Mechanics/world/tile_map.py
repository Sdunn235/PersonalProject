# tile_map.py — Tile map loader and renderer
from __future__ import annotations
import csv
import pygame
import settings
from Mechanics.needs.need_source import NeedSource


FLOOR  = 0
WALL   = 1
FOOD   = 2
WATER  = 3
SLEEP  = 4
RIVER  = 5
BRIDGE = 6
FOOD2  = 7    # Second food source (Heartbeat-3: source variety)
SLEEP2 = 8    # Second sleep source (Heartbeat-3: source variety)
FORAGE = 9    # Goblin camp food — weak, finite (Heartbeat-4)
SILO   = 10   # Storage silo placeholder (Heartbeat-5 visual, non-functional)
RBANK  = 11   # Riverbank — walkable tile adjacent to river, thirst source

_TILE_COLORS = {
    FLOOR:  settings.TILE_FLOOR,
    WALL:   settings.TILE_WALL,
    FOOD:   settings.FOOD_COLOR,
    WATER:  settings.WATER_COLOR,
    SLEEP:  settings.SLEEP_COLOR,
    RIVER:  settings.RIVER_COLOR,
    BRIDGE: settings.BRIDGE_COLOR,
    FOOD2:  (140, 160, 60),     # lighter farm green
    SLEEP2: (60, 45, 100),      # darker purple (rough camp)
    FORAGE: (100, 75, 40),      # muddy brown (goblin forage scraps)
    SILO:   (170, 155, 120),   # warm stone (storage placeholder)
    RBANK:  (45, 100, 160),    # slightly lighter blue — riverbank drinking spot
}

_SOURCE_TYPES = {
    FOOD:   "hunger",
    WATER:  "thirst",
    SLEEP:  "sleep",
    BRIDGE: "thirst",   # NPCs drink at bridge tiles (river access)
    RBANK:  "thirst",   # Riverbank — walkable drinking spots along the river
    FOOD2:  "hunger",
    SLEEP2: "sleep",
    FORAGE: "hunger",
}

# CSV files and game grid are both 18×18 — direct 1:1 mapping, no scaling needed.


class TileMap:
    def __init__(self, cols: int = settings.COLS, rows: int = settings.ROWS,
                 tile_size: int = settings.TILE_SIZE):
        self.cols      = cols
        self.rows      = rows
        self.tile_size = tile_size
        self.grid: list[list[int]]  = [[FLOOR] * cols for _ in range(rows)]
        self.blocked: list[list[bool]] = [[False] * cols for _ in range(rows)]
        self.regions: list[list[str]]  = [["unknown"] * cols for _ in range(rows)]
        self._background: pygame.Surface | None = None
        self._font: pygame.font.Font | None = None
        # Fast lookup set for rock vs tree rendering
        self._RIVER_ROCKS_SET: set[tuple[int, int]] = set(self._RIVER_ROCKS)

    # --- Map building ---

    def generate_demo_map(self) -> None:
        """Simple placeholder map — outer walls + three need-source nodes."""
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1:
                    self._set(c, r, WALL)
        for r in range(4, 8):
            self._set(8, r, WALL)
        for c in range(8, 14):
            self._set(c, 8, WALL)
        for r in range(10, 15):
            self._set(14, r, WALL)
        for dc in range(2):
            for dr in range(2):
                self._set(3 + dc,  3 + dr, FOOD)
                self._set(18 + dc, 3 + dr, WATER)
                self._set(3 + dc, 14 + dr, SLEEP)

    # --- Heartbeat-2: River layout data ---
    # Winding river (col, row) pairs — west=wild, east=civilized
    _RIVER_TILES: list[tuple[int, int]] = [
        (6, 0), (7, 0),
        (6, 1), (7, 1),
        (5, 2), (6, 2),
        (5, 3), (6, 3),
        # rows 4-5: north bridge replaces river
        (4, 6), (5, 6),
        (5, 7), (6, 7),
        (5, 8), (6, 8),
        (6, 9), (7, 9),
        (6, 10), (7, 10),
        # rows 11-12: south bridge replaces river
        (4, 13), (5, 13),
        (4, 14), (5, 14),
        (5, 15), (6, 15),
        (5, 16), (6, 16),
        (6, 17), (7, 17),
    ]
    _BRIDGE_TILES: list[tuple[int, int]] = [
        (4, 5), (5, 5), (4, 4), (5, 4),     # north bridge 2×2 (rows 4-5)
        (5, 12), (6, 12), (5, 11), (6, 11),  # south bridge 2×2 (rows 11-12)
    ]

    # --- Heartbeat-2: Hand-placed obstacles ---
    # Trees in forest (wild west) — scattered for natural feel
    _FOREST_TREES: list[tuple[int, int]] = [
        (0, 0), (3, 0), (0, 2), (1, 3), (3, 4),
        (0, 5), (2, 6), (0, 7), (3, 8), (1, 9),
        (0, 10), (3, 10), (1, 12), (0, 15), (2, 16),
        (0, 17), (3, 17),
    ]
    # Trees near goblin camp — denser cover
    _GOBLIN_TREES: list[tuple[int, int]] = [
        (1, 13), (3, 13), (1, 15), (3, 15),
    ]
    # Rocks along riverbank
    _RIVER_ROCKS: list[tuple[int, int]] = [
        (3, 2), (3, 7), (3, 9), (3, 15),
    ]
    # A few trees on the civilized outskirts (sparse)
    _TOWN_TREES: list[tuple[int, int]] = [
        (16, 0), (17, 3), (17, 10), (16, 17), (8, 17),
    ]

    def load_real_map(self) -> None:
        """
        Build the procedural map (Heartbeat-2):
        - Region-colored ground (no background image)
        - Hand-placed obstacles (trees, rocks)
        - River barrier + bridges
        - Region tags for all tiles
        - Need-source tiles at zone-appropriate positions
        """
        # 1. River barrier + bridges
        self._apply_river()

        # 2. Region tags
        self._assign_regions()

        # 3. Hand-placed obstacles — trees and rocks
        self._place_obstacles()

        # 4. Need-source nodes — positioned for river geography
        for dc in range(2):
            for dr in range(2):
                self._set(1 + dc,  1 + dr, FOOD)     # forest food (wild west)
                self._set(2 + dc, 11 + dr, FOOD)     # south food near bridge (wild)
                self._set(11 + dc, 11 + dr, SLEEP)   # homes/beds — near town center (H5 layout)
        # Water: bridge tiles already set as BRIDGE (thirst source via _SOURCE_TYPES)

        # Heartbeat-3: additional sources for memory-weighted choice variety
        for dc in range(2):
            for dr in range(2):
                self._set(14 + dc, 3 + dr, FOOD2)    # farm food (civilized northeast)
                self._set(2 + dc,  15 + dr, SLEEP2)  # rough camp (wild southwest)

        # Heartbeat-4: goblin forage — weak food in goblin camp
        for dr in range(2):
            self._set(0, 13 + dr, FORAGE)  # 1x2 forage patch, west edge of camp

        # Heartbeat-5: riverbank drinking spots — walkable tiles adjacent to river
        # East bank (civilized side) — 4 spots along the river
        self._set(8, 0, RBANK)    # north civilized bank
        self._set(7, 2, RBANK)    # mid-north civilized bank
        self._set(7, 8, RBANK)    # central civilized bank
        self._set(8, 10, RBANK)   # south-central civilized bank
        # West bank (wild side) — 3 spots
        self._set(3, 6, RBANK)    # mid-west wild bank
        self._set(3, 14, RBANK)   # south wild bank
        self._set(4, 16, RBANK)   # far south wild bank

        # Heartbeat-5: silo placeholder (visual only, no mechanic yet)
        self._set(11, 9, SILO)
        self._set(12, 9, SILO)

    def _place_obstacles(self) -> None:
        """Place hand-picked trees and rocks that fit the zone layout."""
        all_obstacles = (
            self._FOREST_TREES + self._GOBLIN_TREES +
            self._RIVER_ROCKS + self._TOWN_TREES
        )
        placed = 0
        for col, row in all_obstacles:
            # Don't overwrite river, bridge, or need-source tiles
            if self.grid[row][col] in (RIVER, BRIDGE, FOOD, WATER, SLEEP, FOOD2, SLEEP2, FORAGE, SILO, RBANK):
                continue
            self._set(col, row, WALL)
            placed += 1
        print(f"[MAP] Obstacles placed: {placed} (trees + rocks)")

    def _apply_obstacle_csv(self, path: str) -> None:
        """Read an 18×18 obstacle CSV and mark tiles with value >= 0 as WALL (direct 1:1 mapping)."""
        try:
            with open(path) as f:
                grid = list(csv.reader(f))
        except FileNotFoundError:
            print(f"[MAP] Warning: obstacle CSV not found: {path}")
            return

        for r in range(min(self.rows, len(grid))):
            for c in range(min(self.cols, len(grid[r]))):
                try:
                    if int(grid[r][c]) >= 0:
                        self._set(c, r, WALL)
                except ValueError:
                    continue

    def _apply_river(self) -> None:
        """Place river barrier and bridge crossing tiles (Heartbeat-2)."""
        for col, row in self._RIVER_TILES:
            self._set(col, row, RIVER)
        for col, row in self._BRIDGE_TILES:
            self._set(col, row, BRIDGE)
        river_count = len(self._RIVER_TILES)
        bridge_count = len(self._BRIDGE_TILES)
        print(f"[MAP] River placed: {river_count} river tiles, "
              f"{bridge_count} bridge tiles ({bridge_count // 2} crossings)")

    def _assign_regions(self) -> None:
        """Tag every tile with a region string (Heartbeat-2).

        Regions are metadata for future NPC behavior (Heartbeat-3+).
        """
        # Build a set of river column positions per row for boundary detection
        river_cols_by_row: dict[int, list[int]] = {}
        for col, row in self._RIVER_TILES + self._BRIDGE_TILES:
            river_cols_by_row.setdefault(row, []).append(col)

        for r in range(self.rows):
            # Find the river boundary for this row
            rcols = river_cols_by_row.get(r, [])
            river_min = min(rcols) if rcols else self.cols // 2
            river_max = max(rcols) if rcols else self.cols // 2

            for c in range(self.cols):
                tile = self.grid[r][c]
                # River and bridge tiles get their own tags
                if tile == RIVER:
                    self.regions[r][c] = "river"
                elif tile == BRIDGE:
                    self.regions[r][c] = "bridge"
                # West of river = wild side
                elif c < river_min:
                    self.regions[r][c] = "forest"
                # East of river = civilized side
                elif c > river_max:
                    self.regions[r][c] = "town_outskirts"
                else:
                    self.regions[r][c] = "forest"

        # Overlay specific named zones onto the defaults
        # Goblin camp — lower southwest clearing
        for r in range(13, 15):
            for c in range(2, 4):
                if self.grid[r][c] not in (RIVER, BRIDGE):
                    self.regions[r][c] = "goblin_camp"

        # Town center — central east cluster
        for r in range(7, 11):
            for c in range(10, 14):
                if self.regions[r][c] == "town_outskirts":
                    self.regions[r][c] = "town_center"

        # Storage — 2x2 reserved inside town center (Heartbeat-5 placeholder)
        for r in range(8, 10):
            for c in range(11, 13):
                if self.regions[r][c] in ("town_center", "town_outskirts"):
                    self.regions[r][c] = "storage"

        # Homes — around the BED source area (H5: moved near town center)
        for r in range(10, 13):
            for c in range(10, 14):
                if self.regions[r][c] in ("town_outskirts", "town_center"):
                    self.regions[r][c] = "homes"

        # Farm — northeast area (future agriculture)
        for r in range(2, 6):
            for c in range(13, 17):
                if self.regions[r][c] == "town_outskirts":
                    self.regions[r][c] = "farm"

        # Log region summary
        counts: dict[str, int] = {}
        for r in range(self.rows):
            for c in range(self.cols):
                region = self.regions[r][c]
                counts[region] = counts.get(region, 0) + 1
        summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"[MAP] Regions: {summary}")

    def get_region(self, col: int, row: int) -> str:
        """Return the region tag for a tile position."""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return "out_of_bounds"
        return self.regions[row][col]

    def load_from_csv(self, path: str) -> None:
        with open(path) as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                if r >= self.rows:
                    break
                for c, val in enumerate(row):
                    if c >= self.cols:
                        break
                    try:
                        self._set(c, r, int(val))
                    except ValueError:
                        pass

    def _set(self, col: int, row: int, tile_type: int) -> None:
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return
        self.grid[row][col] = tile_type
        self.blocked[row][col] = tile_type in (WALL, RIVER)

    # --- Queries ---

    def is_blocked(self, col: int, row: int) -> bool:
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return True
        return self.blocked[row][col]

    def world_to_grid(self, x: float, y: float) -> tuple[int, int]:
        return int(x // self.tile_size), int(y // self.tile_size)

    def grid_to_world_center(self, col: int, row: int) -> tuple[float, float]:
        return (col * self.tile_size + self.tile_size / 2,
                row * self.tile_size + self.tile_size / 2)

    def get_need_sources(self) -> list[NeedSource]:
        # Collect all tiles for each source type
        tile_groups: dict = {}
        for r in range(self.rows):
            for c in range(self.cols):
                t = self.grid[r][c]
                if t in _SOURCE_TYPES:
                    tile_groups.setdefault(t, []).append((c, r))

        # Source characteristics — secondary sources fill slower but offer variety
        # H5: finite food sources include stock/capacity/regen_rate
        _SOURCE_PROPS = {
            FOOD:   {"satisfaction_amount": 80.0, "interaction_time": 8.0,
                     "stock": settings.FOOD_STOCK_CAPACITY,
                     "capacity": settings.FOOD_STOCK_CAPACITY,
                     "regen_rate": settings.FOOD_STOCK_REGEN},
            WATER:  {"satisfaction_amount": 80.0, "interaction_time": 3.0},
            SLEEP:  {"satisfaction_amount": 80.0, "interaction_time": 30.0},
            BRIDGE: {"satisfaction_amount": 80.0, "interaction_time": 3.0},
            FOOD2:  {"satisfaction_amount": 60.0, "interaction_time": 12.0,
                     "stock": settings.FARM_STOCK_CAPACITY,
                     "capacity": settings.FARM_STOCK_CAPACITY,
                     "regen_rate": settings.FARM_STOCK_REGEN},
            SLEEP2: {"satisfaction_amount": 50.0, "interaction_time": 20.0},
            FORAGE: {"satisfaction_amount": settings.FORAGE_SATISFACTION,
                     "interaction_time": settings.FORAGE_INTERACTION_TIME,
                     "stock": settings.FORAGE_STOCK_CAPACITY,
                     "capacity": settings.FORAGE_STOCK_CAPACITY,
                     "regen_rate": settings.FORAGE_STOCK_REGEN},
            RBANK:  {"satisfaction_amount": 80.0, "interaction_time": 3.0},
        }

        sources = []
        for t, tiles in tile_groups.items():
            nt    = _SOURCE_TYPES[t]
            label = {FOOD: "FOOD", WATER: "WATER", SLEEP: "BED", BRIDGE: "WATER",
                     RBANK: "RIVER", FOOD2: "FARM", SLEEP2: "CAMP", FORAGE: "FORAGE"}[t]
            color = _TILE_COLORS[t]
            props = _SOURCE_PROPS.get(t, {})
            # Center tile for BFS targeting
            center_col = int(sum(c for c, _ in tiles) / len(tiles))
            center_row = int(sum(r for _, r in tiles) / len(tiles))
            src = NeedSource(nt, center_col, center_row, label, color, tiles,
                             satisfaction_amount=props.get("satisfaction_amount", 80.0),
                             interaction_time=props.get("interaction_time", 8.0),
                             stock=props.get("stock", -1.0),
                             capacity=props.get("capacity", -1.0),
                             regen_rate=props.get("regen_rate", 0.0))
            sources.append(src)
        return sources

    # --- Rendering ---

    # --- Zone label config: (region_name, display_label) ---
    _ZONE_LABELS: list[tuple[str, str]] = [
        ("town_center",   "Town"),
        ("homes",         "Homes"),
        ("farm",          "Farm"),
        ("goblin_camp",   "Goblins"),
        ("forest",        "Forest"),
        ("storage",       "Silo"),
    ]

    def draw(self, surface: pygame.Surface,
             offset_x: int | None = None, offset_y: int | None = None) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont(None, 14)
        ts = self.tile_size
        ox = offset_x if offset_x is not None else settings.LEVEL_X
        oy = offset_y if offset_y is not None else settings.LEVEL_Y

        _tile_labels = {FOOD: "F", SLEEP: "Z", BRIDGE: "B", FOOD2: "f", SLEEP2: "c", FORAGE: "g", SILO: "S", RBANK: "~"}
        _special_colors = {
            FOOD:   settings.FOOD_COLOR,
            SLEEP:  settings.SLEEP_COLOR,
            RIVER:  settings.RIVER_COLOR,
            BRIDGE: settings.BRIDGE_COLOR,
            RBANK:  _TILE_COLORS[RBANK],
            FOOD2:  _TILE_COLORS[FOOD2],
            SLEEP2: _TILE_COLORS[SLEEP2],
            FORAGE: _TILE_COLORS[FORAGE],
            SILO:   _TILE_COLORS[SILO],
        }
        region_colors = settings.REGION_COLORS

        for r in range(self.rows):
            for c in range(self.cols):
                t = self.grid[r][c]
                rect = pygame.Rect(c * ts + ox, r * ts + oy, ts, ts)

                # Ground: region-based color
                region = self.regions[r][c]
                ground = region_colors.get(region, region_colors["unknown"])
                pygame.draw.rect(surface, ground, rect)

                # Special tiles drawn on top of ground
                if t in _special_colors:
                    s = pygame.Surface((ts, ts), pygame.SRCALPHA)
                    s.fill((*_special_colors[t], 200))
                    surface.blit(s, rect)
                elif t == WALL:
                    # Obstacles: trees (forest) or rocks (near river)
                    is_rock = (c, r) in self._RIVER_ROCKS_SET
                    color = settings.ROCK_COLOR if is_rock else settings.TREE_COLOR
                    pygame.draw.rect(surface, color, rect)

                # Subtle grid lines
                pygame.draw.rect(surface, (0, 0, 0, 40), rect, 1)

                # Tile letter labels
                if t in _tile_labels:
                    txt = self._font.render(_tile_labels[t], True,
                                            (255, 255, 255))
                    surface.blit(txt, (c * ts + ox + 2, r * ts + oy + 2))

        self._draw_zone_labels(surface, ox, oy)

    def _draw_zone_labels(self, surface: pygame.Surface,
                          ox: int, oy: int) -> None:
        """Render zone name labels at the center of each named region."""
        label_font = pygame.font.SysFont(None, 16)
        ts = self.tile_size
        for region_name, display_label in self._ZONE_LABELS:
            # Find center of this region's tiles
            tiles = [(c, r) for r in range(self.rows)
                     for c in range(self.cols)
                     if self.regions[r][c] == region_name]
            if not tiles:
                continue
            cx = sum(c for c, _ in tiles) / len(tiles)
            cy = sum(r for _, r in tiles) / len(tiles)
            px = int(cx * ts + ox + ts // 2)
            py = int(cy * ts + oy + ts // 2)
            txt = label_font.render(display_label, True, (255, 255, 255))
            # Semi-transparent background for readability
            bg = pygame.Surface((txt.get_width() + 4, txt.get_height() + 2),
                                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            surface.blit(bg, (px - txt.get_width() // 2 - 2,
                              py - txt.get_height() // 2 - 1))
            surface.blit(txt, (px - txt.get_width() // 2,
                               py - txt.get_height() // 2))
