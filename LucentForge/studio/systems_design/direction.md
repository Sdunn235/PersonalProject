# Systems Design — Direction

*Found 2026-11-19, after two design notes (rest/fatigue want, 2026-08-04; perceived-need receptors,
2026-11-19) and the "formulas, not numbers" pass. Status: **proposal**. The department's own
values; Shawn decides if they are the studio's.*

## Values

1. **Formulas, not numbers.** A value is a strategy over attributes, recomputed as they grow. *Why:*
   creatures change, so their numbers have to follow them (Shawn: "I see you doing a lot of hard
   number sets").
2. **Author in the world's terms.** Write "reaches half in ½ day" or "a fifth of the comfort band", then
   derive per-frame rates. *Why:* game-term targets survive changes to FPS, day length and engine; a
   per-frame literal breaks under all three.
3. **Wants are citizens.** A new drive slots into brain → chemical → drive → urgency; no parallel engine.
   *Why:* emergence comes from one substrate interacting with itself, not from bolted-on systems.
4. **Model how things are, not how they should be.** Self-destructive outcomes are valid. *Why:* a sim
   where nothing can go wrong for its creatures has no agency in it.
5. **Design the drive, never the script.** Behavior has to fall out of needs, chemistry and traits.
   *Why:* the project is about emergent autonomy. A scripted outcome is a failed design.
6. **Every design is honest about the code.** Name the gap between doctrine and code reality
   (LF-043: decisions don't read drives yet) and design across it. *Why:* a design built for code that
   doesn't exist is inert (fatigue v1).

## Craft

**How a design note is built:**
1. **Substrate check:** what exists today (read the code, not the memory of it).
2. **Doctrine check:** which § rules govern it; what the bible stresses as a goal versus what it leaves open.
3. **Authored targets** in game terms (days, band fractions, reference individual).
4. **Derivation:** formulas over attributes and traits, solved into per-frame rates.
5. **Modulation:** how traits and attributes bend it (endurance → fatigue gain; fearfulness → strain).
6. **Acceptance examples** an observer could see, for QA.
7. **Costs and interactions:** what else it touches; what must land together (runnable state).

**Patterns this department reuses:**
- **The reference individual.** Define targets for an average member (endurance 10, resilience 4), and
  derive everyone else by ratio.
- **Bands and fractions.** Pulls and boosts are fractions of a need's comfort band, never raw points.
- **The receptor bridge.** Until LF-043, a chemical reaches decisions through a perceived-need receptor
  (`biochem/receptor.py`).
- **Caps by fraction.** Summed effects are capped at a fraction of the band (`PULL_CAP_FRACTION`).

**Artifacts:** the **design note** (`drafts/YYYY-MM-DD_<slug>.md`), the **authored-targets table**, the
**acceptance examples**.

## Signature

- An **authored targets** table: target, game-term value, why that value.
- Every rule cites its § section and labels itself *doctrine*, *decision* or *code reality*.
- "What this costs" and "what must land together" sections.
- No bare coefficients. If one appears, it carries its derivation.

## Handoffs

| With | Systems Design receives | Systems Design gives |
|---|---|---|
| **Story/Lore** | **Character seeds**: temperament, wants and affinity leanings in words. | Trait and need parameters that make those seeds *drive* behavior, plus questions where words won't become a formula. |
| **World Building** | Climate, biome and resource distribution for a region. | Source and need pressure per biome (scarcity, danger), as formulas over geography. |
| **Art** | The art genome's gene list. | A proposed **shared gene contract**: which genes are biology (heritable, tied to stats) and which are pure look. |
| **QA** | Questions about whether an example is observable. | **Acceptance examples** and authored targets. QA writes the red tests from them. |
| **Engineering** | Kick-backs when the substrate can't do what the note assumes. | A **locked design note** with implementation acceptance. |
| **QC** | A design-stage verdict. | Notes for review *before* QA writes tests. |
| **Director / Shawn** | Doctrine decisions (which side changes when code and bible disagree). | Classified options: what the bible stresses vs. what is open. |

## Beyond 2D

- **Mechanics are dimension-agnostic math.** Needs, chemistry, drives and stats don't care how the
  world is drawn.
- **Time in game units.** Authored targets are in days and minutes, never frames, so a 3D build at
  another tick rate recomputes the per-frame rates.
- **Space in world units.** Distances in tiles become distances in metres. Designs say "a short walk"
  or "within a panel" and leave the geometry to the world. 3D adds height (climbing, line of sight), so
  any spatial formula names its distance metric.

## Open questions

1. **LF-043, decisions follow the strongest drive (§B1).** The biggest open design. Ready to draft
   whenever Shawn makes it the next arc.
2. **One biology or two?** Should the art genome and the stat/trait genome become one heritable genome,
   so a goblin's build and its STR share genes? This decides the shape of the biology arc (LF-179).
3. **LF-044:** move the rest of the chemical table to authored game-term values, the same pass fatigue
   and strain got.
