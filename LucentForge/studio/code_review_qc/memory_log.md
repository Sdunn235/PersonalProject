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

## 2026-08-04 — Rest/Fatigue Want design note (`systems_design/drafts/2026-08-04_rest_fatigue_want.md`)
- **Stage × domain:** Design × Systems Design.
- **Verdict:** PASS WITH NOTES.
- **Top finding:** (major) The note asserts the fatigue→`tiredness` boost sits "right beside" the strain boost, but `tiredness` is NOT computed generically in `chemical.py` — it has a dedicated sleep branch (lines 41-47) that hard-decays it `_DECAY*5` while sleeping. A boost applied every tick can partially fight that sleep-time decay while an NPC is at a bed but still in an EXERTING locus classification, unless the emitter has already driven fatigue to ~0 by then. Parity at fatigue=0 still holds; but the "same shape as strain" claim understates that tiredness is a special case. Implementer must trace the sleep-branch/boost ordering, not copy the strain block blindly.
- **Ruling set:** (1) A design note that says it mirrors an existing mechanism must name any special-casing in the target code path it rides — "same shape as X" is a claim QC verifies against the real branch, not a pass. (2) Design notes may cite a settings block as the home for new constants without listing values (formulas-not-numbers is satisfied by naming tunables); QC does not demand numeric values at design stage.
- **Deliberately skipped:** All Implementation/Refactor/Closeout cells — SOLID/GRASP checklist, `run_all_tests.py` gate, mock-parity, coverage, README/migration closeout. No code exists yet; per the charter's stage axis these are out of scope for a design note.
