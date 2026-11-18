# Session Start

**Caelum Session Start**

**Date:** [YYYY-MM-DD]
**Session topic:** lucentforge_strain_receptor

## What I'm working on
LucentForge PyGame prototype. Give `affinity_strain` the same perceived-need receptor fatigue got
(BACKLOG LF-042), so strain actually changes behavior. Then the July live spot-checks (LF-002), then start
Arc B "The World Opens" (map loader, LF-010).

## Last verified state
- **master** (`Personal Project` repo): C0073 = merge of the Rest/Fatigue want v1.1 (C0070 build, C0072
  fix); C0074–C0075 docs. `py scratchpad/run_all_tests.py` → 23/23 green; fatigue live gate passed
  2026-11-18.
- `biochem/receptor.py` holds `apply_perceived_pulls(needs, chemicals)`. It currently sets only
  fatigue → sleep. `Need.perceived_pull` / `perceived_value`; `zone` reads the perceived value.
- `affinity_strain` (C0046) only boosts need chemicals, which decisions never read, so it's inert
  (bible biochem §B7 code-gap note).
- Uncommitted on purpose: `TheForge/global.json` (SDK rollForward change in the read-only blueprint;
  waiting on Shawn's call).
- Brief is a hypothesis — check `git log` / `git status` first.

## Tasks for this session
1. Design the strain pull: strain × a named constant on **all** survival needs (hunger, thirst, sleep).
   Combine it with fatigue's sleep pull (additive?) and cap the total so a just-satisfied need stays FINE.
2. Write the test first: a same-seed `SimulationKernel` day with vs without the strain pull (pattern:
   `run_fatigue_tests.py` §8). Pick NPCs that actually sit in hostile-affinity ground long enough.
3. Implement in `receptor.py`, run `run_all_tests.py`, then the live gate (Shawn).
4. If time: LF-002 live spot-checks (relocate `RELO`, region memory across save/reload, Grace entities).

## What feels unclear
- Does anyone accumulate enough strain in normal play to show the effect? Villagers live on neutral
  town ground; goblins leave their camp to raid. Measure peak strain headlessly first.
- Should strain's pull be smaller than fatigue's (it's a background tax, not exhaustion)?

## Files likely to touch
- `Mechanics/biochem/receptor.py` — the strain receptor
- `settings.py` — `AFFINITY_STRAIN_PULL` (+ a total-pull cap, if needed)
- `scratchpad/run_affinity_behavior_tests.py` — integrated behavior test
- `docs/bible/lucentforge_biochem_affinity_addendum_v1.md` §B7 — replace the code-gap note
- `CHANGELOG.md`, `BACKLOG.md`, `context/session_state.md`, `Mechanics/biochem/README.md`

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
