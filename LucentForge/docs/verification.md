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

## 2026-11-19 night — Upper-reach genomes (C0100, LF-184)
- Owner go: Shawn, "Start LF-184, grow the upper reach genomes."
- Test-first: the art suite went red for the right reasons (the three genomes missing; `load_all` accepted
  an orphan parent), then green.
- **My own test bug, found by its control:** the first lean check compared each oak's centroid with the
  tile centre. The upright control failed: an oak with no lean sits at x 14.98, because a seed's canopy
  lobes aren't symmetric. That check was measuring the seed, not the lean. It now compares each oak with
  its upright twin (same seed, lean 0): west +2.14 px, east +1.94 px toward the water. The negative control
  (the west oak leaned away) gives −2.19 px and fails the check.
- Local gate: 32/32 GREEN. Hosted CI: see the run on C0100.
- Evidence: `logs/screens/latest/art_upper_reach.png` (each parent beside its child, plus a riverbank
  strip), looked at by eye. The canopies lean visibly but subtly. The stone is larger and more angular.
- Gaps: only the canopy leans (the trunk stays upright; the renderer has no trunk tilt). Same-bank oaks
  are clones until runtime mutation exists (LF-179). The ground colour in the evidence image is a stand-in,
  not the game's tile, so value contrast against real ground is untested (LF-180). Not wired in (LF-178).

## 2026-11-19 evening — The world opens upriver (C0095, LF-010 step 2)
- Owner decision: Shawn, "The river flows north to south, open upriver first" (LF-182).
- Test-first: `run_panel_transition_tests.py` red for the right reason (Panel(0,-1) undefined), then the
  data made the edge contract pass, then 12 behavior checks red (no transition engine) → green.
- Test fixes made before the build, recorded here: (1) the "villagers drawn" probe read drawn text,
  but name labels use another font, so it passed vacuously upriver and failed its home control; replaced
  by recording which sprites the shell draws. (2) "Arrives on the edge" measured after 20 frames of
  walking on; the walk now stops on the crossing frame. (3) Home-map comparisons used a fresh map
  without chest tiles; regions identify the panel instead. (4) After loading, the test still held the
  last "walk south" intent and walked home; it now clears the intent (the live shell sets it from keys
  every frame).
- Characterization updates: `smoke_phase32.py`, `smoke_phase36.py`, `run_runtime_tests.py` (and
  `run_stage3_tests.py`, which runs them) pinned "all edges null". Each check now pins the new truth with
  the same strictness; the closed-edge message moved to the SOUTH edge and a NORTH entry must now log
  nothing.
- Local gate: 32/32 GREEN. Hosted CI: see the run on C0095.
- Evidence: `logs/screens/latest/20_upper_reach.png` (the player alone upriver),
  `21_back_home.png`. Panel(0,0)'s NPCs moved and their needs changed over 600 frames with the player away.
- Gaps: no live look yet. Upriver has no residents and only the riverbank's water as a need source.
  Off-screen panels run at full fidelity (fine at 2 panels; §R6 reduced scope comes with more).

## 2026-11-19 evening — Grom regrown as a human; skin_marks gene (C0092)
- Test-first: species-agreement check added to `run_art_tests.py`; red (`grom: species matches the
  game's grom (human)`, genome said ''), then green.
- Local gate: see the pre-push run on C0092. Hosted CI on C0091: green.
- Evidence: `logs/screens/latest/art_contact_sheet.png`. A first regrowth with dark cloth (70, 72, 84)
  passed every test but its legs vanished against the dark background (value too close). Fixed by
  lifting the cloth's value. Not covered by a test yet (see the Gaps line).
- Gaps: no test checks value contrast (readability); "species" is read from sprite filename prefixes,
  because entities.json has no species field.

## 2026-11-19 evening — Lucent Light house style (C0091)
- Test-first: `run_art_style_tests.py` written first; red on import (no style module), then green.
- Local gate: 31/31 GREEN (`run_all_tests.py`), including the re-baked `assets/generated/` matching fresh
  renders in `run_art_tests.py`.
- Hosted CI: see the run on C0091.
- Live look: none (generated art is not wired into the game).
- Evidence: `logs/screens/latest/art_style_sheet.png` (row block 1: the same genomes with no light;
  block 2: Lucent Light; last row: five generations of Gobby's lineage, then Gobby growing up). Negative
  control: with `light_from` (0, 0) the one-light check fails, so the check discriminates.
- Gaps: "looks good" is not tested; the checks pin coherence (one light, grown ramps), not taste. The
  style is a proposal from the Art department; Shawn decides whether it is the direction.

## 2026-11-19 ~01:35 — Panels as data (C0089, LF-010 step 1)
- Local: `run_panel_data_tests.py` red first (no map file), then CLEAN: data Panel(0,0) == procedural in
  tiles, blocking, regions, rock/tree art, need sources and rendered pixels; runtime never calls the
  procedural builder. Full gate via the pre-push hook.
- Gaps: no second panel and no transitions yet (that needs world/lore decisions).

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
