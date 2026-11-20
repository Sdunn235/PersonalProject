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
