# Lucent Forge World Map & Scale Addendum v1 — Draft

**Proposed filename:** `lucentforge_world_map_scale_addendum_v1.md`  
**Authority:** Bible bridge between planetary maps and existing Panel doctrine  
**Status:** Draft  
**Section IDs:** `§S1–§S9`

## §S1 — Purpose

This addendum reconciles planetary authoring maps with the existing Rooms & Panels Addendum.

It does not replace the Panel as the lived world unit.

## §S2 — Existing Panel Invariant

A Panel remains:

- one fixed 18x18 tile map;
- addressed by `(panel_x, panel_y)`;
- the same physical gameplay scale everywhere;
- inhabited directly by players and NPCs.

## §S3 — Planetary Map Role

A planetary map is a sparse authoring and indexing layer.

It may store or reference:

- plate ID;
- crust type;
- elevation;
- ocean depth;
- temperature;
- rainfall;
- watershed;
- biome;
- resource tendencies;
- affinity state;
- settlement density;
- simulation partition;
- panel-generation profile.

The player does not shrink into a different world-map body.

## §S4 — Projection

Recommended master projection: equirectangular, width twice height.

Candidate resolutions:

- 2048x1024 master authoring map;
- 1024x512 strategic derivative;
- lower previews derived from those sources.

A square 1024x1024 image may be retained as artwork, but it should not be treated as equal-distance geographic projection unless an explicit custom projection is adopted.

## §S5 — Pixel Meaning

A pixel is a **macro data sample**, not necessarily one Panel.

A single macro pixel may map to:

- a rectangular panel range;
- a region-generation seed;
- a sparse quadtree node;
- a background simulation cell;
- a collection of authored panel IDs.

Do not promise one million manually authored cells.

## §S6 — Scale Decision Required

The following values must be chosen together:

- planetary circumference;
- master map width and height;
- target kilometers per macro pixel at the equator;
- approximate physical size of one gameplay tile;
- physical span of an 18x18 Panel;
- number of Panels per macro pixel;
- polar coordinate behavior.

Until those values are approved, map pixels remain unitless design coordinates.

## §S7 — Recommended Data Address

A future global locator may wrap the existing `WorldPos` rather than replace it:

```text
PlanetCoord
  macro_x
  macro_y
  panel_x
  panel_y
  col
  row
```

Exact data types and conversion formulas belong in architecture/ADR documents.

## §S8 — Sparse Detail

Most planetary coordinates need only low-detail persistent state.

Detailed Panels are authored or generated when:

- the location is playable;
- an important entity inhabits it;
- nearby simulation requires it;
- historical events create lasting detail;
- the location is intentionally curated.

## §S9 — Out-of-Scope

This draft does not choose final physical distances. It creates the authority boundary needed to choose them safely.
