# Art — Direction

*Found 2026-11-19, the day after the department's first renders. Shawn: "Definitely gives me that child
taking first steps. Love that. Now the art needs to get in-depth, find a style, a flow."*
Status: **proposal**. The values and style below are the department's own; Shawn decides if they are the
studio's.

## Values

1. **Grown, not painted.** Every pixel traces back to a gene or a style formula. *Why:* only art that
   comes from data can inherit, mutate and grow up the way the creatures do. That is the biology.
2. **One world, one light.** Everything shares the Lucent Light house style. *Why:* many generated
   things only feel like one place if they are lit the same way, and the game is named for light.
3. **Silhouette first.** At 32 px you should see at a glance what it is and which way it faces.
   *Why:* in an autonomy sim the player reads behavior from figures, and a figure has to read first.
4. **Character lives in proportions, not decoration.** Gobby's thinness and big eyes are genes.
   *Why:* proportions can be inherited and mutated; decoration can't.
5. **Keep the charm of first steps.** Simple, honest, a little naive. Detail is added only when a need
   earns it. *Why:* Shawn loves the first-steps quality, and the simplicity keeps the biology readable.
6. **Provenance always.** Every image says where it came from. *Why:* the morning check takes seconds,
   and nothing anonymous slips in.

## Craft

**The flow** (how a thing comes to be seen):

```
Brief (who: Story/Lore · where: World Building)
  → Genome (bounded genes + one base color per material)
    → Form (renderer draws shapes in base colors + OUTLINE contours)
      → Light (style.apply: coloured outlines, lit rims, form shading)
        → Lineage check (5 generations of mutation, 4 growth stages: does it stay itself?)
          → Bake + registry → Contact sheet for Shawn
```

**Artifacts the department makes:**
- **Genome**: `Mechanics/data/art/<id>.json`.
- **The Style**: `Mechanics/data/art_style.json`, the Lucent Light constants.
- **Contact sheet** and **lineage strip**: `logs/screens/latest/art_*.png`.
- **Art report**: the charter's output contract.

**Working patterns:**
- **Materials, not colours.** A genome names a material's base color once (skin, cloth, eye; bark, leaf;
  stone), and the style grows its outline, shadow and light. Hand-picking a shadow is a smell.
- **The readability ladder.** First get the silhouette right, then the value (light vs. dark), and only
  then the hue. A design that needs hue to be read is not finished.
- **Species, then individual.** A species is a range of genes. An individual is a seed plus mutations.
  The lineage strip proves an individual stays inside its species (next step: species files, LF-179).
- **Relative, not absolute.** Shading depends on a shape's own size (`form_light_until` / `form_shadow_from`),
  so a newborn and a giant are lit the same way. The same rule as Systems Design: formulas, not numbers.

**Checks** (`run_art_tests.py`, `run_art_style_tests.py`):
- Determinism.
- Genes stay in bounds.
- Growth makes things larger.
- Palette discipline: every pixel is a ramp shade.
- One light per cell, with a no-light negative control.
- Outlines are never black.
- Provenance.

## Signature

- **Hue-shifted ramps.** Shadows lean cool (toward blue-violet) and highlights lean warm (toward gold).
  Nothing is darkened by mixing in grey.
- **Outlines in the material's own deepest shade**, lighter on the side that faces the light.
- **Light from the upper left**, everywhere, always.
- **Every asset can answer "which gene made this?"** If it can't, it isn't Art's work.
- **Every change comes with a contact sheet.** Art is shown, not described.

## Handoffs

| With | Art receives | Art gives |
|---|---|---|
| **Story/Lore** | A **creature brief**: who the creature is, its temperament and culture, and what its body should say (Gobby: thin, small, empathetic, forest-dwelling). | Questions about the look ("are River-tribe goblins blue?") and a lineage strip, so lore can watch a family resemblance. |
| **World Building** | A **biome sheet**: climate, flora, stone and light conditions, which become palette families plus tree and rock genomes. | Prop genomes per biome, and the art budget for a panel (which props are needed). |
| **Systems Design** | Which genes are *biology*: heritable and possibly tied to stats (does `body_width` follow STR?). | A shared gene contract proposal, so the art genome and the stat genome don't drift into two different biologies. |
| **QA** | Red tests for a new style invariant or gene behavior. | Style invariants written as plain claims ("every lit rim is brighter than its shadow rim") for QA to turn into checks. |
| **Engineering** | Runtime needs: wiring sprites (LF-178), and growth and inheritance at runtime (LF-179). | Renderer changes and genomes that are ready to wire, plus their tests. |
| **QC** | An **art review** at each stage: canon (does Gobby read as Gobby?) and standards (provenance, palette discipline). | The contact sheet and art report, as evidence. |
| **Director / Shawn** | The yes or no on direction and on wiring art into the game. | The contact sheet, lineage strip and open look questions. |

## Beyond 2D

The split that makes this survive is **genome = what a thing is; renderer = one way of seeing it**.

- **Dimension-agnostic now:** genes (proportions as fractions of the body, not pixels), materials (base
  colors), seed, growth stage, lineage, and the style's *ideas*: a single light direction, hue-shifted
  ramps, outlines from the material.
- **Isometric (64×32):** a second renderer reads the same genes. `light_from` becomes a 3D light vector
  projected onto the tile. Ramps are unchanged.
- **3D / Unreal Engine 5:**
  - Genes become morph targets or procedural mesh parameters.
  - Materials become base colors in a PBR material.
  - The ramp formula becomes a toon/cel shading ramp.
  - Lucent Light becomes the scene's key light plus a stylized shading model.
  - The lineage and growth logic carries over unchanged.
- **What will not survive:** pixel contours and the 2D form-shading pass. That is why the light is a
  post-pass, not part of the genes: it can be replaced without touching a single genome.

## Open questions

1. **Is Lucent Light the direction?** It's bright and storybook-like, with cool shadows and warm light.
   The alternative is a darker, grittier look closer to the detailed armored originals in `assets/images/`.
2. **Proportions.** The originals are chibi (big heads, compact bodies); the generated goblins are leaner.
   Should goblin genes drift toward the originals' head size, or keep their own look?
3. **Gear.** The original sprites wear armor and carry weapons. Should equipment be a layer grown from
   item data (a "gear genome" drawn over the body), so a goblin's look changes when it picks up an axe?
4. **When to wire** the grown art into the game (LF-178), and whether Grom's first in-game look should be
   generated or stay hand-made.
