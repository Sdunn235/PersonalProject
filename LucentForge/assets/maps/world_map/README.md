# World Map Assets — Tectonic Plate Source

Handcrafted source artwork for LucentForge's canonical world (the tectonic/plate layer). This is the **tectonic source of record** cited by the Bible world documents.

## Authority

- World truth: `../../../docs/bible/lucentforge_world_foundation_v1.md` and `lucentforge_planetary_tectonics_addendum_v1.md`
- Asset standard governing this folder: `../../../docs/maps/map_layer_standard_v1.md`
- Generator use of these assets: `../../../docs/genesis/`

## Source-of-truth order

1. `source/layered/` — layered `.psd` masters (authoritative)
2. `registries/` — approved registries (stable IDs, hex, status)
3. `exported_layers/` — lossless PNG layers, identical dimensions
4. `working/` — derived previews / composites (never authoritative)
5. `generated/` — future Genesis outputs (empty; carries provenance when populated)

## Structure

```text
world_map/
├── README.md
├── source/
│   ├── layered/      # ExportedLayers.psd, plate_draft v1/v2/v2_01 PSDs
│   └── notes/        # design notes + original pipe-delimited hex key (unmodified source)
├── exported_layers/  # Layer1..Layer13 PNG (1 boundaries, 2 directions, 3-12 plates, 13 background)
├── registries/
│   ├── plate_registry.csv   # corrected + expanded (stable IDs, §08 fields)
│   └── layer_registry.csv
├── working/          # preview composites (v1, v2_01, plates_v2_01, composite_current)
└── generated/        # Genesis outputs (placeholder)
```

## Layer map

Layer1 = plate boundaries, Layer2 = plate directions (motion arrows), Layer3–Layer12 = the ten named plates, Layer13 = background. Hex colors resolve to plate identity **only through** `registries/plate_registry.csv` — never by color alone.

## Notes on source preservation

- `source/notes/plate_hex_color_key_source.csv` is the **original** pipe-delimited key, preserved unchanged (it contains a known malformed quote on the Greaterlands row). The corrected, machine-readable version is `registries/plate_registry.csv`.
- Nothing under `source/` or `exported_layers/` is edited — those are canonical source intent pending Shawn's registry approval (§T1).

## Distinct artifact — do not confuse

`../world_map.csv` + `../world_map_legend.md` one level up are an **older macro biome sketch** (14 terrain tokens), not this plate work. See `../../../docs/maps/README.md`.
