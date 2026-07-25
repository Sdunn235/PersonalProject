"""run_all_tests.py — Master test runner (Stage 4.6R / R0 golden-master gate).

Discovers and runs EVERY scratchpad/*.py suite (excluding itself), headless,
each as its own subprocess. A suite is RED if it exits nonzero OR prints "FAIL"
on stdout/stderr (some legacy scripts print PASS/FAIL without a nonzero exit —
see Stage 2 closeout lesson: exit codes are not sufficient for print-only tests).

This is the safety net for the Stage 4.6R runtime refactor: run it GREEN before
and after every stage (R0–R6) to prove behavior was preserved.

Usage (Windows PowerShell):
    $env:SDL_VIDEODRIVER='dummy'; py scratchpad/run_all_tests.py

Exit code: 0 if every suite is GREEN, 1 otherwise.
"""
import os
import re
import sys
import glob
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_SELF = os.path.basename(__file__)

# Headless SDL for every child process.
_ENV = dict(os.environ)
_ENV.setdefault("SDL_VIDEODRIVER", "dummy")
_ENV.setdefault("SDL_AUDIODRIVER", "dummy")

_PER_SUITE_TIMEOUT = 600  # seconds — generous; most suites finish in <30s.

# Nonzero fail-count in a summary line, e.g. "3 FAIL", "2 FAILED".
_NONZERO_COUNT_RE = re.compile(r"[1-9]\d*\s+FAIL", re.IGNORECASE)
# Any fail-count summary (incl. "0 FAIL", "0 FAIL:") — used to SKIP benign lines.
_COUNT_LINE_RE = re.compile(r"\b\d+\s+FAIL", re.IGNORECASE)
# A bare FAIL marker (per-check line, "PARITY FAILED", "FAIL:", "FAIL —").
_MARKER_RE = re.compile(r"\bFAIL(ED|URE)?\b", re.IGNORECASE)


def _discover():
    """All scratchpad/*.py except this runner, sorted for stable output."""
    files = sorted(glob.glob(os.path.join(_HERE, "*.py")))
    return [f for f in files if os.path.basename(f) != _SELF]


def _classify_output(out):
    """Return a failure reason string if output signals a real failure, else None.

    Distinguishes benign count summaries ('13 PASS | 0 FAIL', '0 FAIL:') from
    real failures (nonzero counts, per-check FAIL markers, tracebacks). Some
    suites print PASS/FAIL without a nonzero exit (Stage 2 closeout lesson), so
    stdout must be inspected, not just the exit code.
    """
    if _NONZERO_COUNT_RE.search(out):
        return "nonzero FAIL count"
    if "Traceback (most recent call last)" in out:
        return "traceback"
    for line in out.splitlines():
        if _COUNT_LINE_RE.search(line):
            continue  # benign summary line like "... | 0 FAIL" or "0 FAIL:"
        if _MARKER_RE.search(line):
            return "FAIL marker: " + line.strip()[:60]
    return None


def _run_suite(path):
    """Run one suite. Return (ok: bool, reason: str, tail: str)."""
    try:
        proc = subprocess.run(
            [sys.executable, path],
            cwd=_ROOT,
            env=_ENV,
            capture_output=True,
            text=True,
            timeout=_PER_SUITE_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT (>{_PER_SUITE_TIMEOUT}s)", ""

    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return False, f"exit={proc.returncode}", _tail(out)
    reason = _classify_output(out)
    if reason:
        return False, reason, _tail(out)
    return True, "ok", ""


def _tail(text, n=12):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines[-n:])


def main():
    suites = _discover()
    print("=" * 70)
    print(f"run_all_tests — {len(suites)} suites discovered in scratchpad/")
    print("=" * 70)

    results = []
    for path in suites:
        name = os.path.basename(path)
        ok, reason, tail = _run_suite(path)
        results.append((name, ok, reason, tail))
        status = "GREEN" if ok else "RED  "
        print(f"[{status}] {name:<38} {reason}")

    reds = [r for r in results if not r[1]]
    print("=" * 70)
    for name, ok, reason, tail in reds:
        print(f"\n--- RED: {name} ({reason}) ---")
        if tail:
            print(tail)
    print("=" * 70)
    green = len(results) - len(reds)
    print(f"SUMMARY: {green}/{len(results)} GREEN, {len(reds)} RED")
    print("=" * 70)
    return 1 if reds else 0


if __name__ == "__main__":
    sys.exit(main())
