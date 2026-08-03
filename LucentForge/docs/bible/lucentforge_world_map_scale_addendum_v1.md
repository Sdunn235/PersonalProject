# LucentForge World Map & Scale Addendum v1

**Created:** 2026-08-02 | **Stage:** World / Planetary (Arc B foundation) | **Authority:** LucentForge Bible — bridge between planetary maps and the existing Panel doctrine
**Status:** Draft for Shawn approval — establishes the authority boundary; does NOT choose final physical distances (see §S6, §S9)
**Section IDs:** §S1–§S9

---

## Purpose

This addendum reconciles planetary authoring maps with the existing **Rooms & Panels Addendum** (`lucentforge_rooms_panels_addendum_v1.md`, §R1–§R8).

> **Reconciliation stance:** The planetary map is an *authoring, indexing, and simulation-partition layer.* It **extends** the Panel doctrine; it does **not** supersede or replace it. The Panel remains the one lived-world scale.

Cite this addendum whenever planetary coordinates, macro maps, or map-to-panel resolution are involved.

---

## §S1 — Purpose

This addendum reconciles planetary authoring maps with the existing Rooms & Panels Addendum. It does not replace the Panel as the lived world unit.

## §S2 — Existing Panel Invariant (unchanged)

Per `rooms_panels_addendum §R1`, a Panel remains:

- one fixed 18×18 tile map;
- addressed by `(panel_x, panel_y)`;
- the same physical gameplay scale everywhere;
- inhabited **directly** by players and NPCs.

The player and NPCs do **not** shrink into a different world-map body. There is no Final Fantasy-style world-map zoom (this preserves `rooms_panels §R2`, the Zelda pre-N64 world model).

## §S3 — Planetary Map Role

A planetary map is a **sparse authoring and indexing layer.** It may store or reference:

- plate ID; crust type; elevation; ocean depth; temperature; rainfall; watershed; biome;
- resource tendencies; affinity state; settlement density; simulation partition; panel-generation profile.

## §S4 — Projection

Recommended master projection: **equirectangular, width twice height.** Candidate resolutions:

- 2048×1024 master authoring map;
- 1024×512 strategic derivative;
- lower previews derived from those sources.

A square 1024×1024 image may be retained as artwork, but should not be treated as an equal-distance geographic projection unless an explicit custom projection is adopted. See `docs/maps/map_projection_and_coordinates_v1.md`.

## §S5 — Pixel Meaning

A pixel is a **macro data sample**, not necessarily one Panel. A single macro pixel may map to:

- a rectangular panel range;
- a region-generation seed;
- a sparse quadtree node;
- a background simulation cell;
- a collection of authored panel IDs.

Do not promise one million manually authored cells. See `docs/maps/pixel_to_panel_resolution_v1.md`.

## §S6 — Scale Decision Required

The following values must be chosen **together** and are not yet canon:

- planetary circumference;
- master map width and height;
- target kilometers per macro pixel at the equator;
- approximate physical size of one gameplay tile;
- physical span of an 18×18 Panel;
- number of Panels per macro pixel;
- polar coordinate behavior.

Until those values are approved, **map pixels remain unitless design coordinates.**

## §S7 — Recommended Data Address

A future global locator may **wrap** the existing `WorldPos` rather than replace it:

```text
PlanetCoord
  macro_x
  macro_y
  panel_x    ┐
  panel_y    │  existing WorldPos, unchanged
  col        │
  row        ┘
```

`PlanetCoord` is a **proposed** wrapper, not an approved type. It adds a macro index above `WorldPos`; it does not introduce a second movement scale. Exact data types and conversion formulas belong in architecture/ADR documents and in `docs/genesis/genesis_data_contracts_v1.md`.

## §S8 — Sparse Detail

Most planetary coordinates need only low-detail persistent state. Detailed Panels are authored or generated when:

- the location is playable;
- an important entity inhabits it;
- nearby simulation requires it;
- historical events create lasting detail;
- the location is intentionally curated.

## §S9 — Out-of-Scope

This draft does not choose final physical distances. It creates the authority boundary needed to choose them safely.

---

## Related documents

- `lucentforge_rooms_panels_addendum_v1.md` (§R1–§R2) — the Panel invariant and Zelda world model this addendum extends
- `lucentforge_runtime_architecture_addendum_v1.md` — `WorldPos` and runtime ownership
- `docs/maps/map_projection_and_coordinates_v1.md`, `docs/maps/pixel_to_panel_resolution_v1.md`
- `docs/genesis/genesis_data_contracts_v1.md` — macrocell / panel-manifest contracts
