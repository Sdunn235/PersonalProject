# LucentForge Needs / Wants / Drives Addendum v1

**Created:** 2026-07-24 | **Authority:** Supplements Foundation §9 and §13

---

## Purpose

The Foundation §9 Needs Model already defines the three-tier structure (Tier 1 Survival → Tier 2
Stability → Tier 3 Aspirational). This addendum extends that doctrine into the **biochem and drive
implementation layer** built during the Affinity Behavioral Arc (C0040–C0047), so the code knows
what §9 intends and §9 knows what the code can carry.

Cite this addendum alongside the Foundation when implementing any new drive, want, or need-layer
interaction.

---

## §W1 — Tiers as Implemented (Reference §9)

The Foundation §9 tiers are canonical. This section gives them implementation names.

### Tier 1 — Survival Needs (coded, active)

| Need | Chemical | HP/SP/BP Link |
|---|---|---|
| Hunger | `hunger_chem` | `hp` drains when `hunger` hits zero |
| Thirst | `thirst_chem` | `hp` + `sp` drain when `thirst` hits zero |
| Sleep / Energy | `tiredness` | `sp` drains; cognitive drives (Tier 3) locked when critical |

**Survival floor:** HP, SP, and (for some entities) BP are the ultimate survival metrics Tier 1 needs
protect. When Tier 1 needs go unmet long enough, these pools drain. When they hit zero, the entity
dies or collapses. Everything else is downstream of this floor.

### Tier 2 — Stability Needs (designed, not yet coded)

Shelter / Safety, Income / Resource Access, Routine, Social Belonging. These needs exist in §9 and
will eventually have their own drives and chemicals. They are not implemented yet.

### Tier 3 — Aspirational Wants (designed, not yet coded)

Power, Status, Wealth, Knowledge, Purpose, Legacy — and a parallel set of **destructive compulsions**
(substances, addiction, violence/murder, sex, specific social dominance patterns) that can emerge when
survival needs are met and personality permits. These are **wants**, not needs. They are implemented
exactly the same way as drives with lower base_weight, but they carry risk of self-harm (see §W4).

---

## §W2 — Maslow Emergence Rule

> As survival pressure decreases, more complex behavior emerges. (Foundation §9.2)

Implementation corollary: **a Tier 2 or Tier 3 drive's urgency is suppressed when Tier 1 needs
are in the CRITICAL or WARNING zone.**

The drive architecture already supports this. `Drive.compute_urgency()` reads a chemical level and
applies a fearfulness-weighted multiplier. Tier 1 need chemicals (`hunger_chem`, `thirst_chem`,
`tiredness`) naturally spike first when physical resources are low — these commands cognitive
attention before Tier 2 and 3 drives can compete.

**Implementation path when adding Tier 2/3 drives:**
- Give each want a low `base_weight` (e.g., 0.15–0.35 for Tier 2; 0.05–0.20 for Tier 3)
- Give each want a slow-building chemical (low gain rate, like `affinity_strain`)
- Let the urgency formula suppress them naturally when Tier 1 chemicals dominate
- No explicit gating needed — it emerges from the weight arithmetic

---

## §W3 — Self-Destructive Wants

Some Tier 3 wants can harm the entity's own Tier 1 survival floor. Examples: addiction to a
substance that drains HP/SP over time, compulsive violence that creates threat exposure, wealth
accumulation that ignores thirst. The want's drive has real urgency; satisfying it may harm or kill
the entity.

**This is intentional.** It is how living systems behave. An entity with high enough want-urgency
will act to satisfy the want even against survival interest. The tension is the simulation.

**Implementation rule:** wants that have self-destructive effects should call `Chemicals.tick()`
side-effects (HP drain, SP drain, stress injection) as part of their satisfaction or sustained-
hold path, just as sustained hostile-affinity exposure builds `affinity_strain`. The entity doesn't
"know" it's being harmed — it only sees the want chemistry pulling.

---

## §W4 — HP / SP / BP as the Survival Floor

The three vital pools are the owned ground. Everything else floats above them.

| Pool | Owners | What drains it |
|---|---|---|
| `hp` | All entities | Unmet hunger/thirst, damage, self-destructive want effects |
| `sp` | All entities | Unmet sleep/energy, sustained exertion, stress-driven drain (future) |
| `bp` | Some entities (Hobs, dragons) | Magic expenditure, spiritual stress (future) |

These are **not** biochemical chemicals. They are hard resources with their own drain rules.
When they hit zero: death, collapse, or unconsciousness depending on entity type.

The wants and drives operate above this floor. Any want whose satisfaction path happens to drain a
vital pool is a self-destructive want (§W3).

---

## §W5 — Implementation Sequence (Recommended)

The existing architecture (Brain → Chemicals → Drives → Drive.compute_urgency) can carry Tier 2
and 3 wants without structural change. The recommended sequence for adding new wants:

1. **Add the chemical** in `Mechanics/biochem/chemical.py` `__init__()` (slow-building)
2. **Add the emitter or trigger** that pushes the chemical toward a target (needs satisfaction,
   world event, proximity, etc.)
3. **Register a Drive** in `Mechanics/biochem/brain.py` with appropriate `base_weight` and
   `need_id` pointing at the new chemical
4. **Wire the satisfaction behavior** in the AI state that would fulfill it
5. **Test parity** — new drive at 0 chemical level → behavior byte-identical to before

The brain already iterates all drives and computes urgency. A new want is just a new citizen in
the same ecosystem.

---

## §W6 — Relationship to Affinity Strain

`affinity_strain` (§B7 of the Biochem Affinity Addendum) demonstrates the full pattern at small
scale: a slow-building chemical that does not directly need anything but modifies how urgently the
brain perceives existing needs. This is precisely the mechanism that would power many Tier 2/3
wants — not fast demands like thirst, but slow-building pressure that gradually shifts what the
brain prioritizes.

The same `_approach()` emitter pattern, the same `Chemicals.tick()` boost path, the same
`Drive.compute_urgency()` receptor — wants are instances of the same infrastructure, not a new
system.

---

## §W7 — Open Design (Not Yet Scoped)

The following are **designed but not scheduled** for implementation. Write them here so they
aren't lost; implement when the next planning session scopes a behavioral arc.

- Tier 2: **Social Belonging want** — NPCs near familiar entities accumulate a belonging-comfort
  chemical; far from all known entities, they accumulate a loneliness chemical that elevates Tier 1
  need urgency (same shape as `affinity_strain`). Gobby is the design test case.
- Tier 3: **Knowledge want** — exposure to new objects, regions, or entity subtypes builds a
  curiosity chemical; satisfaction = successful exploration or imitation. Base weight varies by
  `curiosity` trait value.
- Tier 3: **Power want** — wanting to control or defeat other agents; satisfaction = successful
  combat or intimidation outcome; base weight driven by `aggression` trait. Side effect: threat
  exposure → stress spike (self-destructive under the wrong odds).
- Self-destructive compulsion example: **substance addiction** — a consumable or region provides
  a high-gain comfort/euphoria chemical but drains HP/SP over time; want drive builds on exposure
  history. Entities with high `fearfulness` + low `resilience` are more susceptible.
