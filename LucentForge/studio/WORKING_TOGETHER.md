# Working Together — how the LucentForge Studio works as one

*Written 2026-11-19, the day each department found its direction (`<dept>/direction.md`). Status:
**proposal**. Shawn decides if this is how the studio works.*

Each department has its own groove: values, craft and signature. This page is what they share: the
studio's values, the two loops work flows through, and the map of every artifact that passes between
departments. Read this page and the relevant `direction.md` before dispatching anyone.

## Studio values (what every department holds)

1. **Tests carry the trust.** Shawn's time goes to decisions, not checks (`docs/autonomy.md`).
2. **Formulas, not numbers.** Rates, shades, thresholds and proportions are derived from authored intent
   in the world's terms. That holds for Systems Design's fatigue, Art's ramps and QA's thresholds alike.
3. **Source and canon beat invention.** The bible and Shawn's Gobby story come first. Anything new is a
   **proposal**, tagged as such, until Shawn decides.
4. **Emergent, not scripted. Grown, not painted.** Behavior falls out of needs and chemistry; looks fall
   out of genes and light; land falls out of physics. No department hand-places an outcome the
   simulation should produce.
5. **Write it down.** Every run ends with a `memory_log.md` entry. A department that doesn't write back
   has no memory the next time it runs.
6. **Built to leave 2D.** Truth lives in data and the headless simulation; drawing is a view. Each
   department's `## Beyond 2D` says how its craft survives isometric, 3D and the UE5 port.

## The two loops

**The feature loop** (a mechanic or system):

```
Systems Design (design note) → QC (design review) → QA (red tests) → Engineering (green)
  → QC (implementation review) → Director commits under docs/autonomy.md
```

**The world loop** (a new place, people or creature):

```
World Building (region + biome sheets) ─┐
                                         ├→ Director reconciles → Shawn decides canon
Story/Lore (lore note + character seeds) ┘
  → Art (genomes grown from biome sheets + creature briefs)
  → Systems Design (seeds and biomes become formulas: needs, traits, source pressure)
  → QA (red tests: edge contract, character A/B) → Engineering (green) → QC → Director commits
```

World Building and Story/Lore can run **in parallel** on the same place. Physics and meaning are
different lanes, and the Director reconciles the two (2026-11-19: both independently chose the river's
upper reach as the first neighbour). Art, Systems Design and QA wait for Shawn's canon decision. Building
on a proposal makes rework.

## Handoff map

| Artifact | From | To | What it carries | Where it lives |
|---|---|---|---|---|
| Region sheet | World Building | Story/Lore, Art, Systems Design | Geography, climate, water, edge continuity, the physical facts of a place | `world_building/proposals/` |
| Biome sheet | World Building | Art | Flora, stone, light conditions → palette families, tree and rock genomes | inside the region proposal |
| Edge contract | World Building | QA, Engineering | Seam rules in testable form (what must match across a panel edge) | inside the region proposal |
| Lore note | Story/Lore | Systems Design, Art, World Building | Who lives there, what they want, history; SOURCED vs PROPOSED per claim | `story_lore/drafts/` |
| Character seed | Story/Lore | Systems Design, QA | Hunger, want, wound, threshold, direction of change, in words | inside the lore note |
| Creature brief | Story/Lore | Art | What a body should say (Gobby: thin, small, big-eyed, forest goblin) | inside the lore note |
| Canon decision | Shawn | World Building, Story/Lore | Which proposal becomes canon (and what changes in the bible) | bible PR / BACKLOG |
| Design note | Systems Design | QC, QA, Engineering | Formulas, authored targets, acceptance examples, costs | `systems_design/drafts/` |
| Gene contract | Systems Design, Art | Engineering | Which genes are biology (heritable, tied to stats) vs. pure look | proposal (LF-179) |
| Red tests + red report | QA | Engineering | The definition of done, failing for the right reason | `scratchpad/run_*.py` |
| Style invariants | Art | QA | Look rules as plain claims ("lit rims are brighter than shadow rims") | `art/direction.md` |
| Genome + contact sheet | Art | Director, Shawn, QC | What was grown, from which genes, shown not described | `Mechanics/data/art/`, `logs/screens/latest/` |
| Build | Engineering | QC | A diff with a green gate and what only a live look can show | working tree |
| Kick-back | Engineering | Systems Design, Director | "The substrate can't do what this assumes", with a concrete question | design note thread |
| Review verdict | QC | Director | PASS / PASS WITH NOTES / BLOCK, findings with failure scenarios | department memory logs |
| Finding | QC | QA | A defect caught by eye, to become a test | QA's next suite |
| Commit + evidence | Director | Shawn | The merged change and its verification-log entry | `CHANGELOG.md`, `docs/verification.md` |

## How disagreements work

- **Departments don't overrule each other.** They write a **kick-back** (Engineering → Systems Design), a
  **block** (QC, with what would clear it), or a **question** (anyone → the Director).
- **The Director reconciles** across lanes and owns the integrated result.
- **Shawn decides** canon, doctrine and anything on the PR list in `docs/autonomy.md`.
- A department may record a **dissent** in its memory log when it is overruled. The next run reads it.

## Shared language

| Word | Means |
|---|---|
| **proposal** | Not canon. Written so Shawn can decide. Every new place, people or style starts here. |
| **canon** | Decided by Shawn; lives in the bible or the Gobby source. |
| **SOURCED / PROPOSED** | Per-claim tags in lore: from Shawn's material, or new. |
| **red / green** | A test failing for the right reason / passing. |
| **kick-back** | "Can't build this as specified"; goes back up the loop with a question. |
| **code reality** | A dated note where the code and the bible disagree; it doesn't decide which side is right. |
| **grown** | Generated from data (genes, physics, needs), not hand-placed. |
