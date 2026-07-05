# Week 15: Final Project — ConsoleRPG World Builder

> **Template Purpose:** This is the capstone template. Everything you've built from Week 12 through Week 14 is here, extended with a polished dual-mode UI, a richer seeded world, and reference implementations you can study and extend.

---

## Overview

Over the course of this semester you've built an RPG data model piece by piece:

| Week | What you added |
|------|----------------|
| **W9** | EF Core + migrations (first contact with the database) |
| **W10** | TPH inheritance for Monsters and Abilities |
| **W11** | Equipment system (legacy W11-era design, superseded in W12) |
| **W12** | `Item` and `Container` TPH hierarchies — the foundation |
| **W13** | `Chest` + `MonsterLoot` + the `ILockable` interface |
| **W14** | `Room` as a Container + `Door` using `ILockable` |
| **W15** | **→ You are here** — dual-mode UI, richer world, final presentation |

Week 15 is **not** about rewriting architecture. The model layer from W14 is already complete. Your job is to:

1. **Understand and explore** the finished framework (the hardest part)
2. **Use advanced LINQ** to answer new questions about the world
3. **Extend the world** with your own rooms, items, monsters, or small architecture additions
4. **Make it your own** — creative freedom is strongly encouraged for A+ work

## Learning Objectives

By the end of this project you will have demonstrated:
- [x] Proficiency with EF Core, migrations, and LINQ across a non-trivial domain model
- [x] Ability to read and extend a service-layered application
- [x] Understanding of TPH inheritance for multiple entity hierarchies
- [x] Application of all five SOLID principles in a connected example
- [x] Creative world-building on top of a working framework

## Prerequisites

- [ ] Completed Week 12-14 assignments (or caught up using this template)
- [ ] SQL Server LocalDB installed and working
- [ ] EF Core migrations experience
- [ ] Basic familiarity with Spectre.Console (introduced lightly in W14)

---

## The World

The seed data builds a 7-room dungeon with a clear narrative arc:

- **7 rooms** on an orthogonal grid (all door connections horizontal or vertical — required for mini-map rendering)
- **5 enemy NPCs** placed in specific rooms
- **2 story NPCs** (Mira the Innkeeper, Erasmus the Unbound boss)
- **6 doors** with various states (locked, trapped, open, secret)
- **4 chests** throughout the dungeon
- **2 bookshelves** with readable books
- **Elara** starts at the Inn with Iron Sword + Leather Vest equipped + 1 Healing Potion

### World Layout

```
col0         col1              col2
             ┌────────────┐
             │ Inn Cellar │         row0 — Giant Cellar Rat; Cellar Cask
             └─────┬──────┘
                   │ Cellar Stairs
             ┌─────┴──────────────┐
             │  Wayward Crow Inn  │  row0 — Mira (shop + quest); YOU START HERE
             └─────┬──────────────┘
                   │ Thornwood Gate
┌──────────┐ ┌─────┴──────┐ ┌────────────┐
│  Goblin  ├─┤  Thornwood ├─┤   Ruined   │  row1 — Camp Crate; Chapel Gate (locked+trapped)
│   Camp   │ │    Path    │ │   Chapel   │
└──────────┘ └────────────┘ └─────┬──────┘
                                  │ Crypt Passage
                             ┌────┴──────┐
                             │   Crypt   │  row2 — Risen Acolyte; Crypt Hound
                             │ Entrance  │
                             └─────┬─────┘
                                   │ Vault Descent (requires vault_key)
                             ┌─────┴─────┐
                             │  Sealed   │  row3 — Erasmus the Unbound (boss); Sealed Reliquary
                             │   Vault   │
                             └───────────┘
```

### The Progression Loop

1. Start at **The Wayward Crow Inn** — talk to Mira, check gear
2. Clear **Inn Cellar** (Giant Cellar Rat) — return to Mira for reward dialogue
3. Head to **Goblin Camp** via Thornwood Path — fight Gobby, loot the vault_key from his bag
4. Take the path east to **Ruined Chapel** — disarm the trap, unlock the Chapel Gate
5. Fight through **Crypt Entrance** (Risen Acolyte + Crypt Hound)
6. Use the vault_key on **Vault Descent** — enter **The Sealed Vault**
7. Survive Erasmus's monologue, defeat him, loot the Sealed Reliquary

---

## Project Structure

This template preserves the two-project architecture you've been using since Week 7:

```
ConsoleRpgFinal.sln
README.md
CONTRIBUTIONS.md                            # REQUIRED: your honest summary
│
├── ConsoleRpg/                            # UI, services, game loop
│   ├── Program.cs
│   ├── Startup.cs                         # DI configuration
│   ├── appsettings.json
│   ├── Models/
│   │   └── ServiceResult.cs               # NEW: service return type
│   ├── Services/
│   │   ├── GameEngine.cs                  # Tiny dispatcher (SRP)
│   │   ├── PlayerService.cs               # Exploration actions
│   │   └── AdminService.cs                # Admin-mode CRUD + LINQ
│   ├── Helpers/
│   │   ├── MapManager.cs                  # NEW: Spectre.Console ASCII map
│   │   ├── ExplorationUI.cs               # NEW: split-panel layout
│   │   ├── MenuManager.cs                 # Legacy menu helper
│   │   └── OutputManager.cs               # Legacy output buffer
│   └── ParserDemo/
│       └── ParserDemo.cs                  # NEW: Zork-style parser stretch goal
│
└── ConsoleRpgEntities/                    # Data + models (unchanged from W14)
    ├── Data/
    │   ├── GameContext.cs                 # All DbSets + TPH config
    │   └── GameContextFactory.cs
    ├── Models/
    │   ├── Characters/
    │   │   ├── Player.cs                  # Same Player from W14
    │   │   └── Monsters/
    │   │       ├── Monster.cs
    │   │       ├── Goblin.cs              # from W10
    │   │       ├── Wolf.cs                # NEW for W15
    │   │       └── Skeleton.cs            # NEW for W15
    │   ├── Containers/                    # W12 hierarchy + W13 + W14
    │   │   ├── IItemContainer.cs
    │   │   ├── ILockable.cs
    │   │   ├── SlotType.cs                # W13 - equipment slot enum
    │   │   ├── EquipmentSlot.cs           # W13 - per-slot row owned by Equipment
    │   │   ├── Container.cs
    │   │   ├── Inventory.cs
    │   │   ├── Equipment.cs               # W13 - has EquipmentSlots collection
    │   │   ├── Chest.cs
    │   │   ├── MonsterLoot.cs
    │   │   ├── Room.cs
    │   │   ├── Item.cs                    # W13 - has EligibleSlot column
    │   │   ├── Weapon.cs / Armor.cs / Consumable.cs / KeyItem.cs
    │   ├── World/
    │   │   └── Door.cs                    # W14 lockable door
    │   └── Abilities/
    │       └── PlayerAbilities/ ...       # TPH from W10
    ├── Helpers/
    │   ├── ConfigurationHelper.cs
    │   └── MigrationHelper.cs
    └── Migrations/
        ├── InitialCreate (W12)
        ├── SeedInitialData (W12)
        ├── AddChestsAndMonsterLoot (W13)
        ├── SeedWorldContent (W13)
        ├── AddRoomsAndDoors (W14)
        ├── AddMonsterTypes (W15 - Wolf/Skeleton columns)
        ├── AddChestLocation (W15 - Chest.LocationRoomId for placement)
        ├── SeedFinalWorld (W15)
        ├── AddEquipmentSlots (W13 slot system)
        └── Scripts/
            ├── SeedInitialData.sql        # W12
            ├── SeedWorldContent.sql       # W13
            └── SeedFinalWorld.sql         # NEW for W15
```

---

## The Two Game Modes

When you run the game you're greeted by a Figlet title and dropped into **Exploration Mode**. Switching between modes is a menu option in each.

### Exploration Mode

A split-panel Spectre.Console layout:

- **Left panel:** the world map, drawn with ASCII art. Your current room is marked with `[@]`, rooms with monsters are `[M]`, empty rooms are `[■]`, and connections are drawn as horizontal/vertical lines. Rooms hidden behind undiscovered secret doors are NOT shown — find the door with Inspect Room to reveal them.
- **Right panel (top):** current room description, visible exits, monsters present, chests in the room (with status: locked / open / empty), and items on the floor.
- **Right panel (bottom):** combined character panel — name, level, HP, XP, attack/defense, what's equipped, and a one-line bag summary (`Bag: 14 items (5 wpn, 4 arm, 4 csm, 1 key) · 31/100 lbs`). The full per-item list is one click away via the **View Inventory** menu action.
- **Bottom:** a context-sensitive selection menu with only the actions that make sense right now — "Attack Monster" only shows if there's a live monster here, "Open Chest" only if a chest is in the room, "Equip Item" only if there's something equippable in your bag, and so on.

The full action list is: **Go N/S/E/W**, **Attack Monster**, **Pick Up Item**, **Open Chest**, **Equip Item**, **Unequip Item**, **Drop Item**, **Use Consumable**, **View Inventory**, **Inspect Room**, **Switch to Admin Mode**, **Quit**. Locked doors prompt you to pick a key from your bag before you walk through them — same with locked chests.

### Admin Mode

A straightforward arrow-key menu grouped by rubric tier:

**Base tier:**
- Add Character
- Display All Characters
- Search Character by Name

**B tier:**
- Display Room Details
- List All Rooms with Monsters

**A tier:**
- Add Ability to Character
- Display Character Abilities
- Find Item Location (LINQ)
- Monster Census (LINQ GroupBy)

**Stretch goal:**
- **Parser Demo** — a self-contained Zork-style text parser running on a tiny mock world (the original "West of House" mailbox/leaflet from 1980). Type `help` to see verbs, try `open mailbox`, `read leaflet`, `take leaflet`, `inventory`. See [Parser Demo](#parser-demo-stretch-goal) below for what it teaches and how to extend it.

---

## Getting Started

### 1. Apply the migrations

From the solution directory:

```bash
dotnet ef database update --project ConsoleRpgEntities --startup-project ConsoleRpg
```

This applies nine migrations in order, ending with `AddEquipmentSlots` which carries the slot system forward. If you ever want a fresh start, run:

```bash
dotnet ef database update 0 --project ConsoleRpgEntities --startup-project ConsoleRpg
dotnet ef database update   --project ConsoleRpgEntities --startup-project ConsoleRpg
```

### 2. Build and run

```bash
dotnet build
dotnet run --project ConsoleRpg
```

### 3. Explore

Start by wandering around Town Square and surrounding rooms. Check the admin menu features. Fight the wolf. See how the map updates as you move. Try to figure out the maze.

---

## Design Deviations (Justified)

This section logs deliberate engineering decisions made throughout the
semester rolling codebase. Carried forward from Module14 (W12–W14
work) plus new W15 entries. Each row is a place where we chose
something different from the template approach — and why it was the
better call.

### Carried Forward from W14

#### Pre-W14 polish — Consumable Effect refactor (Phase B)

| Old approach (W12/W13) | New approach (Phase B) | Reason |
|---|---|---|
| `Consumable.Effect` is `string`. Free text. Lowercased and switched on inside `Character.UseItem`. | `Consumable.Effect` is the typed `ConsumableEffect` enum (`None / Heal / Stamina / BitPool / BytePool`). | Eliminates magic strings. Makes the create-item menu a numbered picker that auto-updates when a new enum value is added. |
| Unrecognized effect strings silently consumed the item without doing anything. | `UseItem` tracks an `applied` flag; consumption only fires when a real effect was applied. | Compile-time exhaustiveness + behavior fix. Lockpicks no longer "vanish" on accidental use-item attempts. |
| `Effect = "keyitem"` and `Effect = "lockpick"` overloaded the column with type-discriminator meaning. | Migrated to `ConsumableEffect.None`. Phase C moved them to `KeyItem : Item`. | One smell at a time. Phase B narrows `Effect`'s contract; Phase C removes the rows that don't belong here. |

#### Pre-W14 polish — W12 unique-index filter fix (Phase B.1)

| Old approach (W12) | New approach (Phase B.1) | Reason |
|---|---|---|
| `IX_Containers_Inventory_OwnerCharacterId` had a filter clause referencing the wrong column (`[OwnerCharacterId]` instead of `[Inventory_OwnerCharacterId]`). Crashed on multi-character insert. | `W14_FixContainerInventoryIndexFilter` drops and recreates with the correct filter. | EF's TPH auto-generated two FK columns; the filter must reference the index's own column, not its TPH sibling's. |

#### Phase C.1 — Room as 5th Container TPH subclass

| Template / default approach | Our implementation | Reason |
|---|---|---|
| EF scaffolded `DropTable("Rooms")` — would have lost all room data. | Hand-edited migration uses `MERGE...OUTPUT INTO #RoomMap` to atomically insert each Room into Containers while capturing the old→new id mapping. Then UPDATEs every FK column before dropping. | Preserves seeded world through the schema change. The MERGE+OUTPUT mapping pattern is reusable for future TPH promotions. |
| Both `Character.RoomId` and `Chest.RoomId` kept `OnDelete(SetNull)`. | Changed both to `NoAction`. | Combining two `SetNull` cascades on a self-referential `Containers` table triggers SQL Server error 1785. `RemoveRoom` handles cleanup application-side. |

#### Phase C.2 — Door bidirectional + ILockable

| Old approach | New approach (Phase C.2) | Reason |
|---|---|---|
| Door: `SourceRoomId / DestinationRoomId / Direction`; two rows per passage. | Door: `RoomAId / RoomBId`; one row per passage. | Single source of truth for lock/trap state. Lock state can't drift between two "paired" rows. |
| `MovePlayer` matched `door.Direction == requested`. | `Door.GetOtherRoom(currentRoom)` returns the opposite-side room. `MovePlayer` asks the door directly. | **GRASP information-expert**: the Door owns its endpoints; it answers "which side is mine?" Player code stays direction-agnostic. |
| EF scaffolded the migration as `RenameColumn(SourceRoomId → UnlockDC)` (both are int, wrong semantics). | Hand-edited migration: `DropColumn(Direction)` first, then correct renames + new ILockable fields. | EF scaffolds by type compatibility, not semantic intent. Reviewing every scaffolded migration is non-negotiable. |

#### Phase C.3-lite — Drop `Item.IsKeyItem`, sentinel lockpick KeyId

| Old approach | New approach (Phase C.3-lite) | Reason |
|---|---|---|
| 3 states, 2 columns: `IsKeyItem=0`, `IsKeyItem=1/KeyId=NULL` (lockpick), `IsKeyItem=1/KeyId='foo'` (key). | 2 states, 1 column: `KeyId=NULL` (not a key), `KeyId='lockpick'` (sentinel), `KeyId='foo'` (specific key). | One source of truth. The boolean was redundant the moment lockpicks gained a non-null identifier. |
| Hand-edited migration needed: bare `DropColumn(IsKeyItem)` would have orphaned lockpick rows. | `UPDATE [Items] SET [KeyId] = N'lockpick' WHERE [IsKeyItem] = 1 AND [KeyId] IS NULL` runs before drop. | Same hand-edit discipline as Phase B. Scaffolds reason by type; semantic review is non-negotiable. |

#### Phase C.4 — TryUnlock LSP refactor + InspectForSecretDoors

| Old approach | New approach (Phase C.4) | Reason |
|---|---|---|
| `Character.TryUnlock(Chest, Item)` and `DisarmTrap(Chest, Item)`. Hardcoded to one host type. | Both take `ILockable target`. Same algorithm; doors, chests, and any future `ILockable` plug in with zero changes. | The Liskov payoff. TryUnlock now works on Door, Chest, and anything else that implements ILockable. |
| No player-facing unlock verb for doors. | New `Doors → Try to unlock door` and `Disarm door trap` options. Same picker pattern as chest submenu. | Door-unlock is now a player verb, not an admin override. UX symmetry with chests is intentional. |
| `InspectForSecretDoors` didn't exist. | New `Character.InspectForSecretDoors(IEnumerable<Door>)` — deterministic, wired to `Rooms → Inspect the room`. | Rubric +10% stretch. Deterministic = testable, RNG-free, lower risk for a stretch-goal landing. |

#### Phase D — Graded LINQ, Spectre.Console intro, merged unlock helper

| Feature | Implementation | Reason |
|---|---|---|
| `ShowAllRooms` (Task 4) | Spectre.Console `Table` — sorted LINQ, per-room item/exit counts, "you are here" marker, hides undiscovered secrets from exit count. | Two displays, two audiences: player-facing map vs. admin debug listing. Conflating them would leak unsolved puzzles. |
| `FindKeyLocation` (Task 5) | `.Include(i => i.Container)` — the graded eager-load. Auto-fires inline when an unlock fails with a `RequiredKeyId`. | Hint only shows when it would help: not on lockpick snaps, not when no RequiredKeyId exists. |
| `IContext.QueryItems()` + `QueryContainers()` | New `IQueryable<T>` accessors for the two LINQ tasks that require `.Include()`. | Project standing preference is lazy-loading proxies; `.Include` only where the rubric grades it. New accessors are documented as "use sparingly." |
| `TryUnlockTarget(ILockable)` merge (+5 challenge) | `ChestTryUnlock` + `DoorTryUnlock` collapse into one helper. ~40 LOC removed. | LSP at the UI layer: the same helper, the same flow, regardless of whether the target is a chest or a door. |
| Spectre Panel on `DisplayCurrentRoom` | Room header rendered as a rounded panel with yellow-bold room name, green HP display. | Taste of Spectre.Console before W15 introduces the full split-panel UI. Intro item per W14 README. |

#### File layout deviation — no template split into PlayerService/AdminService/MapManager

The W15 template references `Services/PlayerService.cs`, `Services/AdminService.cs`,
`Helpers/MapManager.cs`, and `Helpers/ExplorationUI.cs` as the intended
architecture. This codebase uses a different shape: `Services/GameEngine.cs`
(monolithic, organized by submenu) + `UI/ConsoleGameUi.cs` / `UI/IGameUi.cs`.

**Why:** The W14 `GameEngine.cs` already has the correct separation of concerns
*within the file* — exploration actions, admin CRUD, LINQ queries, and UI
rendering each live in distinct method groups. Refactoring into the template's
four-file split would rename existing, tested code without changing what it does.
The rubric grades behavior, not filenames. The deviation is documented here and
in `CONTRIBUTIONS.md` so the grader can navigate directly to the equivalent code.

**Equivalent methods for grader reference:**
- Template `PlayerService.PlayerTurn()` → our `GameEngine.ExplorationMenu()`
- Template `AdminService.MonsterCensus()` → our `GameEngine.ShowMonsterCensus()`
- Template `AdminService.FindItemLocation()` → our `GameEngine.FindKeyLocation()`
- Template `MapManager.DrawMap()` → our `GameEngine.ShowAllRooms()`

### W15 Implementation Deviations

#### Phase E — MonsterLoot Eliminated (C0036)

**Decision:** Deleted `MonsterLoot : Container`. NPC loot now lives in the
NPC's `Inventory`, which already existed via the Phase 1.5 Character promotion.

**Why:** The LucentForge bible (Simulation Foundation §2.3–2.4) treats enemies
as agents, not loot containers. An NPC with `alive=false` still owns their
possessions — they don't teleport into a separate bucket. A `MonsterLoot`
container implies the world exists to serve the player; the Inventory model
treats the NPC as a real entity whose belongings happen to become accessible
after death. More honest, and one fewer Container subclass.

**Template divergence:** Template keeps `MonsterLoot`. We dropped it with a
hand-edited migration that atomically moves items before dropping columns.

---

#### Phase F1 — LockedJournal: ILockable on an Item (C0037)

**Decision:** `LockedJournal : Item, ILockable` — a single class that is both
a loot Item and a lockable object. `TryUnlock` is called with zero changes.

**Why:** The W14 Phase C.4 LSP refactor made `TryUnlock(ILockable, Item)`
substitutable — any ILockable works without touching the method. LockedJournal
is the proof: same algorithm, third host type, zero code changes. Gobby's
journal is seeded in Hidden Alcove, locked with the same `dungeon-main` key
that opens the Ornate Chest — one key, three locks.

---

#### Phase F2 — Bookshelf + Tome (C0038)

**Decision:** `Bookshelf : Container` (mirrors Chest: has RoomId FK to Room)
and `Tome : Item` (has LoreText column). Ancient Library room added with Stone
Archway door from Antechamber.

**Why:** The bible's Bits/Bytes magic system needs a home in the schema.
Readable lore objects are also a clean demonstration that Container and Item
TPH are extensible at zero cost to existing code. The three seeded Tomes
include a deliberate narrative contradiction with Gobby's journal — two
accounts of the same event, neither acknowledging the other's framing.

---

#### Phase F3 — Wolf: NPC Subtype (C0039)

**Decision:** `Wolf : Npc` with `PackSize` int property. Seeded at Forest Edge
with Stats, Resources, Inventory, Equipment, and a Raw Wolf Pelt loot item.

**Why:** Phase E needs a second test case. Only proving the Inventory loot path
works for Gobby is not enough — the proof of generalization is a completely
different monster type hitting the same code path. `PackSize` encodes the
bible's swarm principle at the schema level: one wolf is a scout; the number
tells you how many you can't see.

---

#### Phase G — LINQ Queries Submenu (C0040)

**Decision:** Three graded LINQ queries in a `QueriesMenu()` method on
`GameEngine` (not a new `AdminService` class). Wired to main menu option `q`.

**Why:** The template calls for an `AdminService` class. Our `GameEngine`
already has the full character/room/inventory context and all the helper
methods these queries need. Splitting into `AdminService` would be a rename,
not a refactor — thin wrapper calling GameEngine helpers. Better to document
the divergence than to introduce a class for its own sake.

**Queries:**
- `InventoryAudit` — GroupBy container type. Post-Phase-E payoff: monster loot
  shows as `Inventory`, not `MonsterLoot`. The schema unification is visible in
  the output.
- `MostDangerousRoom` — GroupBy room name, Sum current HP. Forest Edge is
  non-trivial after Phase F3.
- `LockedTreasures` — All ILockable entities the active player can't unlock.
  Spans Chests + Doors + LockedJournals — LSP visible at the query layer.

---

#### Phase H — UX Polish (C0041)


**Decision:** `SelectCharacter()` now shows a numbered list and accepts `#` or
partial name search. Main menu reorganized into Game / Admin sections.

**Why:** A verbatim-name prompt with no reference is a friction point during
the presentation demo. The numbered list makes the app navigable without
memorizing database content. Menu sections make it immediately clear which
options are player-facing vs. admin/debug tools.

---

### Post-Grade Polish (C0043–C0055)

These entries document work added after W15 was submitted and graded (115/115).
They extend the submission toward the LucentForge runtime arc.

---

#### Play / Admin Mode Split (C0043)

| Old | New | Reason |
|-----|-----|--------|
| Single menu mixing game and admin options | Startup gate: `p` (Play) / `a` (Admin) / `0` (Exit) | Cleaner demo flow; player mode is self-contained |
| `GetMenuChoice()` was the only entry point | `GetModeChoice()` added to `IGameUi` and `ConsoleGameUi` | SRP: mode selection is distinct from menu selection |

Bug fixed in this commit: `ChestRichestLocked()` crashed with "DataReader already open" because
`c.ItemsCollection` was accessed while an outer query was still streaming. Fix: `.ToList()` before
`.OrderByDescending(c => c.ItemsCollection.Sum(...))`.

---

#### [Flags] Enums (C0044)

| Feature | Decision | Why |
|---------|----------|-----|
| `TrapType` (teacher-suggested) | New `[Flags]` enum: `None/Mechanical/Magical/Poison/Electric` | Chests and doors can have multiple simultaneous trap types; boolean `IsTrapped` can't encode that |
| `SlotType` power-of-2 redesign | Added `[Flags]`, assigned `1<<n` values; `AnyHand = MainHand \| OffHand` | Items can declare multiple eligible slots; bitwise AND replaces equality check in `PickSlotFor` |
| `ILockable.IsTrapped` | Replaced `bool IsTrapped { get; set; }` with `bool IsTrapped => TrapTypes != TrapType.None` (default interface impl) | Single source of truth; IsTrapped is always derived, never stale |
| DB migration | Old sequential SlotType ints (0,1,2...) converted to power-of-2 via `CASE WHEN` SQL | No data loss; existing items automatically get correct new values |

---

#### Room-First Player Loop + Spectre Styling (C0045)

**Decision:** Full `PlayerLoop()` replacing the flat admin-style menu. Key changes:
- Room rendered as a Spectre `Panel` with color-coded HP bar (green/yellow/red threshold)
- Numbered exits + lettered room objects (NPCs, chests, bookshelves, floor items)
- Type dispatch via `_roomObjects: List<object>` field — letter index resolves to runtime type
- `PauseAndClear()` at end of every interaction handler so messages survive the next `Console.Clear()`

NPC dialogue system added: Mira (shop + cellar quest), Gobby (3 HP-gated branches), Erasmus (monologue).
Combat expanded with BitPool/BytePool split — magic correctly draws from the right resource.

---

#### 7-Room Level Redesign (C0051)

| Template world | Our world | Reason |
|----------------|-----------|--------|
| 5 abstract rooms (Forest Edge, Ancient Library, etc.) | 7 narrative rooms (Inn, Cellar, Camp, Path, Chapel, Crypt, Vault) | Story needs a progression arc with a clear beginning (Inn) and boss (Erasmus) |
| No shop NPC | Mira the Innkeeper with interactive shop | LucentForge bible: NPCs are agents, not scenery |
| Grubnak (placeholder name) | Gobby the Outcast Goblin (narrative backstory) | Goblins are scouts, not individual powerhouses; Gobby was exiled, which is why he guards the vault key alone |
| No dialogue | Named dialogue dispatch: `switch(npc.Name)` | Characters should have different interaction models, not a generic "fight or examine" |

Migration C0051 is one of the largest in the project — replaces all room/door/NPC/chest seed data.
Key lessons: Bookshelf uses `[Bookshelf_RoomId]` column (EF TPH name), not `RoomId`; Door INSERT
requires Description (NOT NULL constraint).

---

#### Grid Coordinates + Mini-Map (C0046 / C0053)

**Decision:** `Room.GridX` / `Room.GridY` (nullable int) added. All 7 rooms assigned orthogonal
coordinates. Mini-map renders from these coordinates using H/V connector logic.

**Critical constraint:** All door connections must be strictly horizontal or vertical. Diagonal
connections (e.g., Camp at (0,2) to Path at (1,1)) produce no connector line. Migration C0053
redesigned the grid so Camp, Path, and Chapel all share row1 — eliminating the diagonal.

---

#### AdminResetWorld (C0055)

**Decision:** Admin menu option `r` that restores the game world to its seeded starting state
without touching migrations or the database schema.

**Why:** During development, repeated playtesting changes world state (NPCs die, chests empty,
Elara gets rich). Rather than rolling back migrations, a single reset operation restores all
resources, inventories, lock/trap states, and Elara's starting gear in one `SaveChanges()` call.

---

## Grading Rubric

This assignment is worth **500 points** total, with up to **+50 bonus** available via the stretch goal. The rubric is intentionally tiered so students at different levels can succeed.

| Tier | Points | What it requires |
|------|--------|------------------|
| Base | up to **375** | Run, explore, explain |
| B    | up to **425** | + 2+ LINQ queries |
| A    | up to **475** | + 1 architecture extension (new entity + migration) |
| A+   | up to **500** | + creative addition |
| Stretch (parser port) | **+50** bonus, max **550** | Replace the menu UI with a working text parser |
| **No `CONTRIBUTIONS.md`** | capped at **250** | 50% cap regardless of code quality |

### Required for ALL Tiers: `CONTRIBUTIONS.md`

Every submission must include a completed `CONTRIBUTIONS.md` at the repo root, following the template provided in this directory. It has two parts:

**Sections 1-4 (graded — the gate to all tiers):**
1. Where you started (your own W14 repo, the W15 template, or a hybrid)
2. What you added on top of that starting point
3. What you used from the template / AI / other sources, with attribution
4. A brief reflection on the project (hardest part, what you'd do next)

**Section 5 (NOT graded — honest course feedback):**
A short feedback form covering what you learned, what worked, what didn't, surprises, hardest parts of the semester, what to add or remove from next year's version, and anything else you want me to know. I read this AFTER grades are submitted and use it to revise the course content. A blank or critical answer doesn't affect your grade; the only "wrong" answer is a fake one.

**Without Sections 1-4, the project caps at 250 points (50% of full credit) regardless of code quality.** Using template code with clear attribution is fine and earns full credit; claiming to have written code you didn't is not. During your final presentation I may ask you to walk through any file you describe as "added" or "modified" — be ready.

The file is the gate, not a grade penalty. Filling out the graded sections honestly takes 15 minutes and protects everyone — students who did the work get clearly credited for it, and students who used the template heavily get evaluated on what they actually contributed instead of what's already in the codebase. The feedback section is just a chance to tell me how to make this better next year.

### Base Tier (up to 375 points)

This tier is **comprehension + exploration**. You should be able to:

- [ ] Apply the migrations successfully
- [ ] Explore the entire world (find every room, including the secret shrine)
- [ ] Fight every monster and collect their loot
- [ ] Open every chest in the world (including the trapped one)
- [ ] Use both the Exploration and Admin menus
- [ ] Read and explain in your own words what each of these files does:
  - `Services/GameEngine.cs` (the dispatcher)
  - `Services/PlayerService.cs` (exploration actions)
  - `Services/AdminService.cs` (admin CRUD and LINQ)
  - `Helpers/MapManager.cs` (Spectre map rendering)
  - `Models/Containers/Container.cs` (the TPH base that makes everything tick)

**Everything at this tier is already working in the template.** You do not need to write code — you need to understand it, use it, and be able to discuss it during your final presentation.

### B Tier (up to 425 points)

Add **LINQ queries that answer new questions** about the world. Pick at least TWO of the following and implement them as new methods on `AdminService`:

- [ ] **"Inventory Audit"**: list every item in the game grouped by what kind of container it's in (Inventory, Chest, MonsterLoot, Room floor). Use `GroupBy` and join through `Item.Container`.
- [ ] **"Most Dangerous Room"**: find the room with the highest total monster HP. Use `GroupBy` on `Monster.CurrentRoomId` and `Sum` on Health.
- [ ] **"Locked Treasures"**: list every locked chest OR locked door that the player cannot currently open (i.e. the player doesn't have the required key). Use `Where` with a subquery.
- [ ] **"Floor Sweep"**: find the total gold value of all items lying on the floors of all rooms. Use `OfType<Room>()` + nested `Sum`.
- [ ] **Your own query**: any meaningful LINQ query that answers a question you came up with. Document what it does in a comment.

Wire each new method into the Admin menu so it's callable at runtime.

### A Tier (up to 475 points)

All of the B-tier work, PLUS a **small architecture extension** that requires a new class and a migration. Pick ONE:

- [ ] **Add a new Monster type** (e.g. `Orc`, `Troll`, `Dragon`) with at least one subclass-specific property and a distinctive `Attack()` behavior. Register it in `GameContext`, generate a migration, and add at least one instance to the seed world (by editing `SeedFinalWorld.sql` or a new seed migration).
- [ ] **Add a new Container type** (e.g. `Shop`, `Bookshelf`, `AltarOffering`) as a new TPH subclass. The new container should serve a world-building purpose: a shop exchanges items for gold, a bookshelf holds KeyItems called "tomes" that reveal lore, etc.
- [ ] **Add a new Item type** (e.g. `Scroll`, `Ring`, `Rune`) with subclass-specific behavior. Wire it into `Player.UseItem` or a new method.
- [ ] **Add a new ILockable entity** (e.g. a `LockedJournal`, a `MagicPortal`) that reuses `Player.TryUnlock` without modification. This is the Liskov Substitution payoff: your unlock code should work on it with zero changes.

### A+ Tier (up to 500 points) — Be Creative

Do all of A tier, PLUS show real creativity. Some ideas (not an exhaustive list):

- [ ] **Expand the world** with 5+ new rooms that form a coherent new area (a sewer, a swamp, a noble's manor, a pirate ship, whatever)
- [ ] **Add a shop with buying and selling** using a new Container type and a Gold field on Player
- [ ] **Add a quest system** — a table of active quests with a goal state and a reward
- [ ] **Add a combat abilities upgrade** — buff the existing ShoveAbility with new levels, or add a second ability like `Fireball` or `Heal`
- [ ] **Add save/load slots** so the player can roll back to a previous state
- [ ] **Improve the map rendering** — color-code rooms by biome, add a true "fog of war" where rooms you haven't visited yet are hidden (the template already hides rooms behind undiscovered secret doors — extend that to all unvisited rooms)
- [ ] **Take it somewhere we haven't seen** — a previous student built a WPF frontend for their ConsoleRPG. The data model is yours to play with.

The A+ tier is worth showing off in your final presentation, so pick something you'll enjoy demonstrating.

### Stretch Goal (+50 bonus, max 550)

**Port the Parser Demo to drive the real game.** Replace the SelectionPrompt menu with a Zork-style command line backed by `GameContext`. This is a separate, ambitious extension that goes above the standard 500 — full credit on the rest of your project does NOT require this, but landing it is a significant accomplishment.

See the [Parser Demo](#parser-demo-stretch-goal) section below — the demo in `ConsoleRpg/ParserDemo/ParserDemo.cs` gives you a complete reference to copy from, and the doc-comment block at the top lists the concrete porting steps.

---

## Parser Demo (Stretch Goal)

Open the Admin menu and pick **"Parser Demo (Stretch Goal)"**. You'll be dropped into a self-contained mini-game: one room (West of House from the 1980 original Zork), one mailbox, one leaflet, and a Zork-style text parser. Type `help` to see the verbs.

### What it is

A complete reference implementation of a text parser, living in one file ([ConsoleRpg/ParserDemo/ParserDemo.cs](ConsoleRpg/ParserDemo/ParserDemo.cs)) and sharing **zero** code with the rest of the game. You can delete the entire `ParserDemo/` folder and the game still builds. It's there as something to study, not something the rubric requires you to use.

### What it teaches

Two ideas, both directly applicable to the real game:

1. **The Command pattern as an OCP demonstration.** Every verb is a class implementing `IParserCommand`. The parser holds a `Dictionary<string, IParserCommand>` and dispatches by name. Adding a new verb is one new class plus one new line in the registry — the parser code itself never changes. This is the same Open/Closed payoff you saw with the TPH discriminators in `GameContext`, applied to *behavior* instead of *data*.

2. **A minimal text parser pipeline.** Tokenize → canonicalize the verb (synonym lookup) → dispatch → resolve nouns against visible objects. Real parsers add prepositions and indirect objects ("put leaflet **in** mailbox"); this one stops at `verb [noun]` so you can read the whole pipeline in 15 lines.

### Why it's separate from the main game

The W15 rubric uses Spectre.Console SelectionPrompt menus because menus are accessible — you can play the game without first solving the parsing problem. The parser demo exists for students who want to learn how text input works and have a complete, readable reference to study.

### How to earn the +50 stretch bonus

The stretch goal — **"port the parser to drive the real game"** — sits above the 500-point standard rubric and is worth +50 bonus. Concretely, that means:

- Replace `MockWorld` with `GameContext` + `Player.CurrentRoom`
- Replace `MockItem` with the existing `Item` TPH (`Weapon`, `Armor`, `Consumable`, `KeyItem`)
- Each command class delegates to `PlayerService` instead of mutating local state
- Run the REPL inside `GameEngine.ExplorationTurn` instead of calling `RenderAndPrompt`

When you're done, you've replaced the entire menu UI with a Zork-style command line, using none of the existing UI code. That's a serious project — plan on 4-8 hours — but you start from a working reference and the path is fully documented inside `ParserDemo.cs`.

The doc-comment block at the top of [ParserDemo.cs](ConsoleRpg/ParserDemo/ParserDemo.cs) lists smaller extensions too (new verbs, synonyms, prepositions, disambiguation prompts) ranked easy → hard, so you can dip in at whatever level matches your interest.

---

## Final Presentation

Everyone presents their world in the last class. Prepare:

1. **A 5-minute demo** — walk the class through your world, showing the changes you made
2. **A short explanation** — what rubric tier did you target, what did you add, what was hardest
3. **A code walk-through** — pick ONE file you changed and explain what it does

---

## Tips

- **The admin menu is your friend.** Before writing any new LINQ, use the existing queries to understand the data shape.
- **Check SQL Server Object Explorer** while the game is running. Watch the `Containers`, `Items`, and `Doors` tables update in real time. That's the model layer in action.
- **Read `PlayerService.cs` before modifying `Player.cs`.** Most actions are already wired — you might not need to touch the entity at all.
- **The map rendering uses `Room.X` and `Room.Y`**, so if you add new rooms, give them sensible coordinates and they'll appear on the map automatically.
- **If you break the seed data, reset.** Run `dotnet ef database update 0` to wipe everything, then `dotnet ef database update` to reseed.
- **Ask questions.** W15 is deliberately "here's the framework, go build something." If you're stuck on where to start, ask — I'll be teaching more during office hours than I did any other week.

---

## Reference: LINQ Patterns You'll Use

```csharp
// Find all rooms with monsters
var dangerous = _context.Containers
    .OfType<Room>()
    .Where(r => _context.Monsters.Any(m => m.CurrentRoomId == r.Id && m.Health > 0))
    .ToList();

// Group items by container type
var itemsByLocation = _context.Items
    .Include(i => i.Container)
    .GroupBy(i => i.Container!.ContainerType)
    .Select(g => new { Location = g.Key, Count = g.Count() })
    .ToList();

// Sum the value of everything on every floor
var floorValue = _context.Containers
    .OfType<Room>()
    .SelectMany(r => r.Items)
    .Sum(i => i.Value);

// Find locked containers the player cannot open
var playerKeys = player.Inventory!.Items
    .OfType<KeyItem>()
    .Select(k => k.KeyId)
    .Where(k => k != null)
    .ToHashSet();

var unopenable = _context.Containers
    .OfType<Chest>()
    .Where(c => c.IsLocked && c.RequiredKeyId != null && !playerKeys.Contains(c.RequiredKeyId))
    .ToList();
```

---

## Submission

1. **Fill in `CONTRIBUTIONS.md` at the repo root** (required — see Grading Rubric above)
2. Commit your changes with meaningful messages throughout the project
3. Push to your GitHub Classroom repository
4. Submit the repository URL in Canvas
5. Be ready to present on the final day

---

## Resources

- [Spectre.Console documentation](https://spectreconsole.net/)
- [EF Core TPH Inheritance](https://learn.microsoft.com/en-us/ef/core/modeling/inheritance)
- [EF Core Eager Loading](https://learn.microsoft.com/en-us/ef/core/querying/related-data/eager)
- [LINQ Query Syntax vs Method Syntax](https://learn.microsoft.com/en-us/dotnet/csharp/linq/)
- The **README files for Weeks 12-14** — go back and re-read the discussion sections. They explain the patterns you'll be extending.

---

## Need Help?

- Office hours are expanded for the final week
- Canvas discussion board
- In-class review sessions
- The in-class repository has examples of everything discussed above

Good luck! Build something you'd want to show off.