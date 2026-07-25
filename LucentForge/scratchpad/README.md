# scratchpad/ — headless test suites & smoke runners

Pygame-free verification for LucentForge. Every script runs headless (SDL dummy
drivers) and reports `PASS`/`FAIL` with a nonzero exit on failure. Not shipped
with the game — this is the developer test surface.

## Run everything (the safety-net gate)

```powershell
$env:SDL_VIDEODRIVER='dummy'; py scratchpad/run_all_tests.py
```

`run_all_tests.py` discovers and runs **every** `scratchpad/*.py` as its own
subprocess, then prints a GREEN/RED table. A suite is RED if it exits nonzero
**or** prints a real `FAIL` marker (benign `0 FAIL` count summaries are ignored).
Exit code is nonzero if any suite is red.

**This is the golden-master gate for the Stage 4.6R runtime refactor (R0–R6):**
run it green *before and after every stage* to prove behavior was preserved.

## Key suites

| Script | Covers |
|--------|--------|
| `run_runtime_tests.py` | **R0 characterization net** — New Game reset, double save/load (no drift), zone-subscriber survival, defeated→kill selection, item+chest round-trip. Pins runtime-lifecycle behavior that Stage 4.6R will extract from `main.py`. |
| `smoke_test.py` | Save/load round-trip, autosave, slot isolation (Phase 1.5/1.6). Its `_build_game`/`_tick_n` harness is reused by `run_runtime_tests.py`. |
| `run_grace_tests.py` | The Grace 8-affinity lattice doctrine (§18). |
| `run_affinity_behavior_tests.py` | Affinity emitter/receptor + region-comfort memory + persistence (§B6/§D). |
| `run_stage2_tests.py` / `run_stage3_tests.py` | Consolidated Stage 2 (items) / Stage 3 (rooms-as-zones) suites. |
| `test_attr_parity.py` / `test_combat_parity.py` | Attribute-derivation and combat behavior parity guards. |
| `smoke_phase3x.py` / `smoke_phase4x.py` | Historical per-phase smokes (superseded by the consolidated runners but kept green). |
| `test_chest_bfs.py` / `test_chest_flows.py` / `test_outcome_resolver.py` | Chest placement/pathing, chest interaction flows, §12.2 outcome resolver. |

Run any suite individually the same way, e.g.
`$env:SDL_VIDEODRIVER='dummy'; py scratchpad/run_runtime_tests.py`.
