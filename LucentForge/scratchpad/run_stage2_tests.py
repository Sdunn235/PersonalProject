"""run_stage2_tests.py — Stage 2 consolidated smoke suite runner.

Runs all four Stage 2 test modules as subprocesses, reports pass/fail per module,
and exits nonzero if any fail.

Usage (from LucentForge root):
    py scratchpad/run_stage2_tests.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (label, relative_path, needs_pygame_env)
TESTS = [
    ("test_combat_parity",   "scratchpad/test_combat_parity.py",   False),
    ("test_outcome_resolver","scratchpad/test_outcome_resolver.py", False),
    ("test_chest_flows",     "scratchpad/test_chest_flows.py",      False),
    ("test_chest_bfs",       "scratchpad/test_chest_bfs.py",        True),
]


def run_test(relpath, needs_pygame_env):
    env = os.environ.copy()
    if needs_pygame_env:
        env.setdefault("SDL_VIDEODRIVER", "dummy")
        env.setdefault("SDL_AUDIODRIVER", "dummy")
    result = subprocess.run(
        [sys.executable, relpath],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )
    failed = result.returncode != 0 or "FAIL" in result.stdout
    return not failed, result.stdout, result.stderr


def main():
    print("=" * 60)
    print("Stage 2 — Consolidated Smoke Suite")
    print("=" * 60)
    passed = 0
    for label, relpath, needs_pygame in TESTS:
        ok, stdout, stderr = run_test(relpath, needs_pygame)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
        if not ok:
            combined = (stdout + stderr).strip()
            for line in combined.splitlines()[-15:]:
                print(f"       {line}")
        else:
            last = stdout.strip().splitlines()
            if last:
                print(f"       {last[-1]}")
        passed += int(ok)

    total = len(TESTS)
    print("=" * 60)
    print(f"{passed}/{total} modules passed.")
    print("=" * 60)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
