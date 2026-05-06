# Lucent Forge Sim Core Schema v1

## Purpose
This document defines the plain-language structural schema for the first Lucent Forge simulation prototype. It is intended to bridge the design documents and the implementation phase by giving a coding agent clear object boundaries, ownership rules, and update responsibilities without forcing premature code architecture.

This is not source code. It is a system schema for implementation planning.

---

# 1. Top-Level Hierarchy

```plaintext
Lattice
    └── World
```

## 1.1 Lattice

### Purpose
Meta-container for one or more simulation worlds.

### Owns
- active World reference
- optional future list of World instances

### Does Not Own
- NPC logic
- map logic
- event resolution
- town systems
- simulation rules for individual worlds

### v1 Note
In v1, Lattice should remain extremely thin. It exists primarily as:
- philosophical top layer
- future-proof container
- entry point to the active world

It should not become a major implementation focus during the first prototype.

---

# 2. World

## Purpose
Primary simulation container for one running world instance.

## Owns
- Map
- collection of NPCs
- Town
- GoblinThreat
- ResourceState
- SimulationClock
- optional Logger reference
- optional EventPlaceholder

## Does Not Own
- deep per-NPC psychology logic
- rendering logic
- UI logic
- multi-world coordination

## v1 Note
World is the practical heart of the prototype. Most simulation orchestration happens here.

---

# 3. Map

## Purpose
Represents the grid-based region and spatial truth of the simulation.

## Owns
- grid dimensions
- tile data
- traversability rules
- tile tags or region tags
- references to important locations

## Required v1 Regions / Locations
- Town Center
- Homes / Rest Area
- Farm
- Forest
- River
- Goblin Camp

## Does Not Own
- NPC behavior
- goblin escalation rules
- world food totals
- town stability calculations

## v1 Note
Map should answer questions such as:
- where is an NPC?
- can a tile be crossed?
- what type of place is this tile?

Map should not decide what an NPC wants or what global systems mean.

---

# 4. NPC

## Purpose
Represents an autonomous agent acting within the world.

## Owns
- ID
- optional name
- location
- alive/dead state
- needs
- traits
- skills
- current goal
- current action
- target
- minimal memory / bias state

## Suggested v1 Internal Groups

### Core
- id
- location
- alive

### Needs
- hunger
- energy

### Traits
- risk
- fear
- greed
- curiosity
- discipline

### Skills
- combat
- gathering
- survival

### State
- current_goal
- current_action
- target

### Minimal Memory
- last_action_type
- last_outcome
- bias_modifier

## Does Not Own
- global food totals
- map structure
- goblin threat level
- town-wide state
- simulation clock

## v1 Note
NPC should know about itself and react to world state, but should not own the world or system-wide truth.

---

# 5. Town

## Purpose
Represents the settlement being evaluated for survival, strain, or collapse.

## Owns
- town condition / town state
- references to town-relevant locations
- optional simple population metadata
- optional town-level flags

## Suggested v1 Town States
- stable
- strained
- collapsing

## Does Not Own
- individual NPC needs
- map tile logic
- goblin threat logic
- simulation loop

## v1 Note
Town is a tracked entity, not just scenery. It should allow the simulation to answer:
- is the settlement holding together?
- is it under pressure?
- has it begun to fail?

---

# 6. GoblinThreat

## Purpose
Represents the primary escalating external pressure source for the prototype.

## Owns
- threat_level
- growth_rate
- raid_pressure
- crossing_pressure or crossing_state

## Does Not Own
- individual goblin unit AI for v1
- map geometry
- town food totals
- NPC decision logic

## v1 Note
GoblinThreat is not a full faction system. It is a threat-state object that drives escalation.

It should answer:
- how dangerous are the goblins right now?
- are they passive, raiding, or attempting crossing?
- is their influence growing or shrinking?

---

# 7. ResourceState

## Purpose
Tracks shared world resources needed for pressure and survival simulation.

## Owns
For v1, keep this intentionally small:
- food_total
- food_production_rate
- food_consumption_rate

## Does Not Own
- per-NPC hunger
- farm tile rules
- town collapse logic
- goblin logic

## v1 Note
ResourceState exists so the simulation can measure whether the settlement has enough food to remain stable.

Later expansion may include:
- water
- materials
- trade goods
- shortages / surpluses

These are out of scope for v1.

---

# 8. SimulationClock

## Purpose
Provides a single source of temporal truth for the simulation.

## Owns
- tick_count
- optional day/night flag
- optional time-of-day phase

## Does Not Own
- NPC update logic
- event logic
- map logic
- resource state logic

## v1 Note
SimulationClock should stay extremely simple. It only needs to answer:
- what tick is it?
- has time advanced?
- is it day or night, if included?

---

# 9. Optional Support Objects

## 9.1 Logger

### Purpose
Captures simulation output for debugging and validation.

### Recommended Usage
- per-tick summary output
- important event output
- NPC decision or action logs

### v1 Note
Logger may be owned by World or passed into World-related systems. It should not become a complicated service architecture in the first prototype.

---

## 9.2 EventPlaceholder

### Purpose
Light future-proofing hook for event expansion.

### v1 Note
Do not build a full event queue unless the prototype truly needs it. The goblin threat and town state already function as direct event drivers.

---

# 10. Ownership Summary

```plaintext
Lattice
└── World
    ├── Map
    ├── NPC[]
    ├── Town
    ├── GoblinThreat
    ├── ResourceState
    └── SimulationClock

Optional:
World
├── Logger
└── EventPlaceholder
```

---

# 11. Schema Law

Each object should own only the state it is responsible for maintaining.

Shared simulation behavior should emerge through interaction between objects, not by collapsing all logic into a single god-object.

---

# 12. Update Responsibility

## Core Rule
World orchestrates the simulation update.
Subobjects store state.
Dedicated update functions or systems apply changes.

This means World is the coordinator, not a dumping ground for every line of logic.

---

# 13. Recommended Update Order

Each simulation tick should conceptually follow this order:

```plaintext
1. Advance SimulationClock
2. Update ResourceState
3. Update each NPC
4. Update GoblinThreat
5. Recalculate Town state
6. Emit logs / summaries
```

---

# 14. Object-by-Object Update Responsibility

## 14.1 SimulationClock

### Updated By
- World orchestrator

### Responsibility
- increment tick count
- update optional time phase

---

## 14.2 ResourceState

### Updated By
- World orchestrator calling resource update logic

### Responsibility
- apply food production changes
- apply food consumption changes
- maintain current shared food totals

### Should Not Do
- decide individual NPC behavior
- decide town collapse directly

---

## 14.3 NPC

### Updated By
- World orchestrator calling NPC update logic per NPC

### Responsibility
- update needs
- evaluate pressures
- choose goal
- choose action
- move if needed
- resolve action
- adjust minimal memory/bias

### Should Not Do
- change global world rules
- own town-wide survival logic
- manage the goblin system

---

## 14.4 GoblinThreat

### Updated By
- World orchestrator calling goblin threat update logic

### Responsibility
- raise or lower threat level
- determine escalation stage
- respond to system conditions such as failed defense or unchecked growth

### Should Not Do
- directly kill NPCs unless through a mediated event or encounter step
- own map routing logic

---

## 14.5 Town

### Updated By
- World orchestrator calling town evaluation logic

### Responsibility
- derive current town condition from shared pressures
- reflect whether the town is stable, strained, or collapsing

### Inputs Likely Used
- food availability
- living NPC count
- goblin threat pressure

### Should Not Do
- individually update NPCs
- own food production logic
- own goblin behavior

---

## 14.6 Logger

### Updated By
- World orchestrator and/or update systems

### Responsibility
- record tick summaries
- record important changes
- support debugging and later visualization

---

# 15. Recommended System/Module Boundaries

These are not required filenames, but they are the right conceptual boundaries for implementation.

## Suggested Modules
- lattice
- world
- map
- npc
- town
- goblin_threat
- resource_state
- simulation_clock
- simulation_runner or simulation_engine
- logger

## Update Helpers / Systems
Optional helper modules or internal systems may handle:
- npc_update
- resource_update
- goblin_update
- town_evaluation

The exact code layout can vary, but these responsibilities should remain distinct.

---

# 16. Handoff Guidance for Implementation

If this schema is used by a coding agent, implementation should follow these rules:

- Build only one active World in v1
- Keep Lattice thin
- Do not expand object scope during initial implementation
- Prefer simple data ownership over clever abstraction
- Prefer clear updates over premature optimization
- Use logs first, visuals second

---

# 17. Closing Statement

This schema exists to keep Lucent Forge Sim Core v1 honest.

The purpose of the first prototype is not to simulate everything.
It is to prove that a small, spatial world containing a town, a threat, and a handful of differentiated NPCs can produce believable change over time through structured interaction.

If that works, the deeper world can be earned from there.

