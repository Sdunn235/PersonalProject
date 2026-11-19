# Mechanics/art/ — art genomes (art is grown, not painted)

Shawn's goal (2026-11-19): a *biology* for how the world's art and objects come to be. Every generated
creature, tree and rock is rendered from an **art genome**: data that can vary, grow and evolve. Owned
by the Art department (`studio/art/charter.md`).

| File | Role |
|---|---|
| `genome.py` | `Genome` (kind, seed, growth `stage`, bounded `genes`, `palette`); `GENE_BOUNDS` + defaults per kind; `load_all()`; `mutate(genome, rng, rate)` (stays in bounds); `grow(genome, stage)`. |
| `render.py` | Genome → `pygame.Surface`. Creatures: the game's 3×4 walk sheet (rows down/left/right/up, 3 frames, 32-px cells). Trees/rocks: one 32-px tile. Deterministic from the genome's own seed. |
| `bake.py` | `py -m Mechanics.art.bake [ids]`: writes `assets/generated/<id>.png` and records it in `assets/registry.json` (genome + seed). Never touches `assets/images/`. |

Genomes live in `Mechanics/data/art/*.json` (`gobby`, `grom`, `azure_oak`, `river_stone` to start). Any
extra keys (e.g. `_lore`) are notes for people and are ignored by the loader.

**Rules:** genes are named for what they do and bounded; adding a gene means adding a default, so older
genomes stay valid. Growth scales size-like features from `GROWTH_NEWBORN_SCALE` (a newborn's fraction
of adult size) to 1. Renderers read genes only, so an isometric renderer can come later without
changing a single genome.

**Not yet:** generated sheets are not wired into `entities.json` (Shawn's call), and nothing grows or
evolves at runtime yet. That's the biology arc (BACKLOG LF-179). Tests: `scratchpad/run_art_tests.py`.
