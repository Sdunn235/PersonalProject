# Acceptance test guide (QA)

How QA turns "what should happen" into tests that fail first. The owning doc for test kinds and commands
is `../../../docs/testing.md`; this guide is the department's working checklist.

## From a design note to red tests
1. **List acceptance examples.** One observable sentence each. Pull them from the design note's
   Implementation Acceptance section, the BACKLOG item, or the bible § it serves.
2. **Classify each one** (testing.md table) and pick the cheapest test that truly proves it:
   - "value X follows formula F": unit
   - "real entities reach a visible level over in-game time": integrated (real `entities.json` roster)
   - "NPCs *do* something differently": behavior A/B (same seed, feature on vs off, `harness.SEED`)
   - "the player can *see* it": render (`render_text` + a negative control)
   - "nothing breaks over days": soak invariant
   - "a refactor changed nothing": characterization against the current behavior
   - "it survives save/load": persistence via the real SaveManager
3. **Write the test**, run it, and confirm it fails *because the behavior is missing*. Paste the failing
   lines into the QA report.
4. **Hand off** to Engineering with the report. Engineering is done when these tests and the full gate
   are green.

## Harness cheatsheet (`scratchpad/harness/headless.py`)
```python
from harness.headless import new_kernel, headless_shell, step, render_text, save_frame, controller_of
ctx, kernel = new_kernel()             # seeded (SEED), temp DB, built like main.py
shell = headless_shell(ctx, kernel)    # real PresentationShell, off-screen, SpyFont
step(kernel, 120, shell)               # advance frames (keeps sprites + rewind ring in sync)
drawn = render_text(shell, subject="Gruk", inspect=True)   # every string the frame drew
save_frame(shell, "name")              # PNG evidence in logs/screens/latest/
```
In-game time: `settings.FRAMES_PER_DAY`; the controller runs every frame.

## Lessons this department carries
- **Fatigue v1 (2026-11-17):** 17 unit checks green, feature inert in play. The emitter and the decay were
  each right; together they cancelled. *Always add an integrated test with real authored data.*
- **Soak (2026-11-19):** the first soak run found IDLE↔MOVING thrashing every live look had missed.
  *Stated invariants beat "does anything look odd?"*
- **Determinism (2026-11-19):** two seeded kernels built before either ran shared the RNG and "failed"
  determinism. *Build and run each seeded world in turn.*
