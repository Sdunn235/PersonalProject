# Code Review / QC — Memory Log

Append-only history of reviews and rulings. Newest at the top.

**Entry format:**
```
## YYYY-MM-DD — <artifact reviewed>
- **Stage × domain:** e.g. Design × Systems.
- **Verdict:** PASS / PASS WITH NOTES / BLOCK.
- **Top finding:** the single most important thing flagged (or "clean").
- **Ruling set:** any standard you asserted that future reviews should hold to.
- **Deliberately skipped:** the matrix cells you did not apply, and why.
```

A "ruling" is a precedent — e.g. "design notes must name tunable weights, not leave bare numbers."
Record rulings so QC stays consistent across invocations. Keep entries short — this is a review
ledger, not project state and not a lesson.

---

## 2026-11-17 — Ruling added after the fatigue live gate failed
- **Stage x domain:** Implementation x Systems Design (retro).
- **Finding QC missed:** the 2026-08-09 PASS WITH NOTES verified the sleep-side invariant (boost < sleep
  decay) but not the *accrual-side* one (gain > natural decay). Fatigue was inert for every real NPC.
- **Ruling:** for any emitter -> chemical change, Implementation-stage QC requires an **integrated test**:
  real authored entities, full emitter + `Chemicals.tick` path, many ticks, asserting the chemical
  actually moves to a visible level. Unit tests of each half are not sufficient. Check both invariants
  (accrual beats decay for the strongest entity; recovery beats boost while resting).

## 2026-08-09 — Rest/Fatigue Want IMPLEMENTATION (`Mechanics/` fatigue want)
- **Stage × domain:** Implementation × Systems Design.
- **Verdict:** PASS WITH NOTES.
- **Top finding:** (minor) `scratchpad/run_fatigue_tests.py` is **untracked** at review time, not staged with the change it validates — violates the test-gate protocol's "a test worth creating is worth staging in the same commit." It still runs (run_all_tests auto-discovers it: 23/23 green) and no commit exists yet, so this is a staging note for the Director's integration commit, not a blocker.
- **Verified:** All 3 gates green as run by QC — `run_all_tests.py` 23/23 (fatigue suite included), `run_affinity_behavior_tests.py` clean, `run_fatigue_tests.py` 15/15, all exit 0. Independently confirmed the tiredness special-case math: sleep-decay `_DECAY*5=0.001` > worst-case combined boost `fatigue*FATIGUE_SLEEP_BOOST(0.0003)+strain*AFFINITY_STRAIN_NEED_BOOST(0.0002)=0.0005`, so a sleeping fatigued NPC nets tiredness DOWN; test asserts this both as a live tick and as the standalone tuning invariant (not a replicated shape). All 5 Implementation Acceptance items met (parity, special-case test, legibility in all 4 surfaces, save round-trip via real SaveManager, live gate deferred to Shawn). `EXERTING_STATES` matches locked Director Q1 set exactly; boost targets ONLY `tiredness`; endurance is a live-recomputed polymorphic derivation strategy; bit/byte firewall untouched; boost is additive per Q4.
- **Ruling set:** (1) A scratchpad acceptance suite is part of the change under review — QC flags it as a finding if it is unstaged/untracked at review time, even when run_all_tests auto-discovers it, because the integration commit must carry it. (2) When a design note names an approximate insertion point ("step 2b"), the implementation landing it at the correct adjacent point ("step 2c", after the affinity emitter) is NOT a deviation — QC checks behavior/ordering correctness, not comment-literal fidelity to the note's prose.
- **Deliberately skipped:** The **live gate** (Acceptance item 5) — a human driving an NPC hard at the window to confirm it beds down sooner and fatigue is visible/decays on sleep. That is Shawn's tier per the test-gate protocol (green proves sim behavior, not feel); QC does not run it. Did not re-open any locked design decision (Q1–Q5) — none were revealed infeasible by the code. Did not apply Refactor/Closeout cells (this is a feature implementation, not a behavior-preserving move or a doc/migration closeout — though I note READMEs for every touched dir were in fact updated, which is ahead of schedule).

## 2026-08-04 — Rest/Fatigue Want design note (`systems_design/drafts/2026-08-04_rest_fatigue_want.md`)
- **Stage × domain:** Design × Systems Design.
- **Verdict:** PASS WITH NOTES.
- **Top finding:** (major) The note asserts the fatigue→`tiredness` boost sits "right beside" the strain boost, but `tiredness` is NOT computed generically in `chemical.py` — it has a dedicated sleep branch (lines 41-47) that hard-decays it `_DECAY*5` while sleeping. A boost applied every tick can partially fight that sleep-time decay while an NPC is at a bed but still in an EXERTING locus classification, unless the emitter has already driven fatigue to ~0 by then. Parity at fatigue=0 still holds; but the "same shape as strain" claim understates that tiredness is a special case. Implementer must trace the sleep-branch/boost ordering, not copy the strain block blindly.
- **Ruling set:** (1) A design note that says it mirrors an existing mechanism must name any special-casing in the target code path it rides — "same shape as X" is a claim QC verifies against the real branch, not a pass. (2) Design notes may cite a settings block as the home for new constants without listing values (formulas-not-numbers is satisfied by naming tunables); QC does not demand numeric values at design stage.
- **Deliberately skipped:** All Implementation/Refactor/Closeout cells — SOLID/GRASP checklist, `run_all_tests.py` gate, mock-parity, coverage, README/migration closeout. No code exists yet; per the charter's stage axis these are out of scope for a design note.
