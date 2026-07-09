# LucentForge Stats & Magic Addendum v1

**Created:** 2026-07-08 | **Stage:** 4.0 | **Authority:** LucentForge Bible (Foundation v1 + this addendum)

---

## Purpose

This addendum defines the **attribute, magic, and affinity** doctrine for Stage 4 of the TheForge
Combine Arc. Stage 4 replaces the Stage 2 attribute *shim* with real attribute objects and stands up
the **Bits/Bytes magic system** (Foundation §6), giving magic a living, place-aware identity through
affinities. Cite this addendum alongside the Foundation when implementing any Stage 4+ attribute,
magic, or affinity feature.

Section numbering: §M1–§M9.

Stage 4 is scoped as a bounded **Foundation** layer. What is explicitly *deferred* is listed in §M9.
Do not build deferred systems without a new planning session.

---

## §M1 — Standing Rules for Stage 4

- **TheForge is reference-only.** TheForge's `.NET` patterns (`CoreAttribute` enum, `BitPool`/`BytePool`,
  §12.2 trap checks) get a reconciliation pass against **bible naming** and our **Python / SOLID /
  modular** structure before landing. Adapt intent, not idioms. See `lucentforge_terminology_map_v_1.md`.
- **The shim is the seam.** Per items addendum §A5, only `attribute_term()` and the inputs to
  `derive_stats()` change when real attributes land. All existing call sites remain valid.
- **Ripple filter.** The data model lives on *every* entity (player, NPC, goblin). Nothing is
  player-only at the model layer. Player casting is wired first; NPC/Hob autonomy is seeded, not built.
- **Never flatten `Mechanics/`.** Attributes → `entities/`; magic pools & casting → `combat/` +
  `entities/`; affinity field → `world/`; the Talent-emergence read → `biochem/`.

---

## §M2 — The Layered Character Model

Foundation §11 describes character data as layered: true attribute values run underneath, derived
combat values surface on top. Stage 4 makes this real.

> **Attributes (7, primary) → `derive_stats()` → Stats (derived, combat-facing).**

`Stats` (STR/MAG/LCK/DEF/RES/DEX) remains the combat-facing layer. It is now *derived from* attributes
instead of authored directly. The 7 bible attributes (§4.1) become real objects; only a subset carries
mechanics this stage.

| Attribute (§4.1) | Drives (this stage) | Status |
|---|---|---|
| Physique | `Stats.STR` | Wired |
| Reflexes | `Stats.DEX` | Wired |
| Luck | `Stats.LCK` | Wired |
| Intellect | `Stats.MAG` + **Byte** pool capacity | Wired (new) |
| Constitution | `Stats.DEF` | Wired (new) |
| Intuition | **Bit** pool capacity + §12.2 trap perception (§M8) | Wired (new) |
| Linguistic | — | **Inert** — defined, no mechanic until Stage 5+ |

**Shim contract update** (supersedes terminology_map §1 shim for Stage 4):
```
attribute_term(attributes, attribute) reads the real attribute value directly.
derive_stats() maps:
    Physique     → STR
    Reflexes     → DEX
    Luck         → LCK
    Intellect    → MAG            (+ Byte capacity, see §M3)
    Constitution → DEF
    Intuition    → (Bit capacity, trap perception — not a combat Stat)
    Linguistic   → (inert)
```
**RES is not attribute-derived this stage.** Today's data has DEF and RES independent per entity, and
RES (elemental resistance) belongs to the deferred §7 per-element resist model. It is carried as a
pass-through `resist` value on the entity (`Attributes.to_stats(resist=…)`) until §7 lands.

Attributes are authored per-entity in `entities.json` and are **static** this stage (no XP/growth —
progression is Stage 5+, §M9). Because nothing mutates them at runtime, they are **not persisted** and
need no migration — the factory rebuilds them from JSON on load. Persistence arrives with the mutable
affinity modifier layer (§M5, migration m0009).

---

## §M3 — Derived Resources: Bits and Bytes (Two Pools)

Foundation §5 lists Bits/Bytes as derived resources; §6 defines the magic system. Stage 4 splits the
Stage 2 bridge field `entity.mp` into **two independent pools**, `bits` and `bytes` (each with a max).
Persistence: migration **m0008**. The `RESTORE_MP` consumable splits into `RESTORE_BITS` /
`RESTORE_BYTES` (terminology_map §4.5).

**Both pools are always needed.** A caster is never purely one or the other.

| Pool | Nature (§6.2 / §6.3) | Capacity driver |
|---|---|---|
| **Bits** | Raw, primal, volatile magical energy. Fast, instinctive, less efficient. | **Intuition** |
| **Bytes** | Structured constructs formed from Bits. Stable, repeatable, complex. | **Intellect** |

**Universal pools, emergent Talent.** Every creature is born with an affinity (§M5) and has Bit/Byte
pools scaled by its attributes — a low-Intuition, low-Intellect brute simply has *tiny* pools.
**"Talent" is not a gate or a flag**; it is what we call a creature that rolls notably high innate
magical attributes/affinity strength. The goblin **Hob** is a goblin gifted this way. The biochem
`Brain` may later *read* gifted-ness to drive behavior — that read is seeded in §M9, not built here.

---

## §M4 — Bits/Bytes Casting Economy

Magic flows `Bits → Bytes → Pattern → Outcome` (§6.4). Two casting modes fall out of this, and map to
two archetypes:

- **Bit-spells** (druid-leaning) — cast *directly* from the Bit pool. Cheap, fast, instinctive, a
  little volatile. Lean on environmental affinity for power (§M6).
- **Byte-spells** (wizard-leaning) — cast from the Byte pool. Structured compositions of Bit-patterns:
  stronger, more reliable, more complex. Require Bytes to have been built and banked first.

Each spell is authored with `magic_kind: BIT | BYTE` (`abilities.json`) and costs from the matching
pool.

**Conversion & storage (§6.5, §6.6):**
- **Convert** turns Bits into Bytes. Reliable when out of combat; costs a turn under combat pressure.
- **Internal Byte storage** lets a caster bank Bytes for later. Built this stage.
- **Overburn / collapse** (interrupted or overloaded conversion causing backlash) is coded as a
  **present-but-disabled hook** — the code path exists; the risk is off this stage.
- **External focus storage** (a staff/tome/crystal holding Bytes so the caster doesn't have to) is
  **seeded only** (§M9). See §A6 (weapon resonance = attack-path; focus resonance = pool-path).

---

## §M5 — Affinity Axis

Reality is structured information; elements are patterns of it (§7). Stage 4 brings in the **affinity
axis** — the tag layer that makes Bits/Bytes feel alive — while leaving the heavy §7 emergent
pattern-physics (hybrid combination, elements-define-behavior) deferred (§M9).

**Six elements:** `EARTH, FIRE, AIR, WATER, VOID, LIGHT`.

- **Innate creature affinity.** Every creature is *born* with a **single** affinity (Chrono Cross–style
  innate color). Some affinities are rarer; some races/creature-types skew toward certain ones; the
  circumstances of birth/creation nudge the roll (birth-generation itself is deferred — affinities are
  authored per-entity this stage).
- **Affinity is mutable.** Stored as a **base innate value + a modifier layer** (mirroring `Traits` and
  the `Effect` system) so spells, events, curses, and blessings can temporarily or permanently add,
  remove, or change affinities. It is never a fixed immutable field.
- **Environment affinity.** Each region/room carries an affinity element + intensity
  (`RoomDefinition.affinity`, `affinity_intensity`), reusing the Stage 3 rooms/zone system. A saturated
  area amplifies like-affinity casting. Ties into the world-geography track. Persistence: migration
  **m0009**.

---

## §M6 — Affinity in Combat

Two-directional this stage (both the bonus *and* the penalty), unlike the minimal one-directional start:

- **Like-affinity amplification.** When the caster's affinity, the spell's element, and/or the current
  region's affinity align, casting is amplified (scaled by region `affinity_intensity`). This is where
  the druid archetype shines in a saturated zone.
- **Opposition matrix.** Opposing elements create weakness/resistance. The three pairs:

  | Pair | |
  |---|---|
  | FIRE | ↔ WATER |
  | EARTH | ↔ AIR |
  | LIGHT | ↔ VOID |

  Casting your opposite element is weakened; being struck by your opposite is worse.

Resolved in `damage_resolver.py`, reading the active room's affinity field.

---

## §M7 — Resonance Mechanism

Weapon `resonance` already exists (§A6, terminology_map §3.3) feeding `Stats.MAG` via `gear_mods`.
Stage 4 adds its *mechanism*:

> Resonance is a **multiplier on the structured (Byte-spell / MAG) outcome**: `final = raw × (1 + resonance/K)`.

- A high-resonance weapon is a **Byte caster's force multiplier**. It does **not** boost raw Bit-spells
  (those lean on affinity/environment instead).
- The formula is deliberately structured to accept a later **affinity-match / build gate** (the "fire
  sword rewards the fire battlemage specifically" idea) — a documented seam, same pattern as the
  disabled overburn hook. That build-identity layer is Stage 5+ (§M9).

---

## §M8 — Intuition → Trap Perception

With real Intuition (§M2), the §12.2 **perceive-trap** check finally functions (it was `= 0`, i.e.
impossible, under the Stage 2 shim — items addendum §A5).

- **Passive reveal on approach.** When an entity nears a trapped tile/container, an Intuition check runs
  automatically against the trap DC. On success the trap is revealed (highlight + HUD/log hint). No
  extra input — building Intuition means noticing more.
- Reuses the Stage 2 trap DC data and the `MECHANICAL` trap type. `MAGICAL` ward perception remains a
  later concern.

---

## §M9 — Deferred and Seeded (Stage 5+)

Captured here so the vision is canon, not chat memory. None of these are built this stage.

| Item | State | Notes |
|---|---|---|
| **Build identity / focus-channeling** | Seeded (§M7 seam) | Casters channel through foci (staff/rod/tome) to enhance casting; battlemages (Red Wizard / War Wizard / Artificer) "bring out" a weapon's magic. Needs the skills/abilities/build layer. |
| **External focus storage** | Seeded (§M4) | Focus resonance = pool-path (§A6); a focus banks Bytes externally. |
| **Overburn / collapse** | Hook disabled (§M4) | Flip on when combat-pressure risk is designed. |
| **§7 emergent pattern-physics** | Deferred (§M5) | Hybrid combination, elements-define-behavior, per-element resist matrix. |
| **Status-effect application** | Deferred | `StatusFlags` stub exists; poison/stun/etc. unapplied. |
| **Skills & ability progression** | Deferred | XP, learn-by-use, attribute/skill growth (§10). Attributes are static this stage. |
| **Birth-generation of affinity** | Deferred (§M5) | Runtime roll from race weights + birth conditions; authored per-entity for now. |
| **Talent read by the Brain** | Seeded (§M3) | `biochem/brain.py` may later read gifted-ness to drive behavior. |
| **World-death / durability decay** | Deferred | Traps still clamp to 1 HP. |

---

## Stage 4 Section Cross-Reference

| Concern | This addendum | Foundation | Terminology map |
|---|---|---|---|
| Attributes | §M2 | §4.1, §11 | §1 |
| Bits/Bytes pools | §M3, §M4 | §5, §6 | §2, §4.5 |
| Affinity | §M5, §M6 | §7 | (new §8) |
| Resonance | §M7 | §6.6 | §3.3, items §A6 |
| Trap perception | §M8 | §12.2 | §4.6, items §A5 |
