# Lucent Forge — Vision Document

## Core Identity

Lucent Forge is not fundamentally a game.

It is a **persistent emergent ecosystem simulation framework** in which autonomous entities (NPCs, creatures, factions) exist, evolve, and interact independently of player presence.

The "game" is an interface layer that allows human players to:
- Enter the simulation
- Influence it
- Observe it
- Become part of its history

The simulation does not exist for the player. The player exists within the simulation.

---

## The PyGame Prototype vs Full System

### PyGame Prototype Purpose
The current PyGame implementation is not Lucent Forge.

It is a **sandbox for validating core principles**, specifically:
- NPC needs systems
- Drive-based behavior
- Early decision loops
- Interaction scaffolding
- Biochemical abstraction layer (early form)

It is intentionally:
- Simplified
- Non-performant at scale
- Lacking persistence depth
- Lacking full memory modeling

### Relationship to Final System

The prototype exists to answer:
- Can autonomous behavior emerge from internal systems?
- Can needs + environment produce believable decisions?
- Can we structure cognition modularly?

If the answer is yes → we scale the architecture.

---

## Target Platform

### Primary Target: Unreal Engine 5 (initially)
Reasons:
- Strong world-building tools
- Large ecosystem and support
- Blueprint + C++ hybrid for rapid iteration + performance
- Proven scalability for large environments

### Long-Term Possibility: Custom Engine
If UE5 becomes restrictive in:
- Simulation scale
- Data persistence models
- Threading / ECS limitations

Then migration to a custom simulation-first engine becomes viable.

---

## What "Done" Looks Like

Lucent Forge is considered functionally realized when:

### World
- The world persists independently of players
- Terrain can be altered over long timeframes
- Ecosystems regenerate, collapse, and evolve

### NPCs
- NPCs have:
  - Internal drives
  - Memory
  - Social relationships
  - Long-term identity formation
- NPCs can:
  - Form goals without scripting
  - Adapt behavior over time
  - Affect the world in lasting ways

### Systems
- Economy emerges from scarcity and production
- Settlements grow, decline, and disappear
- Factions form, evolve, and conflict organically

### Player Role
- Player is not the center of the world
- Player influence is real but not dominant
- The world continues meaningfully without the player

---

## Scope Boundaries — What Lucent Forge Is NOT

Lucent Forge is NOT:

- A scripted RPG with branching dialogue trees
- A theme park MMO with fixed content loops
- A purely procedural world with no persistence
- A system where NPCs are disposable or reset3
- A game where all meaning comes from player action

---

## Design Hierarchy (Non-Negotiable)

1. Emergent Ecosystem Integrity
2. Simulation Consistency
3. Player Experience

If a design improves player experience but breaks simulation integrity, it is rejected.

---

## Guiding Principle

If the world cannot meaningfully exist without the player,
then the system has failed.1