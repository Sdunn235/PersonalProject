"""run_stage3_tests.py — Stage 3 consolidated smoke suite runner.

Runs all six Stage 3 phase smoke tests as subprocesses, reports pass/fail per
module, and exits nonzero if any fail.

Usage (from LucentForge root):
    py scratchpad/run_stage3_tests.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# All Stage 3 smoke tests need pygame env vars (they import Mechanics modules)
TESTS = [
    ("Phase 3.1 — room data layer",            "scratchpad/smoke_phase31.py"),
    ("Phase 3.2 — world coord + migration",    "scratchpad/smoke_phase32.py"),
    ("Phase 3.3 — zone crossing Observer",     "scratchpad/smoke_phase33.py"),
    ("Phase 3.4 — O-panel ZONE + HUD flash",  "scratchpad/smoke_phase34.py"),
    ("Phase 3.5 — ZoneAIResponder",            "scratchpad/smoke_phase35.py"),
    ("Phase 3.6 — PanelLoader + edge detect", "scratchpad/smoke_phase36.py"),
]


def run_test(relpath):
    env = os.environ.copy()
    env.setdefault("SDL_VIDEODRIVER", "dummy")
    env.setdefault("SDL_AUDIODRIVER", "dummy")
    result = subprocess.run(
        [sys.executable, relpath],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )
    # All Stage 3 smoke tests call sys.exit(1) on failure — returncode is sufficient.
    # (Don't scan stdout for "FAIL": summary lines say "0 FAIL" even on clean runs.)
    failed = result.returncode != 0
    return not failed, result.stdout, result.stderr


def main():
    print("=" * 64)
    print("Stage 3 — Rooms as Zones / Multi-Panel World")
    print("Consolidated Smoke Suite")
    print("=" * 64)

    results = []
    for label, relpath in TESTS:
        ok, stdout, stderr = run_test(relpath)
        results.append(ok)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
        if not ok:
            combined = (stdout + stderr).strip()
            for line in combined.splitlines()[-20:]:
                print(f"       {line}")
        else:
            lines = stdout.strip().splitlines()
            # Print the PASS count line from each module
            for line in lines:
                if "PASS" in line and "|" in line:
                    print(f"       {line.strip()}")
                    break

    total = len(TESTS)
    passed = sum(results)
    print("=" * 64)
    print(f"{passed}/{total} modules passed.")
    if passed == total:
        print("Stage 3 smoke CLEAN")
    print("=" * 64)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
