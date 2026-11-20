# Epics — the Director's record

How each epic was decomposed, which departments ran, and how their outputs were reconciled. Newest at
the top. (README "Scaling further": started 2026-11-19, when the world loop first ran.)

---

## 2026-11-19 — The studio finds its groove + Arc B "what lies beyond Panel(0,0)"

**Shawn's ask:** "Start the studio and go to work… each department needs to find its values and direction
and how to work together."

**Decomposition:**

| Department | Ran as | Task | Output |
|---|---|---|---|
| World Building | dispatched agent (first run) | Direction + first neighbour proposal | `world_building/direction.md`, `world_building/proposals/2026-11-19_beyond_panel_0_0.md` |
| Story/Lore | dispatched agent (first run, in parallel) | Direction + who lives beyond | `story_lore/direction.md`, `story_lore/drafts/2026-11-19_beyond_panel_0_0.md` |
| Art | Director acting under the charter | Direction + a house style | `art/direction.md`; Lucent Light (C0091) |
| QA | Director acting under the charter | Direction; red tests for the style and the studio | `qa/direction.md`; `run_art_style_tests.py`, studio direction checks |
| Engineering | Director acting under the charter | Direction; the style engine | `engineering/direction.md`; `Mechanics/art/style.py` |
| QC | Director acting under the charter | Direction | `code_review_qc/direction.md` |
| Systems Design | Director acting under the charter | Direction | `systems_design/direction.md` |

**Reconciliation (Director):**

1. **World Building and Story/Lore converged without talking to each other.**
   - World Building recommends **one** neighbour first: **Panel(0,-1), the river's upper reach**. The
     river is the one feature that must carry across an edge, so proving the seam there proves it
     everywhere. It needs no new tile types, and Art already has its genomes.
   - Story/Lore recommends **upriver, the river clan's home water**. It's the best-sourced people in
     Gobby's story, and it turns GoblinThreat from a timer into a hungry, aggrieved people.
   - These are the same place if the river flows north to south (World Building's recommendation).
   - **Decision left for Shawn:** the river's direction, and whether the upper reach opens first.
2. **Cross-lane findings, verified by the Director:**
   - **Grom is a human** (`entities.json` npc_03). Art's first genome grew a goblin. *Fixed in C0092*
     (genomes declare `species`, which is now tested).
   - **`brain_dump.docx` is readable** (UTF-8 text with a .docx name). *LF-005 closed in C0092.*
   - **"Azure Woods / Azure River"** are **sourced** (`Gobby_the_Goblin/… Worldbuilding.csv`,
     `Characters.csv`), so World Building's worry that they are invented doesn't hold. They are not in the
     bible's terminology map, though. Whether to add them is a canon question for Shawn (§W8 leaves names
     open).
   - Claude memory `project_gobby_world` had forest goblins as "more peaceful". The source makes Gobby's
     people warlike and Gobby the exception. *Memory corrected.*
3. **Conflicts inside the Gobby source** (Story/Lore found them; only Shawn can settle them):
   - The knight's name: Rhiener / Roland / Reihner.
   - The rescued woman: Clara the merchant's daughter, or a princess.
   - Which wins when the Outline and `brain_dump` disagree.
4. **Bible housekeeping, for QC:** the needs/wants addendum and the world foundation both use `§W1…`
   section labels, so a bare "§W3" is ambiguous. Proposed fix: cite with the file prefix until one
   series is renamed (a doctrine PR).

**Waiting on Shawn:** the canon decisions above. Then the world loop continues: Art grows the upper
reach's props and the river clan from the biome sheet and creature briefs; Systems Design turns the
clan's character seeds into needs and traits; QA writes the edge contract (World Building's EC1–EC6) as
red tests; Engineering builds panel transitions (LF-010).
