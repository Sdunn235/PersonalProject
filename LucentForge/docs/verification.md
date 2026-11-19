# Verification log

Chronological evidence: what was actually run, on which revision, with what result. Newest at the top.
An entry describes its own date and revision, not the current state. Later entries supersede earlier
ones; never rewrite an old result. Keep **local runs**, **hosted CI**, and **Shawn's live looks**
separate. Kinds of tests: [testing](testing.md). Who may merge on this evidence: [autonomy](autonomy.md).

Entry template:
```
## YYYY-MM-DD — <change> (<commit(s)>)
- Local gate: <N/N GREEN> (`run_all_tests.py`), plus focused suites run.
- Hosted CI: <run link + result, or "not run">.
- Live look (optional): <what Shawn saw, or "none">.
- Evidence: <screenshots / A-B numbers / soak stats>.
- Gaps: <what these checks do NOT establish>.
```

---

## 2026-11-19 — Autonomy foundation: render + soak suites, queueing fix (C0079)
- Local gate: **25/25 GREEN** on C0079 (Windows, Python 3.14.6, pygame-ce 2.5.7). Red first:
  `run_soak_tests.py` failed 2 thrash checks before the fix.
- Hosted CI: not yet. The workflow arrives with the policy PR (C0080).
- Live look: none (this change exists to replace them).
- Evidence: soak (3 in-game days, seed 1234) worst state changes per minute fell from Ignarix 900 /
  Alder 444 to 12 / 13 (limit 60); no out-of-range chemicals or needs; no deaths; every NPC ate,
  drank and slept at least once a day; no frozen movers; same seed replayed identically. Render: 12/12,
  screenshots `01_fatigue_hud_panel`, `02_inspector_elara_fatigued`, `03_inspector_gruk_after_rewind`
  in `logs/screens/latest/`.
- Gaps: modal screens (combat, inventory, pause, chest) are not render-tested. The kernel still needs
  a pygame display (BACKLOG LF-046). Feel/pacing is not assessed.

## 2026-11-19 — Strain receptor + fatigue/strain as formulas (C0077–C0078)
- Local gate: 23/23 GREEN on C0078. Fatigue suite (with §9 authored targets) and affinity §E (21) clean.
- Hosted CI: none existed.
- Live look: Shawn, brief run (~1 game minute in the run-log): "Things look fine." Run-log: Gruk
  fatigue 0.47, Skrix 0.36, Elara strain starting (0.02).
- Evidence: same-seed A/B: Elara first sleep frame 12,454 vs 13,131 without strain; Alder 12,042 vs
  12,187. Authored targets reproduce exactly (fatigue ½ day to 0.5, plateau 0.667; strain half-time
  0.125 day, settles at T − 0.05).
- Gaps: the live look was too short to observe strain behavior directly; the A/B carries that claim.

## 2026-11-18 — Fatigue want v1.1 (C0072–C0073)
- Local gate: 23/23 GREEN. Fatigue suite 38/38.
- Hosted CI: none existed.
- Live look: Shawn, all six checks yes. Run-log: Gruk peak fatigue 0.71, Skrix 0.62, both falling
  while asleep.
- Evidence: same-seed A/B: Gruk first sleep frame 8,108 vs 12,087 without the receptor.

## 2026-11-17 — Fatigue want v1 live gate FAILED (built 2026-08-09, C0070)
- Local gate: 23/23 GREEN (the unit tests passed).
- Live look: Shawn: fatigue never rose. Run-log: 0.0000 for all 7 NPCs over 238 rows.
- Lesson: the tests checked the emitter and the decay separately; no test ran real NPCs through
  both. This is why integrated, A/B, render and soak tests exist now.
