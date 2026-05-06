# Lucent Forge Micro Simulation v1

## Purpose
This document defines the first buildable prototype of Lucent Forge. It is a constrained simulation designed to prove that a small world can evolve believably over time without player input.

This is not a full game. It is a proof of system behavior.

---

# 1. Core Goal

Create a small autonomous simulation where NPCs act, adapt, and produce visible world changes over time without player intervention.

---

# 2. Success Criteria

The prototype is successful if:

- A town can survive or collapse without player input
- NPCs behave differently under similar conditions
- A goblin threat escalates naturally over time
- World changes feel explainable and non-scripted

---

# 3. World Layout

## Map Type
Grid-based map

## Geography
- Forest-dominant region
- River divides map into two halves

## Civilized Side
- Town Center
- Homes (rest area)
- Farm (food production)

## Wild Side
- Goblin Camp
- Dense forest

## River
- Acts as movement barrier
- Crossing limited or probabilistic

---

# 4. NPC Structure

Each NPC contains:

## Core
- ID
- Location
- Alive state

## Needs
- Hunger (0–100)
- Energy (0–100)

## Traits (4–6)
- Risk
- Fear
- Greed
- Curiosity
- Discipline

## Skills
- Combat
- Gathering
- Survival

## State
- Current Goal
- Current Action
- Target

## Memory (minimal)
- Last Action Type
- Last Outcome
- Bias Modifier

---

# 5. NPC Initialization

NPCs use soft role initialization:

- Slight variation in traits
- Slight variation in skills
- No fixed roles

Roles emerge through behavior.

---

# 6. Core Systems Included

## Needs System
- Hunger increases over time
- Energy decreases over time

## Trait Influence
- Affects decisions and interpretation

## Skills
- Modify success chance

## Decision Loop

Update State → Evaluate Pressures → Select Goal → Choose Action → Move → Resolve Outcome → Update Memory

## Goblin Threat System

Variables:
- Threat Level (0–100)
- Growth Rate

Behavior:
- Increases over time
- Decreases from NPC success
- Thresholds trigger escalation

## Resource Loop

- Farm produces food
- NPCs consume food
- Low food increases pressure

## Outcome Resolution

Success based on:
- Skill
- Relevant stat
- Context
- Small randomness

---

# 7. Systems Excluded

Do NOT include in v1:

- Full magic system
- Full economy
- Complex inventory
- Deep memory
- Social systems
- Factions
- Advanced UI

---

# 8. Simulation Tick Loop

Each tick:

1. Update World State
2. Update NPCs
3. Update Goblin Threat
4. Evaluate World Conditions

---

# 9. World Conditions

States:
- Stable
- Strained
- Collapsing

Determined by:
- Food levels
- NPC survival
- Threat level

---

# 10. Test Scenarios

## Stable Town
Food stable, threat controlled

## Pressure State
Food fluctuates, threat rises and falls

## Collapse
Food fails, threat overwhelms

## Divergence
NPCs behave differently

---

# 11. Debug Output

Logs must include:

## Per Tick
- Tick number
- Food level
- Threat level
- Town state

## Per NPC
- ID
- Location
- Hunger
- Energy
- Goal
- Action
- Outcome

## Events
- Food success/failure
- Threat changes
- NPC death
- Town collapse

---

# 12. Observation

Use both:

- Console logs (primary)
- Simple visual grid (secondary)

---

# 13. Completion Condition

The prototype is complete when:

- The simulation runs consistently
- Outcomes vary between runs
- Behavior is understandable
- The world evolves without player input

---

# 14. Next Phase

After completion:

- Add player observation
- Add limited interaction
- Expand systems gradually

---

# 15. Constraint

Do not expand scope during implementation.

Focus only on proving the system works.

