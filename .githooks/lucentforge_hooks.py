"""Git hooks for the Personal Project repo (LucentForge/docs/testing.md "Hooks").

  pre-commit : every staged LucentForge .py file must compile (fast — seconds).
  pre-push   : if the pushed commits touch LucentForge/, the full headless gate must be green
               (scratchpad/run_all_tests.py) — the same check CI runs.

Install once per clone (from the repo root):   git config core.hooksPath .githooks
"""
from __future__ import annotations

import os
import py_compile
import subprocess
import sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                      text=True, check=True).stdout.strip()
LF = os.path.join(ROOT, "LucentForge")


def git_lines(*args: str) -> list[str]:
    out = subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT)
    return [line for line in out.stdout.splitlines() if line.strip()]


def pre_commit() -> int:
    staged = [f for f in git_lines("diff", "--cached", "--name-only", "--diff-filter=ACMR")
              if f.startswith("LucentForge/") and f.endswith(".py")]
    bad = []
    for rel in staged:
        try:
            py_compile.compile(os.path.join(ROOT, rel), doraise=True)
        except py_compile.PyCompileError as err:
            bad.append(f"{rel}: {err.msg}")
    if bad:
        print("pre-commit: these LucentForge files do not compile:\n  " + "\n  ".join(bad))
        return 1
    return 0


def pre_push(stdin_lines: list[str]) -> int:
    touched = False
    for line in stdin_lines:                       # "<local ref> <local sha> <remote ref> <remote sha>"
        parts = line.split()
        if len(parts) != 4 or set(parts[1]) == {"0"}:
            continue
        local_sha, remote_sha = parts[1], parts[3]
        rng = local_sha if set(remote_sha) == {"0"} else f"{remote_sha}..{local_sha}"
        if any(f.startswith("LucentForge/") for f in git_lines("diff", "--name-only", rng)):
            touched = True
    if not touched:
        return 0
    print("pre-push: LucentForge changed - running the headless gate (scratchpad/run_all_tests.py)")
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONUTF8="1")
    result = subprocess.run([sys.executable, os.path.join("scratchpad", "run_all_tests.py")],
                            cwd=LF, env=env)
    if result.returncode != 0:
        print("pre-push: gate is RED - push refused. Fix the failing suites (see output above).")
    return result.returncode


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "pre-commit":
        sys.exit(pre_commit())
    if mode == "pre-push":
        sys.exit(pre_push(sys.stdin.read().splitlines()))
    print("usage: lucentforge_hooks.py pre-commit|pre-push")
    sys.exit(2)
