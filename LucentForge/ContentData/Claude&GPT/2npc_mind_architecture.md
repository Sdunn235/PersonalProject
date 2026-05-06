# NPC Mind Architecture

## Core Philosophy

NPCs are not scripted actors.

They are **state-driven agents** whose behavior emerges from:
- Internal drives
- Memory
- Environmental context
- Social influence

---

## Core Model Layers

### 1. Biochemical / Drive Layer

Inspired by Creatures (1996), but abstracted.

NPCs maintain internal variables such as:
- Hunger
- Thirst
- Fatigue
- Safety
- Social need
- Curiosity
- Aggression
- Comfort

These are NOT binary states.
They are continuous values that:
- Decay over time
- Increase based on actions
- Influence decision weighting

---

### 2. Interpretation Layer

The NPC evaluates:
- Current internal state
- Immediate environment
- Known memory references

Example:
"Hunger high + food known nearby = strong motivation to move"

---

### 3. Goal Formation

Goals are NOT pre-scripted.

They emerge from:
- Dominant drives
- Memory of solutions
- Environmental affordances

Example:
Goal: "Find food"
Derived from:
- Hunger threshold exceeded
- Previous success memory
- Visible or remembered food source

---

### 4. Decision Layer

NPC selects actions based on:
- Weighted drive urgency
- Known successful behaviors
- Risk evaluation

This is not random selection.
It is weighted and adaptive.

---

### 5. Execution Layer

Actions are performed through:
- Movement
- Interaction
- Social behavior

---

## Learning & Adaptation

NPCs adapt through:
- Reinforcement of successful actions
- Memory of failure
- Environmental feedback

No hard-coded learning trees.

---

## Creatures (1996) Influence

Inspired by:
- Internal chemistry driving behavior
- Emergent outcomes

We diverge by:
- Avoiding over-complex biochemistry
- Using modular, scalable systems
- Supporting large populations (not individual pet-level simulation)

---

## Connection to Current Prototype

The PyGame prototype:
- Represents early Drive Layer
- Simplifies Interpretation and Decision layers
- Lacks deep memory integration

It is a proof-of-concept, not the final architecture.

---

## Non-Negotiable Rule

NPC behavior must emerge from internal state.

If behavior is externally scripted without internal cause,
it violates the system.