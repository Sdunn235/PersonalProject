# Lucent Forge Simulation Foundation v1

## Purpose
This document defines the current foundational design for Lucent Forge as a readable, engine-minded system reference. It is intended to be understandable by a human collaborator and structured enough to hand to an IDE agent later for implementation planning.

This is not a final game design document and not a code specification. It is the core simulation philosophy and system architecture for the first buildable layer of Lucent Forge.

---

# 1. Project Direction

Lucent Forge is not being designed as a traditional game-first RPG. It is being designed as a persistent simulation world that can be inhabited by players and shaped by autonomous agents. The immediate practical goal is to build it under current technical limits as a simulation-first game framework. The long-term vision is to create a world where agents can develop persistent identity, continuity, and emergent behavior through memory, consequence, and environmental pressure.

The game is the usable shell. The simulation is the deeper substrate.

---

# 2. Core Design Philosophy

## 2.1 Easy to Learn, Difficult to Master
Lucent Forge should be approachable at the surface level while hiding deep systemic interaction underneath. Mastery comes from learning how hidden systems behave, not from memorizing arbitrary complexity.

## 2.2 Simple Verbs, Complex Consequences
The world should be driven by simple actions such as moving, speaking, attacking, casting, crafting, resting, observing, and using tools. Depth emerges from context, character state, skill, environment, timing, memory, and consequences.

## 2.3 The World Does Not Revolve Around the Player
Players are not the center of reality. They are one force among many. NPCs, factions, environments, and events continue evolving whether or not a player is present.

## 2.4 Persistent Truth, Variable Detail
Everything important exists continuously, but not everything is simulated with the same level of detail at all times.

All entities maintain persistent state.
Simulation fidelity changes based on relevance, proximity, and importance.

## 2.5 Context Over Universal Balance
No build, role, or strategy is universally dominant. Effectiveness is contextual. Specialization increases advantage windows, while generalization increases flexibility.

---

# 3. Character Philosophy

## 3.1 What Defines a Character
A character is not defined by a class label or single personality tag. A character is defined by the interaction of:

- Core attributes
- Needs and wants
- Skills and abilities
- Traits
- Memory
- Environment
- Social position
- Lived outcomes

## 3.2 Character Growth Philosophy
Characters should not be able to naturally maximize all paths. Growth in one direction should usually create cost, tradeoff, or opportunity loss elsewhere.

## 3.3 Specialization vs Generalization
- Generalists survive broadly and adapt more easily.
- Specialists excel strongly within narrower conditions.
- Related skills transfer partially, but true mastery requires direct experience.
- Resource efficiency is a major expression of mastery.

---

# 4. Core Attributes

The current foundational stat set is:

- Physique
- Reflexes
- Constitution
- Intellect
- Intuition
- Linguistic
- Luck

## 4.1 Attribute Intent

### Physique
Raw bodily output: carrying, lifting, melee force, physical labor, draw strength, physical momentum.

### Reflexes
Speed of response: timing, dodge windows, recovery speed, attack cadence, reaction control.

### Constitution
Durability and internal stability: regen, fatigue tolerance, poison resistance, sustained effort, pain tolerance, physical resilience.

### Intellect
Deliberate understanding and stored knowledge: theory, memory of formal systems, planned problem solving, spell complexity.

### Intuition
Instinctive pattern recognition: practical judgment, danger sense, social reading, trap recognition, fast inference.

### Linguistic
Meaning-making and communication: persuasion, deception, translation, rhetoric, emotional framing, instruction.

### Luck
Probability pressure at margins, rare outcomes, edge-case influence, discovery, and pivotal moments. Luck should not become a universal power stat.

---

# 5. Derived Resources

Current core derived resources:

- Health
- Stamina
- Bits / Bytes

These are not primary attributes. They are system states influenced by attributes, conditions, skills, and environment.

---

# 6. Bits and Bytes Magic System

## 6.1 Core Law
Magic in Lucent Forge is not just flavored mana. Reality is treated as structured and alterable through informational patterns.

## 6.2 Bits
Bits are raw magical energy.
They are volatile, unstructured, and less efficient.
They may exist naturally in the world.
They can be used directly for unstable, instinctive, or quick magic.

## 6.3 Bytes
Bytes are structured magical constructs formed from Bits.
They are more stable, repeatable, and suitable for controlled or complex spellcasting.

## 6.4 Magic Flow
Magic can be understood as:

Bits -> Bytes -> Pattern -> Outcome

A caster may:
- use Bits directly
- convert Bits into Bytes before use
- hold stored Bytes internally or externally

## 6.5 Conversion
Bits can be converted into Bytes:
- safely outside combat
- riskily under pressure in combat or unstable conditions

Interrupted or overloaded conversion may cause overburn, instability, or spell collapse.

## 6.6 Storage
Characters may store Bytes:
- internally through their own magical capacity
- externally through arcane focuses

Arcane focuses act like structured magical storage and may expand or specialize capacity.

## 6.7 Environment
Some locations contain elevated ambient Bits and/or pattern bias. These areas affect recovery, casting behavior, and magical disciplines differently.

---

# 7. Elemental Pattern Model

Traditional elements exist in Lucent Forge, but not as primitive magical substances. They are emergent patterns of structured magic.

Examples:
- Fire = energetic dispersal pattern
- Water = continuity and flow pattern
- Earth = density and stability pattern
- Air = motion and propagation pattern
- Light = coherence and ordered structure
- Void / Darkness = collapse, entropy, corruption, silence, absence of structure

Elements define how magic behaves rather than what magic fundamentally is.

Hybrid effects are formed through combined patterns rather than needing separate foundational elements for every blend.

---

# 8. Traits and Personality Formation

## 8.1 Core Philosophy
Characters are defined by interacting traits, not by fixed personality types.
Personality labels are descriptive interpretations, not hard-coded rules.

Traits -> Interactions -> Behavior Patterns -> Perceived Personality

## 8.2 Trait Model
The system should begin with a manageable number of trait axes rather than a giant list of disconnected tags.

Possible early axes include:
- Risk aversion <-> risk seeking
- Order <-> chaos
- Attachment <-> detachment
- Control <-> acceptance
- Fear sensitivity <-> fear resistance
- Compulsion <-> restraint
- Greed <-> contentment
- Trust <-> suspicion
- Curiosity <-> apathy

## 8.3 Personality Emergence
Recognizable personality types such as hoarder, hypochondriac, germaphobe, zealot, coward, or visionary should emerge from trait combinations and life history.

Similar trait profiles may overlap, but different combinations, emphasis, and memory weighting create distinct identities.

---

# 9. Needs Model

## 9.1 Tiered Needs
Needs are context-dependent and evolve with environment and civilization.

### Tier 1: Survival Needs
- Hunger
- Thirst
- Sleep

### Tier 2: Stability Needs
- Shelter / safety
- Income / access to resources
- Routine
- Social belonging

### Tier 3: Aspirational Needs
- Power
- Status
- Wealth
- Knowledge
- Purpose
- Legacy

## 9.2 Core Law
Survival needs always exist, but in advanced societies they may be partially outsourced to infrastructure, trade, and institutions.
As survival pressure decreases, more complex behavior emerges.

---

# 10. Skills and Abilities

## 10.1 Skills
Skills represent learned competence developed through repetition, training, or teaching.
They modify efficiency, precision, and reliability.
They are narrower than attributes and broader than named techniques.

## 10.2 Abilities
Abilities are unlocked techniques, breakthroughs, maneuvers, or special expressions that emerge from combinations of:
- skill thresholds
- attribute thresholds
- conditions
- equipment
- events or experiences

Abilities should not all be pretreated as simple level rewards. Many should emerge from use, specialization, and circumstance.

---

# 11. Character Information Layers

Character data should be layered in visibility.
The system may always run in full underneath, while the player sees only what is relevant, knowable, or learned.

## 11.1 Layer 1: Surface
Immediate information for readability:
- health
- stamina
- Bits / simplified magic state
- basic visible conditions
- broad stat impressions

## 11.2 Layer 2: Intermediate
Character growth and build identity:
- true attribute values
- skills
- resource rates
- equipment influence
- visible tendencies or partial traits

## 11.3 Layer 3: Deep Layer
Underlying simulation truth:
- full trait web
- needs and wants weighting
- memory
- decision biases
- conversion efficiency
- adaptation resistance
- hidden modifiers

Mastery comes from learning how the deeper layers behave, not from forcing all players to micromanage them.

---

# 12. Outcome Resolution Philosophy

## 12.1 Core Law
Lucent Forge uses hybrid outcome resolution.
The world follows predictable rules, but uncertainty exists at the margins.

## 12.2 Outcome Model
Outcomes are shaped by:
- action or ability base value
- skill influence
- attribute modifiers
- context factors
- difficulty threshold
- variance layer

Variance should affect close outcomes, edge cases, and uncertain conditions, but should not completely override overwhelming advantage.

## 12.3 Design Intent
This allows:
- consistency
- mastery
- suspense
- contextual surprise

---

# 13. NPC Identity and Decision Loop

## 13.1 Core Loop
Update State -> Evaluate Pressures -> Select Goal -> Choose Action -> Resolve Outcome -> Interpret Result -> Update Memory -> Reinforce or Shift Traits

## 13.2 Step Breakdown

### Update State
Refresh the character's current truth:
- needs
- resources
- location
- time
- environment
- ongoing conditions

### Evaluate Pressures
Assess what is pushing on the character:
- needs
- wants
- threats
- social obligations
- opportunities

### Select Goal
Choose the current objective.
Examples: find food, gain wealth, escape, seek revenge, protect another.

### Choose Action
Determine how to pursue the goal based on skills, resources, habits, and personality.

### Resolve Outcome
Use the action resolution framework.

### Interpret Result
The character filters the outcome through traits, stress, memory, and worldview.
This is what allows two characters to react differently to the same event.

### Update Memory
Store what happened, where, with whom, and how it mattered.

### Reinforce or Shift Traits
Characters may adapt, resist change, deepen habits, or transform over time.

## 13.3 Failure Philosophy
Characters do not respond to failure uniformly.
Some adapt.
Some stay trapped.
Some reinforce harmful patterns.
Some change only under sufficient pressure.

---

# 14. World Simulation Philosophy

## 14.1 Persistent Truth, Variable Fidelity
All meaningful entities maintain state at all times.
Simulation detail scales based on proximity, importance, and relevance.

## 14.2 Event Escalation Model
The world evolves through local conditions that may escalate if ignored or reinforced.

Event lifecycle:
Trigger -> Growth -> Pressure -> Response -> Outcome

## 14.3 Event Scales

### Local Events
Small, frequent, contained.
Examples: goblin raids, crop blight, minor illness.

### Regional Events
Escalated conditions affecting multiple settlements or systems.
Examples: town collapse, trade disruption, river poisoning.

### Systemic Events
Rare, large-scale disruptions that reshape regions or nations.
Examples: major faction threat, environmental collapse, war.

## 14.4 Core Law
Most changes begin locally.
Sustained neglect, reinforcement, or compounding conditions allow escalation.
Most events remain contained unless pressure accumulates beyond thresholds.

---

# 15. Economy and Social Complexity

Economy should emerge from need, production, exchange, and specialization rather than exist as a disconnected game menu.

Basic prototype model:
- production
- consumption
- shortage or surplus
- response

As survival pressure lowers, social complexity increases:
- specialized labor
- trade dependency
- institutional roles
- politics
- ambition-driven behavior

---

# 16. Prototype Direction: Sim Core First

Lucent Forge should begin as a simulation-first prototype, not a full game.

## 16.1 Recommended Path

### Phase 1: Python Simulation Core
Prove the invisible heart of the world.
Focus on:
- one small map
- one town
- one nearby threat
- 5 to 10 NPCs
- tiered needs
- traits
- identity loop
- simple event escalation
- simplified economy/resource logic

### Phase 2: Python Proof of Emergence
Expand just enough to test divergence and long-term consequence.
Add:
- memory updates
- adaptation vs stagnation
- role drift
- one magic-using NPC or advanced event chain

### Phase 3: Engine Translation Layer
Define the data structures and simulation schema before visual embodiment.
This protects the design from being trapped inside one engine.

### Phase 4: Embodiment in Unreal or another future engine
Expose the living simulation through a playable world.

---

# 17. Immediate Deliverable Goal

The next concrete build target should be:

## Lucent Forge Micro Simulation v1

This should answer one question:

Can a small world with a few NPCs, needs, traits, memory, and one escalating local threat produce believable change over time without the player being required to drive everything?

---

# 18. Sections Still Open for Future Expansion

The following sections are not missing, but intentionally deferred until later design passes:

- exact formulas and tuning values
- trait list v2+
- full memory schema
- full itemization and crafting design
- detailed social systems and faction law
- exact combat flow model
- exact UI implementation
- multiplayer/server sync logic
- external advanced AI integration layer

These should be treated as later layers built on top of this foundation, not prerequisites for the first prototype.

---

# 19. Closing Statement

Lucent Forge is being built as a simulation substrate where identity, consequence, and systemic change can emerge through persistent state, memory, pressure, and interaction.

The first responsibility is not to prove digital life.
It is to build a world structure where life-like agency can plausibly emerge.

That begins with a small, honest prototype that works.

