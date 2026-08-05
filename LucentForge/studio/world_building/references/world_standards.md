# World Building — References & Standards

The bible + world foundation are authority; this file routes you to them.

## Bible slices (in `docs/bible/`)
| Concern | File | Use for |
|---|---|---|
| **Naming + world authority** | `lucentforge_terminology_map_v_1.md`, `lucentforge_world_foundation_v1.md` (§W) | Every place-name and world fact. |
| Tectonics / plates | `lucentforge_planetary_tectonics_addendum_v1.md` (§T) | 10-plate registry, boundary classification (§T3, one segment at a time). |
| Map scale | `lucentforge_world_map_scale_addendum_v1.md` (§S) | Planet↔Panel scale. **§S EXTENDS §R1 — no rogue zoom.** |
| Climate / hydrology | `lucentforge_climate_hydrology_addendum_v1.md` (§C) | Rainfall, rivers, rain shadows — coherence rules. |
| Panel doctrine | `lucentforge_rooms_panels_addendum_v1.md` (§R1) | The one 18×18 scale everywhere. `PlanetCoord` wraps `WorldPos`. |

## Assets (`assets/maps/`)
- `world_map/registries/plate_registry.csv` — 10 plates, stable IDs `PLATE-*`. `layer_registry.csv`.
- `world_map/{source,exported_layers,working,generated}/` — the plate/tectonic pipeline.
- `world_map.csv` + `world_map_legend.md` — the SEPARATE 14-token biome sketch. Don't conflate with the plate source.

## The hard rules (condensed — full text in charter)
1. **Planet map extends the Panel doctrine** — one 18×18 scale, `PlanetCoord` wraps `WorldPos`, no navigable zoom.
2. **Canonical structure with known gaps** — extend structure, name gaps in an Out-of-Scope register, never fabricate finished canon.
3. **Coherence over completeness** — plates/climate/hydrology/biomes internally consistent.
4. **Don't conflate** the plate source with the biome sketch.
5. **Boundary classification one segment at a time** (§T3), off the composite — often needs Shawn at the map.

## Genesis link
`docs/genesis/` is the separate-but-tandem generator design (docs-only today). Cite it when your canon
feeds the generator; don't assume generator code exists.
