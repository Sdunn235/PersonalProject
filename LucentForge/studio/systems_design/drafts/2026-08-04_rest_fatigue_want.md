# Design Note — Rest/Fatigue Want (v1, REVIEWED — PASS WITH NOTES; implementation gated on Shawn's open-question decisions)

> **Status:** Design accepted by the Director on 2026-08-04 after QC review (PASS WITH NOTES). This is
> an *accepted design*, not yet canon and not yet implemented — see the Director Reconciliation section
> at the bottom. It stays in `studio/systems_design/drafts/` until Shawn answers the open questions and
> it is implemented; only then does a distilled version graduate to `design/` or a bible addendum.

## 1. Problem / intent

The existing `sleep` need decays purely on a clock (`decay_per_day: 90.0` in `needs.json`) — an NPC gets sleepy at the same rate whether it spent the day pacing the map or standing still in a bed. That misses a core piece of lived biology: **effort tires you out.** This want introduces *activity-driven fatigue* — a slow-building chemical that rises while an NPC is exerting itself (moving, satisfying, raiding) and relaxes while it rests, and which elevates the perceived urgency of the existing sleep drive. It is the exertion half of tiredness the clock cannot express. Critically, it is **not a new need with its own bed** — it is a modifier that makes the *existing* sleep loop fire sooner for NPCs who have been working hard. This is exactly the `affinity_strain` pattern (§B7 / §W6) applied to a new locus: activity instead of hostile-affinity exposure.

## 2. Proposed mechanic

Add one chemical, `fatigue`, and one emitter, `ExertionEmitter`, to the biochem substrate. Each tick the emitter reads the controller's current AI state as the *locus* (§B2 emitter definition — a body-state that emits a chemical): active-exertion states (`MOVING`, `RAIDING`, `RELOCATING`, `PATROLLING`, and `SATISFYING` for effortful sources) push `fatigue` upward toward a target; restful states (`IDLE`, and `SATISFYING` at a `sleep` source) let it approach zero. Accrual is gain-controlled and scaled by the entity's attributes so a hardy NPC tires slower than a frail one — recomputed from *current* attributes every tick, never frozen.

`fatigue` is then consumed exactly like `affinity_strain`: in `Chemicals.tick()`, when `fatigue > FATIGUE_ACTIVE_FLOOR`, it adds a boost to the **`tiredness`** chemical (the sleep need's chemical, per `needs.json`). The existing `Sleep Drive` receptor (`Drive.compute_urgency`) reads the slightly-elevated `tiredness` and produces higher urgency — so a worked NPC crosses into the sleep WARNING/CRITICAL zone sooner and routes to a bed through the *unchanged* IdleState → select_source → SatisfyingState path. Resting at a bed both fills the `sleep` need (existing behavior) and, because the NPC is now in a restful locus, lets `fatigue` decay — so sleep discharges fatigue as a natural consequence, no special discharge code.

No new need, no new source type, no new state, no new bed. Fatigue is a pressure that bends the existing sleep loop.

## 3. Formula(s)

All weights below are **named tunable constants** (to live in `settings.py` beside the `AFFINITY_STRAIN_*` block), never inline numbers. Attribute inputs read *current* `Attributes` each tick via the existing derivation seam (`derivation.py` strategy pattern), so growth/ascension recompute them.

**(a) Per-tick exertion target.** The emitter approaches `fatigue` toward a target set by whether the current locus is exerting:

```
exertion_target = EXERTION_TARGET_MAX   if state ∈ EXERTING_STATES
                = 0.0                   otherwise

fatigue ← fatigue + (exertion_target − fatigue) × effective_gain
```

**(b) Accrual gain — attribute-derived (formula, not coefficient).** Endurance resists fatigue. Physique (raw strength) and Constitution (durability) are the natural attribute basis; express as a **polymorphic endurance formula** registered alongside `bit_capacity`/`byte_capacity` in `derivation.py`, so per-race variants can be swapped without touching the emitter:

```
endurance(attrs)     = attrs.constitution × ENDURANCE_CON_WEIGHT
                       + attrs.physique × ENDURANCE_PHY_WEIGHT      # ≥ 1, clamped

effective_gain       = FATIGUE_BASE_GAIN / endurance(attrs)
```

Higher Constitution/Physique → larger `endurance` → smaller `effective_gain` → slower accrual. Recomputed each tick from live attributes (never spawn-frozen), satisfying the derivation rule. `FATIGUE_BASE_GAIN` should sit on the slow end (strain-like, ~`AFFINITY_STRAIN_GAIN` order of magnitude) so fatigue is a background tide, not a spike.

**(c) Decay while resting.** Natural decay in `Chemicals.tick()` (register `fatigue` in its decay list) at `_DECAY × FATIGUE_DECAY_MULT`, plus the emitter's own approach-to-zero when at rest. Recovery should out-rate accrual so a full night's sleep clears an honest day's work — `FATIGUE_DECAY_MULT` tuned to that.

**(d) Receptor boost — perceived sleep urgency.** Mirror the §B7 strain boost, but targeted only at the sleep chemical (fatigue is specifically about rest, not a general survival multiplier):

```
if fatigue > FATIGUE_ACTIVE_FLOOR:
    tiredness ← min(1.0, tiredness + fatigue × FATIGUE_SLEEP_BOOST)
```

The Sleep Drive's `compute_urgency` reads the boosted `tiredness` unchanged — no new urgency math. **Parity invariant:** `fatigue = 0` (or all NPCs idle) → boost loop is a no-op → behavior byte-identical to today.

## 4. Where it slots in

Adds **instances/parameters** to existing files — no new architecture:

- **`Mechanics/biochem/chemical.py`** — register `"fatigue"` in `Chemicals.__init__` `_levels`; add it to the `tick()` natural-decay list (`FATIGUE_DECAY_MULT`); add the fatigue→`tiredness` boost block right beside the existing `affinity_strain` boost. This is the same shape as the strain code already there.
- **`Mechanics/biochem/emitter.py`** — add `ExertionEmitter` alongside `AffinityComfortEmitter`, using the module's existing `_approach()` helper. One small class, matching the "keep emitters minimal, no manager forest" note in that file's header.
- **`Mechanics/entities/derivation.py`** — register the `endurance(attrs)` capacity-style formula next to `bit_capacity`/`byte_capacity`. This is the polymorphic seam the charter demands for attribute derivations.
- **`Mechanics/ai/controller.py`** — instantiate `ExertionEmitter` beside `self._affinity_emitter`; call `.emit()` in `update()` step 2b, passing `self.state` (the locus) and `self.npc`'s attributes. Surface `fatigue` for observability (mirror `self.affinity_comfort`). One `EXERTING_STATES` set names the exerting loci.
- **`settings.py`** — the named constants: `FATIGUE_BASE_GAIN`, `EXERTION_TARGET_MAX`, `FATIGUE_DECAY_MULT`, `FATIGUE_ACTIVE_FLOOR`, `FATIGUE_SLEEP_BOOST`, `ENDURANCE_CON_WEIGHT`, `ENDURANCE_PHY_WEIGHT`.

**No changes** to `need.py`, `need_factory.py`, `needs_system.py`, `source_selector.py`, `needs.json`, `sources.json`, `drive.py`, `brain.py`, or any `states/` file. The Sleep Drive and bed source already exist; fatigue only feeds them. This is a citizen in the brain → chemical → drive → urgency substrate: new chemical (`fatigue`) + new emitter locus (activity) feeding an **existing** drive (Sleep), per §W5/§W6.

## 5. Interactions & risks

- **Sleep need coupling (intended).** Fatigue's entire visible effect is through `tiredness`. A worked NPC sleeps earlier and, arguably, appears to "need less clock-time" before bed. That is the design. The raw `need.current_value` decay is untouched — fatigue changes *perceived* urgency, not physical decay, exactly per §B7's design intent. Physical SP/stamina drain from exertion (§W4 hints "sustained exertion" drains `sp`) is a **deliberate non-goal** here — this note is the perceived-urgency layer only; SP-drain-on-exertion is a future arc to keep this change additive.
- **Maslow / suppression (§W2).** Fatigue is Tier-1-adjacent (it feeds Sleep, a survival need), so it does not need the low-`base_weight` suppression that Tier 2/3 wants use — it rides the existing Sleep Drive's weight. No explicit gate, consistent with the charter's "suppression falls out of `base_weight` arithmetic."
- **Double-counting caution.** `affinity_strain` already boosts *all* survival chemicals including `tiredness`. Fatigue adds a second boost to `tiredness`. Both are clamped to `[0,1]` by `Chemicals.set`, so no runaway; but a strained *and* exhausted NPC will prioritize sleep hard. That is defensible biology (stressed + tired → collapse), but the Director should eyeball the combined tuning.
- **Runnable-state discipline.** Fully additive; no enum or data-schema change; nothing lands in a broken intermediate. `fatigue = 0` reproduces current behavior exactly. Chemical rides the generic chemicals save blob (like `affinity_strain`, §B8) — no save migration.
- **Legibility (§B1 requirement).** Fatigue MUST surface in the observation panel and `npcs.csv`, same as `comfort`/`stress`/`affinity_strain`. Creatures' cardinal sin was opacity; a hidden chemical that changes behavior is a regression. This is a hard requirement on the implementer, called out here so QC can gate it.

## 6. Open questions

1. **`SATISFYING` classification.** Is *eating/drinking* exertion? I've assumed effortful sources exert and only a `sleep` source rests. Simpler alternative: `SATISFYING` is always restful except when it's not a bed. Director/Shawn to pick the locus split — it's a one-line set membership decision.
2. **Endurance attribute basis.** I chose Constitution (durability, already the pool-capacity attribute) + Physique. Should Reflexes or a future dedicated stamina attribute factor in? The formula is swappable, so this is tunable, not structural.
3. **SP-drain deferral.** §W4 explicitly lists "sustained exertion" as an SP drain. I deferred that to keep this additive. Does the Director want fatigue to *also* nibble `sp` now, making it partly self-destructive (§W3), or hold that for the SP-drain arc?
4. **Interaction with `affinity_strain` on `tiredness`.** Do we want fatigue and strain to stack additively on `tiredness` (current proposal) or take a max? Additive is more punishing; max is gentler. Tuning call.

## 7. Bible citations

- `lucentforge_needs_wants_drives_addendum_v1.md` — **§W5** (implementation sequence: add chemical → add emitter → the brain already iterates drives; a new want is a citizen), **§W6** (`affinity_strain` is the exact pattern — slow chemical that modifies perceived need urgency, not a new system), **§W2** (Maslow suppression falls out of weight arithmetic, no explicit gate), **§W4** (SP as survival floor; "sustained exertion" drains SP — basis for deferring the SP-drain question).
- `lucentforge_biochem_affinity_addendum_v1.md` — **§B2** (emitter samples a locus and pushes a chemical toward a gain-controlled target; keep emitters minimal), **§B7** (the strain mechanism I'm mirroring — build slow, decay slow, boost a survival need chemical so the drive perceives higher urgency; parity invariant at chemical = 0), **§B1/§B4** (legibility is a requirement; observation-panel + run-logger surfacing).
- `lucentforge_terminology_map_v_1.md` — line 77 (`stamina`/`Sp` is canonical; `cycles` is a pre-bible holdover — used to name the SP-drain deferral correctly and avoid reintroducing `cycles`).
- `lucentforge_stats_magic_addendum_v1.md` §M3, via `derivation.py` — the polymorphic capacity-formula seam (`bit_capacity`/`byte_capacity`) that `endurance(attrs)` registers alongside, satisfying "formulas, not numbers."

---

## Director Reconciliation (Caelum, 2026-08-04)

**Verdict:** Design **accepted, PASS WITH NOTES.** No canon or naming conflict between Systems Design
and QC — QC independently verified the bible citations and code attach points and they hold. QC's
findings refine the design; they do not defeat it. **Implementation is a separate future arc, gated on
Shawn's decisions to the open questions below.**

**QC notes folded in as implementation-stage requirements** (these become live at the Implementation
review, not now):
1. **(Major) `tiredness` is special-cased.** Unlike the other survival chemicals, `tiredness` has a
   dedicated sleep-decay branch in `chemical.py` (hard-decays at `_DECAY×5` while sleeping). The
   fatigue boost must be **traced against that branch**, not copied from the `affinity_strain` block on
   faith. Implementation acceptance must include a test: fatigue nonzero + NPC sleeping → `tiredness`
   still nets downward.
2. **(Minor) Constitution is already load-bearing** (drives `bit/byte` capacity *and* DEF). Folding
   fatigue-resistance onto it too is defensible but couples three systems to one attribute — a tuning
   decision for Shawn (Open Q2).
3. **(Minor) Double-count on `tiredness`** (`affinity_strain` + `fatigue` both boost it) is real,
   clamped, and correctly surfaced — resolve additively-vs-max at Open Q4.
4. **(QC-added open item, now Q5) Legibility attach points unverified.** The note *asserts* fatigue must
   appear in the observation panel + `npcs.csv` (a hard §B1 requirement) but didn't confirm
   `observation_panel.py` / `run_logger.py` have an obvious slot. Confirm before implementation so
   legibility isn't an afterthought.

**Consolidated open questions for Shawn** (design does not proceed to implementation until these are
answered — none are structural, all are tuning/scope):
- **Q1** — Is `SATISFYING` (eating/drinking) exertion, or restful-unless-at-a-bed? (one-line locus split)
- **Q2** — Endurance basis: Constitution + Physique as proposed, or bring in Reflexes / a future stamina attribute?
- **Q3** — Should fatigue also nibble `sp` now (partly self-destructive, §W4), or hold SP-drain for its own arc?
- **Q4** — Fatigue + `affinity_strain` on `tiredness`: stack additively (punishing) or take max (gentler)?
- **Q5** *(from QC)* — Confirm the observation-panel + `npcs.csv` slots for `fatigue` before building.

**Next step:** this is a *future implementation arc* for LucentForge, not part of the studio proof.
When Shawn wants it built, answer Q1–Q5, then it runs back through the studio at Implementation stage
(Systems Design implements → QC reviews with the test gate live). Until then it rests here as an
accepted design.
