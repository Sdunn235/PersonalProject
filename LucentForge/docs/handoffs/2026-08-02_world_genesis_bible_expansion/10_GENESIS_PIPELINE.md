# Genesis Generation Pipeline v1 — Proposed Technical Document

## Pipeline

```text
G00 Input and provenance
G01 Planet parameters
G02 Projection and coordinate grid
G03 Plate topology
G04 Plate motion and boundary classification
G05 Crust age and composition
G06 Elevation and bathymetry
G07 Sea level and coastlines
G08 Atmosphere and circulation
G09 Ocean circulation
G10 Temperature and rainfall
G11 Hydrology and erosion
G12 Biomes and soils
G13 Resources and affinity fields
G14 Ecology and species
G15 Civilization seeding
G16 History simulation
G17 Panel-space conversion
G18 Validation and package export
```

## Important correction

The pipeline may iterate.

Examples:

- erosion changes elevation;
- elevation changes climate;
- climate changes erosion;
- vegetation changes soil and water;
- civilization changes land cover.

The pipeline is an execution graph with controlled feedback, not necessarily one irreversible pass.

## Canonical-home-world mode

Genesis should support:

```text
mode = authored_canonical
```

In that mode:

- plate IDs and source shapes may be locked;
- Shawn's approved motion vectors may be fixed;
- selected landmarks may be protected;
- algorithms fill unresolved layers;
- validation reports conflicts instead of silently changing canon.

## Generated-world mode

```text
mode = procedural
```

In that mode, Genesis may create plate topology and geography from configuration and seed.

## First implementable milestone

Do not start with tectonic simulation.

Start with:

1. artifact contract;
2. deterministic random source;
3. stage dependency ordering;
4. provenance;
5. a no-op or test stage;
6. validation;
7. a simple raster import/export stage.

That core can later host real geography.
