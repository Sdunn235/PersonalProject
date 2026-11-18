# Mechanics/needs/ — survival needs

Data-driven needs (hunger, thirst, sleep) from `Mechanics/data/needs.json`, their decay, and the sources
that satisfy them.

| File | Role |
|---|---|
| `need.py` | `Need` dataclass + `NeedZone` (FINE / WARNING / CRITICAL); rates computed per frame from per-day JSON |
| `need_factory.py` | Builds an entity's needs from the data layer |
| `needs_system.py` | Decay, source-aware fill, HP drain/regen, `get_priority_need` (the pick every AI state uses) |
| `need_source.py` | `NeedSource` — finite stock, capacity, regen, depletion |
| `source_selector.py` | 4-weight source choice (distance / memory / stock / novelty) |

## Actual vs perceived value
`current_value` is the real need. `perceived_pull` (runtime-only, never saved) is set each frame by the
NPC controller from biochem receptors (`biochem/receptor.py`); `perceived_value = current_value − pull`.
**`zone`, `is_urgent`, `urgency_score` and priority sorting all read `perceived_value`**, so every decision
path sees the same thing. Parity: pull 0 → identical to before (2026-11-17, fatigue receptor).

## Design deviations
- 2026-11-17 — zone now reads `perceived_value` instead of `current_value` (equal when no pull is set).
  Regen gating (`apply_regen`, "all needs FINE") therefore also pauses for an NPC whose fatigue makes
  sleep feel urgent. Intended: exhaustion halts recovery.
