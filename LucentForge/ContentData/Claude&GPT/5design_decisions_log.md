# Design Decisions Log

## Decision: Emergent Over Scripted

WHY:
Scripted systems do not scale into true simulation.

Rejected:
- Behavior trees as primary logic
- Hard-coded quest structures

---

## Decision: Drive-Based AI

WHY:
Internal state produces more believable behavior than external scripting.

Trade-off:
Harder to debug and predict.

---

## Decision: Player Is Not Central

WHY:
Player-centric design collapses simulation depth.

Trade-off:
Less immediate gratification for players.

---

## Decision: Prototype First (PyGame)

WHY:
Faster iteration on logic without engine overhead.

Trade-off:
Requires later rebuild in UE5.

---

## Decision: Persistence Is Required

WHY:
Without persistence, nothing matters.

---

## Rejected Approaches

- Fully procedural reset worlds
- NPCs as disposable units
- Script-heavy design pipelines

---

## Open Decisions

- Memory scaling architecture
- Faction system depth
- Multiplayer synchronization model