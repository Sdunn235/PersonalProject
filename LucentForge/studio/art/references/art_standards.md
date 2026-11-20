# Art standards

## Sheets and tiles (what the game loads today)
- **Character walk sheet:** 3 columns × 4 rows of 32×32 cells = 96×128 PNG. Rows top-to-bottom:
  **down, left, right, up**. Columns: 3 walk frames; frame 0 is the idle pose. Loaded by
  `Mechanics/renderer/sprite.py` (`EntitySprite`), path from `entities.json` `"sprite"`.
- **Prop / tile:** a single 32×32 PNG (trees, rocks, objects). The map grid is 18×18 tiles of 32 px.
- **Transparent background** (alpha); sprites are drawn over the tile map.
- **Isometric later:** 64×32 tiles with Z layers (memory: art direction). Renderers must stay separate
  from genomes so an isometric renderer can read the same genes.

## Art genomes (the biology)
- Files: `Mechanics/data/art/<id>.json`. Fields: `id`, `kind` (`creature` | `tree` | `rock`), `seed`,
  `stage` (growth, 0..1), `genes` (name → value), `palette` (role → RGB).
- **Genes are bounded.** The bounds live in `Mechanics/art/genome.py` (`GENE_BOUNDS` per kind) with a
  default for each gene, so an old genome stays valid when new genes are added.
- **Mutation** (`mutate`) nudges genes within bounds and drifts palette slightly; it never invents new
  genes. **Growth** (`grow`) changes `stage`; size-like genes scale with stage.
- **Determinism:** rendering uses only the genome and its `seed` (a private `random.Random`), never the
  global RNG or the clock.

## Provenance (`assets/registry.json`)
One entry per image under `assets/`: `path`, `kind`, `source` (`hand-made` / `third-party` /
`generated` / `unknown`), `licence`, and for generated art `genome` + `seed`. The ten original sheets
are `unknown` until Shawn says where they came from.

## Palette
Earthy, readable at 32 px. A genome names **one base color per material**; the house style
(`Mechanics/data/art_style.json`, `Mechanics/art/style.py`, Lucent Light) grows outline / shadow / base /
light from it. Never store a shadow or outline color in a genome. Check value against the ground: a
material whose shadow sits near the tile colors disappears (Grom's first regrowth).
Goblin skin greens; River-goblin blue tint (Gobby lore: Azure River pigmentation); keep UI semantic colors
(red/amber/green) out of creature palettes.
