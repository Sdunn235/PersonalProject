# Heartbeat Arc — Bible Convergence Vision

## What This Is
Analysis of how the three bible documents (Simulation Foundation, Sim Core Schema, Micro Simulation v1) merge with the existing LucentForge PyGame prototype. Written 2026-04-06 after deep read of all bible content and full codebase exploration.

This is the **reference document** for the Heartbeat arc. Individual phases each get their own plan.

---

## The Core Insight

The PyGame prototype (11 sessions, ~9,700 lines) is the **body**: renderer, combat, player movement, entity systems, needs, biochem, AI state machine, data-driven architecture, pathfinding.

The bible describes the **heart**: world-level simulation, settlement pressure, resource economy, threat escalation, personality emergence, event lifecycles.

These aren't competing designs. They're complementary layers. The body is waiting for the heart.

---

## Alignment Map

| Bible Concept | Existing Implementation | Gap |
|---|---|---|
| NPC with needs, traits, skills, memory | Entity + Traits + Needs + Biochem + AI states | Memory is minimal (last_action + bias only) |
| Trait-driven personality | 4 traits (curiosity, aggression, fearfulness, sociability) | Bible wants 5-9 axes + drift over time |
| Needs (hunger, energy) | 3-zone needs (hunger, thirst, sleep) with health drain | We have MORE than bible v1 asks for |
| Decision loop (evaluate → goal → action → resolve → interpret → memory) | State machine (idle → moving → satisfying) | Missing: interpret result, update memory, trait shift |
| Grid map with regions | 18×18 tile grid with obstacles, need sources | Missing: river barrier, region tagging, wild/civilized sides |
| Skills modify outcomes | Combat skills (STR, MAG, DEX, DEF) + abilities | Missing: gathering, survival as standalone skills |
| Data-driven content | Full JSON + DAO pattern | Bible fits perfectly into this |
| Simulation tick loop | Frame-based dt updates | Need proper tick abstraction |

---

## What the Bible Adds

1. **World-Level Orchestration** — Town, ResourceState, GoblinThreat, SimulationClock. The layer that makes individual behavior matter at scale.
2. **Interpretation + Drift Loop** — NPCs interpret outcomes through traits and shift over time. Personality earned through lived experience.
3. **Event Escalation Model** — Trigger → Growth → Pressure → Response → Outcome. Narrative arc without scripting.
4. **Variable Fidelity** — Persistent truth, variable detail. Key to scaling from 5 NPCs to 500.
5. **Bits/Bytes Magic** — Deferred for v1, but the most daring piece. Magic as simulation property of reality.

---

## The Dream

A day in the simulation:

- **Dawn**: SimulationClock advances. Farm produces food into ResourceState. Alder's gathering skill adds bonus.
- **Morning**: Grom patrols toward the river (discipline + low fear). Elara wanders toward the forest (curiosity).
- **Midday**: Food dips because not enough NPCs gathering. Town shifts STABLE → STRAINED.
- **Afternoon**: GoblinThreat triggers a raid. Gruk crosses the river. Nobody's defending. Sylva at the farm must choose: fight or flee.
- **Evening**: Food critical. Town shifts to COLLAPSING. NPCs either mount emergent defense... or don't.

Not one outcome — *different, explainable, non-scripted outcomes* from the same starting conditions.

---

## Heartbeat Arc Phases

| Phase | Name | Core Question |
|-------|------|---------------|
| Heartbeat-1 | World Orchestration | Can we add Town, ResourceState, GoblinThreat, SimulationClock as live objects? |
| Heartbeat-2 | Map Enhancement | Can we zone the grid into civilized/wild with a river barrier? |
| Heartbeat-3 | NPC Decision Loop | Can NPCs interpret outcomes and drift over time? |
| Heartbeat-4 | Goblin Behavior | Can goblins wake up as a pressure system? |
| Heartbeat-5 | Resource Economy | Can food production/consumption create real strain? |
| Heartbeat-6 | Observation Layer | Can we log and prove emergence? |

---

## What We Defer (Bible Agrees)

- Full magic system (Bits/Bytes)
- Full economy (just food for now)
- Complex inventory
- Deep memory (minimal first)
- Social systems / factions
- Advanced UI
- Multiplayer

---

## Success Criteria

1. A town can survive or collapse without player input
2. NPCs behave differently under similar conditions
3. A goblin threat escalates naturally over time
4. World changes feel explainable and non-scripted

---

## The Bigger Picture

If 5-10 NPCs on an 18×18 grid can produce believable, divergent, non-scripted outcomes through structured interaction — then the foundation holds. And if the foundation holds, everything in the Simulation Foundation document becomes buildable. The SimCore C++ engine is waiting for these same concepts. What we prove in PyGame translates directly.
