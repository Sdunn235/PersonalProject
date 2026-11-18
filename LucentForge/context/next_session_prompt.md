# Session Start

**Caelum Session Start**

**Date:** [YYYY-MM-DD]
**Session topic:** lucentforge_fatigue_fix

## What I'm working on
LucentForge PyGame prototype — fixing the parked Rest/Fatigue want (BACKLOG LF-001) so it can pass its
live gate and merge to master, before starting Arc B "The World Opens" (map loader, LF-010).

## Last verified state
- **master** (`Personal Project` repo): C0069 = CHANGELOG + BACKLOG + full sync, C0071 = suite-count fix (2026-11-17).
  `py scratchpad/run_all_tests.py` → 22/22 green (23/23 on the branch).
- **Branch `wip/fatigue-want`** (C0070): the fatigue want (fatigue chemical, `ExertionEmitter`,
  `endurance(attrs)`, legibility in HUD / `V` inspector / `O` panel / npcs.csv, `run_fatigue_tests.py`
  17 checks) + the Engineering department. Headless tests are green, but the **live gate FAILED
  2026-11-17**: fatigue stays 0 for every NPC.
- **Cause (proven headlessly):** per-tick gain `FATIGUE_BASE_GAIN / endurance` = 0.0003 / (6–23) ≤
  natural decay `0.0002 × FATIGUE_DECAY_MULT` = 0.00005, which runs even while exerting.
- Brief is a hypothesis — check `git log` / `git status` / `git branch -a` first.

## Tasks for this session
1. `git checkout wip/fatigue-want`. Add the missing **integrated test** to `run_fatigue_tests.py`: every
   real NPC from `entities.json`, full emitter + `Chemicals.tick` path, exerting for thousands of ticks →
   fatigue reaches a visible level (e.g. > 0.1). Confirm it FAILS on the current tuning.
2. Fix: start with the tuning option (raise `FATIGUE_BASE_GAIN` about 10×, ≈0.003) and re-check the
   sleep invariant (fatigue × `FATIGUE_SLEEP_BOOST` + strain boost < 0.001). If tuning feels wrong, the
   structural option (no natural decay while exerting) needs a Systems Design + QC pass first.
3. Legibility: show chemicals to 4 decimals (or a per-tick delta) in the `V` inspector, so stepping
   with `.` visibly changes them.
4. Run `run_all_tests.py` → live gate (Shawn) → merge `wip/fatigue-want` into master → move LF-001 to
   the CHANGELOG.

## What feels unclear
- How fast *should* an NPC tire? Pick a target, e.g., "a goblin patrolling non-stop reaches fatigue 0.5
  in about half an in-game day", and derive the gain from it (formula, not a magic number).
- Whether the hardiest entity (Ignarix, endurance 23) should tire at all on short trips.

## Files likely to touch
- `settings.py` — fatigue constants
- `scratchpad/run_fatigue_tests.py` — integrated real-NPC test
- `Mechanics/renderer/inspector.py` — chemical precision
- `Mechanics/biochem/emitter.py` / `chemical.py` — only if the structural fix is chosen
- `CHANGELOG.md`, `BACKLOG.md`, `context/session_state.md`, `studio/engineering/memory_log.md`

## How to start
1. Read `Caelum/Caelum_Framework_Shawn_2026-03-12_Workflow_Expansion/CLAUDE.md` directly (identity +
   core memory + router).
2. Read `memory/projects/lucentforge_active.md` (Caelum) for current state.
3. Read `Personal Project/LucentForge/BACKLOG.md` ("Where you left off" + LF-001 details).
4. Read the latest session log: `sessions/2026-11-17_2230_lucentforge_review_sync.md`.
5. `git log` + `git status` + `git branch -a` in `Personal Project`.
6. Confirm the task list is still the right priority before writing code.

## ***IMPORTANT ADDITIONAL INFORMATION***
- Maintain SOLID, GRASP, LINQ, CRUDE principles; never flatten `Mechanics/`
- Directory + file names: basic, clear, short
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
