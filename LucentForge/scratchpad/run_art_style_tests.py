# run_art_style_tests.py — the Lucent Light house style (studio/art/direction.md; docs/testing.md "Render").
#
# Art found its style 2026-11-19: every grown asset shares ONE light and colors that are grown from a
# single base color per material, the way genes grow proportions. These checks pin that contract so the
# look stays coherent as genomes multiply and mutate:
#   1. the style is data (Mechanics/data/art_style.json), not constants scattered through drawing code;
#   2. genomes carry base materials only; every shade is derived (formulas, not hand-picked shadows);
#   3. a ramp is ordered dark -> light, shadows lean cool and highlights lean warm (hue shifting);
#   4. palette discipline: every rendered pixel is a ramp shade of one of the genome's materials;
#   5. one light: on every cell, a material's lit-side rim is brighter than its shadow-side rim
#      (negative control: the same render with no light fails this check);
#   6. outlines are the material's own darkest shades, never pure black; form shading exists.
#
#   py scratchpad/run_art_style_tests.py
import colorsys
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness.headless import SCREENS_DIR  # noqa: E402  (also sets SDL dummy drivers + sys.path)

import pygame  # noqa: E402
import settings  # noqa: E402

T = settings.TILE_SIZE
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


def bail() -> None:
    print("=" * 64)
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)


def lum(rgb) -> float:
    r, g, b = rgb[:3]
    return 0.299 * r + 0.587 * g + 0.114 * b


def hue_deg(rgb) -> tuple[float, float]:
    h, _l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb[:3]))
    return h * 360, s


def arc(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


print("=" * 64)
print("Art style tests - Lucent Light: one light, grown ramps, coloured outlines")
print("=" * 64)
pygame.init()
if pygame.display.get_surface() is None:
    pygame.display.set_mode((1, 1))

try:
    from Mechanics.art import style as st
    from Mechanics.art.genome import MATERIALS, grow, load_all, mutate
    from Mechanics.art.render import render
except Exception as ex:  # noqa: BLE001
    check(f"style package importable (Mechanics.art.style, genome.MATERIALS): {ex!r}", False)
    bail()

# 1. The style is data.
style = st.load_style()
check("style loads from Mechanics/data/art_style.json", os.path.isfile(st.STYLE_PATH))
for key in ("light_from", "lightness_step", "outline_steps", "hue_shift_degrees",
            "cool_hue_degrees", "warm_hue_degrees", "grey_tint_saturation", "flat_materials"):
    check(f"style defines {key}", hasattr(style, key))

# 2. Genomes carry base materials only.
genomes = load_all()
for g in genomes:
    extra = set(g.palette) - set(MATERIALS[g.kind])
    check(f"{g.id}: palette is base materials only (shades are derived)", not extra, f"extra {sorted(extra)}")

# 3. Ramp contract, on every base color the genomes use (plus the kind defaults).
bases = {}
for kind, mats in MATERIALS.items():
    for m, rgb in mats.items():
        bases[f"default {kind}.{m}"] = rgb
for g in genomes:
    for m, rgb in g.palette.items():
        bases[f"{g.id}.{m}"] = rgb
for name, base in sorted(bases.items()):
    if name.endswith(tuple(f".{m}" for m in style.flat_materials)):
        continue
    r = st.ramp(base, style)
    check(f"ramp {name}: 4 shades (outline, shadow, base, light), base kept", len(r) == 4 and r[2] == tuple(base[:3]))
    lums = [lum(c) for c in r]
    check(f"ramp {name}: ordered dark -> light", all(a < b for a, b in zip(lums, lums[1:])),
          f"{[round(x) for x in lums]}")
    h0, s0 = hue_deg(base)
    if s0 >= 0.15:
        hs, _ = hue_deg(r[1])
        hl, _ = hue_deg(r[3])
        if arc(h0, style.cool_hue_degrees) > style.hue_shift_degrees:
            check(f"ramp {name}: shadow leans cool", arc(hs, style.cool_hue_degrees) < arc(h0, style.cool_hue_degrees),
                  f"base {h0:.0f} shadow {hs:.0f}")
        if arc(h0, style.warm_hue_degrees) > style.hue_shift_degrees:
            check(f"ramp {name}: light leans warm", arc(hl, style.warm_hue_degrees) < arc(h0, style.warm_hue_degrees),
                  f"base {h0:.0f} light {hl:.0f}")
    else:
        hs, ss = hue_deg(r[1])
        check(f"ramp {name} (grey): shadow takes a cool tint",
              ss > 0.02 and arc(hs, style.cool_hue_degrees) <= style.hue_shift_degrees, f"h {hs:.0f} s {ss:.2f}")
    check(f"ramp {name}: outline is not pure black", r[0] != (0, 0, 0))


# Helpers over a rendered surface.
def cells_of(g, surf):
    if g.kind == "creature":
        return [surf.subsurface((c * T, rr * T, T, T)) for rr in range(4) for c in range(3)]
    return [surf]


def shade_map(g):
    """color -> (material, ramp index) for this genome's resolved palette."""
    out = {}
    for m, rgb in st.resolved_palette(g).items():
        if m in style.flat_materials:
            out[tuple(rgb[:3])] = (m, -1)
            continue
        for i, c in enumerate(st.ramp(rgb, style)):
            out.setdefault(c, (m, i))
    return out


def rim_report(cell, smap, light):
    """{material: (mean lum of lit-side rim, mean lum of shadow-side rim)} for one cell."""
    lx, ly = light
    w, h = cell.get_size()
    px = {(x, y): cell.get_at((x, y)) for y in range(h) for x in range(w)}

    def clear(x, y):
        return not (0 <= x < w and 0 <= y < h) or px[(x, y)].a == 0

    lit, shade = {}, {}
    for (x, y), c in px.items():
        if c.a == 0:
            continue
        mat = smap.get((c.r, c.g, c.b), (None, None))[0]
        if mat is None or mat in style.flat_materials:
            continue
        toward_light = (lx and clear(x + lx, y)) or (ly and clear(x, y + ly))
        toward_shadow = (lx and clear(x - lx, y)) or (ly and clear(x, y - ly))
        if toward_light:
            lit.setdefault(mat, []).append(lum(c))
        elif toward_shadow:
            shade.setdefault(mat, []).append(lum(c))
    return {m: (sum(lit[m]) / len(lit[m]), sum(shade[m]) / len(shade[m])) for m in lit if m in shade}


# 4-6. Renders obey the style.
light = tuple(style.light_from)
for g in genomes:
    surf = render(g)
    smap = shade_map(g)
    colors = {tuple(surf.get_at((x, y)))[:3] for y in range(surf.get_height()) for x in range(surf.get_width())
              if surf.get_at((x, y)).a > 0}
    stray = colors - set(smap)
    check(f"{g.id}: every pixel is a ramp shade of its materials ({len(colors)} colors)", not stray,
          f"{len(stray)} stray e.g. {sorted(stray)[:3]}")
    check(f"{g.id}: no pure-black pixels", (0, 0, 0) not in colors)
    bad_cells = []
    for i, cell in enumerate(cells_of(g, surf)):
        rep = rim_report(cell, smap, light)
        if not rep or any(lit <= shd for lit, shd in rep.values()):
            bad_cells.append((i, {m: (round(a), round(b)) for m, (a, b) in rep.items()}))
    check(f"{g.id}: one light - every cell's lit rim is brighter than its shadow rim", not bad_cells,
          str(bad_cells[:2]))
    main = {"creature": "cloth", "tree": "leaf", "rock": "stone"}[g.kind]
    shades = {smap[c][1] for c in colors if smap.get(c, (None,))[0] == main}
    check(f"{g.id}: form shading - its {main} shows outline, shadow, base and light", {0, 1, 2, 3} <= shades,
          str(sorted(shades)))

# Negative control: with no light, the one-light check must fail (proves it discriminates).
dark = st.Style(**{**style.__dict__, "light_from": (0, 0)})
g0 = next(g for g in genomes if g.kind == "creature")
cell0 = cells_of(g0, render(g0, style=dark))[0]
rep0 = rim_report(cell0, shade_map(g0), light)
check("negative control: the same creature with no light fails the one-light check",
      not rep0 or any(lit <= shd for lit, shd in rep0.values()), str(rep0))

# Mutated and growing individuals stay in the style (the biology can't escape the look).
rng = random.Random(11)
kid = g0
for _ in range(5):
    kid = mutate(kid, rng, rate=0.15)
for name, gg in (("5th-generation child", kid), ("newborn", grow(g0, 0.0))):
    surf = render(gg)
    smap = shade_map(gg)
    stray = {tuple(surf.get_at((x, y)))[:3] for y in range(surf.get_height()) for x in range(surf.get_width())
             if surf.get_at((x, y)).a > 0} - set(smap)
    check(f"{g0.id} {name}: still every pixel a ramp shade", not stray, f"{len(stray)} stray")

# Evidence: unstyled vs Lucent Light, then a lineage and growth strip, at 4x.
os.makedirs(SCREENS_DIR, exist_ok=True)
scale, gap = 4, 8
rows = [[render(g, style=st.Style(**{**style.__dict__, "light_from": (0, 0)})) for g in genomes],
        [render(g) for g in genomes]]
lineage, m = [], g0
lrng = random.Random(2026)
for _ in range(5):
    lineage.append(render(m).subsurface((0, 0, T, T)).copy())
    m = mutate(m, lrng, rate=0.12)
growth = [render(grow(g0, s)).subsurface((0, 0, T, T)).copy() for s in (0.0, 0.33, 0.66, 1.0)]
rows.append(lineage + growth)
W = max(sum(s.get_width() * scale + gap for s in row) for row in rows)
H = sum(max(s.get_height() for s in row) * scale + gap for row in rows)
sheet = pygame.Surface((W, H), pygame.SRCALPHA)
sheet.fill((40, 44, 52, 255))
y = 0
for row in rows:
    x = 0
    for s in row:
        sheet.blit(pygame.transform.scale(s, (s.get_width() * scale, s.get_height() * scale)), (x, y))
        x += s.get_width() * scale + gap
    y += max(s.get_height() for s in row) * scale + gap
pygame.image.save(sheet, os.path.join(SCREENS_DIR, "art_style_sheet.png"))

print("=" * 64)
if _fails:
    bail()
print("Art style tests CLEAN")
