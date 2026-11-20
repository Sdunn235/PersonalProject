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
    from Mechanics.art.genome import (GENE_BOUNDS, KINDS, Genome, grow, load_all, mutate)
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

# --- A genome that portrays a game character agrees with the game about what it is. ------------------
# Found by Story/Lore 2026-11-19: the first Grom genome was a goblin, but entities.json's Grom (npc_03)
# is a human. The species is read from the game sprite's prefix (human_*, goblin_*), the only species
# signal entities.json carries today.
game_species = {e["name"].lower(): os.path.basename(e["sprite"]).split("_")[0]
                for e in entities if e.get("sprite") and e.get("name")}
for g in creatures:
    check(f"{g.id}: declares its species", bool(getattr(g, "species", "")))
    if g.id in game_species:
        check(f"{g.id}: species matches the game's {g.id} ({game_species[g.id]})",
              getattr(g, "species", "") == game_species[g.id], f"genome says {getattr(g, 'species', '')!r}")

# --- Lineage: a variant names the genome it was grown from (LF-184). --------------------------------
# A parent must exist and be the same kind; load_all refuses an orphan (negative control below).
for g in genomes:
    parent = getattr(g, "parent", "")
    if parent:
        p = by_id.get(parent)
        check(f"{g.id}: parent {parent!r} exists and is a {g.kind}", p is not None and p.kind == g.kind)
import tempfile  # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    with open(os.path.join(tmp, "orphan.json"), "w", encoding="utf-8") as f:
        json.dump({"id": "orphan", "kind": "rock", "seed": 1, "parent": "no_such_stone"}, f)
    try:
        load_all(tmp)
        refused = False
    except ValueError:
        refused = True
    check("control: load_all refuses a genome whose parent does not exist", refused)


# --- Props fit their tile: nothing cut off at the top, left or right (trees stand on the bottom). -----
def opaque_rect(surface):
    return surface.get_bounding_rect(min_alpha=1)


def centroid_x(surface) -> float:
    xs = n = 0
    for px in range(surface.get_width()):
        for py in range(surface.get_height()):
            if surface.get_at((px, py)).a:
                xs += px
                n += 1
    return xs / n if n else 0.0


for g in genomes:
    if g.kind in ("tree", "rock"):
        r = opaque_rect(render(g))
        check(f"{g.id}: fits its tile (a clear pixel above, left and right: x{r.left}..{r.right}, y{r.top})",
              r.top >= 1 and r.left >= 1 and r.right <= T - 1)

# --- Biome: the upper reach, Panel(0,-1) (World Building proposal §9; BACKLOG LF-184). ----------------
# "Trees: azure_oak base, mature, slightly larger trunk_height and canopy_radius; riverside trees lean
#  toward the water. Stone: river_stone variant, less worn: roughness up, facets up, flatness down,
#  size up (it hasn't travelled far)." The river runs down the middle of the panel, so a west-bank oak
#  leans east (+x) and an east-bank oak leans west.
UPPER_REACH = {"reach_oak_west": ("azure_oak", +1), "reach_oak_east": ("azure_oak", -1),
               "reach_stone": ("river_stone", 0)}


def with_lean(g, lean: float):
    """The same oak (same seed, same lobes) with another lean: isolates what the lean gene draws."""
    return Genome.from_dict({**g.to_dict(), "genes": {**g.genes, "lean": lean}})


def lean_shift(g, toward: int) -> float:
    """How far (px) the render's mass moves toward the water versus its upright twin. A seed's lobes are
    not symmetric, so the tile centre is the wrong reference (found 2026-11-19: an upright oak sits at
    x 14.98, not 16); the twin is the right one."""
    return (centroid_x(render(g)) - centroid_x(render(with_lean(g, 0.0)))) * toward


for gid, (parent_id, toward) in UPPER_REACH.items():
    g, p = by_id.get(gid), by_id.get(parent_id)
    check(f"upper reach: {gid} exists, grown from {parent_id}",
          g is not None and p is not None and getattr(g, "parent", "") == parent_id)
    if g is None or p is None:
        continue
    gn, pn = g.genes, p.genes
    if g.kind == "tree":
        check(f"{gid}: mature (stage 1.0)", g.stage == 1.0)
        check(f"{gid}: taller trunk than {parent_id}", gn["trunk_height"] > pn["trunk_height"])
        check(f"{gid}: wider canopy than {parent_id}", gn["canopy_radius"] > pn["canopy_radius"])
        check(f"{gid}: leans toward the water (gene)", gn["lean"] * toward > 0, f"lean {gn['lean']}")
        shift = lean_shift(g, toward)
        check(f"{gid}: its mass sits toward the water in the render ({shift:+.2f} px vs upright twin)",
              shift > 0.5)
        check(f"{gid}: renders bigger than {parent_id}",
              render(g).get_bounding_rect(min_alpha=1).height >= render(p).get_bounding_rect(min_alpha=1).height
              and sum(1 for x in range(T) for y in range(T) if render(g).get_at((x, y)).a)
              > sum(1 for x in range(T) for y in range(T) if render(p).get_at((x, y)).a))
    else:
        check(f"{gid}: rougher than {parent_id}", gn["roughness"] > pn["roughness"])
        check(f"{gid}: more facets than {parent_id}", round(gn["facets"]) > round(pn["facets"]))
        check(f"{gid}: less flat than {parent_id}", gn["flatness"] < pn["flatness"])
        check(f"{gid}: larger than {parent_id}", gn["size"] > pn["size"])
        rg, rp = opaque_rect(render(g)), opaque_rect(render(p))
        check(f"{gid}: renders wider and taller than {parent_id} ({rg.size} vs {rp.size})",
              rg.width > rp.width and rg.height > rp.height)
# Control: the lean check discriminates. The west oak leaned the wrong way (away from the water) fails it.
if "reach_oak_west" in by_id:
    wrong = with_lean(by_id["reach_oak_west"], -by_id["reach_oak_west"].genes["lean"])
    bad = lean_shift(wrong, +1)
    check(f"control: an oak leaning away from the water fails the lean check ({bad:+.2f} px)", not bad > 0.5)

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

# Evidence: the upper reach (LF-184). Top: each parent beside its upper-reach child. Bottom: a riverbank
# strip as the panel would place them (west oaks, the channel with a stone at its margin, east oaks), on
# a shady forest floor. For Shawn's eye: does the stand read as leaning toward the water?
if all(k in by_id for k in UPPER_REACH):
    scale, ground, water = 4, (50, 60, 40, 255), (52, 92, 136, 255)
    top = ["azure_oak", "reach_oak_west", "reach_oak_east", None, "river_stone", "reach_stone"]
    strip = ["reach_oak_west", "reach_oak_west", "~reach_stone", "~", "reach_oak_east", "reach_oak_east"]
    reach = pygame.Surface((len(top) * T, 2 * T + 4), pygame.SRCALPHA)
    reach.fill((40, 44, 52, 255))
    for i, gid in enumerate(top):
        if gid:
            reach.fill(ground, (i * T, 0, T, T))
            reach.blit(render(by_id[gid]), (i * T, 0))
    for i, cell in enumerate(strip):
        y = T + 4
        reach.fill(water if cell.startswith("~") else ground, (i * T, y, T, T))
        gid = cell.lstrip("~")
        if gid:
            reach.blit(render(by_id[gid]), (i * T, y))
    pygame.image.save(pygame.transform.scale(reach, (reach.get_width() * scale, reach.get_height() * scale)),
                      os.path.join(SCREENS_DIR, "art_upper_reach.png"))

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Art tests CLEAN")
