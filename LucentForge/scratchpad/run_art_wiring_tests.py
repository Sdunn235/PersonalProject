# run_art_wiring_tests.py — the grown art is IN the game (BACKLOG LF-178; Shawn 2026-11-19: "Wire the
# grown art into the game").
#
# Until now the art genomes were baked to assets/generated/ but the game never showed them: Grom wore
# the player's sheet, and every tree and rock was a flat coloured square. These checks pin what the
# player now sees:
#   1. Grom walks in his own grown sheet (assets/generated/grom.png), no longer the player's twin;
#   2. every tree and rock tile on a panel shows its grown prop, chosen by that panel's data:
#      Panel(0,0) the Azure Woods oak and river stone; Panel(0,-1) the upper reach's oaks (each leaning
#      toward the river on its own bank) and its less-worn stone (World Building's biome sheet, §9);
#   3. a panel that names a prop genome with no baked art is refused at load (negative control);
#   4. the pixel check discriminates: the wrong oak on a tile fails it (negative control).
# Evidence: logs/screens/latest/art_wired_panel_0_0.png and art_wired_panel_0_-1.png.
#
#   py scratchpad/run_art_wiring_tests.py
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness.headless import SCREENS_DIR, headless_shell, new_kernel, quiet  # noqa: E402

import pygame  # noqa: E402
import settings  # noqa: E402
from Mechanics.world.tile_map import TileMap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = settings.TILE_SIZE
DATA = os.path.join(ROOT, "Mechanics", "data")
_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


def grown(genome_id: str) -> pygame.Surface:
    return pygame.image.load(os.path.join(ROOT, "assets", "generated", f"{genome_id}.png")).convert_alpha()


def tile_shows(surface: pygame.Surface, col: int, row: int, sprite: pygame.Surface) -> tuple[int, int]:
    """(pixels compared, mismatches): every opaque sprite pixel inside the tile (the 1-px grid line
    excluded) must appear exactly where the tile is drawn."""
    compared = bad = 0
    for x in range(1, T - 1):
        for y in range(1, T - 1):
            p = sprite.get_at((x, y))
            if p.a == 255:
                compared += 1
                if surface.get_at((col * T + x, row * T + y))[:3] != p[:3]:
                    bad += 1
    return compared, bad


def load_panel(panel_x: int, panel_y: int) -> TileMap:
    m = TileMap()
    with quiet():
        m.load_real_map(panel_x, panel_y)
    return m


def drawn(m: TileMap, labels: bool = True) -> pygame.Surface:
    """The panel as the game draws it. labels=False leaves out the zone-name labels, a separate layer
    drawn over the tiles (found 2026-11-19: "Goblins" covers the tree at (3,13) on Panel(0,0))."""
    surf = pygame.Surface((settings.COLS * T, settings.ROWS * T))
    if not labels:
        m._draw_zone_labels = lambda *a, **k: None
    m.draw(surf, 0, 0)
    return surf


print("=" * 64)
print("Art wiring tests - the grown art in the game")
print("=" * 64)
pygame.init()
if pygame.display.get_surface() is None:
    pygame.display.set_mode((1, 1))

# --- 1. Grom wears his grown sheet. ------------------------------------------------------------------
entities = {e["id"]: e for e in json.load(open(os.path.join(DATA, "entities.json"), encoding="utf-8"))}
check("entities.json: Grom (npc_03) points at assets/generated/grom.png",
      entities["npc_03"].get("sprite") == "assets/generated/grom.png", str(entities["npc_03"].get("sprite")))
ctx, kernel = new_kernel()
shell = headless_shell(ctx, kernel)
grom_sprite, player_sprite = shell.sprites.get("npc_03"), shell.sprites.get(kernel.session.player.entity_id)
size = grom_sprite.image.get_width() if grom_sprite else 0
expected = pygame.transform.scale(grown("grom").subsurface((0, 0, T, T)), (size, size)) if size else None
check("in game, Grom's first frame is his grown sheet's first cell",
      grom_sprite is not None and expected is not None
      and pygame.image.tobytes(grom_sprite.image, "RGBA") == pygame.image.tobytes(expected, "RGBA"))
check("in game, Grom no longer looks like the player",
      grom_sprite is not None and player_sprite is not None
      and pygame.image.tobytes(grom_sprite.image, "RGBA") != pygame.image.tobytes(player_sprite.image, "RGBA"))


# --- 2. Props: every tree and rock tile shows its grown prop, chosen by the panel's data. -------------
def expected_props(panel_file: str) -> dict:
    """(col, row) -> genome id, worked out here from the panel's own rows (independent of TileMap)."""
    d = json.load(open(os.path.join(DATA, "panels", panel_file), encoding="utf-8"))
    props, rocks = d.get("props", {}), {tuple(rc) for rc in d.get("rocks", [])}
    wall = next(ch for ch, name in d["tile_legend"].items() if name == "wall")
    river = {ch for ch, name in d["tile_legend"].items() if name in ("river", "bridge")}
    out = {}
    for r, row in enumerate(d["tiles"]):
        river_cols = [c for c, ch in enumerate(row) if ch in river]
        for c, ch in enumerate(row):
            if ch != wall:
                continue
            spec = props.get("rock" if (c, r) in rocks else "tree")
            if isinstance(spec, dict):
                spec = spec["west"] if river_cols and c < min(river_cols) else spec["east"]
            out[(c, r)] = spec
    return out


PANELS = {"panel_0_0.json": (0, 0), "panel_0_-1.json": (0, -1)}
WANT = {"panel_0_0.json": {"tree": "azure_oak", "rock": "river_stone"},
        "panel_0_-1.json": {"tree": {"west": "reach_oak_west", "east": "reach_oak_east"}, "rock": "reach_stone"}}
for panel_file, (px, py) in PANELS.items():
    d = json.load(open(os.path.join(DATA, "panels", panel_file), encoding="utf-8"))
    check(f"{panel_file}: names its props {WANT[panel_file]}", d.get("props") == WANT[panel_file],
          str(d.get("props")))
    pygame.image.save(drawn(load_panel(px, py)), os.path.join(SCREENS_DIR, f"art_wired_{panel_file[:-5]}.png"))
    surf = drawn(load_panel(px, py), labels=False)
    want = expected_props(panel_file)
    ids = sorted({g for g in want.values() if g})
    check(f"{panel_file}: every wall tile has a prop genome ({len(want)} walls: {ids})",
          bool(want) and all(want.values()))
    sprites = {g: grown(g) for g in ids}
    wrong = []
    flat = 0
    for (c, r), gid in want.items():
        if not gid:
            continue                                   # already failed above: no prop genome named
        compared, bad = tile_shows(surf, c, r, sprites[gid])
        if compared == 0 or bad:
            wrong.append(((c, r), gid, compared, bad))
        flat += sum(1 for x in range(1, T - 1) for y in range(1, T - 1)
                    if surf.get_at((c * T + x, r * T + y))[:3] in (settings.TREE_COLOR, settings.ROCK_COLOR))
    check(f"{panel_file}: every tree and rock tile shows its grown prop", not wrong, str(wrong[:3]))
    check(f"{panel_file}: no flat tree/rock squares remain", flat == 0, f"{flat} flat pixels")

# --- 3/4. Negative controls. ---------------------------------------------------------------------------
d = json.load(open(os.path.join(DATA, "panels", "panel_0_-1.json"), encoding="utf-8"))
try:
    TileMap().load_panel_data({**d, "props": {"tree": "no_such_oak", "rock": "reach_stone"}})
    refused = False
except ValueError:
    refused = True
check("control: a panel naming a prop with no grown art is refused at load", refused)
surf = drawn(load_panel(0, -1), labels=False)
west_tree = next(rc for rc, g in expected_props("panel_0_-1.json").items() if g == "reach_oak_west")
_, bad = tile_shows(surf, *west_tree, grown("reach_oak_east"))
check(f"control: the east-bank oak does not match a west-bank tile {west_tree} ({bad} mismatches)", bad > 0)

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Art wiring tests CLEAN")
