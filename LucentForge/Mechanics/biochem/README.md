# Mechanics/biochem — Creatures-Inspired Biochem Layer

Implements the emitter/receptor biochem model from *Creatures* (1996). See `docs/bible/lucentforge_biochem_affinity_addendum_v1.md` for full doctrine.

## Chemicals (chemical.py)

Dict-based registry keyed by string name. Three affinity chemicals emitted by the AffinityComfortEmitter:

| Chemical | Role | Gain | Decay mult |
|---|---|---|---|
| `comfort` | Positive affinity match signal | 0.05/tick | 0.7× |
| `stress` | Negative affinity mismatch signal (instantaneous) | 0.05/tick | 0.7× |
| `affinity_strain` | Accumulated cost of sustained hostile exposure (§B7) | 0.0003/tick | 0.3× |

Need-driven chemicals (`hunger_chem`, `thirst_chem`, `tiredness`) are populated dynamically from need definitions and updated in `tick()`. When `affinity_strain > 0.01`, a small boost (`strain × AFFINITY_STRAIN_NEED_BOOST`) is added to each survival need chemical per tick — making needs feel more urgent sooner without changing their physical decay rate.

## Emitter (emitter.py)

`AffinityComfortEmitter.emit()` samples the entity's current region each tick and pushes `comfort`, `stress`, and `affinity_strain` toward their lattice-score-derived targets. The `_approach(key, target, gain)` helper moves any chemical a gain fraction toward a target, clamped to [0, 1].

## Drive (drive.py)

`Drive.compute_urgency()` is the receptor half: reads a need chemical and applies a fearfulness × reactive-chemical multiplier (`pain + fear + stress`). This is the Phase A mechanism — instantaneous, resets when stress drops.

## Settings knobs (settings.py)

```
AFFINITY_STRAIN_GAIN       = 0.0003   # per-tick approach rate (~60s to ~50% under full discomfort)
AFFINITY_STRAIN_NEED_BOOST = 0.0002   # per unit strain added to each need chemical per tick
COMFORT_RELOCATE_STRESS_THRESHOLD = 0.4
COMFORT_RELOCATE_MARGIN           = 0.3
COMFORT_CONTENT_THRESHOLD         = 0.4
```
