# LucentForge World Map Asset Standard v1

**Authority:** Asset/implementation standard. Cites the Bible for world truth; governs how map assets are stored and exported.

---

## Source-of-truth order

1. Layered source artwork (`.psd` or native project format)
2. Approved layer registry
3. Lossless exported PNG layers
4. Derived previews
5. CSV/rasterized machine data
6. Generated outputs

**A JPG (or any lossy) preview is never the authoritative boundary source.**

## Required layers

Recommended base stack (the current plate art covers layers 2–4 + a background fill):

```text
 1 projection guides        11 ocean currents
 2 plate boundaries         12 rainfall
 3 plate movement           13 temperature
 4 plate IDs / fills        14 watersheds
 5 crust type               15 rivers/lakes/wetlands
 6 tectonic boundary types  16 biomes
 7 elevation                17 affinity fields
 8 bathymetry               18 resources
 9 coastlines               19 civilizations
10 atmosphere/winds         20 labels and annotations
```

## Naming

```text
world_<layer>_vNNN.<ext>
plate_<plate_id>_vNNN.png
```

Examples: `world_plate_boundaries_v003.png`, `world_plate_motion_v002.png`, `plate_central_v004.png`.

## Layer registry fields

```text
layer_id  layer_name  purpose  source_file  format  width  height
projection  color_model  alpha  authority  version  status  approved_by  notes
```

## Plate registry fields

```text
plate_id  display_name  source_layer  source_hex  crust_composition
motion_x  motion_y  motion_confidence  canonical_status  notes
```

See `../../assets/maps/world_map/registries/plate_registry.csv` and `layer_registry.csv`.

## Color rule

Hex color identifies a class or plate **only through a registry.** Do not embed meaning solely in visual color. The registry must contain the stable ID (e.g. `PLATE-CENTRAL`).

## Export rule

Export individual lossless PNG layers at **identical dimensions** with transparency retained. **Never rescale one layer independently.**

## Coordinate rule

Top-left pixel is `(0,0)` in asset space unless the projection document explicitly states otherwise. For equirectangular maps, the **left and right edges wrap; top and bottom do not.** See `map_projection_and_coordinates_v1.md`.

## Generated artifacts

Generated maps belong under `../../assets/maps/world_map/generated/` and should include provenance: generator version; configuration; seed; input asset versions; date; validation result (per `../genesis/genesis_data_contracts_v1.md`).
