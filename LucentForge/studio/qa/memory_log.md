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

## 2026-11-19 — Department founded (LF-174)
- Founded by the Director under Shawn's tonight owner exception. Inherits the suites written before it
  existed: `run_render_tests.py`, `run_soak_tests.py`, fatigue sections 6-9, affinity section E, studio
  structure. The soak suite's first run caught the IDLE-MOVING thrash (C0079).
