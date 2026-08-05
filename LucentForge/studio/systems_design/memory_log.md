# Systems Design — Memory Log

Append-only working history of mechanics this department has designed. Newest entries at the top.

**Entry format:**
```
## YYYY-MM-DD — <mechanic name>
- **Intent:** one line.
- **Shape:** the core of the design in 1–3 lines.
- **Formula core:** the derivation, named inputs (not numbers).
- **Slots into:** files/classes extended.
- **QC verdict:** pass / pass-with-notes / block — + the one thing they flagged.
- **Status:** design accepted / revised / superseded / implemented (C####).
- **Open question left:** the honest unknown, if any.
```

Keep entries short — this is a craft ledger, not project state (that lives in Caelum
`active_context.md`) and not a lesson (that lives in `reflection_log.md`).

---

## 2026-08-04 — Rest / Fatigue want
- **Intent:** activity-driven fatigue that makes the *existing* time-based sleep loop fire sooner for NPCs who've been exerting themselves.
- **Shape:** new `fatigue` chemical + `ExertionEmitter` reading AI-state as locus (exerting states raise it, restful states/sleep discharge it); it boosts the existing `tiredness` chemical so the existing Sleep Drive perceives higher urgency. No new need/source/state/bed. Mirrors the `affinity_strain` pattern exactly.
- **Formula core:** `effective_gain = FATIGUE_BASE_GAIN / endurance(attrs)` where `endurance = constitution×ENDURANCE_CON_WEIGHT + physique×ENDURANCE_PHY_WEIGHT` (polymorphic, registered beside bit/byte capacity, recomputed from current attributes); receptor boost `tiredness += fatigue × FATIGUE_SLEEP_BOOST` when `fatigue > FATIGUE_ACTIVE_FLOOR`. All weights named in settings.py.
- **Slots into:** `biochem/chemical.py` (register + decay + boost block), `biochem/emitter.py` (new `ExertionEmitter` via existing `_approach`), `entities/derivation.py` (`endurance` formula), `ai/controller.py` (instantiate + emit in step 2b, EXERTING_STATES set, observability), `settings.py` (named constants). No change to needs/, drive.py, brain.py, states/, or JSON data. Additive; parity at fatigue=0; rides generic chemicals save blob (no migration).
- **QC verdict:** PASS WITH NOTES — top flag: `tiredness` is special-cased in `chemical.py` (dedicated sleep-decay branch), so "same shape as strain" understates it; implementer must trace that branch. Constitution-coupling + double-count on `tiredness` noted; QC added a 5th open item (verify observation-panel/`npcs.csv` legibility slots).
- **Status:** design ACCEPTED by Director (PASS WITH NOTES) — implementation deferred to a future arc, gated on Shawn answering open Q1–Q5. Draft carries the Director Reconciliation.
- **Open question left:** Q1 SATISFYING locus split · Q2 endurance attribute basis · Q3 SP-drain now vs own arc · Q4 fatigue+strain additive vs max on `tiredness` · Q5 (QC) confirm legibility attach points.
