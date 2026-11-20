# Engineering — Memory Log

Append-only history of implementations this department has shipped into `Mechanics/`. Newest at the top.

**Entry format:**
```
## YYYY-MM-DD — <feature> (from <design note>)
- **Built:** the change in 1–3 lines.
- **Files:** the files touched.
- **Tests:** acceptance tests added + which suites were run.
- **Gate:** pass/fail counts (parity + regression).
- **QC verdict:** pass / pass-with-notes / block.
- **Live-gate left:** what only Shawn's `py main.py` can confirm.
- **Gotcha:** anything the next implementer should know.
```

Keep entries short — this is a build ledger, not project state (`active_context.md`) and not a lesson
(`reflection_log.md`).

---

## 2026-11-19 — Panel transitions (LF-010 step 2, C0095)
- **Built:**
  - `WorldSession.panel_maps` (a live map per visited panel), `map_for` / `sources_on` / `chests_on` /
    `enter_panel`.
  - `kernel._cross_panel_edge` (on an edge, pushing outward, neighbour defined → same column, far edge).
  - Panel-aware occupancy, combat, zones, trap perception, chest stamping and drawing; `Chest.panel_x/y`.
  - Saves write `entity_state.panel_x/y` (the columns existed since m0006).
- **Design note:** NPC controllers already held their own `tile_map`, so the departing panel keeps
  simulating without new machinery (§R6).
- **Gate:** 32/32.
- **Watch:** off-screen panels run at full fidelity. Fine for two panels; §R6 reduced scope when there are
  many (LF-120).

## 2026-11-19 — Lucent Light style engine (from Art's style direction, QA's red suite)
- **Built:** `Mechanics/art/style.py` (ramp formula, `apply` post-pass: coloured outlines, lit rims, form
  shading by relative position between lit and shadow contours), `art_style.json`, `MATERIALS` + palette
  validation in `genome.py`; render runs every cell through `apply`. `OUTLINE` contour marker = alpha 254.
- **Gate:** 31/31 (C0091, C0092); CI green on C0091.
- **Kick-back noted:** the charter still says Engineering doesn't commit "(Shawn's gate)". Autonomy policy
  moved commits to the Director on a green gate, so the charter needs a PR edit.

## 2026-11-17/18 — Rest/Fatigue want v1.1 FIX (LF-001; Director-implemented with Shawn present)
- **Built:** (1) per-frame tuning `FATIGUE_BASE_GAIN` 0.0003 -> 0.0015, derived from "human ref (endurance 10)
  reaches 0.5 in ~1/2 day"; every authored NPC now out-gains natural decay. (2) **Perceived-need receptor**:
  `biochem/receptor.py` sets `Need.perceived_pull = fatigue x FATIGUE_SLEEP_PULL (30)` on sleep; `Need.zone`/
  `urgency_score`/priority sort read `perceived_value`. Needed because decisions read need ZONES, never
  chemicals — the v1 tiredness boost could not change behavior even when tuned. (3) Inspector: chemicals to
  4 decimals + needs show `actual>perceived` when a pull is active.
- **Files:** settings.py, needs/need.py, needs/needs_system.py, biochem/receptor.py (new), ai/controller.py
  (step 2d), renderer/inspector.py; READMEs (biochem, ai, new needs/README); bible needs/wants §W6 + §W6.1,
  biochem §B7 code-gap note.
- **Tests:** run_fatigue_tests.py 17 -> 38: §6 integrated accrual over the real roster (written first, FAILED
  14/14 on old tuning — reproduced the live gate), §7 receptor unit + parity + no-bed-loop, §8 full-loop
  SimulationKernel same-seed with vs without pull (goblins bed down ~1/5 day sooner).
- **Gate:** run_all_tests.py 23/23 GREEN; run_fatigue_tests 38/38.
- **QC verdict:** not run as a separate department pass this time (Director-implemented, Shawn live-gating).
- **Live-gate left:** Shawn's py main.py re-run of the 5 checks.
- **Gotcha:** `affinity_strain` has the same inert-boost gap — reuse the receptor pattern (LF-042). Any new
  want must reach behavior through a receptor, not a chemical boost.

## 2026-11-19 — LF-046: the player moves by intent; kernel needs no display (from QA's red tests)
- **Built:** `PlayerController.move_intent` (dx, dy) replaces `pygame.key.get_pressed()` inside the sim;
  `PresentationShell._apply_player_intent()` sets it from the arrow keys before each kernel step. Ripple
  Kernel doctrine (§RT: the player is one more agent) now holds in code; an AI player or replay can drive
  the same intent.
- **Files:** `Mechanics/ai/player.py`, `Mechanics/runtime/shell.py`, `scratchpad/harness/headless.py`
  (display workaround removed).
- **Tests:** QA's `run_kernel_headless_tests.py` 5/5 (red first). Full gate on push.
- **Gotcha:** `_advance_one_tick` (the `.` single-step) reuses the intent set by the last loop iteration,
  which is fine: the loop sets it every frame before stepping.

## 2026-11-17 — Rest/Fatigue want v1: LIVE GATE FAILED (Director, after Shawn's `py main.py` check)
- **Seen live:** fatigue row/suffix present but fatigue stayed 0.00 for every NPC; stepping (`.`) showed no change.
- **Cause:** per-tick accrual `FATIGUE_BASE_GAIN / endurance` (0.0003 / 6–23 = 0.000013–0.000050) is
  <= natural decay `_DECAY x FATIGUE_DECAY_MULT` (0.0002 x 0.25 = 0.00005), and natural decay runs every
  tick *including while exerting*. All 7 authored NPCs have endurance >= 6 -> fatigue can never rise.
  Confirmed headlessly with a probe over the real `entities.json` roster.
- **Why the gate missed it:** `run_fatigue_tests.py` tests the emitter and `Chemicals.tick` separately with
  low test attributes; no check ran a real NPC through emitter + decay together over many ticks.
- **Status:** parked on branch `wip/fatigue-want` (not on master). Fix options + missing test: BACKLOG LF-001.
- **Gotcha:** any emitter whose target chemical is also in the natural-decay list must out-gain that decay
  for the *strongest* authored entity, or it is silently inert. Check `gain_min > decay` explicitly.

## 2026-08-09 — Rest/Fatigue want v1 (from 2026-08-04_rest_fatigue_want.md)
- **Built:** New `fatigue` chemical + `ExertionEmitter` mirroring `affinity_strain`/`AffinityComfortEmitter`.
  Exerting AI states (MOVING/RAIDING/RELOCATING/PATROLLING) accrue fatigue; resting at a bed pulls it to 0;
  IDLE / non-bed SATISFYING are neutral. Fatigue boosts ONLY `tiredness` (fatigue>floor), elevating perceived
  Sleep urgency through the unchanged drive. Accrual gain = `FATIGUE_BASE_GAIN / endurance(attrs)` where
  `endurance` is a new polymorphic derivation strategy (Constitution-led, Physique secondary), recomputed live.
  Perceived-urgency only — no SP drain (deferred to Fatigue Arc 2 per Director Q3).
- **Files:** `settings.py` (7 named constants + ENDURANCE_MIN clamp); `Mechanics/entities/derivation.py`
  (`endurance` strategy); `Mechanics/biochem/emitter.py` (`ExertionEmitter` + `EXERTING_STATES`);
  `Mechanics/biochem/chemical.py` (register `fatigue`, decay list, tiredness-only boost block);
  `Mechanics/ai/controller.py` (emitter instance + step-2c emit + `self.fatigue`); legibility in
  `run_logger.py` (npcs.csv header+value), `hud.py` (chem row), `inspector.py` (Col-2 line),
  `observation_panel.py` (suffix chain). READMEs bumped: biochem, entities, ai, observation, scratchpad.
- **Tests:** New `scratchpad/run_fatigue_tests.py` (17 checks): (1) fatigue=0 parity, (2) accrual in an
  exerting locus + decay at rest + neutral loci + locked EXERTING set, (3) the QC special-case — sleeping
  with fatigue=1.0 still nets tiredness DOWN, 50-tick monotone-down, tuning-invariant, awake-boosts-up
  contrast, (4) save round-trip via real SaveManager (no migration), (5) endurance strategy (hardy tires
  slower, live-attr recompute).
- **Gate:** `run_all_tests.py` 23/23 GREEN (incl. new suite + `test_attr_parity`/`test_combat_parity`).
  `run_affinity_behavior_tests.py` CLEAN. `run_fatigue_tests.py` 17/17 PASS. Parity proven headlessly.
- **QC verdict:** PASS WITH NOTES (Implementation × Systems, 2026-08-09). QC ran the gate itself (23/23; fatigue suite green) + independently recomputed the tiredness math (0.0005 < 0.001). No blockers/majors. Minor: **stage `scratchpad/run_fatigue_tests.py` in the integration commit** (untracked at review → gate silently loses a suite otherwise). Nits: `is_sleeping`→`at_bed` param name; doc said "step 2b", code correctly at 2c.
- **Live-gate left:** Shawn's `py main.py` — drive an NPC hard, confirm it seeks a bed sooner, fatigue is
  visible in HUD/inspector/panel and decays on sleep (feel/timing not provable headless).
- **Gotcha:** The tiredness boost runs AFTER the sleep-decay branch (`_DECAY*5=0.001`), so it ADDS back while
  sleeping. `FATIGUE_SLEEP_BOOST=0.0003` (+ strain ≤0.0002) stays under 0.001 → sleeping NPC still recovers.
  Do not raise it above ~0.0007 without re-checking. Console is cp1252 — keep test print strings ASCII
  (arrows/§ crash a standalone run, though run_all_tests pipes fine). `derivation.py` now imports `settings`
  (no cycle: settings is pure constants).
