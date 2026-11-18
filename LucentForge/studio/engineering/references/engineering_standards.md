# Engineering — References & Standards

You implement locked designs. The design note is the spec; these are the house rules.

## Authority docs
| Concern | Where |
|---|---|
| Architecture rules | `LucentForge/CLAUDE.md` — never flatten `Mechanics/`; keep needs/biochem/ai separate; data-driven JSON; SOLID; every system a building block toward the UE5 port. |
| The gate you must pass | `../code_review_qc/references/test_gate_protocol.md` (shared with QC — it's what QC checks). |
| Implementation traps | `../code_review_qc/references/solid_grasp_checklist.md` (mock-parity, debug-print-after, execution-order, stale-SQLite-blob). |
| The spec | the locked design note handed to you — its **Director Decisions** + **Implementation Acceptance** sections are authoritative. |

## Run / verify
- Run headless suites via Bash from `LucentForge/`: `python scratchpad/run_all_tests.py` (the golden-master
  aggregate) + the relevant characterization suite (`run_affinity_behavior_tests.py`, `run_grace_tests.py`,
  `run_runtime_tests.py`, etc.). Use the interpreter that resolves on this machine (try `py`, then `python`,
  then `python3` — LucentForge uses `pygame-ce` on Python 3.14).
- **The window blocks headless.** `py main.py` opens a blocking window — you **cannot** run the live game;
  prove everything you can headlessly and hand the visual/behavioral confirmation to Shawn's live gate.

## Patterns worth reusing (from the reflection log)
- **Compat property** to split/rename a load-bearing field with near-zero churn (old name → property over new storage).
- **Reserved-but-unconsumed seams** — often the work is to *use* what's there, not add.
- **Faithful tests reuse the real pipeline** (e.g. `SaveManager.snapshot()/restore()` through a temp DB), not a replicated shape.
- **Parity harness first, swap second** when changing numeric/behavioral systems.

## Hard limits
- Do **not** commit (Shawn's gate). Leave changes in the working tree.
- Do **not** redesign — if the locked design is infeasible, STOP and kick back to the Director.
- Do **not** touch files the design doesn't name without saying why in the report.
