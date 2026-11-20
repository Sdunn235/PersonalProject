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

## 2026-11-19 — Direction written (no design note this run)
- Next design candidates named in `direction.md`: LF-043 (decisions follow the strongest drive), the
  shared gene contract with Art (one biology or two, LF-179), LF-044.
- Waiting on: Story/Lore's character seeds for the river clan (in `story_lore/drafts/2026-11-19_beyond_panel_0_0.md`),
  once Shawn decides canon.

## 2026-08-04 — Rest / Fatigue want
- **Intent:** activity-driven fatigue that makes the *existing* time-based sleep loop fire sooner for NPCs who've been exerting themselves.
- **Shape:** new `fatigue` chemical + `ExertionEmitter` reading AI-state as locus (exerting states raise it, restful states/sleep discharge it); it boosts the existing `tiredness` chemical so the existing Sleep Drive perceives higher urgency. No new need/source/state/bed. Mirrors the `affinity_strain` pattern exactly.
- **Formula core:** `effective_gain = FATIGUE_BASE_GAIN / endurance(attrs)` where `endurance = constitution×ENDURANCE_CON_WEIGHT + physique×ENDURANCE_PHY_WEIGHT` (polymorphic, registered beside bit/byte capacity, recomputed from current attributes); receptor boost `tiredness += fatigue × FATIGUE_SLEEP_BOOST` when `fatigue > FATIGUE_ACTIVE_FLOOR`. All weights named in settings.py.
- **Slots into:** `biochem/chemical.py` (register + decay + boost block), `biochem/emitter.py` (new `ExertionEmitter` via existing `_approach`), `entities/derivation.py` (`endurance` formula), `ai/controller.py` (instantiate + emit in step 2b, EXERTING_STATES set, observability), `settings.py` (named constants). No change to needs/, drive.py, brain.py, states/, or JSON data. Additive; parity at fatigue=0; rides generic chemicals save blob (no migration).
- **QC verdict:** PASS WITH NOTES — top flag: `tiredness` is special-cased in `chemical.py` (dedicated sleep-decay branch), so "same shape as strain" understates it; implementer must trace that branch. Constitution-coupling + double-count on `tiredness` noted; QC added a 5th open item (verify observation-panel/`npcs.csv` legibility slots).
- **Status:** design LOCKED (2026-08-09) — all open Qs resolved by Director; ready for Implementation stage. Draft carries the Director Reconciliation + Director Decisions.
- **Decisions (2026-08-09):** Q1 eating≠exertion (`EXERTING={MOVING,RAIDING,RELOCATING,PATROLLING}`, sleep-source=restful) · Q2 Constitution(primary)+Physique, no new attribute, seam swappable · Q3 **defer SP-drain** to its own arc, v1 = perceived-urgency only · Q4 **additive** on `tiredness` (tune `FATIGUE_SLEEP_BOOST` conservatively) · Q5 legibility verified — 4 slots beside `affinity_strain` (run_logger/hud/inspector/observation_panel).
- **Open question left:** none — see Implementation acceptance (5 items incl. the `tiredness`-special-case test + parity + live gate).
- **Outcome (2026-11-18):** shipped as v1.1 (C0073) after a failed first live gate. Two design misses to remember: (1) the note gave rates without saying they're **per frame**, and never checked gain vs the natural decay that runs every frame; (2) it assumed `Drive.compute_urgency()` drives decisions — it doesn't; decisions read need zones. Future want designs must name the **receptor** that turns their chemical into a perceived-need pull, and check the gain-beats-leak invariant for the hardiest entity.
