# LucentForge Biochemistry — Affinity Comfort Addendum v1

**Status:** Canon (approved planning session 2026-07-18)
**Authority target:** Lucent Forge Bible — Stage 4 biochem/affinity doctrine
**Companion docs:** `lucentforge_stats_magic_addendum_v1.md` (§M3 pools, §M5 affinity, §M6 deferred combat), the Grace drafts (`lucentforge_affinity_grace_foundation_v1_derived_revision.md`, `lucentforge_cosmology_foundation_v1_derived_revision.md`)

> This addendum makes affinity **live**: an entity feels comfort or stress from the affinity of the region it occupies, and that feeling flows through biochemistry into behavior. It is the first application of a Creatures-style **emitter/receptor** biochem layer.

---

## §B1 — Lineage and Intent

LucentForge's biochem is a deliberate descendant of *Creatures* (1996): chemicals with decay, drives that read chemicals, a decision that follows the strongest drive. Creatures connected body-state to chemistry through **emitters** (a locus/state emits a chemical) and **receptors** (a chemical drives a locus). LucentForge already has the receptor half — `Drive.compute_urgency` reads a chemical and produces urgency. This addendum adds the **emitter** half, with affinity comfort as its first citizen.

**Improve where Creatures failed.** Creatures' primary failure was *opacity* — you could not see why a creature acted. Therefore: every chemical, drive, and comfort signal introduced here **must be legible** in the observation panel and run-logger. Legibility is a requirement, not polish.

**Deferred (seeded, not built):** chemical *reactions* (`r1+r2 → p1+p2`) and *heritable genetics* (affinity from DNA / the Hob "innate spark"). These are the natural next Creatures layers; they are out of scope until a future planning session.

---

## §B2 — The Emitter/Receptor Model

- **Emitter** — samples a *locus* (a world/body/relationship state) each tick and pushes a chemical toward a target concentration (gain-controlled). Creatures-faithful.
- **Chemical** — a named concentration in `[0, 1]` with natural decay (half-life analog). Extensible dict store.
- **Receptor** — reads a chemical and drives a *locus* (here: need urgency). Already embodied by `Drive.compute_urgency`.

Ad-hoc chemical injections that predate this model (`proximity` fear, `zone_ai` anger/fear) are **legacy injectors** that will be re-expressed as emitters in a later, parity-gated phase — one cohesive mechanism, not N special cases.

---

## §B3 — Affinity Comfort

**Comfort is a lattice relationship, not a flat weakness chart** (Grace §12.2–§13.1). It is derived from **lattice distance** on the eight-position Grace ring (clockwise: Fire, Plasma, Air, Colloidal Dispersion, Water, Non-Newtonian, Earth, Bingham Placidity):

| Ring distance | Meaning | Comfort |
|---|---|---|
| 0 | same affinity | **+1.0** |
| 1 | adjacent (a primal and its bridging derived) | **+0.5** |
| 2 | shares a derived bridge / one step removed | **+0.2** |
| 3 | far | **−0.4** |
| 4 | across the lattice | **−0.8** |

`comfort_score(entity_effective_affinities, region_affinity, region_intensity)` = the **best** (most comfortable) pairing across the entity's effective affinities, scaled by the region's `affinity_intensity`. **Neutral** entity (no effective affinity, e.g. the player) or **neutral** region (`affinity = None`) → comfort `0.0` — neutral is *not* Dark, and produces no felt effect.

---

## §B4 — Physiology (this arc)

- Comfort emits two chemicals: **`comfort`** (positive part of the score) and **`stress`** (negative part). Both decay naturally.
- **Receptor effect (Phase A — built, C0040):** `stress` joins the drive urgency multiplier alongside pain and fear — a stressed entity acts more urgently and settles less. Additive: with `stress = 0`, behavior is unchanged.
- **Behavior (Phase B — built, C0042):** sustained `stress` raises a relocate/comfort priority so an entity with no urgent survival need drifts toward remembered-comfortable ground; entities **learn** region comfort (an EMA per region), so two same-affinity beings diverge by lived experience (Grace §14.2).
  - *Learned memory:* `Memory.record_region_comfort` / `best_region` blend each tick's comfort into a per-region EMA (`settings.MEMORY_EMA_ALPHA`), defaulting to `0.0` (unknown = neutral). `best_region` only returns a **positively** remembered region.
  - *Relocate drive:* `IdleState` routes a non-urgent, stressed entity toward its best remembered region via a distinct **`RELOCATING`** state (legibility — §B1). It outranks patrol/idle-wander but **never** an active raid or an urgent survival need.
  - *Comfort's dampening/settling role:* an entity already at/above `settings.COMFORT_CONTENT_THRESHOLD` comfort stays put — comfort suppresses the urge to move.
  - *Thresholds:* `COMFORT_RELOCATE_STRESS_THRESHOLD`, `COMFORT_RELOCATE_MARGIN`, `COMFORT_CONTENT_THRESHOLD` (settings). Additive: below threshold / already content → no relocate → byte-identical to pre-Phase-B.

---

## §B5 — What This Is Not

- Not a combat damage table (affinity combat stays deferred, §M6).
- Not personality (a Fire being is not "angry"; comfort influences body-state and preference, not character — Grace §7.3).
- Not moral (comfort is not good/evil; a being may be comfortable somewhere harmful).
- Not a manager framework — the emitter concept stays minimal until a second/third emitter earns generalization.

---

## §B7 — Affinity Strain (sustained need urgency elevation) — Phase C (built, C0046)

**The problem it solves.** Phase A gave instantaneous stress-modulated urgency; Phase B gave relocation preference. Neither answered: what happens to a creature that *stays* in a hostile region against its will — outnumbered, unable to flee, or simply lost? The body is being taxed. Needs should feel more urgent sooner.

**Mechanism.** A third affinity chemical, `affinity_strain`, builds slowly under sustained discomfort and decays slowly when comfort returns.

- **Source:** `AffinityComfortEmitter.emit()` approaches `affinity_strain` toward `max(0, -comfort_score)` each tick at `AFFINITY_STRAIN_GAIN = 0.0003` (167× slower than `stress`'s 0.05 gain). A score of -0.8 with gain 0.0003 reaches ~50% strain after ~60 real seconds.
- **Decay:** Natural chemical decay in `Chemicals.tick()` at `_DECAY × 0.3` per tick (slower than comfort/stress at 0.7×). Combined with the emitter's own approach-to-zero when score ≥ 0, strain falls off when the entity reaches comfort.
- **Effect:** When `affinity_strain > 0.01`, `Chemicals.tick()` adds `strain × AFFINITY_STRAIN_NEED_BOOST` to each survival need chemical per tick. The brain reads a slightly elevated need chemical → `Drive.compute_urgency()` computes higher urgency → NPC acts on hunger/thirst/sleep sooner than the raw `current_value` alone would trigger.
- **Parity invariant:** `affinity_strain = 0` → the boost loop does nothing → behavior is byte-identical to C0044. Fully additive.

**Design intent.** The effect is perceived urgency through the biochem layer, not raw need decay acceleration. The actual `need.current_value` decays at its normal rate; the entity only *feels* the need as more pressing. This matches the lived experience of stress-taxed biology and stays within the existing emitter/receptor abstraction. Physical decay acceleration is a future arc.

**Observability.**
- ZONE panel (observation_panel.py): when `affinity_strain > 0.01` and no active relocation, the suffix slot shows `s{strain:.2f}` (red). Relocation target always takes priority when RELOCATING.
- npcs.csv (run_logger.py): `affinity_strain` column added alongside `comfort` and `stress`.
- Settings knobs: `AFFINITY_STRAIN_GAIN`, `AFFINITY_STRAIN_NEED_BOOST` in settings.py near the existing `COMFORT_*` constants.

---

## §B6 — Testing Doctrine

1. `comfort_score`: same = +1.0×intensity; ring-distance tiers monotonic; neutral entity or region = 0.0.
2. `lattice_distance` is symmetric, in `[0, 4]`, 0 iff equal.
3. Emitter moves `comfort`/`stress` toward the score-derived target and never leaves `[0, 1]`.
4. `stress` raising increases drive urgency monotonically; `stress = 0` reproduces pre-arc urgency exactly.
5. (Phase B — built) region-comfort memory is an EMA; a comfortable region's preference rises with repeat exposure; `best_region` picks the highest positive and is `None` when only neutral/negative regions are known. A stressed, non-urgent entity with a better-remembered region enters `RELOCATING`; with `stress = 0` (or already content) it does not (parity).
6. Legibility: comfort/stress and current-region comfort appear in the observation panel and run-logger; Phase B adds best-remembered region + active relocate target (panel) and `best_region`/`best_region_pref`/`relocating` columns (npcs.csv).
