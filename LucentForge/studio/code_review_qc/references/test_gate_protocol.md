# Test Gate Protocol (Implementation / Refactor / Closeout stages)

Apply **only** when there is code. A design note has nothing to gate.

## The gate
- `scratchpad/run_all_tests.py` is the golden-master aggregate. It must be **green after every commit**
  in a refactor arc — not just at the end. The net is a *precondition*, not a deliverable.
- Characterization suites: `run_runtime_tests.py`, `run_affinity_behavior_tests.py`, `run_grace_tests.py`,
  `run_stage2_tests.py`, `run_stage3_tests.py`, plus `test_*_parity.py`.
- A scratchpad test that is worth creating is worth **staging in the same commit** it validates.
- Tests must `assert` or `sys.exit(1)` on failure — stdout "FAIL" inspection is a workaround for tests
  not designed to run as subprocesses. Flag exit-code-only checks.

## What "green" does and does not prove
- **Green proves behavior-preservation of the sim.** It does **not** prove *feel*: sprite-sync timing,
  rendering, console noise, and input are only provable at the **live gate** (a human at the window).
  For any view/input/timing/output change, require the live gate as a distinct verification tier and
  budget for a follow-up polish commit. Do not call a view feature done at "gate green."
- **"Generated file exists" ≠ "renders/decodes correctly."** For any output artifact (PDF, QR, image),
  the definition of done is "opened/decoded in the target tool," not "process exited 0."
- **Config-verified ≠ topology-verified.** A dev-machine loopback smoke is not evidence a three-tier
  (server/client/hardware) path works on separate physical boxes.

## Closeout gate
- Every directory a change touched gets its README confirmed/updated in the closing commit.
- Migration applied if schema changed; deferred items recorded honestly.
- Faithful tests reuse the *real* pipeline (e.g. `SaveManager.snapshot()/restore()` round-trip through a
  temp DB) rather than replicating the serialized shape — a parallel serializer can drift and pass anyway.
