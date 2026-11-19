"""style.py — Lucent Light, the house style every grown asset shares (studio/art/direction.md).

Genes decide a thing's *form*; the style decides how light falls on it, the same way for everything:

- **One light.** `light_from` (data) says where the light comes from. Rims facing it are lighter, form
  shadows fall away from it.
- **Ramps are grown, not picked.** A genome gives one base color per material; `ramp()` derives
  outline / shadow / base / light from it by formula (lightness steps + a hue shift: shadows lean cool,
  light leans warm). Formulas, not numbers: no genome stores a shadow color.
- **Coloured outlines.** An outline is its material's own darkest shade, never black.

Renderers draw form with base colors (plus derived shades where they want explicit shading) and mark
contour lines with `OUTLINE`; `apply()` then lights the finished cell. Because the light is a direction
and the ramps are formulas, an isometric or 3D renderer can reuse both unchanged.
"""
from __future__ import annotations

import colorsys
import json
import os
from collections import Counter
from dataclasses import dataclass

import pygame

STYLE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "art_style.json")

# Contour marker drawn by renderers: alpha 254 tags a pixel as "outline here"; apply() replaces it.
OUTLINE = (0, 0, 0, 254)
_OUTLINE_ALPHA = 254


@dataclass(frozen=True)
class Style:
    light_from: tuple
    lightness_step: float
    outline_steps: float
    hue_shift_degrees: float
    cool_hue_degrees: float
    warm_hue_degrees: float
    grey_tint_saturation: float
    form_light_until: float
    form_shadow_from: float
    flat_materials: tuple


def load_style(path: str = STYLE_PATH) -> Style:
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return Style(light_from=tuple(d["light_from"]), lightness_step=float(d["lightness_step"]),
                 outline_steps=float(d["outline_steps"]), hue_shift_degrees=float(d["hue_shift_degrees"]),
                 cool_hue_degrees=float(d["cool_hue_degrees"]), warm_hue_degrees=float(d["warm_hue_degrees"]),
                 grey_tint_saturation=float(d["grey_tint_saturation"]),
                 form_light_until=float(d["form_light_until"]),
                 form_shadow_from=float(d["form_shadow_from"]),
                 flat_materials=tuple(d["flat_materials"]))


_DEFAULT: Style | None = None


def default_style() -> Style:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = load_style()
    return _DEFAULT


def _toward(h: float, target: float, degrees: float) -> float:
    diff = (target - h + 180) % 360 - 180
    step = max(-degrees, min(degrees, diff))
    return (h + step) % 360


def _shade(base, steps: float, s: Style) -> tuple:
    """Base color moved `steps` lightness steps (negative = darker, toward cool; positive = lighter, warm)."""
    h, l, sat = colorsys.rgb_to_hls(*(c / 255 for c in base[:3]))
    h *= 360
    target = s.cool_hue_degrees if steps < 0 else s.warm_hue_degrees
    if sat < s.grey_tint_saturation:          # greys have no hue to shift: borrow a tint instead
        h, sat = target, s.grey_tint_saturation * min(1.0, abs(steps))
    else:
        h = _toward(h, target, s.hue_shift_degrees * abs(steps))
    l = max(0.04, min(0.96, l + steps * s.lightness_step))
    r, g, b = colorsys.hls_to_rgb(h / 360, l, sat)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def ramp(base, s: Style | None = None) -> tuple:
    """(outline, shadow, base, light) grown from one base color."""
    s = s or default_style()
    base = tuple(int(c) for c in base[:3])
    return (_shade(base, -s.outline_steps, s), _shade(base, -1, s), base, _shade(base, 1, s))


def resolved_palette(genome) -> dict:
    """The genome's base materials over its kind's defaults (genome.MATERIALS)."""
    from Mechanics.art.genome import MATERIALS
    pal = dict(MATERIALS[genome.kind])
    pal.update(genome.palette)
    return {m: tuple(int(c) for c in rgb[:3]) for m, rgb in pal.items()}


def drawing_colors(genome, s: Style | None = None) -> dict:
    """What renderers draw with: each material's base, `<m>_shadow`, `<m>_light`, and the OUTLINE marker."""
    s = s or default_style()
    out = {"outline": OUTLINE}
    for m, rgb in resolved_palette(genome).items():
        if m in s.flat_materials:
            out[m] = (*rgb, 255)
            continue
        o, sh, b, li = ramp(rgb, s)
        out[m], out[f"{m}_shadow"], out[f"{m}_light"] = (*b, 255), (*sh, 255), (*li, 255)
    return out


def apply(cell: pygame.Surface, genome, s: Style | None = None) -> pygame.Surface:
    """Light one finished cell (a sprite frame or a prop tile) in place and return it.

    Every pixel's material is known from its color (shades are unique per material). Then:
    - a pixel on the silhouette (next to transparency) becomes an outline: the material's shadow shade on
      the side facing the light, its outline shade elsewhere;
    - an OUTLINE-marked contour inside the figure takes the darkest shade of the material it borders most;
    - an interior base pixel is shaded by where it sits *within its own shape*: walk toward the light and
      away from it to the contour; t = light-side distance / both. Small t catches the light
      (`form_light_until`), large t falls into shadow (`form_shadow_from`). Relative, so any size works.
    """
    s = s or default_style()
    lx, ly = s.light_from
    w, h = cell.get_size()
    raw = pygame.image.tobytes(cell, "RGBA")
    px = [tuple(raw[i:i + 4]) for i in range(0, len(raw), 4)]

    ramps, owner = {}, {}
    for m, rgb in resolved_palette(genome).items():
        if m in s.flat_materials:
            continue
        r = ramp(rgb, s)
        ramps[m] = r
        for i, c in enumerate(r):
            owner.setdefault(c, (m, i))

    def at(x, y):
        return px[y * w + x] if 0 <= x < w and 0 <= y < h else (0, 0, 0, 0)

    def empty(x, y):
        return at(x, y)[3] == 0

    def contour(x, y):
        p = at(x, y)
        return p[3] == 0 or p[3] == _OUTLINE_ALPHA

    def lit_side(x, y):
        return (lx and empty(x + lx, y)) or (ly and empty(x, y + ly))

    def edge(x, y):
        return empty(x - 1, y) or empty(x + 1, y) or empty(x, y - 1) or empty(x, y + 1)

    def material(x, y):
        p = at(x, y)
        if p[3] == _OUTLINE_ALPHA:
            near = Counter(owner[q[:3]][0] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                           if (q := at(x + dx, y + dy))[3] == 255 and q[:3] in owner)
            if not near:
                near = Counter(owner[q[:3]][0] for dy in range(-2, 3) for dx in range(-2, 3)
                               if (q := at(x + dx, y + dy))[3] == 255 and q[:3] in owner)
            if not near:
                return next(iter(ramps))
            top = max(near.values())
            return min(m for m, n in near.items() if n == top)      # deterministic tie-break
        return owner.get(p[:3], (None,))[0]

    def reach(x, y, dx, dy, m):
        """Steps from (x, y) along (dx, dy) to the shape's contour (empty, OUTLINE, or another material)."""
        n = 0
        while True:
            x, y, n = x + dx, y + dy, n + 1
            p = at(x, y)
            if p[3] != 255 or owner.get(p[:3], (None,))[0] != m:
                return n

    def form_position(x, y, m):
        to_light = reach(x, y, lx, ly, m)
        to_shadow = reach(x, y, -lx, -ly, m)
        return (to_light - 1) / max(1, to_light + to_shadow - 2)

    out = list(px)
    for y in range(h):
        for x in range(w):
            p = px[y * w + x]
            if p[3] == 0:
                continue
            m = material(x, y)
            if m is None:                                          # flat material (eyes): untouched
                continue
            r = ramps[m]
            if edge(x, y):
                c = r[1] if lit_side(x, y) else r[0]
            elif p[3] == _OUTLINE_ALPHA:
                c = r[0]
            elif p[:3] == r[2] and (lx or ly):
                t = form_position(x, y, m)
                c = r[3] if t < s.form_light_until else r[1] if t >= s.form_shadow_from else r[2]
            else:
                c = p[:3]
            out[y * w + x] = (*c, 255)
    lit = pygame.image.frombytes(bytes(v for q in out for v in q), (w, h), "RGBA")
    cell.fill((0, 0, 0, 0))
    cell.blit(lit, (0, 0))
    return cell
