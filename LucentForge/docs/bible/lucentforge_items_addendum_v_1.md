# LucentForge Items Bible Addendum v1

**Created:** 2026-07-05 | **Stage:** 2.0 | **Authority:** LucentForge Bible (Foundation v1)

This document extends the LucentForge Simulation Foundation with Stage 2 item doctrine.
The Foundation (§18) defers full itemization intentionally. This addendum works ahead of the
bible, establishing the behavioral rules that implementation phases 2.1–2.8 will execute.

All section numbers prefixed §A are addendum sections. References to §2.2, §4.1, §6.6, §10.2,
§12.2, §15, §18 cite the Foundation directly.

Cross-reference: `lucentforge_terminology_map_v_1.md` (naming authority for all item fields,
enums, and bridge terms used here).

---

## §A1 — Items as Capability Grants

*Foundation references: §2.2 (simulation verbs), §10.2 (equipment as threshold condition)*

An item is not an inventory entry. It is a simulation verb — a change to what a character can do
or what the world can become.

- **Equipping** a weapon: the character can now deal weapon damage (§10.2 threshold satisfied).
- **Equipping** armor: the character's defense rating increases; threshold for physical vulnerability shifts.
- **Using** a consumable: a resource is immediately modified (HP, stamina, magic pool).
- **Carrying** a key: the character can now unlock matching locks (capability not available before).
- **Taking** from a chest: item transitions from world-state to character-state.

These are the four verbs Stage 2 implements. All other item interactions (crafting, dropping on
floor, loot from dead, trading) are out of scope. See §A8.

**Implication for UI:** Every item interaction should resolve to one of these four outcomes. A
menu option that does not resolve to equip/use/take/key-use is out of scope for Stage 2.

**§10.2 equipment threshold model:**
Equipment modifies the character's capability envelope, not their base stat sheet. A character
without a sword is unarmed; with a sword, they can swing it. The sword's `attack_power` is a
modifier contribution, not a replacement for the entity's base stat — the outcome resolver
(§12.2) combines them. Unequipping removes the contribution; the base stat remains.

---

## §A2 — Carrying as Bodily Budget

*Foundation references: §4.1 (Physique — carrying and lifting as bodily function)*

Carrying capacity is a bodily resource bounded by Physique (§4.1). Stage 2 uses the attribute
shim (§A5): Physique → STR.

**Carry capacity formula:**
```
carry_capacity = CARRY_BASE + 2 × stat.STR
CARRY_BASE     = 20  (weight units)
```
This formula is the Stage 2 shim. When Stage 4 introduces real Physique attribute objects,
only the `attribute_term(Physique)` call changes — the formula structure remains.

**What counts toward capacity:**
Both inventory (bag items) and equipped items count toward carry capacity. An item worn on the
body is still being carried. Removing an item from the bag and equipping it does not change
the weight budget — the item's weight is always in effect when on the character.

**Over-capacity behavior:**
- Attempting to take an item that would exceed capacity: blocked with UI feedback.
- Attempting to equip an item that would exceed capacity: blocked with UI feedback.
- Current equipment is never force-dropped when a stat changes (Physique does not change
  dynamically in Stage 2; this edge case does not exist yet).

**Drop action:**
Drop is out of scope for Stage 2 — the UI will grey the option. If the player is at capacity,
the UI informs them; the solution is to leave items in the chest, not to drop from inventory.
This avoids the "items on the world floor" system (§A8) before Stage 3 is planned.

**Design intent (§4.1):**
Encumbrance should pressure decisions, not strand characters. The player can always choose not
to take something. The system creates meaningful tradeoffs: which items are worth carrying?
It does not punish players by making them helpless.

---

## §A3 — Slot Doctrine

*Foundation references: §10.2 (equipment as threshold condition — requires a slot system)*

LucentForge's slot system is based on TheForge's `SlotType` [Flags] design, extended with
hand-slot support for dual-wield.

### SlotType (equipment assignment flags)

Python `enum.Flag` — bitwise combinable. One flag per physical position.

| Flag | Bit | Meaning |
|---|---|---|
| `MAIN_HAND` | 1 | Dominant hand — weapons, primary tools |
| `OFF_HAND` | 2 | Support hand — shields, off-hand weapons |
| `HEAD` | 4 | Head — helmets, hats |
| `CHEST` | 8 | Chest — breastplates, robes |
| `LEGS` | 16 | Legs — greaves, trousers |
| `FEET` | 32 | Feet — boots, sandals |
| `HANDS` | 64 | Hands — gauntlets (body armor on both hands, not held) |
| `ANY_HAND` | 3 | `MAIN_HAND \| OFF_HAND` — held items eligible for either hand |

### EquipmentSet invariant

At most one item per single-bit slot. A character has exactly one MAIN_HAND, one OFF_HAND,
one HEAD, one CHEST, one LEGS, one FEET, one HANDS position.

### eligible_slots rules by item type

| Item class | eligible_slots | body_slot stored? |
|---|---|---|
| Weapon | `ANY_HAND` (MAIN_HAND \| OFF_HAND) | `MAIN_HAND` |
| Shield | `ANY_HAND` (MAIN_HAND \| OFF_HAND) | `OFF_HAND` |
| Armor (head) | `HEAD` | `HEAD` |
| Armor (chest) | `CHEST` | `CHEST` |
| Armor (legs) | `LEGS` | `LEGS` |
| Armor (feet) | `FEET` | `FEET` |
| Armor (hands) | `HANDS` | `HANDS` |

`eligible_slots` is computed from item class and `body_slot`; it is not stored in the item row.

### pick_slot_for algorithm

```
pick_slot_for(item, equipment_set):
    if eligible_slots == ANY_HAND:
        if OFF_HAND slot is free: return OFF_HAND
        if MAIN_HAND slot is free: return MAIN_HAND
        return None  (both occupied — displacing needed)
    else:
        slot = eligible_slots  (single bit)
        return slot  (always the designated slot; displace if occupied)
```

Preference: for ANY_HAND items, prefer OFF_HAND first. Shields naturally settle in the off-hand.
A weapon being equipped also prefers OFF_HAND — the player may override by equipping to a
specific slot via UI (Phase 2.5 refinement; Phase 2.1 uses auto-assign).

### Displacing

When equipping to an occupied slot, the currently equipped item is automatically returned to
inventory (bag). If the bag would overflow capacity after the swap, the equip is blocked —
report "Not enough carry capacity to swap."

### Dual-wield legality

Dual-wield is legal: weapon in MAIN_HAND and weapon in OFF_HAND, shield in both hands, or any
mixed combination. The slot system does not impose class-based restrictions. Future combat
phases may add penalties or requirements (e.g., Reflexes threshold for effective dual-wield)
but Stage 2 imposes none — equip is allowed.

### Gauntlet distinction

`SlotType.HANDS` (bit 64) is body armor covering both hands simultaneously — gauntlets, gloves.
It is NOT a held item. It is distinct from MAIN_HAND and OFF_HAND. Equipping gauntlets does
not occupy a hand slot; it occupies the HANDS body armor slot.

### TrapType [Flags]

Stage 2 defines all four TrapType values for forward-compatibility; only MECHANICAL is active.

| Flag | Bit | Stage 2 status |
|---|---|---|
| `NONE` | 0 | No trap |
| `MECHANICAL` | 1 | Spring/dart/spike mechanism. **Active in Stage 2.** Triggered on open/fail. Disarmed via Reflexes (DEX) check (§12.2, §A5). |
| `MAGICAL` | 2 | Arcane ward. **Future only** — Intuition check deferred Stage 3/4. |
| `POISON` | 4 | Damage-over-time on trigger. **Future only.** |
| `ELECTRIC` | 8 | Paralysis on trigger. **Future only.** |

Trap damage in Stage 2 clamps to 1 HP minimum (so the player cannot die from a trap) and logs
the event. This is a deliberate scope guard — it explicitly prevents the "world death opens
loot / EXP arc" before that arc is planned (see §A8).

---

## §A4 — Containers as World Memory

*Foundation references: §2.2 (simulation as persistent emergent state), §10.2 (equipment threshold)*

Containers (chests) are persistent world state. They remember:

- Whether they have been opened.
- Whether they are locked and whether the lock has been picked or unlocked.
- Whether they are trapped and whether the trap has been disarmed.
- Which items they currently contain.

This state persists per save slot and is not reset by room transitions.

**Stage 2 scope:** Chests are the only source of items entering the game world. Items do not
drop from defeated enemies (§A8). Items do not spawn on the world floor. Every item in the game
came from a chest seed or the player's starting equipment.

**NPCs do not interact with chests.** This is a scope decision, not a simulation principle.
In future stages, NPCs with appropriate behaviors (scavenging, provisioning) might loot chests.
Stage 2 NPC AI ignores container state entirely.

**Chest state machine:**
```
Chest states:
    LOCKED      → player tries to open → [has key?] UNLOCKED | [picks lock?] UNLOCKED | LOCKED
    UNLOCKED    → player opens → OPEN (if no trap or trap disarmed)
    TRAPPED     → player approaches → [perceives trap (§A5)?] AWARE | [disarms?] DISARMED | TRIGGERED
    TRIGGERED   → trap fires, clamped damage applied (§A5) → chest opens
    OPEN        → player may take items (§A2 carry check)
```

**Locks and traps are §12.2 checks, not minigames.** A lock DC, a skill/attribute roll, a
margin = score − DC, a degree band, and a narrative outcome. No separate puzzle mechanic.

---

## §A5 — Outcome Resolution and Stage 2 Attribute Shim

*Foundation reference: §12.2 (outcome model — base + skill + attributes vs difficulty + bounded variance)*

### §12.2 outcome model (restated for item interactions)

```
score  = base_value + skill_term + attribute_term
margin = score − DC
```

**Degree bands:**

| margin | Band | Meaning |
|---|---|---|
| ≤ −10 | CRITICAL_FAILURE | Badly failed; adverse secondary effect |
| < 0 | FAILURE | Failed; no progress |
| 0–9 | SUCCESS | Passed |
| ≥ 10 | CRITICAL_SUCCESS | Passed with bonus effect |

**Variance:** A small bounded random modifier (e.g., −3 to +3) is added after score computation.
Variance must never be large enough to flip an overwhelming advantage. A character with score 20
against DC 5 cannot critically fail because of a random number. This outlaws raw d20 mechanics
and any unbounded dice.

### Stage 2 attribute shim

Real Physique/Reflexes/Intuition attribute objects do not exist yet. The shim maps bible
attributes to the existing `Stats` fields:

| Bible attribute (§4.1) | Shim mapping | Where used in Stage 2 |
|---|---|---|
| Physique | `stat.STR × ATTR_SCALE` | Carry capacity only (§A2). No §12.2 item interaction uses Physique directly. |
| Reflexes | `stat.DEX × ATTR_SCALE` | Lockpick checks (§A4): attribute_term for the lock-picking score. |
| Intuition | `0` (until Stage 4) | Trap perception hints: always unreliable/rare; effectively no hint system. |
| Luck | `stat.LCK × ATTR_SCALE` | Edge-case variance adjustments. |
| Constitution, Intellect, Linguistic | `0` | Out of Stage 2 scope. |
| Skill term | `0` | No skill objects in Stage 2. |

`ATTR_SCALE` is a tunable constant; set at session start, not here. The shim is a function:

```python
def attribute_term(stats, attribute):
    match attribute:
        case "Physique":    return stats.STR  * ATTR_SCALE
        case "Reflexes":    return stats.DEX  * ATTR_SCALE
        case "Luck":        return stats.LCK  * ATTR_SCALE
        case _:             return 0
```

Only this function changes when Stage 4 introduces real attribute objects. All §12.2 resolvers
that call `attribute_term(...)` remain valid — the shim is the extension point, not the callers.

### Stage 2 item interaction DCs

| Interaction | Base value | Skill term | Attribute term | DC typical |
|---|---|---|---|---|
| Lockpick lock | entity.DEX | 0 (no skill) | attribute_term(Reflexes) | 10–15 |
| Perceive trap | entity — | 0 | attribute_term(Intuition) = 0 | effectively impossible |
| Disarm trap (MECHANICAL) | entity.DEX | 0 | attribute_term(Reflexes) | 12–16 |

Specific DCs are set per chest in the seed data, not in this document.

---

## §A6 — Arcane Focus Hook and Resonance

*Foundation reference: §6.6 (arcane focuses — external Byte storage)*

### The distinction: intrinsic vs external

§6.6 describes arcane focuses as **external** Byte storage. A focus extends or specializes a
caster's capacity to hold and transmit structured Byte patterns (spells, enchantments). A
caster wields a focus; the focus is separate from the caster's own Byte capacity.

A weapon's `resonance` is **intrinsic** — a different concept.

### Resonance: what it is

In LucentForge's world, reality is structured information (Bits → Bytes → Pattern → Outcome).
Magic is the art of shaping Byte-patterns to produce intended outcomes. A weapon forged by a
Bytes-skilled smith has had magical pattern encoded into its material structure during the
crafting process. The weapon does not hold a Bytes pool — it holds a *resonance pattern*: a
fixed alignment that allows it to transmit the wielder's Byte-intent more effectively through
each strike.

`resonance: int` on a weapon measures this attunement depth. High resonance = the weapon's
structure is deeply aligned with Byte-pattern transmission; it amplifies magical attacks.
Low or zero resonance = mundane weapon; no Byte amplification.

**Why "resonance" and not another term:**
The term reflects the informational magic philosophy without lifting CS jargon. Resonance is
a wave/frequency concept — the blade vibrates at the same "frequency" as the caster's Byte
patterns, conducting rather than disrupting them. It is world-native, grounded in lore, and
distinguishes weapon magic from caster magic without erasing the connection.

### Stage 2 mechanics

- `resonance: int` exists as a numeric field on Weapon in the schema.
- In Stage 2, resonance feeds `Stats.MAG` via the gear modifier system (`gear_mods`).
- No active resonance mechanic beyond the stat contribution. No separate "resonance check."

### Stage 4 reconciliation flag

Stage 4 deepens the Bits/Bytes system (see §5 of the terminology map — `mp` flag). When the
full magic pool system lands, the chain becomes:
```
Stage 4: caster's Bit pool → Byte pool → resonance amplification → attack MAG outcome
```
The `resonance` field will remain the correct term. Stage 4 will add the *mechanism* that
consumes Bit/Byte resources and applies resonance as a multiplier or threshold modifier.

### Arcane focus items (future)

A focus item (staff, tome, crystal) may carry a `resonance` field as a Byte-storage amplifier
rather than an attack enhancer — a focus holds Bytes so the caster doesn't have to, and its
resonance rating determines how much it can hold and how cleanly it transmits. This distinction
(weapon resonance = attack-path; focus resonance = pool-path) is flagged for Stage 4 design.

---

## §A7 — Economy Seeds

*Foundation reference: §15 (economy emerges from production and exchange; items are the medium)*

§15 establishes that economy is an emergent simulation property, not a shop system bolted on.
Items are produced, exchanged, and consumed as world-state changes, not as interface transactions.

**Stage 2 contribution:**

- `value: int` is added to all item records in the schema.
- Value is visible in the inventory UI (player can see item worth).
- No shop. No exchange. No currency object. No price-setting system.
- Unit name (coins? marks? weight-gold?) is deliberately undefined in Stage 2 — §15 economy
  design has not yet determined the world's economic unit. Stage 2 plants the field; Stage 5
  (or a dedicated economy arc) names the unit and wires the exchange system.

**Design intent:** Value seeded now means Stage 5 does not have to retrofit it. Every item
record already has a worth by the time economy mechanics arrive. The field is not cosmetic —
it is the economic data layer in embryo.

---

## §A8 — Out-of-Scope Register

Stage 2 deliberately excludes the following. Each entry is listed to prevent scope creep and to
signal where future planning arcs begin.

**Excluded from Stage 2:**

| Feature | Scope status | Future stage |
|---|---|---|
| NPC loot drops from defeated enemies | Out of scope | Stage 3+ (requires lootable dead) |
| Lootable dead bodies (NPC + PC) | Out of scope | Own arc (see seed below) |
| World-floor item pickup | Out of scope | Stage 3+ |
| NPC out-of-combat item use | Out of scope | Stage 3+ (NPC behavior expansion) |
| Item durability decay | Out of scope | Stage 3+ (fields exist, mechanics deferred) |
| Item crafting and recipes | Out of scope | Stage 5+ |
| Shops and player economy | Out of scope | Stage 5+ (§15 economy arc) |
| Per-element elemental resistance | Out of scope | Stage 4+ (§7 element model) |
| Arcane focus mechanics (Byte storage) | Out of scope | Stage 4 (§6.6 + magic system) |
| MAGICAL / POISON / ELECTRIC traps | Out of scope | Stage 3/4 (§A3) |
| Real Physique/Reflexes/Intuition objects | Out of scope | Stage 4 (shim replaced) |
| Drop action (items from bag to world) | Out of scope | Stage 3 (world-floor system) |

**FUTURE-ARC SEED (do not lose):**
World death — PC and NPC dying outside combat — opens EXP/leveling, its effects on the
character sheet, and lootable dead bodies as a persistent world mechanic. This arc has
significant implications for save state, entity tombstones, and loot resolution. It warrants
its own planning conversation. It is a candidate for alongside Stage 4 or as its own Stage 3.5.

Trap damage in Stage 2 clamps to 1 HP minimum + event log specifically to avoid triggering
this arc prematurely. Traps will not kill the player in Stage 2; the "what happens when a
character reaches 0 HP outside combat" system does not need to be designed yet.
