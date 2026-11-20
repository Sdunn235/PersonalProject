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

## Decision: The World Opens Upriver (2026-11-19, Shawn)

The river flows north to south. The first panel beyond the starting area is its upper reach,
Panel(0,-1), opened before any other neighbour. Proposed by World Building and Story/Lore
independently (studio/EPICS.md); decided by Shawn.

WHY:
The river is the one feature that must cross an edge, so proving the seam there proves it everywhere;
upriver is the river clan's home water, the best-sourced people in the Gobby story.

Trade-off:
East (the merchant trail) and west (the deep woods) wait, and the upper reach opens with no residents
until Story/Lore's people are decided.

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