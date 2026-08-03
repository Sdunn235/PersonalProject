# Map Projection & Coordinates v1

**Authority:** Asset/implementation standard. **The authoritative rule is the Bible** — `../bible/lucentforge_world_map_scale_addendum_v1.md` §S4. This document restates and operationalizes it; if the two ever diverge, the Bible wins.

---

## Master projection

Recommended master projection: **equirectangular, width = 2 × height** (Bible §S4).

Candidate resolutions:

- **2048 × 1024** — master authoring map
- **1024 × 512** — strategic derivative
- lower previews derived from those sources

A square (e.g. 1024 × 1024) image may be kept as artwork, but it is **not** an equal-distance geographic projection unless an explicit custom projection is adopted and documented here.

## Coordinate origin & wrap

- Top-left pixel is `(0,0)`.
- Left and right edges **wrap** (longitude seam).
- Top and bottom edges **do not wrap** (poles).
- Polar distortion under equirectangular is expected; polar coordinate behavior is an **open decision** (Bible §S6) and must not be assumed by code.

## Not yet chosen (Bible §S6)

Planetary circumference, km-per-pixel at the equator, tile physical size, Panel physical span, and Panels-per-macro-pixel are **not** canon. Until approved, **map pixels are unitless design coordinates.**

---

## Related

- `../bible/lucentforge_world_map_scale_addendum_v1.md` (§S4, §S6) — authority
- `pixel_to_panel_resolution_v1.md`, `map_layer_standard_v1.md`
