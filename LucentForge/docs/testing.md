# Testing

LucentForge is built **test-first** (from 2026-11-19). Tests are what let Claude work without Shawn at
the window ([autonomy policy](autonomy.md)). This file says which kind of test proves what, and how
to run them. Results are recorded in [verification](verification.md).

## The loop

1. **Acceptance example first.** Take it from the BACKLOG item or the bible § it serves: an observable
   statement ("a worn-out goblin beds down sooner than a rested one, same seed").
2. **Failing test.** Write it and run it; it must fail *for the right reason* (the behavior is missing,
   not a typo). Fatigue §6 failing 14/14 on the old tuning is the model.
3. **Implement** until that suite is green.
4. **Full gate:** `py scratchpad/run_all_tests.py` must be all green.
5. **Commit the test with the code** it proves, then push (CI re-runs the gate).

Anything you would check by eye gets a test instead. If a live look ever finds a problem, the first
fix is the test that would have caught it.

## What each kind of test proves

| Kind | Proves | Examples |
|---|---|---|
| Unit | a formula or rule in isolation | receptor pull math (fatigue §7, affinity §E4) |
| Integrated | real authored entities + the real tick path, over many frames | fatigue §6/§9, affinity §E1–§E3 |
| Behavior A/B | a feature changes what NPCs *do* (same seed, feature on vs off) | fatigue §8, affinity §E5 |
| Render | what the player *sees*: strings drawn on the HUD, O panel and V inspector | `run_render_tests.py` |
| Soak | "nothing odd" over days: ranges, no thrashing, no frozen movers, daily needs met, determinism | `run_soak_tests.py` |
| Characterization | a refactor changed nothing (golden behavior) | `run_runtime_tests.py`, parity suites |
| Persistence | save → load round trip keeps state | `smoke_test.py`, affinity §D, fatigue §4 |

**Tests can't establish:** whether pacing *feels* good, or art quality. Render tests save frames to
`logs/screens/latest/` (and CI uploads them) as evidence for an optional look.

## Writing tests here

- A **suite** is any top-level `scratchpad/*.py`; `run_all_tests.py` discovers and runs each one. Shared
  helpers live in `scratchpad/harness/` (never run directly). Use `harness.headless` for a seeded game
  (`new_kernel`), a real off-screen shell (`headless_shell`), drawn-text capture (`render_text`) and
  screenshots (`save_frame`).
- Print `[PASS]`/`[FAIL] <label>` per check and exit 1 on any failure. Keep output ASCII (the Windows
  console is cp1252).
- **Formulas, not numbers, applies to tests too:** a threshold states its rationale ("one state change
  per second over any minute") or derives from authored settings, never a tuned magic number.
- Seed from `harness.headless.SEED`; build each seeded run fully before starting the next (they share
  the global RNG). Never read or copy real save data; use temporary databases.
- Same-seed behavior tests run the real `SimulationKernel` for in-game time
  (`settings.FRAMES_PER_DAY`); the controller runs every frame.

## Commands

| What | Command (from `LucentForge/`) |
|---|---|
| Full gate | `py scratchpad/run_all_tests.py` |
| One suite | `py scratchpad/run_soak_tests.py` (any suite) |
| Hooks, once per clone | `git config core.hooksPath .githooks` (from the repo root) |

**CI:** `.github/workflows/lucentforge.yml` runs the full gate on hosted Linux for every push to
`master` and every PR touching `LucentForge/`. Its `verify` job rejects a failed or skipped gate.
Screenshots are uploaded as the `lucentforge-screens` artifact. **Hooks:** pre-commit compiles staged
LucentForge `.py` files; pre-push runs the full gate when the push touches `LucentForge/`.
