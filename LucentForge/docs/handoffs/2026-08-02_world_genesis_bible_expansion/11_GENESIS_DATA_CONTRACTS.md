# Genesis Data Contracts v1 — Proposed Technical Document

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

- `planet_parameters`
- `plate_id_raster`
- `plate_motion_vectors`
- `boundary_segments`
- `crust_type_raster`
- `elevation_raster`
- `bathymetry_raster`
- `climate_raster`
- `watershed_raster`
- `biome_raster`
- `affinity_raster`
- `macrocell_registry`
- `panel_generation_manifest`

## Stable IDs over colors

Use stable IDs such as `PLATE-CENTRAL`.

Colors are presentation metadata.

## Boundary representation

Do not infer all boundaries forever from colored pixels.

Create explicit segments or graph edges containing:

- adjacent plate IDs;
- coordinates/polyline;
- boundary classification;
- direction;
- confidence;
- source and version.

## Macrocell record

A macrocell may hold:

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

The contract must preserve existing:

```text
WorldPos(panel_x, panel_y, col, row)
```

Genesis may create panel manifests, but runtime Panel doctrine remains governed by the existing Bible.
