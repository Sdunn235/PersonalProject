# Session Start

**Caelum Session Start**

**Date:** [YYYY-MM-DD]
**Session topic:** lucentforge_arc_b_world

## What I'm working on
LucentForge, Arc B "The World Opens", step 2: decide and build what lies beyond the starting panel, so
walking off an edge loads a real neighbour panel (LF-010). Panels are already data (C0089).

## Last verified state
- master C0089, `run_all_tests.py` 30/30 green, CI green; hooks enabled.
- Starting panel: `Mechanics/data/panels/panel_0_0.json`; `panels.json` edges are all null.
- Studio: 7 departments (QA + Art new); World Building and Story/Lore have never run.
- Waiting on Shawn: LF-178 (wire generated Grom/Gobby art), LF-173 (acceptance examples), registry
  sources for the 10 original sprite sheets.

## Tasks for this session
1. Run **World Building** + **Story/Lore** (their first real job): propose the neighbouring panels (which
   biome/region, who lives there; Gobby lore + world foundation §W). Proposals → Shawn decides canon.
2. **QA:** failing tests for edge transitions (walk off EAST → Panel(1,0) loads, player/NPC positions map
   across, `can_transition` true).
3. **Engineering:** transitions until green; Art grows props for the new biome from genomes.

## What feels unclear
- How big Arc B's first world slice should be (one neighbour, or a ring of four).
- Whether NPCs follow across panels now or later (LF-120 off-screen sim).

## Files likely to touch
- `Mechanics/data/panels.json`, `Mechanics/data/panels/*.json`, `Mechanics/world/world_coord.py`,
  `Mechanics/runtime/kernel.py` (`_detect_panel_edge`), `Mechanics/world/tile_map.py`, new scratchpad suites.

## How to start
1. Read `Caelum/Caelum_Framework_Shawn_2026-03-12_Workflow_Expansion/CLAUDE.md` directly.
2. Read Caelum `memory/projects/lucentforge_active.md`.
3. Read `Personal Project/LucentForge/BACKLOG.md` ("Where you left off" + LF-042).
4. Read the latest session log: `sessions/2026-11-17_2230_lucentforge_review_sync.md`.
5. `git log` + `git status` in `Personal Project`.
6. Confirm the task list is still the right priority before writing code.

## ***IMPORTANT ADDITIONAL INFORMATION***
- Maintain SOLID, GRASP, LINQ, CRUDE principles; never flatten `Mechanics/`
- Rates in the controller/chemicals are **per frame** (60 FPS; a 300 s day = 18,000 frames)
- Any accumulator: test the integrated loop with real authored entities; check that gain beats leak
- Each directory with new/changed contents gets a README update
- Test functional before committing — Shawn runs `py main.py` before any runtime commit
- Commits use the next `C####:` number in the `Personal Project` repo

## Framework
`C:\Users\Shawn\Documents\Workspace\Caelum\Caelum_Framework_Shawn_2026-03-12_Workflow_Expansion`

## Canonical session log location
`...\Caelum\Caelum_Framework_Shawn_2026-03-12_Workflow_Expansion\sessions\` — `YYYY-MM-DD_HHMM_topic.md`

## Project reference to load
`Caelum/.../memory/projects/lucentforge_active.md`; deeper: `Caelum/.../projects/lucent_forge_master.md`;
in-repo: `CHANGELOG.md`, `BACKLOG.md`, `context/session_state.md`, `docs/bible/`.

## What I want from you
1. Help me orient — confirm or correct the "last verified state" above.
2. Choose or adapt the right workflow (this is an existing-project change).
3. Produce an execution plan; ask intent/design/structure/use/future questions before writing code.
