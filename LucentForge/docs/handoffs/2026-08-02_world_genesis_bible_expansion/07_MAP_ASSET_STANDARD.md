# Lucent Forge World Map Asset Standard v1

**Target:** `LucentForge/docs/maps/map_layer_standard_v1.md`

## Source-of-truth order

1. Layered source artwork (`.psd` or native project format)
2. Approved layer registry
3. Lossless exported PNG layers
4. Derived previews
5. CSV/rasterized machine data
6. Generated outputs

A JPG preview is never the authoritative boundary source.

## Required layers

Recommended base stack:

1. projection guides
2. plate boundaries
3. plate movement
4. plate IDs / fills
5. crust type
6. tectonic boundary types
7. elevation
8. bathymetry
9. coastlines
10. atmosphere/winds
11. ocean currents
12. rainfall
13. temperature
14. watersheds
15. rivers/lakes/wetlands
16. biomes
17. affinity fields
18. resources
19. civilizations
20. labels and annotations

## Naming

```text
world_<layer>_vNNN.<ext>
plate_<plate_id>_vNNN.png
```

Examples:

```text
world_plate_boundaries_v003.png
world_plate_motion_v002.png
plate_central_v004.png
```

## Layer registry fields

```text
layer_id
layer_name
purpose
source_file
format
width
height
projection
color_model
alpha
authority
version
status
approved_by
notes
```

## Plate registry fields

```text
plate_id
display_name
source_layer
source_hex
crust_composition
motion_x
motion_y
motion_confidence
canonical_status
notes
```

## Color rule

Hex color identifies a class or plate only through a registry.

Do not embed meaning solely in visual color. The registry must contain the stable ID.

## Export rule

Export individual lossless PNG layers at identical dimensions with transparency retained.

Never rescale one layer independently.

## Coordinate rule

Top-left pixel is `(0,0)` in asset space unless the projection document explicitly states otherwise.

The left and right map edges wrap for equirectangular maps. The top and bottom edges do not wrap.

## Generated artifacts

Generated maps belong under `generated/` and should include provenance:

- generator version;
- configuration;
- seed;
- input asset versions;
- date;
- validation result.
