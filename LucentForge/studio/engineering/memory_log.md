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
