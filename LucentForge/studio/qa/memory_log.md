# QA / Test — Memory Log

Append-only history of the tests this department wrote and what they caught. Newest at the top.

**Entry format:**
```
## YYYY-MM-DD — <feature / item> (from <design note or BACKLOG id>)
- **Acceptance examples:** the observable sentences tested.
- **Tests:** files + kinds (unit / integrated / A-B / render / soak / ...).
- **Red run:** what failed first and why that proves the behavior was missing.
- **Caught:** anything the tests found beyond the feature (bugs, gaps).
- **Not established:** what these tests deliberately do not prove.
```

---

## 2026-11-19 — Kernel runs with no display; player moves by intent (BACKLOG LF-046)
- **Acceptance examples:** (1) a fresh process that never initializes pygame builds a game and steps the
  kernel; (2) intent (1,0) moves the player right, (0,0) leaves them still: the sim never reads keys;
  (3) `Mechanics/ai/player.py` imports no pygame.
- **Tests:** `scratchpad/run_kernel_headless_tests.py`, which runs the scenario in a subprocess so no
  earlier `pygame.init()` can mask a dependency.
- **Red run:** `pygame.error: video system not initialized` from `PlayerController.update`, and player.py
  imports pygame. Both prove the dependency is real, not a fixture problem.
- **Not established:** that the arrow keys still feel the same in the window (shell-side; covered only by
  code review of `_apply_player_intent`).

## 2026-11-19 — Department founded (LF-174)
- Founded by the Director under Shawn's tonight owner exception. Inherits the suites written before it
  existed: `run_render_tests.py`, `run_soak_tests.py`, fatigue sections 6-9, affinity section E, studio
  structure. The soak suite's first run caught the IDLE-MOVING thrash (C0079).
