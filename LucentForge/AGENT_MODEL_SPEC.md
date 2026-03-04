# Agent Model Specification
Lucent Forge

---

## 1. Philosophy

Agents are not NPCs.

Agents are world participants governed by the same systemic rules as players.

They differ only in input origin (AI vs human).

---

## 2. Agent Structure

Each Agent contains:

- AgentID
- TraitSet
- NeedState
- SkillSet
- MemoryLog
- SocialGraph
- Inventory
- Wealth
- Ownership
- CurrentIntent
- Role (Optional)

---

## 3. Traits

Traits are stable modifiers.

Examples:

- Aggression
- Boldness
- Curiosity
- Greed
- Sociability
- Loyalty
- Patience
- RiskTolerance

Traits influence:

- Need tolerance
- Decision weighting
- Fear response
- Economic behavior
- Social behavior

Traits do NOT directly cause actions.
They modify scoring.

---

## 4. Needs

Needs are dynamic meters.

Examples:

- Hunger
- Thirst
- Sleep
- Safety
- Social
- Wealth
- Power
- Curiosity

Each need:

- Decays over time
- Has urgency threshold
- Has critical threshold
- Is trait-modified

---

## 5. Drives

Drive = f(NeedState, TraitModifiers, WorldContext)

Drive produces:
- Priority score

Highest drive wins unless overridden by safety logic.

---

## 6. Memory System

Memory records:

- Events
- Relationships
- Trauma
- Success
- Trade history

Memory affects:

- Trust
- Fear
- Loyalty
- Decision weighting

---

## 7. Social Graph

Tracks:

- Relationships
- Faction alignment
- Reputation
- Debt
- Oaths

Agents respond differently based on social ties.

---

## 8. Skill System

Skills represent:

- Combat ability
- Crafting ability
- Leadership
- Farming
- Mining
- Trade efficiency

Skills influence:

- Success probability
- Output efficiency
- Economic power

---

## 9. Action Intent

ActionIntent contains:

- ActionType
- TargetID
- Location
- NeedContext
- Priority

Intent execution is handled by the engine layer.

---

## 10. Generational Inheritance

Future system:

- Traits may partially inherit
- Wealth transfers
- Land transfers
- Cultural shifts

Agents are not isolated.
They are part of time.