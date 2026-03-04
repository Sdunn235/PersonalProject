# SimCore Architecture Specification
Lucent Forge Simulation Engine (Engine-Agnostic Core)

---

## 1. Purpose

SimCore is the engine-agnostic simulation backbone of Lucent Forge.

It is responsible for:

- Agent cognition and behavior
- World state modeling
- Resource persistence
- Economic systems
- Social relationships
- Event logging
- Time progression (simulation-level)

SimCore must not depend on Unreal Engine or any rendering framework.

It must be:

- Portable
- Testable
- Deterministic where possible
- Capable of headless execution

---

## 2. Architectural Layers

Lucent Forge is divided into 3 strict layers:

### Layer 1 — SimCore (Pure C++)

Contains:
- AgentModel
- NeedSystem
- TraitSystem
- DecisionEngine
- WorldState
- ResourceSystem
- EconomyEngine
- EventLog
- TimeManager

Forbidden:
- Unreal headers
- Engine types
- Rendering logic
- Actor references
- Blueprint logic

---

### Layer 2 — Adapter Layer

Bridges SimCore and Unreal.

Responsibilities:
- Convert Actor → SimID
- Provide WorldQuery interface
- Execute ActionIntent
- Sync transforms
- Feed perception data into SimCore

This layer is thin and replaceable.

---

### Layer 3 — Engine Layer (Unreal)

Responsible for:
- Rendering
- Physics
- Animation
- Navigation
- Editor tooling
- Input
- Interaction UI

It does not decide behavior.
It executes behavior.

---

## 3. Core Modules

### 3.1 Agent Module

Defines:
- AgentID
- AgentState
- TraitSet
- NeedState
- MemoryLog
- SkillSet
- OwnershipRecords

---

### 3.2 Need & Drive Module

Handles:
- Need decay
- Trait-modified thresholds
- Drive calculation
- Priority scoring

Outputs:
- Intent requests

---

### 3.3 Decision Engine

Takes:
- AgentState
- WorldSnapshot
- Drive scores

Produces:
- ActionIntent

No world mutation occurs here.
It only decides.

---

### 3.4 WorldState

Tracks:
- Regions
- Resource nodes
- Settlements
- Ownership
- Environmental state
- Global variables

WorldState must be serializable.

---

### 3.5 Resource System

Supports:
- Finite resource nodes
- Regeneration rules
- Depletion modeling
- Multi-lifetime resource consumption

Examples:
- Tree clusters
- Ore veins
- Wildlife populations
- Soil fertility

---

### 3.6 Economy Engine

Handles:
- Supply and demand
- Resource valuation
- Trade routes
- Production chains
- Wealth accumulation

Must operate without scripting.

---

### 3.7 Event Log

Records:
- Significant actions
- Ownership changes
- Resource changes
- Deaths
- Political events

Enables:
- History
- Memory systems
- Debug replay

---

## 4. Time Model

SimCore must operate independent of frame time.

### Time Layers:

- FrameTime (Engine)
- SimStep (0.5–5 sec per tick)
- WorldDay
- Season
- Year
- Generation

Simulation frequency may vary by:

- Agent proximity
- Importance
- Region activity level

---

## 5. Scalability Design

Supports:
- Agent LOD (High / Medium / Abstract)
- Region LOD
- Reduced update frequency
- Batched simulation

Agents off-screen may:
- Run simplified behavior
- Aggregate economic effects
- Skip detailed pathfinding

---

## 6. Determinism Strategy

To enable:
- Server authority
- Replay debugging
- Predictability

SimCore:
- Owns its own RNG
- Avoids floating-point chaos where possible
- Logs important transitions

---

## 7. Serialization Strategy

WorldState must:
- Serialize to binary or structured format
- Support partial region saving
- Support incremental updates

Persistence must scale beyond small worlds.

---

## 8. Guiding Rule

If SimCore cannot run headless without Unreal,
architecture has failed.cisions, or references -->