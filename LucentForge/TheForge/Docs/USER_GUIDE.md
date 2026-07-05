# User Guide — TheForge (W15 Final State)

How to build, run, and use the application.

---

## Prerequisites

- **.NET 10 SDK** (or later)
- **Network access to WCTC SQL Server** (`bitsql.wctc.edu`)

Verify .NET is installed:
```bash
dotnet --version
```

---

## Build and Run

From the solution root:
```bash
dotnet run --project ConsoleRpg --no-launch-profile
```

Or build first, then run:
```bash
dotnet build
dotnet run --project ConsoleRpg --no-launch-profile
```

---

## Database Setup

Connects to `bitsql.wctc.edu`, database `w9_efcore_SDunn`.

Connection string loaded from config (never hardcoded):
1. `ConsoleRpg/appsettings.json` — committed placeholder
2. `ConsoleRpg/appsettings.Development.json` — real credentials, gitignored

To set up on a new machine: copy `appsettings.json`, rename to `appsettings.Development.json`,
replace the placeholder password with your real SQL credential.

**First run:** migrations apply automatically. To apply manually:
```bash
dotnet ef database update --project ConsoleRpgEntities --startup-project ConsoleRpg
```

To reset the database completely:
```bash
dotnet ef database update 0 --project ConsoleRpgEntities --startup-project ConsoleRpg
dotnet ef database update   --project ConsoleRpgEntities --startup-project ConsoleRpg
```

---

## Mode Selection

On launch you see the title banner and a mode prompt:

```
  p. Play
  a. Admin
  0. Exit
```

- **p — Play** prompts you to select a character, then enters the player loop
- **a — Admin** opens the admin menu loop
- **0 — Exit** quits

---

## Play Mode

### Selecting a Character

A numbered list of available characters is shown. Enter the number or type a partial name.
Elara is the primary player character seeded in The Wayward Crow Inn.

### The Room Display

Each tick shows:
```
╭─ The Wayward Crow Inn ───────────────────────────────╮
│  [green]HP 35/35[/]   Elara · Lv 1 Player           │
╰──────────────────────────────────────────────────────╯
  A warm inn at the edge of Thornwood. Mira tends the bar.

  Exits:
    [1] Cellar Stairs → Inn Cellar
    [2] Thornwood Gate → Thornwood Path

  Here:
    [a] Mira the Innkeeper (Npc) — HP 30/30
    [b] Merchant's Lockbox — open

  [#] move  [letter] interact  [i] inventory  [m] map  [x] inspect  [q] quit
```

### Controls

| Input | Action |
|-------|--------|
| `1`, `2`, `3`... | Move through the numbered exit |
| `a`, `b`, `c`... | Interact with the lettered room object |
| `i` | Open inventory menu |
| `m` | Show ASCII mini-map |
| `x` | Inspect room for secret doors |
| `q` | Return to mode select |

### Interacting with NPCs

Letter input on an NPC opens an interaction menu based on their status:

**Alive NPC:**
- `(f)ight` — enter combat
- `(t)alk` — dialogue (for story NPCs: Mira, Gobby, Erasmus)
- `(e)xamine` — see HP/ATK/DEF stats
- `(c)ancel`

**Defeated NPC:**
- `(l)oot` — open their inventory for looting
- `(e)xamine`
- `(c)ancel`

### NPC Dialogue

**Mira the Innkeeper** — In the Wayward Crow Inn:
- Greets you with inn lore
- Option to browse her shop (potions, lockpicks)
- Will reward you after you clear the cellar (Giant Cellar Rat)
- Responds differently after the world changes

**Gobby the Outcast Goblin** — In Goblin Camp:
- 3 dialogue branches depending on his HP (fresh / wounded / barely standing)
- Always leads to combat if you choose to fight

**Erasmus the Unbound** — In The Sealed Vault:
- Delivers a monologue before combat begins ("At last — a worthy audience...")
- Combat starts automatically after the monologue

### Combat

When you fight an NPC, a round-by-round loop runs until one side reaches 0 HP:

```
  ⚔  Elara vs. Gobby!

  Round 1: You hit for [red]8[/]. Gobby HP: 12/20
  Round 1: Gobby hits for [red]4[/]. Your HP: [green]31[/]/35
  Round 2: You hit for [red]12[/]. Gobby HP: 0/20

  Gobby defeated!
  Loot? (y/n):
```

Combat options (if available):
- `⚔  Attack` — basic weapon attack
- `🛡  Defend` — raise defense for one round
- `🌀  Skill` — use a skill (if SP available)
- `⚡  Magic` — use attack magic (if BitPool/BytePool available)
- `🧪  Heal` — use healing magic (if available)
- `💊  Item` — use a consumable

If you are defeated, you rest at 1 HP.

### Chests

Letter input on a chest:
- `(o)pen` — if unlocked, opens the chest and lets you loot or take all
- `(u)nlock` — pick a key from your bag (lockpick or specific key)
- `(d)isarm` — attempt to disarm the trap before opening
- `(e)xamine` — describes the chest
- `(c)ancel`

Locks and traps are not announced until you examine or interact with the chest.
Traps fire when the chest is opened while armed — you take `TrapDamage` HP.

### Bookshelves

Letter input on a bookshelf shows a numbered list of books. Select one to read it.

### Floor Items

Letter input on a floor item:
- `(p)ick up` — add to inventory
- `(e)xamine` — shows value and weight
- `(c)ancel`

### Mini-Map

Press `m` at any time in the player loop. The map shows all rooms with known grid coordinates,
connected by lines where doors exist. Your current room is marked with `*` in yellow.

```
╭─ World Map ───────────────────────────────╮
│  ┌──────┐                                 │
│  │CELLAR│──┌──────┐                       │
│  └──────┘  │*INN* │                       │
│            └──┬───┘                       │
│  ┌──────┐──┌──┴───┐──┌──────┐            │
│  │ CAMP │  │ PATH │  │CHAPL │            │
│  └──────┘  └──────┘  └──┬───┘            │
│                         │                │
│                       ┌─┴────┐           │
│                       │CRYPT │           │
│                       └──┬───┘           │
│                        ┌─┴────┐          │
│                        │VAULT │          │
│                        └──────┘          │
╰───────────────────────────────────────────╯
```

### Secret Doors

Press `x` (Inspect Room) to search for hidden doors. If the room contains a secret door,
it becomes visible in the exits list. Not all rooms have secrets.

---

## Admin Mode

Admin menu options:

| Key | Submenu | What it does |
|-----|---------|-------------|
| `1` | Characters | List, add, find, level up, delete characters |
| `2` | Items | List, add, find, delete items |
| `3` | Rooms & Doors | List rooms, list doors, add room, add door |
| `4` | Skills | List, add, assign skills |
| `5` | Abilities | List, add, assign abilities |
| `6` | Magic | List, add, assign magic spells |
| `7` | Inventory | View and manage any character's bag |
| `8` | Chests & Loot | Inspect and manage chest contents |
| `9` | Bookshelves | Inspect bookshelf contents |
| `q` | Queries | LINQ query reports (see below) |
| `r` | Reset World | Restore everything to starting state |
| `0` | — | Return to mode select |

### Queries Menu

| Query | What it shows |
|-------|--------------|
| Inventory Audit | GroupBy container type — how many items are in Inventory vs Chest vs on floor |
| Most Dangerous Room | Room with the highest total current NPC HP |
| Locked Treasures | All ILockable entities the active player cannot currently open |
| Chest: Richest Locked | The locked chest with the highest total item value |

### Reset World

Available in Admin menu (`r`). Prompts for confirmation, then:
- Restores all enemy NPC HP/resources to full
- Restocks all NPC inventories
- Re-locks and re-arms doors and chests to starting state
- Resets Elara to the Inn with starting gear (Iron Sword, Leather Vest, 1 Healing Potion)
- Restores Mira's shop and world items

This is the safe way to replay the dungeon without touching the database.

---

## The World

7 rooms forming a linear-with-branches dungeon:

| Room | Connections | Notable |
|------|-------------|---------|
| Inn Cellar | ↕ Inn | Giant Cellar Rat; Cellar Cask chest |
| The Wayward Crow Inn | ↔ Cellar, ↕ Path | Mira (shop, lore, quest reward) |
| Goblin Camp | ↔ Path | Gobby (vault key in his bag) |
| Thornwood Path | ↔ Camp, ↔ Chapel, ↕ Inn | Camp Crate chest |
| Ruined Chapel | ↔ Path, ↕ Crypt | Chapel Gate (locked + trapped); Altar Chest |
| Crypt Entrance | ↕ Chapel, ↕ Vault | Risen Acolyte, Crypt Hound |
| The Sealed Vault | ↕ Crypt | Erasmus the Unbound (boss); Sealed Reliquary |

**Progression hint:** Gobby carries the vault_key. The Vault Gate requires it. The Chapel Gate
is both locked and trapped — disarm the trap before unlocking. Inn Cellar clearing triggers
Mira's reward dialogue.

---

## Migration Commands

```bash
# Add a new migration
dotnet ef migrations add C####_Name --project ConsoleRpgEntities --startup-project ConsoleRpg

# Apply pending migrations
dotnet ef database update --project ConsoleRpgEntities --startup-project ConsoleRpg

# View migration status
dotnet ef migrations list --project ConsoleRpgEntities --startup-project ConsoleRpg

# Full reset
dotnet ef database update 0 --project ConsoleRpgEntities --startup-project ConsoleRpg
dotnet ef database update   --project ConsoleRpgEntities --startup-project ConsoleRpg
```
