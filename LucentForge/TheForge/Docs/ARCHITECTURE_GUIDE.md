# Architecture Guide — TheForge (W15 Final State)

How the system is structured, why it evolved this way, and how to extend it.

---

## Week-by-Week Evolution

```
W9    EF Core + IContext         → SQL Server, first migrations
W10   TPH Monsters + Abilities  → CharacterType discriminator
W11   Equipment system          → EquipmentSlot, owned entity
W12   Item + Container TPH      → 5 container subclasses, 4 item subclasses
W13   Chest + ILockable         → lock/trap/key model, MonsterLoot (later eliminated)
W14   Room as Container + Door  → bidirectional door, secret doors
W15+  Player loop, [Flags],     → TrapType/SlotType enums, dialogue system,
      dialogue, grid + map        7-room dungeon, admin reset, mini-map
```

---

## Project Structure

```
TheForge/
├── ConsoleRpg/                          UI & Game Logic
│   ├── Program.cs                       Entry point — mode loop (Play / Admin / Exit)
│   ├── Startup.cs                       Composition root — all DI wiring
│   ├── Services/
│   │   └── GameEngine.cs                All game logic (player loop, admin menus, queries)
│   └── UI/
│       ├── IGameUi.cs                   Display abstraction
│       └── ConsoleGameUi.cs             Spectre.Console + Console implementation
│
└── ConsoleRpgEntities/                  Data & Models
    ├── Data/
    │   ├── IContext.cs                  DIP anchor — all business logic depends on this
    │   └── GameContext.cs               EF Core DbContext — implements IContext
    ├── Models/
    │   ├── Character.cs                 TPH base: Player, Npc, Wolf, Goblin, Undead, Rat
    │   ├── Stats.cs / Resources.cs      Owned entities on Character
    │   ├── Containers/
    │   │   ├── Container.cs             TPH base: Inventory, Equipment, Chest, Bookshelf, Room
    │   │   ├── ILockable.cs             Lock/trap/key contract (+ default IsTrapped impl)
    │   │   ├── Chest.cs / Bookshelf.cs  Container subclasses with RoomId FK
    │   │   ├── Room.cs                  GridX/GridY for mini-map, Characters nav property
    │   │   ├── Inventory.cs / Equipment.cs / EquipmentSlot.cs
    │   ├── Items/
    │   │   ├── Item.cs                  TPH base: Weapon, Armor, Consumable, KeyItem, Tome
    │   │   └── LockedJournal.cs         ILockable item — TryUnlock works with zero changes
    │   ├── Door.cs                      Bidirectional (RoomAId/RoomBId), ILockable
    │   └── Enums/
    │       ├── TrapType.cs              [Flags] — None/Mechanical/Magical/Poison/Electric
    │       ├── SlotType.cs              [Flags] — power-of-2 values, bitwise slot matching
    │       ├── ConsumableEffect.cs      Typed enum replacing magic strings
    │       └── ...other enums
    └── Migrations/                      All hand-reviewed; sequential C#### naming
```

---

## The IContext Abstraction

`IContext` is the DIP anchor. `GameEngine` depends only on it — never on `GameContext` directly.

```csharp
public interface IContext
{
    IEnumerable<Character> Characters { get; }
    IEnumerable<Container> Containers { get; }
    IEnumerable<Item> Items { get; }
    IEnumerable<Door> Doors { get; }

    IQueryable<Item> QueryItems();
    IQueryable<Container> QueryContainers();

    void AddEntity<T>(T entity) where T : class;
    void RemoveEntity<T>(T entity) where T : class;
    void SaveChanges();
}
```

`IEnumerable<T>` hides whether the backing store is lazy-loaded or materialized.
`IQueryable<T>` accessors (`QueryItems`, `QueryContainers`) are available for the two LINQ
operations that need explicit `.Include()` — used sparingly, only where the rubric requires it.

---

## Entity Model

### Character TPH

All characters share the `Characters` table, discriminated by `CharacterType`.

```
Character (abstract-like base)
├── Player          — the active, player-controlled character (Elara)
├── Npc             — named story NPCs (Mira, Erasmus)
│   ├── Goblin      — Gobby the Outcast
│   ├── Wolf        — PackSize property (lone wolf = scout)
│   ├── Undead      — Risen Acolyte, Crypt Hound
│   └── Rat         — Giant Cellar Rat
└── (others via migration)
```

Every Character has:
- `Stats` (owned entity) — Physique, Reflexes, Intuition, etc.
- `Resources` (owned entity) — Hp/MaxHp, Sp/MaxSp, BitPool, BytePool
- `Inventory` (Container nav) — bag of items
- `Equipment` (Container nav) — EquipmentSlots collection
- `RoomId` / `Room` — current location

### Container TPH

All containers share the `Containers` table, discriminated by `ContainerType`.

```
Container
├── Inventory       — owned by a Character (OwnerCharacterId FK)
├── Equipment       — owned by a Character (OwnerCharacterId FK)
├── Chest           — placed in a Room (RoomId FK); implements ILockable
├── Bookshelf       — placed in a Room (Bookshelf_RoomId FK — TPH column name)
└── Room            — the location entity; has GridX/GridY for mini-map
```

### Item TPH

All items share the `Items` table, discriminated by `ItemType`.

```
Item
├── Weapon          — AttackPower, WeaponType, Durability
├── Armor           — DefenseRating, ArmorWeight, BodySlot
├── Consumable      — ConsumableEffect (typed enum), Potency
├── KeyItem         — KeyId string (sentinel "lockpick" for lockpicks)
├── Tome            — Title, LoreText
└── LockedJournal   — implements ILockable (TryUnlock works with zero changes)
```

### Door

One row per passage. Bidirectional via `RoomAId` / `RoomBId`.

```csharp
public Room GetOtherRoom(Room current)
    => current.Id == RoomAId ? RoomB! : RoomA!;
```

Implements `ILockable` — same `TryUnlock` helper works on Door, Chest, and LockedJournal.

---

## [Flags] Enums

### TrapType (teacher-suggested)

```csharp
[Flags]
public enum TrapType
{
    None       = 0,
    Mechanical = 1 << 0,   // dart/spike — physical disarm
    Magical    = 1 << 1,   // arcane ward — Intuition check
    Poison     = 1 << 2,   // inflicts DoT on trigger
    Electric   = 1 << 3,   // instant stun/paralysis
}
```

`ILockable.IsTrapped` is a default interface implementation:
```csharp
bool IsTrapped => TrapTypes != TrapType.None;
```

### SlotType (power-of-2 for bitwise matching)

```csharp
[Flags]
public enum SlotType
{
    None     = 0,
    MainHand = 1 << 0,
    OffHand  = 1 << 1,
    Head     = 1 << 2,
    Chest    = 1 << 3,
    Legs     = 1 << 4,
    Feet     = 1 << 5,
    Hands    = 1 << 6,
    AnyHand  = MainHand | OffHand,
}
```

`Item.EligibleSlot` stores a flags value. A dagger seeded with `MainHand | OffHand` will equip
in either hand. `Character.PickSlotFor` uses bitwise AND: `(item.EligibleSlot & slot.Slot) != 0`.

---

## ILockable Interface (LSP Payoff)

```csharp
public interface ILockable
{
    bool IsLocked { get; set; }
    bool IsPickable { get; set; }
    bool TrapDisarmed { get; set; }
    int TrapDamage { get; set; }
    TrapType TrapTypes { get; set; }
    string? RequiredKeyId { get; set; }
    bool IsTrapped => TrapTypes != TrapType.None;   // default impl
}
```

`TryUnlockTarget(ILockable target, Character player)` in GameEngine works identically whether
`target` is a Chest, Door, or LockedJournal. Adding a fourth ILockable type requires zero changes
to the unlock method.

---

## Room Grid + Mini-Map

`Room` has `GridX` and `GridY` (nullable ints). The 7 seeded rooms occupy:

```
col0     col1     col2
row0:  Cellar   Inn
row1:  Camp     Path    Chapel
row2:                   Crypt
row3:                   Vault
```

All door connections are orthogonal (horizontal or vertical). Diagonal connections do not render
connectors in the ASCII map. `DrawMiniMap()` in GameEngine:
1. Loads all rooms where GridX/GridY is not null
2. Loads all doors to compute adjacency
3. Renders a `string[rows,cols]` grid with room abbreviations
4. Draws H connectors (`───`) between rooms in the same row with a door between them
5. Draws V connectors (`│`) between rooms in the same column with a door between them
6. Marks the current room with `*` and yellow-bold Spectre markup
7. Wraps the result in a Spectre `Panel`

---

## Play Mode — Player Loop

`PlayerLoop()` in GameEngine drives the play experience:

```
1. Console.Clear()
2. DrawRoomPanel()    — Spectre Panel: room name, HP bar, room description
3. DrawRoomContents() — numbered exits + lettered room objects
4. Read input:
   - "#"    → TakeExitByIndex()
   - letter → HandleRoomObjectInteraction() → dispatch by type
   - "i"    → InventoryMenu()
   - "m"    → DrawMiniMap()
   - "x"    → InspectRoomForSecrets()
   - "q"    → return
```

Room objects are tracked in `_roomObjects: List<object>` (field on GameEngine). Letters `a, b, c...`
map to indices in that list. Type dispatch:
- `Character npc` → `PlayerNpcInteraction()` → named dialogue or generic interact menu
- `Chest` → `PlayerChestInteraction()`
- `Bookshelf` → `PlayerBookshelfInteraction()`
- `Item` (floor) → `PlayerFloorItemInteraction()`

Every interaction handler calls `_gameUi.PauseAndClear()` before returning so the player
can read the outcome message before the room re-renders.

---

## NPC Dialogue System

`PlayerNpcInteraction()` dispatches on `npc.Name`:

| NPC | Handler | Notes |
|-----|---------|-------|
| Mira the Innkeeper | `MiraDialogue()` | Shop, lore, cellar quest, reward |
| Gobby | `GobbyDialogue()` | 3 pre-fight branches based on HP threshold |
| Erasmus the Unbound | `ErasmusDialogue()` | Boss monologue before combat |
| All others | Generic interact menu | Fight / Examine / Loot |

`_cellarRewarded: bool` field on GameEngine gates Mira's cellar-cleared reward to fire only once.
`IsCellarCleared()` checks that all enemy NPCs in Inn Cellar (Rat) have Hp ≤ 0.

---

## Admin Mode

`Program.cs` presents a mode gate on startup: `p` (Play), `a` (Admin), `0` (Exit).

Admin menu options in `GetMenuChoice()`:

| Key | Action |
|-----|--------|
| 1 | Characters submenu (CRUD) |
| 2 | Items submenu (CRUD) |
| 3 | Rooms & Doors submenu |
| 4 | Skills submenu |
| 5 | Abilities submenu |
| 6 | Magic submenu |
| 7 | Inventory (player bag view) |
| 8 | Chests & Loot |
| 9 | Bookshelves |
| q | Queries (InventoryAudit, MostDangerousRoom, LockedTreasures, ChestRichestLocked) |
| r | Reset World |
| 0 | Exit |

---

## AdminResetWorld

`AdminResetWorld()` restores the game world to its seeded starting state:

1. Reset all enemy NPC resources to full (Hp, Sp, BitPool, BytePool)
2. Clear and restock NPC inventories (Gobby, Rat, Undead, Hound, Erasmus)
3. Re-lock Vault Gate; re-arm Chapel Gate trap
4. Restore chest contents and lock/trap states
5. Reset Elara: clear inventory/equipment → Iron Sword (MainHand) + Leather Vest (Chest) + 1 Healing Potion; move to Inn
6. Restore Mira's shop stock
7. Restore Thornwood Path herbs
8. Clear `_visitedRooms`

---

## SOLID Principles in Action

| Principle | Where it shows up |
|-----------|-------------------|
| **SRP** | `Program.cs` = entry/mode loop only; `Startup.cs` = DI wiring only; `ConsoleGameUi` = I/O only; `GameEngine` = business logic only |
| **OCP** | New ILockable type → zero changes to TryUnlock. New Container subclass → zero changes to IContext. |
| **LSP** | `TryUnlockTarget(ILockable)` works on Chest, Door, and LockedJournal interchangeably |
| **ISP** | `IContext`, `IGameUi`, `ILockable` — each interface serves one consumer's needs |
| **DIP** | GameEngine depends on `IContext` and `IGameUi`; only `Startup.cs` knows the concrete types |

---

## Migration Conventions

All migrations follow sequential commit numbering: `C0035_PhaseName`, `C0036_...` etc.
Every scaffolded migration is hand-reviewed before applying — EF resolves by type compatibility,
not semantic intent. TPH column name collisions (`Bookshelf_RoomId` vs `RoomId`) are common
and must be checked manually.

Migration commands:
```bash
dotnet ef migrations add C####_Name --project ConsoleRpgEntities --startup-project ConsoleRpg
dotnet ef database update --project ConsoleRpgEntities --startup-project ConsoleRpg
```
