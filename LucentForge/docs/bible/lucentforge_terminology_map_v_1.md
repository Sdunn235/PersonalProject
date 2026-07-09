# LucentForge Terminology Reconciliation Map v1

**Created:** 2026-07-05 | **Stage:** 2.0 | **Authority:** LucentForge Bible (Foundation v1)

---

## Purpose

Three codebases contribute to LucentForge's item system:

1. **The Bible** (`lucentforge_simulation_foundation_v_1.md`) — naming and semantics authority
2. **TheForge C#** (`TheForge/ConsoleRpgEntities/`) — structural blueprint (read-only reference)
3. **LucentForge Python** (`Mechanics/`) — the live implementation

These three sources have drifted from each other. This map is the managed reconciliation. Every
time a feature is ported from TheForge into LucentForge Python, it gets a reconciliation pass
against this map before implementation.

---

## Standing Rule (applies to all stages, 2.0 through 5)

> **TheForge is the structural blueprint. The bible is the naming and semantics authority.**
>
> When TheForge and the bible agree on a term: use that term.
> When they conflict: the bible wins.
> When the bible is silent: adopt TheForge's name in snake_case, and record it here.
> When neither names the concept: invent a world-native term and record it here.
>
> **Every TheForge import gets a reconciliation pass against this map before implementation.**

Extend this map as each stage imports more concepts from TheForge or the bible deepens.

---

## Section 1 — Core Attributes

The bible (§4.1) defines seven core attributes. TheForge's `CoreAttribute` enum matches exactly.
LucentForge Python does not yet have attribute objects — it uses a combat stat shim.

| Bible (§4.1) | TheForge C# | LucentForge Python today | Stage 2 decision |
|---|---|---|---|
| Physique | `CoreAttribute.Physique` | `Stats.STR` | Docs/comments: "Physique"; runtime shim: Physique → STR |
| Reflexes | `CoreAttribute.Reflexes` | `Stats.DEX` | Docs/comments: "Reflexes"; runtime shim: Reflexes → DEX |
| Intuition | `CoreAttribute.Intuition` | — (no analog) | `attribute_term(Intuition) = 0` until Stage 4; trap recognition hints are unreliable/rare |
| Luck | `CoreAttribute.Luck` | `Stats.LCK` | Docs/comments: "Luck"; runtime shim: Luck → LCK |
| Constitution | `CoreAttribute.Constitution` | — | Out of Stage 2 scope; mapped for the record |
| Intellect | `CoreAttribute.Intellect` | — | Out of Stage 2 scope |
| Linguistic | `CoreAttribute.Linguistic` | — | Out of Stage 2 scope |

**Shim contract** (explicit — see also addendum §A5):
```
attribute_term(stat, attribute):
    Physique    → stat.STR  × ATTR_SCALE
    Reflexes    → stat.DEX  × ATTR_SCALE
    Luck        → stat.LCK  × ATTR_SCALE
    Intuition   → 0         (until Stage 4)
    all others  → 0         (until Stage 4)
```
Only `attribute_term` changes when real attribute objects land in Stage 4. All call sites that
use this shim remain valid — the shim is the extension point, not the callers.

> **Stage 4 update:** Real attribute objects now land. See `lucentforge_stats_magic_addendum_v1.md`
> §M2 for the layered model and the superseding derive map (Intellect→MAG + Byte capacity;
> Constitution→DEF/RES; Intuition→Bit capacity + trap perception). Linguistic remains inert.

---

## Section 2 — Derived Resources

Resources are system states influenced by attributes, conditions, and environment (bible §5).
They are not primary attributes.

| Bible (§5) | TheForge C# | LucentForge Python today | Stage 2 decision |
|---|---|---|---|
| Health | `Hp` (Resources.cs) | `entity.hp` | No change. `hp` = canonical in code. |
| Stamina | `Sp` (Resources.cs) | `entity.cycles` (pre-bible holdover) | **Canonical rename: `stamina`.** `cycles` is a pre-bible holdover. Rename executes in Phase 2.3. New Stage 2 code uses `stamina`. |
| Bits | `BitPool` (ConsumableEffect enum) | `entity.mp` (non-canonical) | **Flagged non-canonical.** Stage 2 bridge: `RESTORE_MP`. Stage 4 reconciles Bits/Bytes → `mp` → two-pool system. |
| Bytes | `BytePool` (ConsumableEffect enum) | `entity.mp` (same field) | Same flag. Bits/Bytes split deferred to Stage 4. |

**`mp` flag:** The Python field `entity.mp` and the `restore_mp` effect key are explicitly
non-canonical. They are Stage 2 bridge terms only. Stage 4 will split into `bits`/`bytes` pools
with separate mechanics. Do not deepen any code against `mp` — only add the Stage 2 bridge.

> **Stage 4 update:** The split is now specified. `mp` → `bits` (capacity ← Intuition) + `bytes`
> (capacity ← Intellect); both pools always present; casting economy and conversion in
> `lucentforge_stats_magic_addendum_v1.md` §M3–§M4. Migration m0008.

---

## Section 3 — Item Field Naming

### 3.1 Item Base (all items inherit these fields)

| Bible | TheForge C# | LucentForge Python today | Stage 2 decision |
|---|---|---|---|
| — | `Id: int` | `id: str` | `id: str` — Python convention (string IDs from JSON seed). No change. |
| — | `Name: string` | `name: str` | `name` — unchanged. |
| — | `Description: string` | `description: str` | `description` — unchanged. |
| §15 (economy) | `Value: int` | — (new in Stage 2) | `value: int` — unit name deferred until §15 economy design matures. |
| §4.1 (Physique) | `Weight: int` | — (new in Stage 2) | `weight: int` — same unit as carry capacity math (CARRY_BASE + 2×STR). |
| — | `KeyId: string?` | — (new in Stage 2) | `key_id: str | None` — semantics exact from TheForge: `None` = not a key; `"lockpick"` = generic pick (consumed on failed attempt); any other string = specific key matching a lock's `required_key_id`. |
| — | `ContainerId: int?` | — (added in Phase 2.2) | `container_id: int | None` — FK to `containers` table. Populated in Phase 2.2 when relational schema lands. |

### 3.2 DurableItem

| Bible | TheForge C# | LucentForge Python today | Stage 2 decision |
|---|---|---|---|
| — | `Durability: int` | — (new in Stage 2) | `durability: int` — decay mechanics are out-of-scope for Stage 2 (addendum §A8). Field exists in schema; value is cosmetic this stage. |

### 3.3 Weapon

| Bible | TheForge C# | LucentForge Python today | Stage 2 decision |
|---|---|---|---|
| — | `AttackPower: int` | `effects.atk` | `attack_power: int` — snake_case port of TheForge. |
| §6.6 (Bits/Bytes) | — (absent in TheForge) | `effects.mag` | `resonance: int` — **new canonical name** (see §A6 of addendum). Weapon-inherent attunement to Byte-structured patterns. Replaces Python `mag`/`magic_power`. Feeds `Stats.MAG` via `gear_mods`. Flagged for Stage 4 reconciliation. |
| — | `WeaponType: WeaponType` | — (no enum; `type` string) | `weapon_type: WeaponType` — enum port from TheForge (see §4, Enum Naming). |
| §10.2 | `EligibleSlot = MainHand` | `slot: "weapon"` | `eligible_slots = MAIN_HAND \| OFF_HAND` — **LucentForge deviation.** TheForge restricts weapons to MainHand; LucentForge allows either hand (dual-wield legal). `eligible_slots` is computed from class, not stored. |

### 3.4 Armor

| Bible | TheForge C# | LucentForge Python today | Stage 2 decision |
|---|---|---|---|
| — | `DefenseRating: int` | `effects.def` | `defense_rating: int` — snake_case port of TheForge. Feeds `Stats.DEF` via `gear_mods`. |
| §7 (elemental model) | — (absent in TheForge) | `effects.res` | `resist_rating: int` — **Stage 2 invention.** §7 establishes the elemental pattern model; resistance exists conceptually. Stage 2 proxy: one field covers all elemental resistance. Per-element split deferred. Feeds `Stats.RES` via `gear_mods`. |
| — | `WeightClass: ArmorWeight` | — | `weight_class: ArmorWeight` — enum port (see §4). |
| — | `Slot: BodySlot` | `slot: "armor"` | `body_slot: BodySlot` — enum port (see §4). Armor worn on the body. Does NOT include hand-held items. |
| §10.2 | `EligibleSlot = per BodySlot` | — | `eligible_slots` computed from `body_slot` (not stored). Each BodySlot body value maps 1:1 to the matching SlotType bit. |

### 3.5 Shield

| Bible | TheForge C# | LucentForge Python today | Stage 2 decision |
|---|---|---|---|
| — | `Shield → Armor`; `EligibleSlot = OffHand` | `slot: "shield"` | `Shield` inherits `Armor`. `body_slot = OFF_HAND`. `eligible_slots = MAIN_HAND \| OFF_HAND` (either hand — same rule as weapons). TheForge restricts to OffHand; LucentForge allows both. |
| — | `DefenseRating: int` | `effects.def` | `defense_rating: int` — same as Armor. |
| — | `resist_rating` not on TheForge Shield | — | `resist_rating: int` — same as Armor (shields may have elemental resist). |

### 3.6 Consumable

| Bible | TheForge C# | LucentForge Python today | Stage 2 decision |
|---|---|---|---|
| — | `Effect: ConsumableEffect` | `effects.{heal/restore_sp/restore_mp}` | `effect: ConsumableEffect` — enum (see §4). Stage 2 values: `HEAL`, `RESTORE_SP`, `RESTORE_MP`. |
| — | `Potency: int` | `effects.{value}` (varies by key) | `potency: int` — magnitude applied to the resource named by `effect`. |

---

## Section 4 — Enum Naming

All Python enums use `SCREAMING_SNAKE_CASE` values per Python convention. Enum class names use PascalCase.

### 4.1 SlotType (equipment assignment system)

Python `enum.Flag` — bitwise combinable. These are the SLOTS the EquipmentSet manages.

| Value | Bit | TheForge | Notes |
|---|---|---|---|
| `MAIN_HAND` | 1 | `MainHand` | Dominant hand: weapons, tools |
| `OFF_HAND` | 2 | `OffHand` | Support hand: shields, off-hand weapons |
| `HEAD` | 4 | `Head` | Helmet, hat |
| `CHEST` | 8 | `Chest` | Chest armor, robes |
| `LEGS` | 16 | `Legs` | Leg armor |
| `FEET` | 32 | `Feet` | Boots |
| `HANDS` | 64 | `Hands` | Gauntlets — body armor worn on both hands |
| `ANY_HAND` | 3 | `AnyHand` | `MAIN_HAND \| OFF_HAND` — weapons + shields may equip to either |

`ANY_HAND = MAIN_HAND | OFF_HAND`. Equip logic prefers `OFF_HAND` for `ANY_HAND`-eligible items
(shields naturally go to the off-hand first), falls back to `MAIN_HAND` if occupied.

### 4.2 BodySlot (item storage descriptor — what body location an item belongs to)

Python `enum` — stored in the `body_slot` column of the items table.

**Stage 2 expansion:** BodySlot now includes hand-held positions. TheForge's `BodySlot` had
only body-armor values (Head/Chest/Legs/Feet/Hands). LucentForge adds `MAIN_HAND` and `OFF_HAND`
so weapons and shields can record their natural slot in the same column.

| Value | TheForge | Notes |
|---|---|---|
| `HEAD` | `Head` | Helmet |
| `CHEST` | `Chest` | Chest armor |
| `LEGS` | `Legs` | Leg armor |
| `FEET` | `Feet` | Boots |
| `HANDS` | `Hands` | Gauntlets — body armor on both hands (not a held slot) |
| `MAIN_HAND` | — (new) | Weapons: primary held position |
| `OFF_HAND` | — (new) | Shields: primary held position |

**BodySlot → SlotType mapping:**
```
BodySlot.HEAD      → SlotType.HEAD
BodySlot.CHEST     → SlotType.CHEST
BodySlot.LEGS      → SlotType.LEGS
BodySlot.FEET      → SlotType.FEET
BodySlot.HANDS     → SlotType.HANDS
BodySlot.MAIN_HAND → SlotType.MAIN_HAND | SlotType.OFF_HAND  (eligible for either)
BodySlot.OFF_HAND  → SlotType.MAIN_HAND | SlotType.OFF_HAND  (eligible for either)
```
Body armor maps 1:1. Held items (MAIN_HAND / OFF_HAND body_slot) map to `ANY_HAND` eligibility,
because both weapons and shields are equippable to either hand by design.

### 4.3 WeaponType

Adopted from TheForge verbatim.

| Python | TheForge | Stage 2 seed items |
|---|---|---|
| `SWORD` | `Sword` | iron_sword |
| `AXE` | `Axe` | — |
| `MACE` | `Mace` | — |
| `BOW` | `Bow` | — |
| `STAFF` | `Staff` | wooden_staff |
| `DAGGER` | `Dagger` | — |
| `SPEAR` | `Spear` | — |

### 4.4 ArmorWeight

| Python | TheForge |
|---|---|
| `LIGHT` | `Light` |
| `MEDIUM` | `Medium` |
| `HEAVY` | `Heavy` |

### 4.5 ConsumableEffect

TheForge has `BitPool`/`BytePool`. LucentForge Stage 2 uses bridge names — `RESTORE_MP` is
explicitly non-canonical.

| Python | TheForge | Notes |
|---|---|---|
| `HEAL` | `Heal` | Restores HP up to max. |
| `RESTORE_SP` | `Stamina` | Restores stamina up to max. |
| `RESTORE_MP` | — (bridge) | Restores magic pool. **Non-canonical — flagged.** TheForge has `BitPool`/`BytePool`; bible uses Bits/Bytes (§6). Stage 4 splits into `RESTORE_BITS` / `RESTORE_BYTES`. |
| `RESTORE_BITS` | `BitPool` | **Stage 4.** Restores the Bit pool. Replaces `RESTORE_MP` for primal energy. |
| `RESTORE_BYTES` | `BytePool` | **Stage 4.** Restores the Byte pool. Replaces `RESTORE_MP` for structured energy. |

### 4.6 TrapType

Python `enum.Flag` — bitwise combinable. Adopted from TheForge.

| Python | TheForge | Stage 2 status |
|---|---|---|
| `NONE` | `None` | No trap. |
| `MECHANICAL` | `Mechanical` | Spring/dart/spike mechanism. **Active in Stage 2.** Disarmed via Reflexes (DEX) check (§12.2). |
| `MAGICAL` | `Magical` | Arcane ward. **Future only** — Intuition-check mechanism deferred to Stage 3/4. |
| `POISON` | `Poison` | Ongoing damage-over-time on trigger. **Future only.** |
| `ELECTRIC` | `Electric` | Instant paralysis on trigger. **Future only.** |

All 4 values are defined in Stage 2 for forward-compatibility. Stage 2 chest seeds use
`MECHANICAL` only. Adding mechanic behavior to `MAGICAL`/`POISON`/`ELECTRIC` in a later
stage requires no enum migration.

---

## Section 5 — Flagged Non-Canonical Terms

These terms exist in the live codebase but are known to be temporary bridge names.
Do not build new mechanics against them — they will change in the named future stage.

| Current term | Location | Non-canonical because | Reconcile in |
|---|---|---|---|
| `mp` | `entity.mp`, `effects.restore_mp`, `Stats.MAG` (partially) | Bible §6 names the two-pool magic system "Bits" and "Bytes." A single `mp` erases that distinction. | **Stage 4 — reconciled** (→ `bits`/`bytes`, addendum §M3) |
| `cycles` | `entity.cycles`, save state | Pre-bible holdover for Stamina (§5). | Phase 2.3 (rename everywhere) |
| `RESTORE_MP` | `ConsumableEffect` | TheForge uses `BitPool`/`BytePool`; bible uses Bits/Bytes (§6). `RESTORE_MP` is a bridge. | **Stage 4 — reconciled** (→ `RESTORE_BITS`/`RESTORE_BYTES`, §4.5) |
| `magic_power` (plan) | Plan contract only | Replaced by `resonance` (canonical). See §3.3 + addendum §A6. | Already reconciled in Stage 2.0 |

---

## Section 6 — Extension Protocol

When a future stage imports a new TheForge concept:

1. Add a row to the relevant table above (or add a new section).
2. Record: Bible term (or "silent") | TheForge name | Python today | Stage N decision.
3. If bible is silent and a new name is invented, add an entry to Section 5 flagging it.
4. The addendum (`lucentforge_items_addendum_v_1.md` or `lucentforge_rooms_panels_addendum_v1.md`) may
   need a new section if the concept has behavioral doctrine attached.

This map is the reference for all reconciliation discussions. Keep it current.

---

## Section 7 — Stage 3 Terms (Rooms / Panels / World Coordinates)

**Created:** Stage 3.0 | **Authority:** `lucentforge_rooms_panels_addendum_v1.md`

Three authorities for Stage 3 reconciliation:

1. **The Foundation** (`lucentforge_simulation_foundation_v_1.md`) — naming and semantics
2. **TheForge C#** (`ConsoleRpgEntities/Models/Containers/Room.cs`, `Models/Containers/Door.cs`) — structural blueprint
3. **LucentForge Python** (`Mechanics/world/`) — live implementation

### 7.1 World Coordinate Terms

| Bible | TheForge C# | LucentForge Python | Stage 3 decision |
|---|---|---|---|
| — | `Room.GridX: int?`, `Room.GridY: int?` | `panel_x: int`, `panel_y: int` | **`panel_x/panel_y`** — LucentForge uses panel grid coordinates, not room-graph indices. Semantically equivalent: GridX/GridY addressed a room in a discrete graph; panel_x/panel_y address a 18×18 tile map in a continuous grid. |
| — | — | `WorldPos(panel_x, panel_y, col, row)` | **New canonical type** — four-component world locator. All Stage 3+ content that needs a world location uses `WorldPos`. Not in TheForge (TheForge rooms are discrete, not tile-grid). |
| — | `Door.RoomAId, Door.RoomBId` | `PanelEdge.NORTH/SOUTH/EAST/WEST` | **`PanelEdge`** — TheForge's bidirectional Door is a graph edge between rooms; LucentForge's PanelEdge is a directional exit from a panel. Semantically: both describe how to traverse from one location to another. TheForge: per-door wiring. LucentForge: per-panel directional stub. |

### 7.2 Room / Zone Terms

| Bible | TheForge C# | LucentForge Python | Stage 3 decision |
|---|---|---|---|
| — | `Room.Name: string` | `RoomDefinition.name: str` | **`name`** — unchanged. Display name of the zone. |
| — | `Room.Description: string` | `RoomDefinition.description: str` | **`description`** — field seeded in Stage 3 data layer. Not rendered until Stage 5 (dialogue arc). |
| — | No RoomType enum in TheForge | `RoomType(enum.Enum)` | **`RoomType`** — new invention. TheForge rooms are typed by name only; LucentForge adds semantic type enum. Values: `WILDERNESS, SETTLEMENT, GOBLIN_TERRITORY, BRIDGE, FARM, STORAGE, RIVER`. See `lucentforge_rooms_panels_addendum_v1.md §R3`. |
| — | `Room.GridX/GridY` → grid coordinates | `tile_bounds: tuple[int,int,int,int]` | **`tile_bounds = (col_min, row_min, col_max, row_max)`** — how a Room maps to tiles in its panel. TheForge has no equivalent (discrete rooms, not tile grids). |

### 7.3 Zone Crossing / Event Terms

| Bible | TheForge C# | LucentForge Python | Stage 3 decision |
|---|---|---|---|
| — | No event system in TheForge | `ZoneCrossingEvent` dataclass | **`ZoneCrossingEvent`** — new invention. Fires when entity's `current_room` changes. See `lucentforge_rooms_panels_addendum_v1.md §R4`. |
| — | — | `ZoneTracker` | **`ZoneTracker`** — Observer implementation. Holds `_current_rooms: dict[str, RoomDefinition | None]` per entity name. Edge-triggered: fires once on change, not every tick. |

### 7.4 Panel Terms

| Bible | TheForge C# | LucentForge Python | Stage 3 decision |
|---|---|---|---|
| — | `Room` is a discrete container | `Panel(panel_x, panel_y)` = 18×18 tile map | **`Panel`** — LucentForge's world unit. Not a direct TheForge equivalent. TheForge rooms are discrete containers with items/NPCs; LucentForge panels are tile maps at world-grid scale. |
| — | `Door → Room navigation` | `PanelLoader.can_transition(...)` | **`PanelLoader`** — stub in Stage 3. TheForge: Door.RoomAId/RoomBId links rooms. LucentForge: PanelLoader checks adjacency graph (`panels.json`) and loads adjacent panels. Architecture only in Stage 3 — no transitions fire. |

### 7.5 Region → Room Mapping (Panel(0,0))

| Python region string | Room ID | RoomType | Notes |
|---|---|---|---|
| `forest` | `panel00_forest` | `WILDERNESS` | |
| `town_center` | `panel00_town_center` | `SETTLEMENT` | |
| `town_outskirts` | `panel00_town_outskirts` | `SETTLEMENT` | |
| `homes` | `panel00_homes` | `SETTLEMENT` | |
| `farm` | `panel00_farm` | `FARM` | |
| `storage` | `panel00_storage` | `STORAGE` | |
| `goblin_camp` | `panel00_goblin_camp` | `GOBLIN_TERRITORY` | |
| `river` | `panel00_river` | `RIVER` | |
| `bridge` | `panel00_bridge` | `BRIDGE` | |

Region strings are `TileMap.get_region(col, row)` return values. They do not change in Stage 3 — Rooms are built on top of them, not replacing them.

---

## Section 8 — Stage 4 Terms (Attributes / Bits & Bytes / Affinity)

**Created:** Stage 4.0 | **Authority:** `lucentforge_stats_magic_addendum_v1.md`

### 8.1 Attributes & Magic Pools

| Bible | TheForge C# | LucentForge Python | Stage 4 decision |
|---|---|---|---|
| §4.1 (7 attributes) | `CoreAttribute` enum | `Attributes` dataclass (7 fields) | **New primary layer.** Authored per-entity; feeds `derive_stats()`. Wired: Physique/Reflexes/Luck/Intellect/Constitution/Intuition. Inert: Linguistic. §M2. |
| §6.2 Bits | `BitPool` | `entity.bits` / `bits_max` | **Canonical.** Capacity ← Intuition. Primal/direct casting pool. §M3. |
| §6.3 Bytes | `BytePool` | `entity.bytes` / `bytes_max` | **Canonical.** Capacity ← Intellect. Structured pool; built via conversion. §M3. |
| §6.4 magic flow | — | `spell.magic_kind: BIT \| BYTE` | **New.** Spell authored as Bit-spell (primal) or Byte-spell (structured composition). §M4. |
| §6.5 conversion | — | `convert()` action | **New.** Bits→Bytes; reliable OOC, costs a turn in combat. Overburn = disabled hook. §M4. |

### 8.2 Affinity

| Bible | TheForge C# | LucentForge Python | Stage 4 decision |
|---|---|---|---|
| §7 (elemental patterns) | — (absent) | `Affinity` enum (6) | **New.** `EARTH/FIRE/AIR/WATER/VOID/LIGHT`. Full §7 pattern-physics deferred. §M5. |
| — | — | `entity` innate affinity (base + modifier) | **New.** Single innate at birth; **mutable** so spells/events/curses/blessings alter it. §M5. |
| — | — | `RoomDefinition.affinity`, `affinity_intensity` | **New.** Per-region environment field; amplifies like-affinity casting. Reuses Stage 3 rooms. §M5. |
| — | — | opposition pairs | **New.** FIRE↔WATER, EARTH↔AIR, LIGHT↔VOID. Weakness/resistance in combat. §M6. |

Weapon `resonance` (§3.3) gains its mechanism in Stage 4: a multiplier on the Byte/MAG outcome (§M7).
