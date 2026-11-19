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

## 2026-11-19 ~01:30 — Modal render tests + §A2 carry-load fix (C0088)
- Local: `run_modal_render_tests.py` CLEAN (pause, inventory, chest, load x2, save, combat; 6 screenshots).
  Red first on the load check (inventory screen 24.0 vs service 4.0 → `take_from` ignored worn gear).
  Full gate via the pre-push hook.
- Gaps: navigation *inside* menus (equip/unequip, lockpick outcomes, spell submenus) isn't scripted yet;
  combat is only opened and closed, not fought.

## 2026-11-19 ~01:20 — LF-046 via QA→Engineering (C0086)
- Local: `run_kernel_headless_tests.py` red first (video system not initialized), then 5/5. Full gate via
  the pre-push hook (see the commit).
- Gaps: arrow-key feel in the window isn't automated (shell-side, small change, code-reviewed).

## 2026-11-19 01:05–01:20 — Owner exception + QA/Art departments + art genome (C0083–C0085)
- **Owner approval:** Shawn (in session, ~01:00): "merged, start on the QA and Art departments… full
  permissions to do what you need to build Lucent Forge and its studio and games", then explicitly:
  merge PR #1 for him; **owner exception for tonight** (charters, agent definitions, Studio README merge on a
  green gate; bible doctrine/canon and docs/autonomy.md still PR); run until 04:00 or session 100%.
  PR #1 merged as C0083 under that approval.
- Local gate: 26/26 GREEN via the pre-push hook on C0084 (the first hook-enforced push). Studio suite red
  first (missing qa/art). Art suite red first (no `Mechanics.art`), then CLEAN on the first build.
- Hosted CI: runs on every master push now (workflow merged).
- Evidence: `logs/screens/latest/art_contact_sheet.png` (Gobby, Grom walk sheets; oak; stone). Gobby renders
  22 px wide vs Grom's 29; growth heights rise with stage (Gobby 12→15→19 px).
- Gaps: generated art is not wired into the game (Shawn's choice, LF-178); art quality and look are
  Shawn's call, which the tests can't judge; the existing ten sheets' sources are unknown (registry flags them).

## 2026-11-19 — First hosted CI run (PR #1 head 28ecccd = C0079–C0081 + C0080 policy)
- Local gate: 25/25 GREEN (Windows, Python 3.14.6, pygame-ce 2.5.7).
- Hosted CI: **25/25 GREEN** on ubuntu-latest, Python 3.14, pygame-ce **2.5.8** (installed from wheels;
  no source build), `verify` green, 54 s end to end.
  https://github.com/Sdunn235/PersonalProject/actions/runs/44475158441
- Evidence: `lucentforge-screens` artifact (309 KB, 3 frames) uploaded from Linux.
- Gaps: CI on `master` pushes starts only once PR #1 merges (the workflow lives on that branch).
  Local 2.5.7 vs CI 2.5.8: same suites green on both.

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
