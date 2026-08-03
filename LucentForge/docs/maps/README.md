# Map Documentation

Standards for how LucentForge's world-map assets are authored, stored, projected, and resolved to gameplay Panels.

These are **implementation/standards documents.** Canonical *world truth* lives in the Bible (`../bible/`). Where a standard here needs an authoritative fact (projection, pixel meaning), it **cites** the Bible rather than redefining it.

## Documents

| File | Purpose |
|---|---|
| `map_layer_standard_v1.md` | Source-of-truth order, required layer stack, naming, registry fields, export/coordinate rules |
| `map_projection_and_coordinates_v1.md` | Projection and coordinate conventions (cites Bible §S4) |
| `pixel_to_panel_resolution_v1.md` | What a macro pixel means and how it resolves to Panels (cites Bible §S5/§S8) |

## Authority chain

- Bible world/scale authority: `../bible/lucentforge_world_map_scale_addendum_v1.md` (§S)
- Asset location and structure: `../../assets/maps/world_map/README.md`
- Generator use of these assets: `../genesis/`

## Related — but distinct — artifact

`../../assets/maps/world_map.csv` + `world_map_legend.md` are an **older macro *biome* sketch** (14 terrain tokens: Ocean, Coast, Forest, Mountains, etc.), not the tectonic plate work. Keep the two separate: the biome sketch is a coarse geography doodle; the plate art under `world_map/` is the tectonic source of record for the world foundation.
