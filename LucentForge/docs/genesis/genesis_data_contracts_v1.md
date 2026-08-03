# Genesis Data Contracts v1

**Authority:** Technical architecture; subordinate to Bible canon.
**Status:** Proposed. Field names are conceptual until accepted through an architecture decision.

---

## Artifact header

Every generated or imported artifact should carry:

```text
artifact_id
artifact_type
schema_version
generator_stage
generator_version
seed_namespace
projection
width
height
coordinate_origin
wrap_x
wrap_y
source_artifacts
created_at
content_hash
canonical_status
```

## Initial artifact types

```text
planet_parameters      plate_id_raster        plate_motion_vectors
boundary_segments      crust_type_raster      elevation_raster
bathymetry_raster      climate_raster         watershed_raster
biome_raster           affinity_raster        macrocell_registry
panel_generation_manifest
```

## Stable IDs over colors

Use stable IDs such as `PLATE-CENTRAL` (see `../bible/lucentforge_planetary_tectonics_addendum_v1.md` §T2 and `assets/maps/world_map/registries/plate_registry.csv`). **Colors are presentation metadata**, resolved to identity only through the registry.

## Boundary representation

Do not infer all boundaries forever from colored pixels. Create explicit segments or graph edges containing:

- adjacent plate IDs;
- coordinates/polyline;
- boundary classification;
- direction;
- confidence;
- source and version.

## Macrocell record

```text
macro_x
macro_y
plate_id
elevation_band
temperature_band
moisture_band
biome_id
watershed_id
affinity_state
panel_manifest_ref
simulation_priority
```

## Panel conversion

The contract must preserve the existing runtime locator:

```text
WorldPos(panel_x, panel_y, col, row)
```

Genesis may create panel manifests, but **runtime Panel doctrine remains governed by the Bible** (`../bible/lucentforge_rooms_panels_addendum_v1.md` §R1, `../bible/lucentforge_world_map_scale_addendum_v1.md` §S7). The proposed `PlanetCoord` wraps `WorldPos`; it does not replace it.

---

## Related

- `genesis_architecture_v1.md`, `genesis_generation_pipeline_v1.md`, `genesis_validation_strategy_v1.md`
- `../maps/map_layer_standard_v1.md` — asset-side registry field definitions
