# Mechanics/biochem — Creatures-Inspired Biochem Layer

Implements the emitter/receptor biochem model from *Creatures* (1996). See `docs/bible/lucentforge_biochem_affinity_addendum_v1.md` for full doctrine.

## Chemicals (chemical.py)

Dict-based registry keyed by string name. Three affinity chemicals emitted by the AffinityComfortEmitter:

| Chemical | Role | Gain | Decay mult |
|---|---|---|---|
| `comfort` | Positive affinity match signal | 0.05/tick | 0.7× |
| `stress` | Negative affinity mismatch signal (instantaneous) | 0.05/tick | 0.7× |
| `affinity_strain` | Accumulated cost of sustained hostile exposure (§B7) | 0.0003/tick | 0.3× |
| `fatigue` | Activity-driven tiredness from sustained exertion (§W6) | `FATIGUE_BASE_GAIN`/endurance | `FATIGUE_DECAY_MULT`× |

Need-driven chemicals (`hunger_chem`, `thirst_chem`, `tiredness`) are populated dynamically from need definitions and updated in `tick()`. When `affinity_strain > 0.01`, a small boost (`strain × AFFINITY_STRAIN_NEED_BOOST`) is added to each survival need chemical per tick — making needs feel more urgent sooner without changing their physical decay rate.

**Fatigue → sleep urgency (§W6).** *Behavior goes through the receptor below (`receptor.py`); this chemical boost is display-side.* When `fatigue > FATIGUE_ACTIVE_FLOOR`, a boost (`fatigue × FATIGUE_SLEEP_BOOST`) is added to **only** `tiredness` (the sleep chemical) — a worked NPC crosses into the sleep WARNING zone sooner via the *unchanged* Sleep drive. This boost runs AFTER the sleep-need branch (which hard-decays `tiredness` at `_DECAY×5` while an NPC sleeps); `FATIGUE_SLEEP_BOOST` is tuned conservatively so a sleeping NPC with nonzero fatigue still nets `tiredness` **downward** (the decay dominates the boost). Additive with the strain boost, clamped to [0,1]. Parity: `fatigue = 0` → no effect.

## Emitter (emitter.py)

`AffinityComfortEmitter.emit()` samples the entity's current region each tick and pushes `comfort`, `stress`, and `affinity_strain` toward their lattice-score-derived targets. The `_approach(key, target, gain)` helper moves any chemical a gain fraction toward a target, clamped to [0, 1].

`ExertionEmitter.emit(chemicals, attrs, state, at_bed)` samples the controller's current AI state (the locus) each tick and pushes `fatigue`. `EXERTING_STATES = {MOVING, RAIDING, RELOCATING, PATROLLING}` push fatigue toward `EXERTION_TARGET_MAX`; resting at a bed (`at_bed=True`, i.e. SATISFYING at a sleep source) pulls it toward 0; every other locus (IDLE, SATISFYING at a non-bed source) is neutral (natural decay only). Accrual gain is attribute-derived — `FATIGUE_BASE_GAIN / endurance(attrs)` — so a hardy NPC tires slower; recomputed from *live* attributes each tick (never spawn-frozen).

## Receptor (receptor.py) — chemicals that change DECISIONS

NPC decisions (IdleState, goblin behavior, patrol/relocate/raid exits) read need **zones**, not
chemicals — `Drive.compute_urgency()` / `Brain.get_priority_need_id()` only feed the HUD and the `V`
inspector. So a chemical changes behavior only through a receptor that writes a **perceived pull** onto a
need (`Need.perceived_pull`; `zone`/`is_urgent`/sorting read `Need.perceived_value`).

`apply_perceived_pulls(needs, chemicals)` runs each frame in `NPCController.update` (step 2d). First
receptor: **fatigue → sleep** — `pull = fatigue × FATIGUE_SLEEP_PULL` need-points (0 at/below
`FATIGUE_ACTIVE_FLOOR`), so a worn-out NPC crosses its sleep WARNING line sooner. Max pull 30 keeps a
just-slept NPC FINE (no bed loop). Side effect by design: a perceived-urgent need also pauses HP/SP regen.
`affinity_strain` does **not** have a receptor yet (BACKLOG LF-042).

## Drive (drive.py)

`Drive.compute_urgency()` is the receptor half: reads a need chemical and applies a fearfulness × reactive-chemical multiplier (`pain + fear + stress`). This is the Phase A mechanism — instantaneous, resets when stress drops.

## Settings knobs (settings.py)

```
AFFINITY_STRAIN_GAIN       = 0.0003   # per-tick approach rate (~60s to ~50% under full discomfort)
AFFINITY_STRAIN_NEED_BOOST = 0.0002   # per unit strain added to each need chemical per tick
FATIGUE_BASE_GAIN     = 0.0015   # numerator of per-FRAME gain (endurance divides it); must beat decay 0.00005
FATIGUE_SLEEP_PULL    = 30.0     # need-points of perceived sleep loss per unit fatigue (receptor)
EXERTION_TARGET_MAX   = 1.0      # fatigue target while in an exerting locus
FATIGUE_DECAY_MULT    = 0.25     # natural-decay multiplier in Chemicals.tick
FATIGUE_ACTIVE_FLOOR  = 0.01     # fatigue must exceed this to boost tiredness
FATIGUE_SLEEP_BOOST   = 0.0003   # per unit fatigue added to tiredness/tick (< sleep-decay 0.001)
ENDURANCE_CON_WEIGHT  = 1.0      # Constitution weight in endurance() (primary)
ENDURANCE_PHY_WEIGHT  = 0.5      # Physique weight in endurance() (secondary)
ENDURANCE_MIN         = 1.0      # endurance clamp floor (guards effective_gain divisor)
COMFORT_RELOCATE_STRESS_THRESHOLD = 0.4
COMFORT_RELOCATE_MARGIN           = 0.3
COMFORT_CONTENT_THRESHOLD         = 0.4
```
