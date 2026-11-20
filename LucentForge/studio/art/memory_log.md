# Art — Memory Log

Append-only history of what this department grew: genomes, seeds, renders, lessons about the biology.
Newest at the top.

**Entry format:**
```
## YYYY-MM-DD — <asset / gene work> (from <task>)
- **Grown:** genomes + seeds, output paths.
- **Genes:** what was added/changed and what each controls.
- **Tests:** art suite results.
- **Open:** look/lore questions for Shawn or Story/Lore.
```

---

## 2026-11-19 — Lucent Light house style; Grom regrown as human (from Shawn: "find a style, a flow")
- **Grown:** all four genomes re-baked under the style (C0091). Grom regrown as a human, seed 2002 (C0092).
- **Genes:** palettes are base materials only (shades derived by `style.py`); new `species` field; new
  gene `skin_marks` (0-4, goblin mottling, heritable).
- **Style:** `Mechanics/data/art_style.json`: one light from the upper left, hue-shifted ramps, outlines in
  the material's own darkest shade, size-relative form shading.
- **Tests:** `run_art_style_tests.py` clean (no-light negative control); art suite adds species agreement.
- **Learned:** palette discipline doesn't guarantee readability. Grom's first human regrowth had dark
  cloth, and his legs vanished against a dark background while every test was green. Next invariant to
  give QA: value contrast between a figure's main shades and typical ground tiles.
- **Open:** direction, chibi vs lean proportions, a gear layer, wiring (all in `direction.md`).

## 2026-11-19 night — The upper reach's props (LF-184, C0100)
- **Grown:** from World Building's biome sheet (§9), `reach_oak_west` and `reach_oak_east` (mature, leaning
  toward the water) from `azure_oak`, and `reach_stone` (less worn) from `river_stone`. This is the department's
  first biome brief turned into genomes.
- **Genes:** no new genes. New genome field `parent` (lineage; orphans are refused). New invariant: props fit
  their tile.
- **Learned:** a seed's lobes are lopsided, so "leans" can't be measured against the tile centre. The
  upright twin (same seed, no lean) is the honest reference, and the upright control is what showed it.
- **Open:** a trunk tilt (today only the canopy leans); per-tree variety on the same bank (runtime mutation,
  LF-179); the upper reach's shadier ground (no ground genome kind yet).

## 2026-11-19 night — The grown art goes into the game (LF-178, C0101)
- **Shawn's call** (open question 4 answered): "Wire the grown art into the game." Grom wears his grown
  sheet; every panel's trees and rocks are its grown props, named in the panel's data.
- **Seen in game:** the trees read clearly, and the upper reach looks like a real wood leaning toward its river. The
  stones read smaller but still as obstacles. Grom reads as himself, not the player.
- **Learned:** in the game, our flat first-steps look sits right beside the detailed originals. The gap is
  now a question Shawn can see (LF-186), not one we describe. A stand of one genome is visibly clones (LF-185).

