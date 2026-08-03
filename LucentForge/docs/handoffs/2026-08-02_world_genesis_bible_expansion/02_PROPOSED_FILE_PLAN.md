# Proposed Repository File Plan

This is a proposed structure. Claude must inspect the live repository first and adapt paths without creating duplicate authorities.

```text
LucentForge/
├── docs/
│   ├── bible/
│   │   ├── README.md                                  # update index only
│   │   ├── lucentforge_world_foundation_v1.md
│   │   ├── lucentforge_planetary_tectonics_addendum_v1.md
│   │   ├── lucentforge_world_map_scale_addendum_v1.md
│   │   └── lucentforge_climate_hydrology_addendum_v1.md
│   │
│   ├── genesis/
│   │   ├── README.md
│   │   ├── genesis_architecture_v1.md
│   │   ├── genesis_generation_pipeline_v1.md
│   │   ├── genesis_data_contracts_v1.md
│   │   ├── genesis_validation_strategy_v1.md
│   │   └── genesis_canonical_world_adapter_v1.md
│   │
│   └── maps/
│       ├── README.md
│       ├── map_projection_and_coordinates_v1.md
│       ├── map_layer_standard_v1.md
│       └── pixel_to_panel_resolution_v1.md
│
└── assets/
    └── maps/
        └── world_map/
            ├── README.md
            ├── source/
            │   ├── layered/
            │   └── notes/
            ├── exported_layers/
            ├── registries/
            │   ├── plate_registry.csv
            │   └── layer_registry.csv
            ├── working/
            └── generated/
```

## Why only four new Bible documents

The Bible should remain navigable. Planetary truth is grouped into four responsibilities:

1. world identity and physical assumptions;
2. tectonic structure;
3. map scale and panel reconciliation;
4. climate, water, and biomes.

Genesis receives more documents because technical concerns change more often and should not burden canon.

## Files that must not be moved casually

Do not relocate existing:

- Bible documents;
- `rooms.json`, `panels.json`, or runtime map data;
- source plate artwork;
- current exported layers;
- context/session files.

Add navigation before considering reorganization.
