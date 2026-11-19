# run_art_tests.py — the art biology: genomes -> renders (studio/art, docs/testing.md "Unit"/"Integrated").
#
# Art is GROWN, not painted (Shawn, 2026-11-19): every generated asset comes from an art genome (data)
# and a seed. These checks pin the biology's contract: renders are deterministic, genes stay in bounds
# under mutation, growth makes things bigger, sheets match the game's 3x4 / 32-px convention and actually
# animate, every image has provenance, and genomes respect the lore they encode.
#
#   py scratchpad/run_art_tests.py
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness.headless import SCREENS_DIR  # noqa: E402  (also sets SDL dummy drivers + sys.path)

import pygame  # noqa: E402
import settings  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = settings.TILE_SIZE
SHEET = (3 * T, 4 * T)                    # the convention EntitySprite slices (3 cols x 4 rows)
_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


def opaque_bbox(surface):
    """(width, height) of the non-transparent pixels."""
    r = surface.get_bounding_rect(min_alpha=1)
    return r.width, r.height


print("=" * 64)
print("Art tests - genomes, renders, provenance")
print("=" * 64)
pygame.init()
if pygame.display.get_surface() is None:
    pygame.display.set_mode((1, 1))

# --- Existing game art follows the sheet convention (never edited by Art). -------------------
entities = json.load(open(os.path.join(ROOT, "Mechanics", "data", "entities.json"), encoding="utf-8"))
for ent in entities:
    path = ent.get("sprite")
    if not path:
        continue
    full = os.path.join(ROOT, path)
    ok = os.path.isfile(full)
    check(f"sprite exists for {ent.get('name', ent.get('id'))}: {path}", ok)
    if ok:
        check(f"{path} is a 3x4 sheet of {T}-px cells", pygame.image.load(full).get_size() == SHEET)

try:
    from Mechanics.art.genome import (GENE_BOUNDS, KINDS, grow, load_all, mutate)
    from Mechanics.art.render import render
    from Mechanics.art import bake
except Exception as ex:  # noqa: BLE001
    check(f"art package importable (Mechanics.art): {ex}", False)
    print("=" * 64)
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)

genomes = load_all()
by_id = {g.id: g for g in genomes}
check("genomes load from Mechanics/data/art/", len(genomes) >= 4, f"{len(genomes)} found")
for kind in ("creature", "tree", "rock"):
    check(f"at least one {kind} genome", any(g.kind == kind for g in genomes))
for g in genomes:
    check(f"{g.id}: known kind", g.kind in KINDS)
    lo_hi = GENE_BOUNDS[g.kind]
    check(f"{g.id}: every gene inside its bounds",
          all(lo_hi[k][0] <= v <= lo_hi[k][1] for k, v in g.genes.items()),
          str({k: v for k, v in g.genes.items() if not lo_hi[k][0] <= v <= lo_hi[k][1]}))
    check(f"{g.id}: carries every gene of its kind (defaults fill gaps)",
          set(g.genes) == set(lo_hi))

# --- Determinism + distinctness. -----------------------------------------------------------------
for g in genomes:
    a, b = render(g), render(g)
    check(f"{g.id}: same genome + seed -> identical pixels",
          pygame.image.tobytes(a, "RGBA") == pygame.image.tobytes(b, "RGBA"))
creatures = [g for g in genomes if g.kind == "creature"]
if len(creatures) >= 2:
    x, y = creatures[0], creatures[1]
    check(f"different genomes look different ({x.id} vs {y.id})",
          pygame.image.tobytes(render(x), "RGBA") != pygame.image.tobytes(render(y), "RGBA"))

# --- Creature sheets match the game and animate. ---------------------------------------------------
for g in creatures:
    sheet = render(g)
    check(f"{g.id}: sheet is {SHEET[0]}x{SHEET[1]} with alpha", sheet.get_size() == SHEET
          and sheet.get_flags() & pygame.SRCALPHA)
    cells = [[sheet.subsurface((c * T, r * T, T, T)) for c in range(3)] for r in range(4)]
    check(f"{g.id}: every cell draws something",
          all(opaque_bbox(cell)[1] > 0 for row in cells for cell in row))
    check(f"{g.id}: walk frames differ within each direction (it animates)",
          all(pygame.image.tobytes(row[1], "RGBA") != pygame.image.tobytes(row[0], "RGBA") for row in cells))
    check(f"{g.id}: the four directions differ",
          len({pygame.image.tobytes(row[0], "RGBA") for row in cells}) >= 3)

# --- Biology: mutation stays in bounds; growth grows. ------------------------------------------------
rng = random.Random(7)
for g in genomes:
    m = g
    for _ in range(50):
        m = mutate(m, rng, rate=0.2)
    lo_hi = GENE_BOUNDS[g.kind]
    check(f"{g.id}: 50 mutations keep every gene in bounds",
          all(lo_hi[k][0] <= v <= lo_hi[k][1] for k, v in m.genes.items()))
    check(f"{g.id}: mutation changes the genome", m.genes != g.genes)
    check(f"{g.id}: rate 0 changes nothing", mutate(g, rng, rate=0.0).genes == g.genes)
for g in genomes:
    heights = []
    for stage in (0.2, 0.6, 1.0):
        surf = render(grow(g, stage))
        cell = surf.subsurface((0, 0, T, T)) if g.kind == "creature" else surf
        heights.append(opaque_bbox(cell)[1])
    check(f"{g.id}: growing up makes it taller {heights}", heights[0] < heights[1] <= heights[2])

# --- Lore encoded in genes (Gobby: thin, small, outcast forest goblin; Grom: tanky goblin). -----------
if "gobby" in by_id and "grom" in by_id:
    gob, grom = by_id["gobby"], by_id["grom"]
    check("Gobby is smaller than Grom (genes)", gob.genes["height"] < grom.genes["height"])
    check("Gobby is thinner than Grom (genes)", gob.genes["body_width"] < grom.genes["body_width"])
    w_gob = opaque_bbox(render(gob).subsurface((0, 0, T, T)))[0]
    w_grom = opaque_bbox(render(grom).subsurface((0, 0, T, T)))[0]
    check(f"Gobby renders narrower than Grom ({w_gob} vs {w_grom} px)", w_gob < w_grom)
else:
    check("gobby and grom genomes exist", False)

# --- Provenance: every character/prop image is registered; generated art matches its genome. ---------
registry = json.load(open(os.path.join(ROOT, "assets", "registry.json"), encoding="utf-8"))
entries = {e["path"]: e for e in registry["assets"]}
for folder in ("images", "generated"):
    base = os.path.join(ROOT, "assets", folder)
    for f in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        if f.lower().endswith(".png"):
            rel = f"assets/{folder}/{f}"
            e = entries.get(rel)
            check(f"registered with a source: {rel}", e is not None and bool(e.get("source")))
for g in genomes:
    rel = f"assets/generated/{g.id}.png"
    full = os.path.join(ROOT, rel)
    ok = os.path.isfile(full)
    check(f"{g.id}: baked to {rel}", ok)
    if ok:
        check(f"{g.id}: baked file matches a fresh render (re-bake if genes changed)",
              pygame.image.tobytes(pygame.image.load(full).convert_alpha(), "RGBA")
              == pygame.image.tobytes(render(g), "RGBA"))
        e = entries.get(rel, {})
        check(f"{g.id}: registry records genome + seed", e.get("genome") == g.id and e.get("seed") == g.seed)

# Evidence: a contact sheet of every genome at 4x, plus growth stages.
os.makedirs(SCREENS_DIR, exist_ok=True)
scale = 4
renders = [render(g) for g in genomes]
w = sum(r.get_width() for r in renders) * scale + 8 * len(renders)
h = max(r.get_height() for r in renders) * scale
contact = pygame.Surface((w, h), pygame.SRCALPHA)
contact.fill((40, 44, 52, 255))
x = 0
for r in renders:
    contact.blit(pygame.transform.scale(r, (r.get_width() * scale, r.get_height() * scale)), (x, 0))
    x += r.get_width() * scale + 8
pygame.image.save(contact, os.path.join(SCREENS_DIR, "art_contact_sheet.png"))

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Art tests CLEAN")
