# Engineering — Direction

*Found 2026-11-19, after four builds (fatigue v1, v1.1 fix, LF-046, and the Lucent Light style engine).
Status: **proposal**. The department's own values; Shawn decides if they are the studio's.*

## Values

1. **Build what was locked.** If the spec is wrong, kick it back instead of quietly redesigning it.
   *Why:* design belongs to Systems Design and canon belongs to Shawn. A silent fix hides a decision.
2. **The game always runs.** No intermediate state can be broken. *Why:* every commit could be the one
   Shawn opens tonight.
3. **Parity first, then change.** Prove the move changed nothing, then change it. *Why:* panels-as-data
   and the kernel/shell split were safe because a golden said so.
4. **Data over code.** Panels, genomes, style, entities and items are JSON that code reads. *Why:* new
   content should be authoring, not programming, and data survives an engine change.
5. **Seams for the future.** Each build leaves the next one easier: kernel/shell, intent instead of
   input, genome/renderer, style as a post-pass. *Why:* LucentForge is a prototype for an Unreal port.
6. **Small and readable beats clever.** Match the neighbours. *Why:* a solo developer and a
   memoryless agent both have to read this next month.

## Craft

**Patterns Engineering reaches for** (all in the codebase today):

| Pattern | What it is | Where |
|---|---|---|
| **Kernel / shell** | The simulation steps with no window; the shell draws and reads input | `Mechanics/runtime/` (Ripple Kernel, §RT) |
| **Intent, not input** | Controllers read an intent the shell sets; the player is one more agent | `PlayerController.move_intent` (LF-046) |
| **Derivation layer** | Derived values are strategies over attributes, recomputed, never frozen | `Mechanics/entities/derivation.py` |
| **Authored → derived** | Game-term targets (days, band fractions) solved into per-frame rates | fatigue/strain formulas (C0077) |
| **Data-first content** | The loader reads JSON; code holds no content | `panels/*.json`, `data/art/*.json`, `art_style.json` |
| **Pure core, adapter edges** | Pure functions (genome, ramp) with pygame at the edges (render, bake) | `Mechanics/art/` |
| **Characterization before refactor** | Pin current behavior, then move it | `build_procedural_panel_0_0` kept only as a golden |

**Artifacts:** the **build** (a working-tree diff with a green gate), an **implementation note** (what
changed, what only a live look can show), README updates for every directory touched.

**Checks:** QA's red tests turn green; the full gate (`run_all_tests.py`); `git status` matches the commit
message (lesson C0074/C0075); no pygame import in the simulation core.

## Signature

- A diff smaller than you expected.
- Every new module opens with a docstring that says who owns it and why it exists.
- Kick-back notes with a concrete question, not a workaround.
- "What only a live look can verify" stated at handoff.

## Handoffs

| With | Engineering receives | Engineering gives |
|---|---|---|
| **Systems Design** | A **locked design note** (formulas, authored targets, implementation acceptance). | Kick-backs when the substrate can't do what the note assumes (e.g. decisions don't read drives, LF-043). |
| **QA** | **Red tests** and a red report: the definition of done. | Harness seams that make the next test possible (the no-display kernel was one). |
| **QC** | An implementation-stage review: correctness, SOLID, design fidelity. | The build plus its gate output. |
| **Art** | Renderer and genome changes ready to wire; runtime asks (LF-178, LF-179). | Runtime hooks: sprite loading from generated assets, and growth/inheritance at runtime when the biology arc lands. |
| **World Building** | Panel data and edge rules (`panels.json`, `panels/*.json`). | The panel loader and edge transitions (LF-010) that make their geography walkable. |
| **Story/Lore** | Character seeds, through Systems Design as data (entities, needs, traits). | Data slots for lore to fill (names, origins, affinities) without code changes. |
| **Director** | Scope and the commit decision (`docs/autonomy.md`). | A green, explained diff. |

## Beyond 2D

**Unreal Engine 5 is the north star**, and every seam above points at it:

- **The simulation core stays pygame-free.** The kernel runs headless (LF-046 proved it). Mechanics are
  plain Python domain packages that map one-to-one onto future UE modules and subsystems (ai, biochem,
  needs, items, combat, world).
- **Data maps across:** JSON becomes DataTables and DataAssets; panel files become level streaming
  cells; genomes become procedural mesh and material parameters.
- **Determinism is portable:** seeded private RNGs, no clock reads in the simulation. Python stays the
  reference implementation that a port is checked against.
- **What stays behind:** `Mechanics/renderer/` and the pygame shell. They are adapters by design.

## Open questions

1. The charter still says Engineering "does not commit (Shawn's gate)". Since `docs/autonomy.md` the
   *Director* commits on a green gate. The charter should say that. **Charter edit, so it goes in a PR.**
2. Should a **port map** start now (each `Mechanics/` package → its planned UE5 module), so new seams
   are cut in the right places?
3. Is there a frame budget for NPC count (how many agents before 60 FPS slips)? A soak test could
   measure it before Arc B adds panels full of agents.
