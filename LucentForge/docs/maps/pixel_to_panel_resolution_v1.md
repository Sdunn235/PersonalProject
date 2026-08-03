# Pixel-to-Panel Resolution v1

**Authority:** Asset/implementation standard. **The authoritative rule is the Bible** — `../bible/lucentforge_world_map_scale_addendum_v1.md` §S5 and §S8, and the Panel invariant `../bible/lucentforge_rooms_panels_addendum_v1.md` §R1. This document operationalizes them; the Bible wins on any conflict.

---

## A pixel is a macro data sample

A macro-map pixel is **not** automatically one Panel (Bible §S5). A single macro pixel may resolve to:

- a rectangular panel range;
- a region-generation seed;
- a sparse quadtree node;
- a background simulation cell;
- a collection of authored panel IDs.

**Do not promise one million manually authored cells.** Most macro coordinates hold only low-detail persistent state.

## The Panel stays fixed

A Panel remains one fixed 18×18 tile map addressed by `(panel_x, panel_y)` (Bible §R1). The macro map indexes *above* the Panel; it does not change the lived scale, and there is no world-map zoom body for the player.

## When detail is materialized (Bible §S8)

Detailed Panels are authored or generated only when:

- the location is playable;
- an important entity inhabits it;
- nearby simulation requires it;
- historical events create lasting detail;
- the location is intentionally curated.

## Proposed address (not yet approved)

`PlanetCoord { macro_x, macro_y, panel_x, panel_y, col, row }` wraps the existing `WorldPos` (Bible §S7). The conversion formula depends on the Panels-per-macro-pixel value, which is **not yet chosen** (Bible §S6).

---

## Related

- `../bible/lucentforge_world_map_scale_addendum_v1.md` (§S5, §S7, §S8) — authority
- `../bible/lucentforge_rooms_panels_addendum_v1.md` (§R1) — Panel invariant
- `../genesis/genesis_data_contracts_v1.md` — macrocell + panel-manifest contracts
