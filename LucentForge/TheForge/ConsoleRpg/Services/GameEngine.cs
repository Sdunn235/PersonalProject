using ConsoleRpg.UI;
using ConsoleRpgEntities.Data;
using ConsoleRpgEntities.Models;
using ConsoleRpgEntities.Models.Abilities;
using ConsoleRpgEntities.Models.Containers;
using ConsoleRpgEntities.Models.Enums;
using ConsoleRpgEntities.Models.Items;
using ConsoleRpgEntities.Models.Races;
using ConsoleRpgEntities.Models.Skills;
using Microsoft.EntityFrameworkCore;
using Spectre.Console;
using MagicEntity = ConsoleRpgEntities.Models.Magic.Magic;

namespace ConsoleRpg.Services;

public class GameEngine
{
    private readonly IContext _dbContext;
    private readonly IGameUi _gameUi;

    // W12: active character concept — set via SelectCharacter, used by detail/inventory/equip.
    private Character? _activeCharacter;

    public GameEngine(IContext dbContext, IGameUi gameUi)
    {
        _dbContext = dbContext;
        _gameUi = gameUi;
    }

    public string? ActiveCharacterLabel =>
        _activeCharacter is null ? null : $"{_activeCharacter.Name} ({_activeCharacter.TypeName})";

    public bool HasActiveCharacter => _activeCharacter is not null;

    // Startup data-integrity sweep:
    //   1. Stats row must exist for every Character (default to all zeros).
    //   2. EquipmentSlots must only hold items whose EligibleSlot matches the slot.
    //      Bad rows from manual SQL inserts get nulled out so the equip pipeline is the
    //      only legal entry point.
    public void EnsureCharacterIntegrity()
    {
        // Materialize everything up-front. With lazy-loading proxies + a single
        // active DataReader, comparisons like `c.Stats == null` mid-enumeration
        // throw "There is already an open DataReader" — so we pull each set
        // fully into memory and compare via projected ID lookups instead.

        // 1. Backfill missing Stats rows.
        var characters = _dbContext.Characters.ToList();
        var statsCharacterIds = _dbContext.Stats.Select(s => s.CharacterId).ToHashSet();

        var orphans = characters.Where(c => !statsCharacterIds.Contains(c.Id)).ToList();
        foreach (var c in orphans)
            _dbContext.AddEntity(new Stats { CharacterId = c.Id });
        if (orphans.Count > 0)
            _dbContext.SaveChanges();

        // 2. Sweep EquipmentSlots for slot/item mismatches. Pull all items
        // first so we can resolve EquippedItemId without triggering proxy loads.
        var slots = _dbContext.EquipmentSlots
            .Where(s => s.EquippedItemId != null)
            .ToList();
        var itemsById = _dbContext.Items.ToList().ToDictionary(i => i.Id);

        int slotsCleared = 0;
        foreach (var slot in slots)
        {
            if (slot.EquippedItemId is not int itemId) continue;
            if (!itemsById.TryGetValue(itemId, out var item)) continue;

            // Shields are valid in either MainHand or OffHand.
            // W15 Phase H: bitwise & because SlotType is now [Flags].
            bool valid;
            if (item is Shield)
                valid = (slot.Slot & (SlotType.MainHand | SlotType.OffHand)) != 0;
            else
                valid = item.EligibleSlot.HasValue && (item.EligibleSlot.Value & slot.Slot) != 0;

            if (!valid)
            {
                slot.EquippedItemId = null;
                slotsCleared++;
            }
        }

        if (slotsCleared > 0) _dbContext.SaveChanges();

        // 3. Phase 1.5: every Character gets Inventory + Equipment containers.
        // Backfill for any pre-existing character (Player, NPC, Animal) that
        // doesn't have them. Re-fetch character list — IDs are stable but
        // EnsureContainersFor calls SaveChanges and we want a clean snapshot.
        int containersBackfilled = 0;
        foreach (var c in _dbContext.Characters.ToList())
        {
            if (EnsureContainersFor(c)) containersBackfilled++;
        }

        if (orphans.Count > 0 || slotsCleared > 0 || containersBackfilled > 0)
            Console.WriteLine($"[Startup] Integrity sweep: backfilled {orphans.Count} Stats row(s), cleared {slotsCleared} invalid equipment slot(s), backfilled containers for {containersBackfilled} character(s).");
    }

    // -------------------------------------------------------------------------
    // Character CRUD
    // -------------------------------------------------------------------------

    public void DisplayCharacters()
    {
        var characters = _dbContext.Characters.ToList();

        if (!characters.Any())
        {
            Console.WriteLine("\nNo characters found in the database.");
            return;
        }

        Console.WriteLine("\n=== Characters ===\n");
        foreach (var c in characters)
        {
            string raceLabel = c.Race?.Name ?? "No Race";
            string roomLabel = c.Room?.Name ?? "No Room";
            Console.WriteLine($"  [{c.Id}] {c.Name} ({c.TypeName}) (Lv {c.Level}) — {raceLabel} — Room: {roomLabel}");
        }
    }

    public void SelectCharacter()
    {
        var all = _dbContext.Characters.ToList();
        if (!all.Any()) { Console.WriteLine("\nNo characters in database."); return; }

        Console.WriteLine("\n--- Characters ---");
        for (int i = 0; i < all.Count; i++)
        {
            var c = all[i];
            string room = c.Room?.Name ?? "no room";
            Console.WriteLine($"  {i + 1,3}. [{c.Id,3}] {c.Name,-20} ({c.TypeName}, Lv {c.Level}) — {room}");
        }

        Console.Write("Select # or type part of a name: ");
        var input = Console.ReadLine()?.Trim() ?? string.Empty;

        Character? character;
        if (int.TryParse(input, out int idx) && idx >= 1 && idx <= all.Count)
            character = all[idx - 1];
        else
            character = all.FirstOrDefault(c => c.Name.Contains(input, StringComparison.OrdinalIgnoreCase));

        if (character is null) { Console.WriteLine("\nCharacter not found."); return; }

        _activeCharacter = character;
        Console.WriteLine($"\nActive character set: [{character.Id}] {character.Name} ({character.TypeName}, Level {character.Level})");
    }

    // Back-compat shim in case anything still references FindCharacter.
    public void FindCharacter() => SelectCharacter();

    public void AddCharacter()
    {
        Console.Write("Character name: ");
        var name = Console.ReadLine() ?? string.Empty;

        Console.Write("Level: ");
        if (!int.TryParse(Console.ReadLine(), out var level))
        {
            Console.WriteLine("Invalid level.");
            return;
        }

        Console.WriteLine("\nCharacter type:");
        Console.WriteLine("  1. Player  (the hero character — playable race required)");
        Console.WriteLine("  2. NPC     (non-player character — shopkeeper, quest giver, enemy)");
        Console.WriteLine("  3. Animal  (wildlife — wolves, birds, etc.)");
        Console.Write("Choice: ");
        var typeChoice = Console.ReadLine()?.Trim();

        var races = _dbContext.Races.ToList();
        if (races.Any())
        {
            Console.WriteLine("\nAvailable Races:");
            foreach (var r in races)
                Console.WriteLine($"  [{r.Id}] {r.Name} ({r.GetType().BaseType?.Name ?? r.GetType().Name})");
        }

        Console.Write("Race ID (or blank for none): ");
        var raceInput = Console.ReadLine()?.Trim();
        int? raceId = null;
        Race? selectedRace = null;

        if (!string.IsNullOrEmpty(raceInput) && int.TryParse(raceInput, out var rid))
        {
            selectedRace = races.FirstOrDefault(r => r.Id == rid);
            if (selectedRace != null)
                raceId = rid;
        }

        var rooms = _dbContext.Rooms.ToList();
        if (rooms.Any())
        {
            Console.WriteLine("\nAvailable Rooms:");
            foreach (var r in rooms)
                Console.WriteLine($"  [{r.Id}] {r.Name}");
        }

        Console.Write("Room ID (or blank for none): ");
        var roomInput = Console.ReadLine()?.Trim();
        int? roomId = null;
        if (!string.IsNullOrEmpty(roomInput) && int.TryParse(roomInput, out var rmId))
        {
            if (rooms.Any(r => r.Id == rmId))
                roomId = rmId;
        }

        Character character;
        switch (typeChoice)
        {
            case "1":
                if (selectedRace != null && selectedRace is not PlayableRace)
                {
                    Console.WriteLine("Players can only be assigned a Playable race.");
                    return;
                }
                character = new Player { Name = name, Level = level, RoomId = roomId, RaceId = raceId };
                break;
            case "2":
                character = new Npc { Name = name, Level = level, RoomId = roomId, RaceId = raceId };
                break;
            case "3":
                character = new Animal { Name = name, Level = level, RoomId = roomId, RaceId = raceId };
                break;
            default:
                Console.WriteLine("Invalid type.");
                return;
        }

        _dbContext.AddEntity(character);
        _dbContext.SaveChanges();

        // Stats default to 0 — never null. Edit via Edit Character menu to raise them.
        var stats = new Stats
        {
            CharacterId = character.Id,
            Physique = 0, Reflexes = 0, Constitution = 0,
            Intellect = 0, Intuition = 0, Linguistic = 0, Luck = 0
        };
        _dbContext.AddEntity(stats);
        _dbContext.SaveChanges();
        character.Stats = stats;

        var resources = new Resources
        {
            CharacterId = character.Id,
            Hp = character.DeriveMaxHp(), MaxHp = character.DeriveMaxHp(),
            Sp = character.DeriveMaxSp(), MaxSp = character.DeriveMaxSp(),
            BitPool = character.DeriveMaxBitPool(), MaxBitPool = character.DeriveMaxBitPool(),
            BytePool = character.DeriveMaxBytePool(), MaxBytePool = character.DeriveMaxBytePool()
        };
        _dbContext.AddEntity(resources);
        _dbContext.SaveChanges();

        // Phase 1.5: every character gets empty Inventory + Equipment containers
        // and a full set of 7 EquipmentSlots — Player, NPC, and Animal alike.
        EnsureContainersFor(character);

        Console.WriteLine($"\n{character.TypeName} '{name}' created.");
    }

    // Backfill empty Inventory + Equipment + EquipmentSlots for any character that
    // doesn't already have them. Used at character creation and during the startup
    // integrity sweep. Saves immediately. Returns true if anything was created.
    private bool EnsureContainersFor(Character character)
    {
        bool changed = false;

        bool hasInventory = _dbContext.Containers
            .OfType<Inventory>()
            .Any(i => i.OwnerCharacterId == character.Id);
        if (!hasInventory)
        {
            var inv = new Inventory
            {
                Name = $"{character.Name}'s Pack",
                OwnerCharacterId = character.Id,
                MaxWeight = 100
            };
            _dbContext.AddEntity(inv);
            changed = true;
        }

        bool hasEquipment = _dbContext.Containers
            .OfType<Equipment>()
            .Any(e => e.OwnerCharacterId == character.Id);
        if (!hasEquipment)
        {
            var eq = new Equipment
            {
                Name = $"{character.Name}'s Gear",
                OwnerCharacterId = character.Id
            };
            _dbContext.AddEntity(eq);
            _dbContext.SaveChanges(); // need eq.Id before seeding slots
            changed = true;

            // One slot per SlotType enum value, all empty.
            foreach (SlotType slotType in Enum.GetValues<SlotType>())
            {
                _dbContext.AddEntity(new EquipmentSlot
                {
                    CharacterId = character.Id,
                    Slot = slotType,
                    EquippedItemId = null,
                    EquipmentContainerId = eq.Id
                });
            }
        }

        if (changed) _dbContext.SaveChanges();
        return changed;
    }

    public void LevelUpCharacter()
    {
        var character = ResolveActiveOrPrompt("level up");
        if (character is null) return;

        character.Level++;
        _dbContext.SaveChanges();
        Console.WriteLine($"\n{character.Name} is now level {character.Level}!");
    }

    // -------------------------------------------------------------------------
    // Edit Character — submenu over Identity / Stats / Abilities / Spells /
    // Equipment / Inventory. Each leaf saves changes after the user confirms.
    // -------------------------------------------------------------------------

    public void EditCharacter()
    {
        var character = ResolveActiveOrPrompt("edit");
        if (character is null) return;

        while (true)
        {
            Console.WriteLine($"\n=== Edit: {character.Name} ({character.TypeName}) ===");
            Console.WriteLine("  1. Identity (Name, Level, Race, Room)");
            Console.WriteLine("  2. Stats");
            Console.WriteLine("  3. Abilities");
            Console.WriteLine("  4. Spells / Magic");
            Console.WriteLine("  5. Equipment");
            Console.WriteLine("  6. Inventory");
            Console.WriteLine("  0. Done");
            Console.Write("Choice: ");
            var choice = Console.ReadLine()?.Trim();

            switch (choice)
            {
                case "1": EditIdentity(character); break;
                case "2": EditStats(character); break;
                case "3": EditAbilities(character); break;
                case "4": EditSpells(character); break;
                case "5": EditEquipment(character); break;
                case "6": EditInventory(character); break;
                case "0": return;
                default: Console.WriteLine("Invalid choice."); break;
            }
        }
    }

    private void EditIdentity(Character c)
    {
        Console.Write($"\nName [{c.Name}] (blank to keep): ");
        var name = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(name)) c.Name = name.Trim();

        Console.Write($"Level [{c.Level}] (blank to keep): ");
        var lvl = Console.ReadLine();
        if (int.TryParse(lvl, out var newLvl)) c.Level = newLvl;

        var races = _dbContext.Races.ToList();
        if (races.Any())
        {
            Console.WriteLine("\nAvailable Races (blank=no change, 0=clear):");
            foreach (var r in races)
                Console.WriteLine($"  [{r.Id}] {r.Name}");
            Console.Write($"Race ID [current: {c.Race?.Name ?? "None"}]: ");
            var raceInput = Console.ReadLine()?.Trim();
            if (int.TryParse(raceInput, out var rid))
            {
                if (rid == 0) { c.RaceId = null; }
                else if (races.Any(r => r.Id == rid))
                {
                    if (c is Player && races.First(r => r.Id == rid) is not PlayableRace)
                        Console.WriteLine("Players require a Playable race — leaving unchanged.");
                    else c.RaceId = rid;
                }
            }
        }

        var rooms = _dbContext.Rooms.ToList();
        if (rooms.Any())
        {
            Console.WriteLine("\nAvailable Rooms (blank=no change, 0=clear):");
            foreach (var r in rooms)
                Console.WriteLine($"  [{r.Id}] {r.Name}");
            Console.Write($"Room ID [current: {c.Room?.Name ?? "None"}]: ");
            var roomInput = Console.ReadLine()?.Trim();
            if (int.TryParse(roomInput, out var rmId))
            {
                if (rmId == 0) c.RoomId = null;
                else if (rooms.Any(r => r.Id == rmId)) c.RoomId = rmId;
            }
        }

        _dbContext.SaveChanges();
        Console.WriteLine("Identity updated.");
    }

    private void EditStats(Character c)
    {
        if (c.Stats is null)
        {
            // Defensive — backfill should prevent this, but never trust assumed state.
            var fresh = new Stats { CharacterId = c.Id };
            _dbContext.AddEntity(fresh);
            _dbContext.SaveChanges();
            c.Stats = fresh;
        }

        var s = c.Stats;
        var stats = new (string Label, Func<int> Get, Action<int> Set)[]
        {
            ("Physique",     () => s.Physique,     v => s.Physique = v),
            ("Reflexes",     () => s.Reflexes,     v => s.Reflexes = v),
            ("Constitution", () => s.Constitution, v => s.Constitution = v),
            ("Intellect",    () => s.Intellect,    v => s.Intellect = v),
            ("Intuition",    () => s.Intuition,    v => s.Intuition = v),
            ("Linguistic",   () => s.Linguistic,   v => s.Linguistic = v),
            ("Luck",         () => s.Luck,         v => s.Luck = v),
        };

        while (true)
        {
            Console.WriteLine($"\n--- Stats: {c.Name} ---");
            for (int i = 0; i < stats.Length; i++)
                Console.WriteLine($"  {i + 1}. {stats[i].Label,-13} {stats[i].Get()}");
            Console.WriteLine("  0. Back");
            Console.Write("Pick stat to edit: ");
            var pick = Console.ReadLine()?.Trim();
            if (pick == "0") return;
            if (!int.TryParse(pick, out var idx) || idx < 1 || idx > stats.Length)
            {
                Console.WriteLine("Invalid."); continue;
            }

            Console.Write($"New {stats[idx - 1].Label} value: ");
            if (!int.TryParse(Console.ReadLine(), out var v) || v < 0)
            {
                Console.WriteLine("Stats must be non-negative integers."); continue;
            }
            stats[idx - 1].Set(v);
            _dbContext.SaveChanges();
            Console.WriteLine($"{stats[idx - 1].Label} = {v}.");
        }
    }

    private void EditAbilities(Character c)
    {
        while (true)
        {
            Console.WriteLine($"\n--- Abilities: {c.Name} ---");
            if (c.Abilities.Any())
                foreach (var a in c.Abilities)
                    Console.WriteLine($"  [{a.Id}] {a.Name} (Power {a.Power})");
            else
                Console.WriteLine("  (none)");

            Console.WriteLine("  1. Add ability   2. Remove ability   0. Back");
            Console.Write("Choice: ");
            var ch = Console.ReadLine()?.Trim();
            if (ch == "0") return;

            if (ch == "1")
            {
                var pool = _dbContext.Abilities.Where(a => !c.Abilities.Contains(a)).ToList();
                if (!pool.Any()) { Console.WriteLine("No abilities available to add."); continue; }
                Console.WriteLine("\nAvailable:");
                foreach (var a in pool) Console.WriteLine($"  [{a.Id}] {a.Name}");
                Console.Write("Ability ID: ");
                if (int.TryParse(Console.ReadLine(), out var aid))
                {
                    var picked = pool.FirstOrDefault(a => a.Id == aid);
                    if (picked != null) { c.Abilities.Add(picked); _dbContext.SaveChanges(); Console.WriteLine($"Added {picked.Name}."); }
                    else Console.WriteLine("Not in pool.");
                }
            }
            else if (ch == "2")
            {
                if (!c.Abilities.Any()) { Console.WriteLine("Nothing to remove."); continue; }
                Console.Write("Ability ID to remove: ");
                if (int.TryParse(Console.ReadLine(), out var aid))
                {
                    var picked = c.Abilities.FirstOrDefault(a => a.Id == aid);
                    if (picked != null) { c.Abilities.Remove(picked); _dbContext.SaveChanges(); Console.WriteLine($"Removed {picked.Name}."); }
                    else Console.WriteLine("Not on character.");
                }
            }
            else Console.WriteLine("Invalid.");
        }
    }

    private void EditSpells(Character c)
    {
        while (true)
        {
            Console.WriteLine($"\n--- Spells / Magic: {c.Name} ---");
            if (c.Magics.Any())
                foreach (var m in c.Magics)
                    Console.WriteLine($"  [{m.Id}] {m.Name} ({m.Element}, Power {m.Power})");
            else
                Console.WriteLine("  (none)");

            Console.WriteLine("  1. Add spell   2. Remove spell   0. Back");
            Console.Write("Choice: ");
            var ch = Console.ReadLine()?.Trim();
            if (ch == "0") return;

            if (ch == "1")
            {
                var pool = _dbContext.Magics.Where(m => !c.Magics.Contains(m)).ToList();
                if (!pool.Any()) { Console.WriteLine("No spells available."); continue; }
                Console.WriteLine("\nAvailable:");
                foreach (var m in pool) Console.WriteLine($"  [{m.Id}] {m.Name} ({m.Element})");
                Console.Write("Spell ID: ");
                if (int.TryParse(Console.ReadLine(), out var mid))
                {
                    var picked = pool.FirstOrDefault(m => m.Id == mid);
                    if (picked != null) { c.Magics.Add(picked); _dbContext.SaveChanges(); Console.WriteLine($"Added {picked.Name}."); }
                    else Console.WriteLine("Not in pool.");
                }
            }
            else if (ch == "2")
            {
                if (!c.Magics.Any()) { Console.WriteLine("Nothing to remove."); continue; }
                Console.Write("Spell ID to remove: ");
                if (int.TryParse(Console.ReadLine(), out var mid))
                {
                    var picked = c.Magics.FirstOrDefault(m => m.Id == mid);
                    if (picked != null) { c.Magics.Remove(picked); _dbContext.SaveChanges(); Console.WriteLine($"Removed {picked.Name}."); }
                    else Console.WriteLine("Not on character.");
                }
            }
            else Console.WriteLine("Invalid.");
        }
    }

    private void EditEquipment(Character c)
    {
        while (true)
        {
            Console.WriteLine($"\n--- Equipment: {c.Name} ---");
            if (c.EquipmentSlots.Any())
                foreach (var slot in c.EquipmentSlots)
                    Console.WriteLine($"  {slot.Slot,-9} {slot.EquippedItem?.Name ?? "(empty)"}");
            else
                Console.WriteLine("  (no slots)");

            Console.WriteLine("  1. Equip from inventory   2. Unequip   0. Back");
            Console.Write("Choice: ");
            var ch = Console.ReadLine()?.Trim();
            switch (ch)
            {
                case "1": InventoryEquip(c); break;
                case "2": InventoryUnequip(c); break;
                case "0": return;
                default: Console.WriteLine("Invalid."); break;
            }
        }
    }

    private void EditInventory(Character c)
    {
        if (c.Inventory is null)
        {
            Console.WriteLine($"\n{c.Name} has no inventory container.");
            return;
        }

        while (true)
        {
            var items = Items(c).ToList();
            Console.WriteLine($"\n--- Inventory: {c.Name} ({items.Count} items) ---");
            foreach (var i in items)
                Console.WriteLine($"  [{i.Id}] {i.Name} ({i.TypeNameForItem()})");

            Console.WriteLine("  1. Add item by ID   2. Remove item by ID   0. Back");
            Console.Write("Choice: ");
            var ch = Console.ReadLine()?.Trim();

            if (ch == "0") return;

            if (ch == "1")
            {
                var pool = _dbContext.Items.Where(i => i.ContainerId == null).ToList();
                if (!pool.Any()) { Console.WriteLine("No unowned items in the database."); continue; }
                Console.WriteLine("\nUnowned items:");
                foreach (var i in pool) Console.WriteLine($"  [{i.Id}] {i.Name} ({i.TypeNameForItem()}, {i.Weight} lbs)");
                Console.Write("Item ID: ");
                if (int.TryParse(Console.ReadLine(), out var iid))
                {
                    var picked = pool.FirstOrDefault(i => i.Id == iid);
                    if (picked != null) { picked.ContainerId = c.Inventory.Id; _dbContext.SaveChanges(); Console.WriteLine($"Added {picked.Name}."); }
                    else Console.WriteLine("Not unowned.");
                }
            }
            else if (ch == "2")
            {
                if (!items.Any()) { Console.WriteLine("Nothing to remove."); continue; }
                Console.Write("Item ID to remove from inventory (item stays in DB, becomes unowned): ");
                if (int.TryParse(Console.ReadLine(), out var iid))
                {
                    var picked = items.FirstOrDefault(i => i.Id == iid);
                    if (picked != null) { picked.ContainerId = null; _dbContext.SaveChanges(); Console.WriteLine($"Removed {picked.Name}."); }
                    else Console.WriteLine("Not in inventory.");
                }
            }
            else Console.WriteLine("Invalid.");
        }
    }

    // -------------------------------------------------------------------------
    // Delete Character
    // -------------------------------------------------------------------------

    public void DeleteCharacter()
    {
        DisplayCharacters();
        Console.Write("\nName of character to delete: ");
        var name = Console.ReadLine()?.Trim();
        if (string.IsNullOrEmpty(name)) { Console.WriteLine("Cancelled."); return; }

        var character = _dbContext.Characters.FirstOrDefault(c =>
            c.Name.Equals(name, StringComparison.OrdinalIgnoreCase));
        if (character is null) { Console.WriteLine($"No character named '{name}'."); return; }

        Console.Write($"Type DELETE to confirm removal of {character.Name} ({character.TypeName}): ");
        if (!string.Equals(Console.ReadLine(), "DELETE", StringComparison.Ordinal))
        {
            Console.WriteLine("Cancelled."); return;
        }

        // Touch nav properties so EF's ClientCascade tracks them before removal.
        _ = character.Stats; _ = character.Resources;
        _ = character.Inventory; _ = character.Equipment;

        if (_activeCharacter?.Id == character.Id) _activeCharacter = null;

        _dbContext.RemoveEntity(character);
        _dbContext.SaveChanges();
        Console.WriteLine($"Deleted {character.Name}.");
    }

    public void DisplayCharacterDetail()
    {
        var character = ResolveActiveOrPrompt("view");
        if (character is null) return;

        Console.WriteLine($"\n=== {character.Name} ({character.TypeName}) ===");
        Console.WriteLine($"  Level: {character.Level}");
        Console.WriteLine($"  Race: {character.Race?.Name ?? "None"}");
        Console.WriteLine($"  Room: {character.Room?.Name ?? "None"}");

        if (character.Stats != null)
        {
            var s = character.Stats;
            Console.WriteLine($"\n  --- Stats ---");
            Console.WriteLine($"  Physique:     {s.Physique}");
            Console.WriteLine($"  Reflexes:     {s.Reflexes}");
            Console.WriteLine($"  Constitution: {s.Constitution}");
            Console.WriteLine($"  Intellect:    {s.Intellect}");
            Console.WriteLine($"  Intuition:    {s.Intuition}");
            Console.WriteLine($"  Linguistic:   {s.Linguistic}");
            Console.WriteLine($"  Luck:         {s.Luck}");
        }

        if (character.Resources != null)
        {
            var r = character.Resources;
            Console.WriteLine($"\n  --- Resources ---");
            int maxHp = character.DeriveMaxHp();
            int maxSp = character.DeriveMaxSp();
            int maxBit = character.DeriveMaxBitPool();
            int maxByte = character.DeriveMaxBytePool();
            Console.WriteLine($"  HP: {Math.Min(r.Hp, maxHp)}/{maxHp}");
            Console.WriteLine($"  SP: {Math.Min(r.Sp, maxSp)}/{maxSp}");
            Console.WriteLine($"  BitPool: {Math.Min(r.BitPool, maxBit)}/{maxBit}");
            Console.WriteLine($"  BytePool: {Math.Min(r.BytePool, maxByte)}/{maxByte}");
        }

        Console.WriteLine($"\n  Attack: {character.GetTotalAttack()} | Defense: {character.GetTotalDefense()}");

        if (character.Abilities.Any())
        {
            Console.WriteLine($"\n  --- Abilities ---");
            foreach (var a in character.Abilities)
                Console.WriteLine($"  {a.Name} (Power: {a.Power}, Cost: {a.StaminaCost} SP, Stat: {a.PrimaryStat})");
        }

        if (character.Magics.Any())
        {
            Console.WriteLine($"\n  --- Magic ---");
            foreach (var m in character.Magics)
                Console.WriteLine($"  {m.Name} ({m.Element}) Power: {m.Power}, BitPool: {m.BitPoolCost}, Bytes: {m.BytePoolCost}");
        }

        if (character.CharacterSkills.Any())
        {
            Console.WriteLine($"\n  --- Skills ---");
            foreach (var cs in character.CharacterSkills)
                Console.WriteLine($"  {cs.Skill.Name} — Proficiency: {cs.Proficiency} (Primary: {cs.Skill.PrimaryAttribute})");
        }

        // --- Inventory (between Skills and Equipment per Shawn's call) ---
        // Carrying line shows the encumbrance fix from C0029: the character's
        // total carried weight is bag + equipped gear, not just bag. Both
        // contributors are itemized so the player can see where the weight
        // is actually living.
        if (character.Inventory is not null)
        {
            int invWeight = character.Inventory.CurrentWeight;
            int eqWeight = character.Equipment?.ItemsCollection.Sum(i => i.Weight) ?? 0;
            int total = invWeight + eqWeight;
            int cap = character.Inventory.MaxWeight;

            Console.WriteLine($"\n  --- Inventory ---");
            Console.WriteLine($"  Carrying: {total}/{cap} lbs total " +
                              $"(bag: {invWeight}, worn: {eqWeight})");

            if (character.Inventory.ItemsCollection.Any())
            {
                foreach (var item in character.Inventory.ItemsCollection
                                              .OrderBy(i => i.TypeNameForItem())
                                              .ThenBy(i => i.Name))
                {
                    Console.WriteLine($"  - {item.Name} ({item.TypeNameForItem()}, {item.Weight} lb, {item.Value}g)");
                }
            }
            else
            {
                Console.WriteLine($"  (bag empty)");
            }
        }

        if (character.EquipmentSlots.Any())
        {
            Console.WriteLine($"\n  --- Equipment ---");
            foreach (var slot in character.EquipmentSlots)
            {
                string itemLabel = slot.EquippedItem?.Name ?? "(empty)";
                Console.WriteLine($"  {slot.Slot}: {itemLabel}");
            }
        }
    }

    // Active-character resolver: returns the active character, prompting to select if none.
    private Character? ResolveActiveOrPrompt(string action)
    {
        if (_activeCharacter != null) return _activeCharacter;

        Console.WriteLine($"\nNo active character. Select one to {action}.");
        SelectCharacter();
        return _activeCharacter;
    }

    // -------------------------------------------------------------------------
    // Room & Navigation
    // -------------------------------------------------------------------------

    public void DisplayRooms()
    {
        var rooms = _dbContext.Rooms.ToList();
        if (!rooms.Any())
        {
            Console.WriteLine("\nNo rooms found.");
            return;
        }

        Console.WriteLine("\n=== Rooms ===\n");
        foreach (var r in rooms)
        {
            Console.WriteLine($"  [{r.Id}] {r.Name} — {r.Description}");

            if (r.Characters.Any())
            {
                foreach (var c in r.Characters)
                    Console.WriteLine($"      · {c.Name} ({c.TypeName}, Lv {c.Level})");
            }

            // Editor view: show ALL doors including undiscovered secrets.
            var allDoors = r.AllDoors.ToList();
            if (allDoors.Any())
            {
                foreach (var d in allDoors)
                {
                    var other = d.GetOtherRoom(r);
                    var flags = (d.IsLocked ? " [LOCKED]" : "")
                              + (d.IsTrapped && !d.TrapDisarmed ? $" [{d.TrapTypes} TRAP]" : "")
                              + (d.IsSecret ? (d.IsDiscovered ? " [secret-found]" : " [SECRET]") : "");
                    Console.WriteLine($"      → {d.Name} → {other.Name}{flags}");
                }
            }
        }
    }

    // W14 Phase D Task 4 — graded LINQ. Player-facing dungeon map view,
    // distinct from DisplayRooms (admin editor view above). Output is
    // a Spectre.Console Table with columns: Room name, items-on-floor
    // count, visible-exits count, "you are here" marker.
    //
    // LINQ contract per the W14 rubric:
    //   * Sort by Name (OrderBy)
    //   * For each room, count items where ContainerId == room.Id
    //     (Room IS-A Container; floor items live in Items.ContainerId)
    //   * For each room, count visible doors (Where(d => d.IsVisible))
    //   * Mark active player's current room with an arrow
    public void ShowAllRooms()
    {
        var player = ResolveActiveOrPrompt("see the map for");
        if (player is null) return;

        var rooms = _dbContext.Rooms.OrderBy(r => r.Name).ToList();
        if (rooms.Count == 0) { Console.WriteLine("\nNo rooms exist."); return; }

        var table = new Table()
            .Border(TableBorder.Rounded)
            .Title("[yellow bold]Dungeon Map[/]")
            .AddColumn(new TableColumn("[bold]Room[/]"))
            .AddColumn(new TableColumn("[bold]Items[/]").Centered())
            .AddColumn(new TableColumn("[bold]Exits[/]").Centered())
            .AddColumn(new TableColumn("[bold]You Are Here[/]").Centered());

        foreach (var r in rooms)
        {
            int itemCount = r.ItemsCollection.Count;
            int exitCount = r.AllDoors.Count(d => d.IsVisible);
            bool youAreHere = r.Id == player.RoomId;

            var nameCell = youAreHere ? $"[green bold]{r.Name}[/]" : r.Name;
            var marker = youAreHere ? "[green]◀[/]" : "";
            table.AddRow(nameCell, itemCount.ToString(), exitCount.ToString(), marker);
        }

        AnsiConsole.Write(table);
    }

    public void AddRoom()
    {
        Console.Write("Room name: ");
        var name = Console.ReadLine() ?? string.Empty;

        Console.Write("Description: ");
        var desc = Console.ReadLine() ?? string.Empty;

        var room = new Room { Name = name, Description = desc };
        _dbContext.AddEntity(room);
        _dbContext.SaveChanges();

        Console.WriteLine($"\nRoom '{name}' created (ID: {room.Id}).");
    }

    public void AddDoor()
    {
        DisplayRooms();

        Console.Write("Room A ID: ");
        if (!int.TryParse(Console.ReadLine(), out var roomAId)) { Console.WriteLine("Invalid."); return; }

        Console.Write("Room B ID: ");
        if (!int.TryParse(Console.ReadLine(), out var roomBId)) { Console.WriteLine("Invalid."); return; }

        if (roomAId == roomBId) { Console.WriteLine("A door must connect two different rooms."); return; }

        Console.Write("Door name (e.g., 'Oak Door'): ");
        var name = Console.ReadLine() ?? string.Empty;

        Console.Write("Description: ");
        var desc = Console.ReadLine() ?? string.Empty;

        Console.Write("Locked? (y/n): ");
        bool locked = (Console.ReadLine()?.Trim().ToLower() ?? "") == "y";

        Console.Write("Secret? (y/n): ");
        bool secret = (Console.ReadLine()?.Trim().ToLower() ?? "") == "y";

        var door = new Door
        {
            Name = name,
            Description = desc,
            IsLocked = locked,
            IsSecret = secret,
            IsDiscovered = !secret, // secret doors start undiscovered; non-secret are always visible
            RoomAId = roomAId,
            RoomBId = roomBId
        };

        _dbContext.AddEntity(door);
        _dbContext.SaveChanges();

        Console.WriteLine($"\nDoor '{name}' connects Room {roomAId} ↔ Room {roomBId}.");
    }

    public void DisplayCurrentRoom()
    {
        var player = ResolveActiveOrPrompt("view current room for");
        if (player is null) return;
        if (player.Room is null) { Console.WriteLine($"\n{player.Name} is not in any room."); return; }

        var room = player.Room;

        // W14 Phase D — Spectre.Console Panel for the room header. The
        // README W14 template introduces Spectre with this exact widget.
        // HP is shown inside the panel body; the room name is the header.
        var hp = player.Resources?.Hp ?? 0;
        var maxHp = player.Resources?.MaxHp ?? 0;
        var panel = new Panel($"[green]HP:[/] {hp}/{maxHp}    [grey]{player.Name}[/]")
        {
            Header = new PanelHeader($"[yellow bold]{room.Name}[/]"),
            Border = BoxBorder.Rounded,
            Padding = new Padding(1, 0, 1, 0)
        };
        AnsiConsole.Write(panel);
        Console.WriteLine($"  {room.Description}");

        var others = room.Characters.Where(c => c.Id != player.Id).ToList();
        if (others.Any())
        {
            Console.WriteLine("\n  Characters here:");
            foreach (var c in others)
                Console.WriteLine($"    {c.Name} ({c.TypeName})");
        }

        // Player view: hide undiscovered secret doors.
        var visibleDoors = room.AllDoors.Where(d => d.IsVisible).ToList();
        if (visibleDoors.Any())
        {
            Console.WriteLine("\n  Exits:");
            for (int i = 0; i < visibleDoors.Count; i++)
            {
                var d = visibleDoors[i];
                var other = d.GetOtherRoom(room);
                var flags = (d.IsLocked ? " [LOCKED]" : "")
                          + (d.IsTrapped && !d.TrapDisarmed ? $" [{d.TrapTypes} TRAP]" : "");
                Console.WriteLine($"    [{i + 1}] {d.Name} → {other.Name}{flags}");
            }
        }
        else
        {
            Console.WriteLine("\n  No visible exits.");
        }
    }

    public void MovePlayer()
    {
        var player = ResolveActiveOrPrompt("move");
        if (player is null) return;
        if (player.Room is null) { Console.WriteLine($"\n{player.Name} is not in any room."); return; }

        DisplayCurrentRoom();

        var visibleDoors = player.Room.AllDoors.Where(d => d.IsVisible).ToList();
        if (!visibleDoors.Any()) { Console.WriteLine("\nNo doors to take."); return; }

        Console.Write("\nDoor number to take (or 0 to cancel): ");
        if (!int.TryParse(Console.ReadLine(), out var choice) || choice < 1 || choice > visibleDoors.Count)
        {
            Console.WriteLine("Cancelled.");
            return;
        }

        var door = visibleDoors[choice - 1];

        if (door.IsLocked)
        {
            Console.WriteLine($"\nThe {door.Name} is locked! (Doors menu → 5 to attempt unlock.)");
            return;
        }

        // W14 Phase C.4 — fire door trap on first traverse, mirroring chest
        // open behavior. Trap auto-disarms after the first hit ("trapped doors
        // only hurt once" per the W14 README dungeon notes).
        if (door.IsTrapped && !door.TrapDisarmed)
        {
            door.TrapDisarmed = true;
            if (player.Resources is not null)
                player.Resources.Hp = Math.Max(0, player.Resources.Hp - door.TrapDamage);
            Console.WriteLine($"\nA {door.TrapTypes} trap on the {door.Name} fires! {player.Name} takes {door.TrapDamage} damage.");
        }

        var destination = door.GetOtherRoom(player.Room);
        player.RoomId = destination.Id;
        _dbContext.SaveChanges();

        Console.WriteLine($"\n{player.Name} passes through the {door.Name} into {destination.Name}.");
        DisplayCurrentRoom();
    }

    // -------------------------------------------------------------------------
    // Items
    // -------------------------------------------------------------------------

    public void AddItem()
    {
        Console.Write("Item type (1=Weapon, 2=Armor, 3=Shield, 4=Consumable): ");
        var typeChoice = Console.ReadLine()?.Trim();

        Console.Write("Name: ");
        var name = Console.ReadLine() ?? string.Empty;

        Console.Write("Description: ");
        var desc = Console.ReadLine() ?? string.Empty;

        Console.Write("Value: ");
        int.TryParse(Console.ReadLine(), out var value);

        Console.Write("Weight: ");
        int.TryParse(Console.ReadLine(), out var weight);

        Item item;
        switch (typeChoice)
        {
            case "1":
                Console.Write("Attack Power: ");
                int.TryParse(Console.ReadLine(), out var atk);
                Console.Write("Weapon Type (Sword/Axe/Mace/Bow/Staff/Dagger/Spear): ");
                Enum.TryParse<WeaponType>(Console.ReadLine(), true, out var wpnType);
                Console.Write("Durability: ");
                int.TryParse(Console.ReadLine(), out var wDur);
                item = new Weapon
                {
                    Name = name, Description = desc, Value = value, Weight = weight,
                    AttackPower = atk, WeaponType = wpnType, Durability = wDur
                };
                break;
            case "2":
                Console.Write("Defense Rating: ");
                int.TryParse(Console.ReadLine(), out var def);
                Console.Write("Weight Class (Light/Medium/Heavy): ");
                Enum.TryParse<ArmorWeight>(Console.ReadLine(), true, out var armorWt);
                Console.Write("Body Slot (Head/Chest/Legs/Feet/Hands): ");
                Enum.TryParse<BodySlot>(Console.ReadLine(), true, out var bodySlot);
                Console.Write("Durability: ");
                int.TryParse(Console.ReadLine(), out var aDur);
                item = new Armor
                {
                    Name = name, Description = desc, Value = value, Weight = weight,
                    DefenseRating = def, WeightClass = armorWt, Slot = bodySlot, Durability = aDur
                };
                break;
            case "3":
                Console.Write("Defense Rating: ");
                int.TryParse(Console.ReadLine(), out var sDef);
                Console.Write("Weight Class (Light/Medium/Heavy): ");
                Enum.TryParse<ArmorWeight>(Console.ReadLine(), true, out var sArmorWt);
                Console.Write("Durability: ");
                int.TryParse(Console.ReadLine(), out var sDur);
                item = new Shield
                {
                    Name = name, Description = desc, Value = value, Weight = weight,
                    DefenseRating = sDef, WeightClass = sArmorWt,
                    Slot = BodySlot.Hands, // placeholder; Shield.EligibleSlot overrides this
                    Durability = sDur
                };
                break;
            case "4":
                // W14 Phase B: Effect is a typed enum. The picker enumerates
                // every defined ConsumableEffect so adding a new value to the
                // enum (e.g., a Cure/Buff effect later) updates this prompt
                // automatically — no menu drift.
                Console.WriteLine("Effect:");
                foreach (var ce in Enum.GetValues<ConsumableEffect>())
                {
                    var hint = ce switch
                    {
                        ConsumableEffect.None     => "no effect (key item / lockpick / non-effect)",
                        ConsumableEffect.Heal     => "restores HP, capped at MaxHp",
                        ConsumableEffect.Stamina  => "restores SP, capped at MaxSp",
                        ConsumableEffect.BitPool  => "restores BitPool, capped at MaxBitPool",
                        ConsumableEffect.BytePool => "restores BytePool, capped at MaxBytePool",
                        _ => string.Empty,
                    };
                    Console.WriteLine($"  {(int)ce}. {ce} — {hint}");
                }
                Console.Write("Choice [0]: ");
                var effect = int.TryParse(Console.ReadLine(), out var ec)
                          && Enum.IsDefined(typeof(ConsumableEffect), ec)
                    ? (ConsumableEffect)ec
                    : ConsumableEffect.None;

                Console.Write("Potency (magnitude added to the resource; ignored when Effect=None): ");
                int.TryParse(Console.ReadLine(), out var potency);
                item = new Consumable
                {
                    Name = name, Description = desc, Value = value, Weight = weight,
                    Effect = effect, Potency = potency
                };
                break;
            default:
                Console.WriteLine("Invalid type.");
                return;
        }

        PromptItemPlacement(item);

        _dbContext.AddEntity(item);
        _dbContext.SaveChanges();

        var where = item.ContainerId is null
            ? "unowned"
            : $"in container #{item.ContainerId}";
        Console.WriteLine($"\n{item.TypeNameForItem()} '{name}' created ({where}).");
    }

    // After-creation placement picker. Sets ContainerId on the new Item so it
    // lands in a Chest / NPC inventory / Room floor / Character inventory in
    // the same step it's created — instead of always saving as ContainerId=NULL.
    // W15 Phase E: option 3 changed from MonsterLoot to NPC inventory.
    private void PromptItemPlacement(Item item)
    {
        Console.WriteLine("\nPlace this item:");
        Console.WriteLine("  0. Unowned (default)");
        Console.WriteLine("  1. Character inventory");
        Console.WriteLine("  2. Chest");
        Console.WriteLine("  3. NPC inventory");
        Console.WriteLine("  4. Room floor");
        Console.Write("Choice [0]: ");
        var choice = Console.ReadLine()?.Trim();

        switch (choice)
        {
            case "1":
                var chars = _dbContext.Characters.Where(c => c.Inventory != null).ToList();
                if (chars.Count == 0) { Console.WriteLine("  No characters with inventories."); return; }
                for (int i = 0; i < chars.Count; i++)
                    Console.WriteLine($"  {i + 1}. {chars[i].Name}  (bag: {chars[i].Inventory!.Name})");
                Console.Write("Pick: ");
                if (int.TryParse(Console.ReadLine(), out var ci) && ci >= 1 && ci <= chars.Count)
                    item.ContainerId = chars[ci - 1].Inventory!.Id;
                else Console.WriteLine("  Invalid — left unowned.");
                break;

            case "2":
                var chests = _dbContext.Containers.OfType<Chest>().ToList();
                if (chests.Count == 0) { Console.WriteLine("  No chests exist."); return; }
                for (int i = 0; i < chests.Count; i++)
                    Console.WriteLine($"  {i + 1}. {chests[i].Name}  (Id {chests[i].Id})");
                Console.Write("Pick: ");
                if (int.TryParse(Console.ReadLine(), out var chi) && chi >= 1 && chi <= chests.Count)
                    item.ContainerId = chests[chi - 1].Id;
                else Console.WriteLine("  Invalid — left unowned.");
                break;

            case "3":
                var npcs = _dbContext.Characters.OfType<Npc>()
                    .Where(n => n.Inventory != null).ToList();
                if (npcs.Count == 0) { Console.WriteLine("  No NPCs with inventories."); return; }
                for (int i = 0; i < npcs.Count; i++)
                    Console.WriteLine($"  {i + 1}. {npcs[i].Name}  (bag: {npcs[i].Inventory!.Name})");
                Console.Write("Pick: ");
                if (int.TryParse(Console.ReadLine(), out var ni) && ni >= 1 && ni <= npcs.Count)
                    item.ContainerId = npcs[ni - 1].Inventory!.Id;
                else Console.WriteLine("  Invalid — left unowned.");
                break;

            case "4":
                var rooms = _dbContext.Containers.OfType<Room>().ToList();
                if (rooms.Count == 0) { Console.WriteLine("  No rooms exist."); return; }
                for (int i = 0; i < rooms.Count; i++)
                    Console.WriteLine($"  {i + 1}. {rooms[i].Name}  (Id {rooms[i].Id})");
                Console.Write("Pick: ");
                if (int.TryParse(Console.ReadLine(), out var ri) && ri >= 1 && ri <= rooms.Count)
                    item.ContainerId = rooms[ri - 1].Id;
                else Console.WriteLine("  Invalid — left unowned.");
                break;
        }
    }

    // -------------------------------------------------------------------------
    // W12 — Inventory Management (any character)
    // -------------------------------------------------------------------------

    public void InventoryMenu()
    {
        var player = ResolveActiveOrPrompt("manage inventory for");
        if (player is null) return;

        if (player.Inventory is null)
        {
            Console.WriteLine($"\n{player.Name} has no inventory container. Seed or create one first.");
            return;
        }

        while (true)
        {
            Console.WriteLine($"\n=== Inventory Management — {player.Name} ===");
            Console.WriteLine("  1. List items (with weight)");
            Console.WriteLine("  2. Search by name");
            Console.WriteLine("  3. Group by type");
            Console.WriteLine("  4. Sort items");
            Console.WriteLine("  5. Equip item from inventory");
            Console.WriteLine("  6. Unequip item");
            Console.WriteLine("  7. Use consumable");
            Console.WriteLine("  8. Strongest weapon (graded)");
            Console.WriteLine("  9. Total value + breakdown (graded)");
            Console.WriteLine("  r. Read journal");
            Console.WriteLine("  t. Read tome (from inventory)");
            Console.WriteLine("  u. Unlock journal");
            Console.WriteLine("  0. Back to main menu");
            Console.Write("Choice: ");
            var choice = Console.ReadLine()?.Trim();

            switch (choice)
            {
                case "1": InventoryList(player); break;
                case "2": InventorySearch(player); break;
                case "3": InventoryGroupByType(player); break;
                case "4": InventorySort(player); break;
                case "5": InventoryEquip(player); break;
                case "6": InventoryUnequip(player); break;
                case "7": InventoryUseConsumable(player); break;
                case "8": InventoryStrongestWeapon(player); break;
                case "9": InventoryTotalValueBreakdown(player); break;
                case "r": InventoryReadJournal(player); break;
                case "t": InventoryReadTome(player); break;
                case "u": InventoryUnlockJournal(player); break;
                case "0": return;
                default: Console.WriteLine("Invalid choice."); break;
            }
        }
    }

    private static IEnumerable<Item> Items(Character p) =>
        p.Inventory?.ItemsCollection ?? Enumerable.Empty<Item>();

    private void InventoryList(Character player)
    {
        var items = Items(player).ToList();
        var max = player.Inventory!.MaxWeight;
        var cur = items.Sum(i => i.Weight);

        Console.WriteLine($"\n--- Inventory ({items.Count} items, {cur} / {max} lbs) ---");
        if (!items.Any()) { Console.WriteLine("  (empty)"); return; }

        foreach (var i in items)
            Console.WriteLine($"  [{i.Id}] {i.Name} — {i.TypeNameForItem()}, {i.Weight} lbs, {i.Value}g");
    }

    private void InventorySearch(Character player)
    {
        Console.Write("Search query: ");
        var q = Console.ReadLine() ?? string.Empty;

        var hits = Items(player)
            .Where(i => i.Name.Contains(q, StringComparison.OrdinalIgnoreCase))
            .ToList();

        Console.WriteLine($"\n--- Results for '{q}' ({hits.Count}) ---");
        if (!hits.Any()) { Console.WriteLine("  No matches."); return; }
        foreach (var i in hits)
            Console.WriteLine($"  [{i.Id}] {i.Name} — {i.TypeNameForItem()}");
    }

    private void InventoryGroupByType(Character player)
    {
        var groups = Items(player)
            .GroupBy(i => i.TypeNameForItem())
            .OrderBy(g => g.Key)
            .ToList();

        Console.WriteLine("\n--- Grouped by type ---");
        if (!groups.Any()) { Console.WriteLine("  (empty inventory)"); return; }

        foreach (var g in groups)
        {
            Console.WriteLine($"  {g.Key} ({g.Count()}):");
            foreach (var i in g)
                Console.WriteLine($"    [{i.Id}] {i.Name}");
        }
    }

    private void InventorySort(Character player)
    {
        Console.WriteLine("\nSort by: 1. Name  2. Value (desc)  3. Weight (asc)");
        Console.Write("Choice: ");
        var choice = Console.ReadLine()?.Trim();

        IEnumerable<Item> sorted = choice switch
        {
            "1" => Items(player).OrderBy(i => i.Name),
            "2" => Items(player).OrderByDescending(i => i.Value),
            "3" => Items(player).OrderBy(i => i.Weight),
            _ => Enumerable.Empty<Item>()
        };

        var list = sorted.ToList();
        if (!list.Any()) { Console.WriteLine("Nothing to show."); return; }

        Console.WriteLine();
        foreach (var i in list)
            Console.WriteLine($"  [{i.Id}] {i.Name} — {i.TypeNameForItem()}, {i.Weight} lbs, {i.Value}g");
    }

    private void InventoryEquip(Character player)
    {
        var equipables = Items(player).Where(i => i is Weapon or Armor).ToList();
        if (!equipables.Any()) { Console.WriteLine("\nNo weapons or armor in inventory."); return; }

        Console.WriteLine("\n--- Equipable items ---");
        foreach (var i in equipables)
            Console.WriteLine($"  [{i.Id}] {i.Name} ({i.TypeNameForItem()})");

        Console.Write("Item ID: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return; }

        var item = equipables.FirstOrDefault(i => i.Id == id);
        if (item is null) { Console.WriteLine("Not in equipables."); return; }

        if (player.Equip(item))
        {
            _dbContext.SaveChanges();
            Console.WriteLine($"Equipped {item.Name}.");
        }
        else Console.WriteLine("Could not equip (no compatible open slot, or no Equipment container).");
    }

    private void InventoryUnequip(Character player)
    {
        if (player.Equipment is null) { Console.WriteLine("\nNo Equipment container."); return; }
        var equipped = player.Equipment.ItemsCollection.ToList();
        if (!equipped.Any()) { Console.WriteLine("\nNothing equipped."); return; }

        Console.WriteLine("\n--- Equipped items ---");
        foreach (var i in equipped)
            Console.WriteLine($"  [{i.Id}] {i.Name} ({i.TypeNameForItem()})");

        Console.Write("Item ID to unequip: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return; }
        var item = equipped.FirstOrDefault(i => i.Id == id);
        if (item is null) { Console.WriteLine("Not equipped."); return; }

        player.Unequip(item);
        _dbContext.SaveChanges();
        Console.WriteLine($"Unequipped {item.Name}.");
    }

    private void InventoryUseConsumable(Character player)
    {
        var consumables = Items(player).OfType<Consumable>().ToList();
        if (!consumables.Any()) { Console.WriteLine("\nNo consumables."); return; }

        Console.WriteLine("\n--- Consumables ---");
        foreach (var c in consumables)
            Console.WriteLine($"  [{c.Id}] {c.Name} — {c.Effect}, potency {c.Potency}");

        Console.Write("Item ID: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return; }
        var item = consumables.FirstOrDefault(i => i.Id == id);
        if (item is null) { Console.WriteLine("Not found."); return; }

        player.UseItem(item);
        _dbContext.SaveChanges();
        Console.WriteLine($"Used {item.Name}.");
    }

    // ---- Graded LINQ Task A: Strongest Weapon ----
    private void InventoryStrongestWeapon(Character player)
    {
        var strongest = Items(player)
            .OfType<Weapon>()
            .OrderByDescending(w => w.AttackPower)
            .FirstOrDefault();

        Console.WriteLine("\n--- Strongest Weapon ---");
        if (strongest is null) Console.WriteLine("  No weapons in inventory.");
        else Console.WriteLine($"  {strongest.Name} — Attack {strongest.AttackPower} ({strongest.WeaponType})");
    }

    // ---- Graded LINQ Task B: Total Value + GroupBy breakdown ----
    private void InventoryTotalValueBreakdown(Character player)
    {
        var items = Items(player).ToList();

        int total = items.Sum(i => i.Value);

        var breakdown = items
            .GroupBy(i => i.TypeNameForItem())
            .Select(g => new { Type = g.Key, Gold = g.Sum(i => i.Value), Count = g.Count() })
            .OrderByDescending(x => x.Gold)
            .ToList();

        Console.WriteLine($"\n--- Inventory Value ---");
        Console.WriteLine($"  Total: {total}g across {items.Count} items");
        if (!breakdown.Any()) return;

        Console.WriteLine("  By type:");
        foreach (var b in breakdown)
            Console.WriteLine($"    {b.Type,-12} {b.Count,3} items   {b.Gold,6}g");
    }

    // ---- W15 Phase F1: Read journal from inventory ----
    private void InventoryReadJournal(Character player)
    {
        var journals = Items(player).OfType<LockedJournal>().ToList();
        Console.WriteLine("\n--- Journals in Inventory ---");
        if (!journals.Any()) { Console.WriteLine("  (none)"); return; }

        for (int i = 0; i < journals.Count; i++)
        {
            var j = journals[i];
            var state = j.IsLocked ? "[LOCKED]" : "[unlocked]";
            Console.WriteLine($"  {i + 1}. {j.Name} {state}");
        }

        Console.Write("Select journal #: ");
        if (!int.TryParse(Console.ReadLine()?.Trim(), out int idx) || idx < 1 || idx > journals.Count)
        { Console.WriteLine("Invalid selection."); return; }

        var journal = journals[idx - 1];
        if (journal.IsLocked)
        {
            Console.WriteLine($"\n{journal.Name} is locked. Use 'u' to unlock it first.");
            return;
        }

        Console.WriteLine($"\n=== {journal.Name} ===");
        Console.WriteLine(journal.Content);
        Console.WriteLine("===================");
    }

    private void InventoryReadTome(Character player)
    {
        var tomes = Items(player).OfType<Tome>().ToList();
        Console.WriteLine("\n--- Tomes in Inventory ---");
        if (!tomes.Any()) { Console.WriteLine("  (none — take a book from a shelf first)"); return; }

        for (int i = 0; i < tomes.Count; i++)
            Console.WriteLine($"  {i + 1}. {tomes[i].Name}");

        Console.Write("Read which # (0 to cancel): ");
        if (!int.TryParse(Console.ReadLine()?.Trim(), out int idx) || idx < 1 || idx > tomes.Count) return;

        var tome = tomes[idx - 1];
        Console.WriteLine($"\n=== {tome.Name} ===");
        Console.WriteLine(tome.LoreText);
        Console.WriteLine("===================");
    }

    // ---- W15 Phase F1: Unlock journal from inventory ----
    private void InventoryUnlockJournal(Character player)
    {
        var journals = Items(player).OfType<LockedJournal>().ToList();
        Console.WriteLine("\n--- Journals in Inventory ---");
        if (!journals.Any()) { Console.WriteLine("  (none)"); return; }

        for (int i = 0; i < journals.Count; i++)
        {
            var j = journals[i];
            var state = j.IsLocked ? "[LOCKED]" : "[unlocked]";
            Console.WriteLine($"  {i + 1}. {j.Name} {state}");
        }

        Console.Write("Select journal #: ");
        if (!int.TryParse(Console.ReadLine()?.Trim(), out int idx) || idx < 1 || idx > journals.Count)
        { Console.WriteLine("Invalid selection."); return; }

        var journal = journals[idx - 1];
        TryUnlockTarget(player, journal, journal.Name);
    }

    // -------------------------------------------------------------------------
    // W15 Phase F2 — Bookshelf (read lore tomes in current room)
    // -------------------------------------------------------------------------

    public void BookshelfMenu()
    {
        var player = ResolveActiveOrPrompt("browse bookshelves for");
        if (player is null) return;
        if (player.Room is null) { Console.WriteLine("\nNot in any room."); return; }

        var bookshelves = _dbContext.QueryContainers()
            .OfType<Bookshelf>()
            .Where(b => b.RoomId == player.RoomId)
            .ToList();

        Console.WriteLine($"\n--- Bookshelves in {player.Room.Name} ---");
        if (!bookshelves.Any()) { Console.WriteLine("  (none in this room)"); return; }

        for (int i = 0; i < bookshelves.Count; i++)
            Console.WriteLine($"  {i + 1}. {bookshelves[i].Name}");

        Console.Write("Select bookshelf #: ");
        if (!int.TryParse(Console.ReadLine()?.Trim(), out int shelfIdx) || shelfIdx < 1 || shelfIdx > bookshelves.Count)
        { Console.WriteLine("Invalid selection."); return; }

        var shelf = bookshelves[shelfIdx - 1];
        var tomes = shelf.ItemsCollection.OfType<Tome>().ToList();

        Console.WriteLine($"\n--- {shelf.Name} ---");
        if (shelf.Description.Length > 0) Console.WriteLine($"  {shelf.Description}");
        if (!tomes.Any()) { Console.WriteLine("  (empty)"); return; }

        for (int i = 0; i < tomes.Count; i++)
            Console.WriteLine($"  {i + 1}. {tomes[i].Name}");

        Console.Write("Select tome # to read (0 to cancel): ");
        if (!int.TryParse(Console.ReadLine()?.Trim(), out int tomeIdx) || tomeIdx < 1 || tomeIdx > tomes.Count)
        { return; }

        var tome = tomes[tomeIdx - 1];
        Console.WriteLine($"\n=== {tome.Name} ===");
        Console.WriteLine(tome.LoreText);
        Console.WriteLine("===================");
    }

    // -------------------------------------------------------------------------
    // W13 — Chest & Monster Loot Interaction (any character)
    // -------------------------------------------------------------------------

    public void ChestMenu()
    {
        var player = ResolveActiveOrPrompt("interact with chests for");
        if (player is null) return;

        while (true)
        {
            Console.WriteLine($"\n=== Chest Interaction — {player.Name} ===");
            Console.WriteLine("  1. List chests in current room");
            Console.WriteLine("  2. Open chest");
            Console.WriteLine("  3. Try unlock chest (key or lockpick)");
            Console.WriteLine("  4. Disarm trap (lockpick) — graded");
            Console.WriteLine("  5. Loot chest");
            Console.WriteLine("  6. Loot defeated monster");
            Console.WriteLine("  7. Richest locked chest (graded)");
            Console.WriteLine("  0. Back to main menu");
            Console.Write("Choice: ");
            var choice = Console.ReadLine()?.Trim();

            switch (choice)
            {
                case "1": ChestList(player); break;
                case "2": ChestOpen(player); break;
                case "3": ChestTryUnlock(player); break;
                case "4": ChestDisarmTrap(player); break;
                case "5": ChestLoot(player); break;
                case "6": ChestLootMonster(player); break;
                case "7": ChestRichestLocked(); break;
                case "0": return;
                default: Console.WriteLine("Invalid choice."); break;
            }
        }
    }

    private List<Chest> ChestsInCharacterRoom(Character player) =>
        _dbContext.Containers
            .OfType<Chest>()
            .Where(c => c.RoomId == player.RoomId)
            .ToList();

    private void ChestList(Character player)
    {
        if (player.RoomId is null) { Console.WriteLine("\nPlayer is not in a room."); return; }

        var chests = ChestsInCharacterRoom(player);
        Console.WriteLine($"\n--- Chests in {player.Room?.Name ?? "this room"} ({chests.Count}) ---");
        if (!chests.Any()) { Console.WriteLine("  (none)"); return; }

        foreach (var c in chests)
        {
            string state = (c.IsLocked, c.IsTrapped && !c.TrapDisarmed) switch
            {
                (true, true)   => "[LOCKED, TRAPPED]",
                (true, false)  => "[LOCKED]",
                (false, true)  => "[TRAPPED]",
                _              => "[OPEN]"
            };
            Console.WriteLine($"  [{c.Id}] {c.Name} {state} — {c.Description}");
        }
    }

    private Chest? PromptForChest(Character player)
    {
        var chests = ChestsInCharacterRoom(player);
        if (!chests.Any()) { Console.WriteLine("\nNo chests in this room."); return null; }

        Console.Write("Chest ID: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return null; }
        var chest = chests.FirstOrDefault(c => c.Id == id);
        if (chest is null) Console.WriteLine("Not in this room.");
        return chest;
    }

    private void ChestOpen(Character player)
    {
        var chest = PromptForChest(player);
        if (chest is null) return;

        var result = player.OpenChest(chest);
        switch (result)
        {
            case OpenResult.Opened:
                Console.WriteLine($"\nThe {chest.Name} opens. {chest.ItemsCollection.Count} item(s) inside.");
                break;
            case OpenResult.Locked:
                Console.WriteLine($"\nThe {chest.Name} is locked. Try option 3 to unlock.");
                break;
            case OpenResult.Trapped:
                Console.WriteLine($"\nA trap fires! {chest.Name} deals {chest.TrapDamage} damage. " +
                                  $"HP now {player.Resources?.Hp ?? 0}/{player.Resources?.MaxHp ?? 0}.");
                _dbContext.SaveChanges();
                break;
            case OpenResult.AlreadyOpen:
                Console.WriteLine($"\nThe {chest.Name} was already open.");
                break;
        }
    }

    private void ChestTryUnlock(Character player)
    {
        var chest = PromptForChest(player);
        if (chest is null) return;
        TryUnlockTarget(player, chest, chest.Name);
    }

    // W14 Phase D / +5 challenge — single helper for all ILockable unlocks.
    // Replaces the chest/door near-twin methods with one shared flow:
    // confirm-locked → check inventory → key picker → TryUnlock → outcome
    // → if failed with a specific RequiredKeyId, inline FindKeyLocation
    // hint (Task 5 graded path).
    //
    // The LSP refactor in C.4 made TryUnlock(ILockable, Item) substitutable
    // across hosts; this method makes the *UI* layer substitutable too. The
    // chest and door wrappers shrink to "pick a target, hand it to this."
    private void TryUnlockTarget(Character player, ILockable target, string targetLabel)
    {
        if (!target.IsLocked) { Console.WriteLine($"\n{targetLabel} is not locked."); return; }
        if (player.Inventory is null) { Console.WriteLine("\nNo inventory."); return; }

        var keys = player.Inventory.ItemsCollection.Where(i => i.KeyId != null).ToList();
        if (!keys.Any())
        {
            Console.WriteLine("\nNo keys or lockpicks in inventory.");
            HintForKeyIfNeeded(target, targetLabel);
            return;
        }

        Console.WriteLine("\n--- Keys & Lockpicks ---");
        foreach (var k in keys)
        {
            string label = k.KeyId == Item.LockpickKeyId ? "(lockpick)" : $"(key: {k.KeyId})";
            Console.WriteLine($"  [{k.Id}] {k.Name} {label}");
        }

        Console.Write("Item ID: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return; }
        var key = keys.FirstOrDefault(k => k.Id == id);
        if (key is null) { Console.WriteLine("Not in keys list."); return; }

        bool ok = player.TryUnlock(target, key);
        _dbContext.SaveChanges();
        if (ok)
        {
            Console.WriteLine($"\n{targetLabel} clicks open.");
            return;
        }

        if (key.KeyId == Item.LockpickKeyId)
        {
            // If the lockpick is gone from inventory it broke; if still there the lock resisted or wasn't pickable.
            bool broke = !(player.Inventory?.ItemsCollection.Contains(key) ?? false);
            if (broke)
                Console.WriteLine($"\nThe lockpick snaps. {targetLabel} stays shut.");
            else if (!target.IsPickable)
            {
                Console.WriteLine($"\nThis lock cannot be picked — it requires a specific key.");
                HintForKeyIfNeeded(target, targetLabel);
            }
            else
                Console.WriteLine($"\nThis lock resists the pick. {targetLabel} stays shut.");
        }
        else
        {
            Console.WriteLine($"\nThat key doesn't fit {targetLabel}.");
            HintForKeyIfNeeded(target, targetLabel);
        }
    }

    // W14 Phase D Task 5 — graded LINQ. Locates an item by its KeyId
    // anywhere in the world (Items table) and reports the container that
    // currently holds it. The .Include(i => i.Container) is the rubric-
    // graded eager-load — pulls the Container row in the same query so
    // we can report ContainerType + Name without a second round-trip.
    //
    // Per the project's lazy-loading-by-default preference, this is one
    // of the few methods that explicitly opts into eager loading via
    // IContext.QueryItems(). Justified by the rubric line: "Uses Include
    // to eager-load the key's container and prints its location."
    public void FindKeyLocation(string requiredKeyId)
    {
        if (string.IsNullOrWhiteSpace(requiredKeyId)) return;

        var matches = _dbContext.QueryItems()
            .Where(i => i.KeyId == requiredKeyId)
            .Include(i => i.Container)
            .ToList();

        if (matches.Count == 0)
        {
            Console.WriteLine($"  Hint: no item with key id '{requiredKeyId}' exists anywhere in the world.");
            return;
        }

        foreach (var m in matches)
        {
            if (m.Container is null)
                Console.WriteLine($"  Hint: {m.Name} is currently unowned — nobody has it yet.");
            else
            {
                string carrier = m.Container is Inventory inv && inv.Owner != null
                    ? inv.Owner.Name
                    : m.Container.Name;
                Console.WriteLine($"  Hint: {m.Name} is held by {carrier}.");
            }
        }
    }

    // Fires FindKeyLocation only when it would actually help: the target
    // requires a specific (non-lockpick) key. Lockpick-only locks and
    // already-failed lockpick attempts don't get the hint — there's no
    // single key to find.
    private void HintForKeyIfNeeded(ILockable target, string targetLabel)
    {
        if (target.RequiredKeyId is null) return;
        Console.WriteLine($"\n{targetLabel} requires a specific key.");
        FindKeyLocation(target.RequiredKeyId);
    }

    private void ChestDisarmTrap(Character player)
    {
        var chest = PromptForChest(player);
        if (chest is null) return;
        if (player.Inventory is null) { Console.WriteLine("\nNo inventory."); return; }

        var lockpick = player.Inventory.ItemsCollection
            .FirstOrDefault(i => i.KeyId == Item.LockpickKeyId);
        if (lockpick is null) { Console.WriteLine("\nNo lockpick available."); return; }

        bool ok = player.DisarmTrap(chest, lockpick);
        _dbContext.SaveChanges();
        Console.WriteLine(ok
            ? $"\nTrap on {chest.Name} disarmed. Lockpick used."
            : $"\nCouldn't disarm — chest isn't trapped, or already disarmed, or item isn't a lockpick.");
    }

    private void ChestLoot(Character player)
    {
        var chest = PromptForChest(player);
        if (chest is null) return;
        if (chest.IsLocked) { Console.WriteLine("\nLocked. Unlock first."); return; }

        LootInteractive(player, chest, $"Inside {chest.Name}");
        _dbContext.SaveChanges();
    }

    private void ChestLootMonster(Character player)
    {
        if (player.RoomId is null) { Console.WriteLine("\nPlayer is not in a room."); return; }

        // W15 Phase E: NPC loot lives in NPC.Inventory (MonsterLoot eliminated).
        // Show NPCs in room with non-empty Inventory — empty inventory = nothing left.
        var monsters = _dbContext.Characters
            .OfType<Npc>()
            .Where(n => n.RoomId == player.RoomId && n.Inventory != null)
            .ToList()
            .Where(n => n.Inventory!.ItemsCollection.Any())
            .ToList();

        if (!monsters.Any()) { Console.WriteLine("\nNo defeated monsters here to loot."); return; }

        Console.WriteLine("\n--- Defeated monsters here ---");
        foreach (var m in monsters)
        {
            int count = m.Inventory?.ItemsCollection.Count ?? 0;
            Console.WriteLine($"  [{m.Id}] {m.Name} ({m.Race?.Name}) ({count} item(s))");
        }

        Console.Write("Monster ID: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return; }
        var monster = monsters.FirstOrDefault(m => m.Id == id);
        if (monster is null) { Console.WriteLine("Not in this room."); return; }

        if (monster.Inventory is null || !monster.Inventory.ItemsCollection.Any())
        {
            Console.WriteLine("\nNothing to loot.");
            return;
        }

        LootInteractive(player, monster.Inventory, $"On {monster.Name}'s body");
        _dbContext.SaveChanges();
    }

    /// <summary>
    /// Interactive loot picker. Shows the source container's items in a
    /// numbered list with weight + value tags; player picks individual
    /// items by number, types "all" to grab everything that fits, or 0
    /// to leave. Re-displays after each take so the player sees the
    /// updated state. Items the looter can't fit show a [too heavy] tag
    /// and are skipped on "all".
    ///
    /// Reusable across chests, monster loot, room floors (W14), and any
    /// future Container subclass — the picker only knows about
    /// <see cref="Container"/> and <see cref="Character.TakeItemFrom"/>.
    /// </summary>
    private static void LootInteractive(Character looter, Container source, string sourceLabel)
    {
        if (looter.Inventory is null)
        {
            Console.WriteLine("\nThis character has no inventory to loot into.");
            return;
        }

        while (true)
        {
            var items = source.ItemsCollection.ToList();
            if (!items.Any())
            {
                Console.WriteLine($"\n{sourceLabel}: empty.");
                return;
            }

            Console.WriteLine($"\n--- {sourceLabel} ---");
            for (int i = 0; i < items.Count; i++)
            {
                var item = items[i];
                string fitsTag = looter.CanCarry(item.Weight) ? "" : "  [too heavy]";
                Console.WriteLine(
                    $"  [{i + 1}] {item.Name} — {item.TypeNameForItem()}, " +
                    $"{item.Weight} lb, {item.Value}g{fitsTag}");
            }
            Console.Write("Take which? (number / 'all' / 0 to leave): ");
            var input = Console.ReadLine()?.Trim().ToLowerInvariant() ?? "";

            if (input == "0" || input == "")
                return;

            if (input == "all")
            {
                var taken = new List<Item>();
                foreach (var item in items)
                {
                    if (looter.TakeItemFrom(source, item))
                        taken.Add(item);
                }
                if (taken.Count > 0)
                {
                    Console.WriteLine($"\nTook {taken.Count} item(s):");
                    foreach (var t in taken)
                        Console.WriteLine($"  - {t.Name}");
                }
                else
                {
                    Console.WriteLine("\nCouldn't take anything (weight?).");
                }
                continue;
            }

            if (int.TryParse(input, out var idx) && idx >= 1 && idx <= items.Count)
            {
                var picked = items[idx - 1];
                if (looter.TakeItemFrom(source, picked))
                    Console.WriteLine($"\nTook {picked.Name}.");
                else
                    Console.WriteLine($"\nCouldn't take {picked.Name} — too heavy.");
                continue;
            }

            Console.WriteLine("Invalid choice.");
        }
    }

    // ---- Graded LINQ Task A: Richest locked chest ----
    private void ChestRichestLocked()
    {
        var richest = _dbContext.Containers
            .OfType<Chest>()
            .Where(c => c.IsLocked)
            .ToList()
            .OrderByDescending(c => c.ItemsCollection.Sum(i => i.Value))
            .FirstOrDefault();

        Console.WriteLine("\n--- Richest Locked Chest ---");
        if (richest is null) { Console.WriteLine("  No locked chests."); return; }

        int gold = richest.ItemsCollection.Sum(i => i.Value);
        Console.WriteLine($"  {richest.Name} — {gold}g across {richest.ItemsCollection.Count} item(s)");
        Console.WriteLine($"  ({richest.Description})");
    }

    // -------------------------------------------------------------------------
    // Phase 1 reshape — thematic top-level submenus.
    // Each Submenu() loops until the user picks 0 (Back).
    // -------------------------------------------------------------------------

    public void CharactersSubmenu()
    {
        while (true)
        {
            Console.WriteLine("\n=== Characters ===");
            Console.WriteLine("  1. List characters");
            Console.WriteLine("  2. Select active character");
            Console.WriteLine("  3. Add character");
            Console.WriteLine("  4. Edit character");
            Console.WriteLine("  5. Delete character");
            Console.WriteLine("  6. Level up character");
            Console.WriteLine("  7. Character detail");
            Console.WriteLine("  0. Back");
            Console.Write("Choice: ");
            switch (Console.ReadLine()?.Trim())
            {
                case "1": DisplayCharacters(); break;
                case "2": SelectCharacter(); break;
                case "3": AddCharacter(); break;
                case "4": EditCharacter(); break;
                case "5": DeleteCharacter(); break;
                case "6": LevelUpCharacter(); break;
                case "7": DisplayCharacterDetail(); break;
                case "0": return;
                default: Console.WriteLine("Invalid."); break;
            }
        }
    }

    // -------------------------------------------------------------------------
    // Items submenu — list / create (subtype-aware) / view / edit / remove
    // -------------------------------------------------------------------------

    public void ItemsSubmenu()
    {
        while (true)
        {
            Console.WriteLine("\n=== Items ===");
            Console.WriteLine("  1. List items");
            Console.WriteLine("  2. Create item");
            Console.WriteLine("  3. View item detail");
            Console.WriteLine("  4. Edit item (common fields)");
            Console.WriteLine("  5. Remove item");
            Console.WriteLine("  0. Back");
            Console.Write("Choice: ");
            switch (Console.ReadLine()?.Trim())
            {
                case "1": ListItems(); break;
                case "2": AddItem(); break;
                case "3": ViewItemDetail(); break;
                case "4": EditItem(); break;
                case "5": RemoveItem(); break;
                case "0": return;
                default: Console.WriteLine("Invalid."); break;
            }
        }
    }

    private void ListItems()
    {
        var items = _dbContext.Items.ToList();
        if (!items.Any()) { Console.WriteLine("\nNo items in database."); return; }
        Console.WriteLine("\n--- Items ---");
        foreach (var i in items.OrderBy(i => i.TypeNameForItem()).ThenBy(i => i.Name))
        {
            // Lazy-loading proxies materialize i.Container on access. Show the
            // container's display name (Inventory: "Elara's Pack", Chest:
            // "Wooden Chest", Room: "Antechamber", etc.) under a single
            // "Owner" label per Shawn's call — works whether the container is
            // a person, a vessel, a room, or any future thing-that-holds-items.
            string ownerLabel = i.Container is { } c
                ? $"Owner: {c.Name}"
                : "Unowned";
            Console.WriteLine($"  [{i.Id}] {i.Name} — {i.TypeNameForItem()}, {i.Weight} lbs, {i.Value}g — {ownerLabel}");
        }
    }

    private Item? PromptItem(string verb)
    {
        ListItems();
        Console.Write($"\nItem ID to {verb}: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return null; }
        var item = _dbContext.Items.FirstOrDefault(i => i.Id == id);
        if (item is null) Console.WriteLine("Not found.");
        return item;
    }

    private void ViewItemDetail()
    {
        var item = PromptItem("view");
        if (item is null) return;
        Console.WriteLine($"\n=== [{item.Id}] {item.Name} ({item.TypeNameForItem()}) ===");
        Console.WriteLine($"  Description: {item.Description}");
        Console.WriteLine($"  Value: {item.Value}g   Weight: {item.Weight} lbs");
        Console.WriteLine($"  KeyId: {item.KeyId ?? "—"}");
        Console.WriteLine($"  EligibleSlot: {(item.EligibleSlot.HasValue ? item.EligibleSlot.ToString() : "—")}");
        switch (item)
        {
            case Weapon w: Console.WriteLine($"  Weapon: {w.WeaponType}, AP {w.AttackPower}, Dur {w.Durability}"); break;
            case Shield s: Console.WriteLine($"  Shield: {s.WeightClass}, DR {s.DefenseRating}, Dur {s.Durability}"); break;
            case Armor a: Console.WriteLine($"  Armor: {a.WeightClass} {a.Slot}, DR {a.DefenseRating}, Dur {a.Durability}"); break;
            case Consumable c: Console.WriteLine($"  Consumable: effect {c.Effect}, potency {c.Potency}"); break;
        }
    }

    private void EditItem()
    {
        var item = PromptItem("edit");
        if (item is null) return;

        Console.Write($"Name [{item.Name}] (blank to keep): ");
        var n = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(n)) item.Name = n.Trim();

        Console.Write($"Description [{item.Description}] (blank to keep): ");
        var d = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(d)) item.Description = d.Trim();

        Console.Write($"Value [{item.Value}] (blank to keep): ");
        if (int.TryParse(Console.ReadLine(), out var v)) item.Value = v;

        Console.Write($"Weight [{item.Weight}] (blank to keep): ");
        if (int.TryParse(Console.ReadLine(), out var w)) item.Weight = w;

        _dbContext.SaveChanges();
        Console.WriteLine("Item updated.");
    }

    private void RemoveItem()
    {
        var item = PromptItem("remove");
        if (item is null) return;

        Console.Write("(d)elete from database, (u)nown only, or (c)ancel? ");
        switch (Console.ReadLine()?.Trim().ToLower())
        {
            case "d":
                _dbContext.RemoveEntity(item);
                _dbContext.SaveChanges();
                Console.WriteLine("Item deleted.");
                break;
            case "u":
                item.ContainerId = null;
                _dbContext.SaveChanges();
                Console.WriteLine("Item is now unowned.");
                break;
            default:
                Console.WriteLine("Cancelled.");
                break;
        }
    }

    // -------------------------------------------------------------------------
    // Rooms & Doors submenu
    // Per design: room delete cascades doors and orphans (a) characters' RoomId,
    // (b) chests' RoomId, (c) items inside those chests' ContainerId.
    // Items themselves are preserved in the database.
    // -------------------------------------------------------------------------

    public void RoomsSubmenu()
    {
        while (true)
        {
            Console.WriteLine("\n=== Rooms & Doors ===");
            Console.WriteLine("  1. List rooms");
            Console.WriteLine("  2. Create room");
            Console.WriteLine("  3. Edit room");
            Console.WriteLine("  4. Remove room");
            Console.WriteLine("  5. Door management ▶");
            Console.WriteLine("  6. View current room (active player)");
            Console.WriteLine("  7. Move active player");
            Console.WriteLine("  8. Inspect the room (find secret doors)");
            Console.WriteLine("  9. Dungeon map (active player)");
            Console.WriteLine("  0. Back");
            Console.Write("Choice: ");
            switch (Console.ReadLine()?.Trim())
            {
                case "1": DisplayRooms(); break;
                case "2": AddRoom(); break;
                case "3": EditRoom(); break;
                case "4": RemoveRoom(); break;
                case "5": DoorsSubmenu(); break;
                case "6": DisplayCurrentRoom(); break;
                case "7": MovePlayer(); break;
                case "8": InspectRoom(); break;
                case "9": ShowAllRooms(); break;
                case "0": return;
                default: Console.WriteLine("Invalid."); break;
            }
        }
    }

    private Room? PromptRoom(string verb)
    {
        DisplayRooms();
        Console.Write($"\nRoom ID to {verb}: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return null; }
        var room = _dbContext.Rooms.FirstOrDefault(r => r.Id == id);
        if (room is null) Console.WriteLine("Not found.");
        return room;
    }

    private void EditRoom()
    {
        var room = PromptRoom("edit");
        if (room is null) return;

        Console.Write($"Name [{room.Name}] (blank to keep): ");
        var n = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(n)) room.Name = n.Trim();

        Console.Write($"Description [{room.Description}] (blank to keep): ");
        var d = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(d)) room.Description = d.Trim();

        _dbContext.SaveChanges();
        Console.WriteLine("Room updated.");
    }

    private void RemoveRoom()
    {
        var room = PromptRoom("remove");
        if (room is null) return;

        // Snapshot dependents before mutation.
        var chestsHere = _dbContext.Containers.OfType<Chest>().Where(c => c.RoomId == room.Id).ToList();
        var doorsTouching = _dbContext.Doors
            .Where(d => d.RoomAId == room.Id || d.RoomBId == room.Id)
            .ToList();
        var charactersHere = _dbContext.Characters.Where(c => c.RoomId == room.Id).ToList();

        Console.WriteLine($"\nRemoving '{room.Name}' will:");
        Console.WriteLine($"  - orphan {charactersHere.Count} character(s) (RoomId cleared)");
        Console.WriteLine($"  - delete {chestsHere.Count} chest(s) in the room (their items become unowned)");
        Console.WriteLine($"  - delete {doorsTouching.Count} door(s) touching the room");
        Console.Write("Confirm? (y/N): ");
        if ((Console.ReadLine()?.Trim().ToLower() ?? "") != "y") { Console.WriteLine("Cancelled."); return; }

        // Orphan items inside chests, then delete chests.
        foreach (var chest in chestsHere)
        {
            var items = _dbContext.Items.Where(i => i.ContainerId == chest.Id).ToList();
            foreach (var i in items) i.ContainerId = null;
            _dbContext.RemoveEntity(chest);
        }
        // Orphan characters.
        foreach (var c in charactersHere) c.RoomId = null;
        // Delete doors.
        foreach (var d in doorsTouching) _dbContext.RemoveEntity(d);

        _dbContext.RemoveEntity(room);
        _dbContext.SaveChanges();
        Console.WriteLine($"Room '{room.Name}' removed.");
    }

    public void DoorsSubmenu()
    {
        while (true)
        {
            Console.WriteLine("\n=== Doors ===");
            Console.WriteLine("  1. List doors");
            Console.WriteLine("  2. Add door");
            Console.WriteLine("  3. Toggle lock on door (admin)");
            Console.WriteLine("  4. Remove door");
            Console.WriteLine("  5. Try to unlock door (active player)");
            Console.WriteLine("  6. Disarm door trap (active player)");
            Console.WriteLine("  7. Edit door (admin: lock/trap/secret/key/DC)");
            Console.WriteLine("  0. Back");
            Console.Write("Choice: ");
            switch (Console.ReadLine()?.Trim())
            {
                case "1": ListDoors(); break;
                case "2": AddDoor(); break;
                case "3": ToggleDoorLock(); break;
                case "4": RemoveDoor(); break;
                case "5": DoorTryUnlock(); break;
                case "6": DoorDisarmTrap(); break;
                case "7": EditDoor(); break;
                case "0": return;
                default: Console.WriteLine("Invalid."); break;
            }
        }
    }

    // W14 Phase C.4 — door unlock UX. After Phase D's +5 challenge,
    // this is now a thin wrapper: pick a target door, hand it to the
    // shared TryUnlockTarget helper. Same algorithm, same outcome
    // messages, same FindKeyLocation hint — proof that the LSP
    // refactor reaches the UI layer too, not just Character.TryUnlock.
    private void DoorTryUnlock()
    {
        var player = ResolveActiveOrPrompt("unlock a door for");
        if (player is null) return;
        if (player.Room is null) { Console.WriteLine("\nNot in any room."); return; }
        var door = PromptForDoorInRoom(player);
        if (door is null) return;
        TryUnlockTarget(player, door, door.Name);
    }

    // W14 Phase C.4 — door trap disarm UX, parallel to ChestDisarmTrap.
    // Same Character.DisarmTrap(ILockable, Item) helper underneath.
    private void DoorDisarmTrap()
    {
        var player = ResolveActiveOrPrompt("disarm a door trap for");
        if (player is null) return;
        if (player.Room is null) { Console.WriteLine("\nNot in any room."); return; }
        if (player.Inventory is null) { Console.WriteLine("\nNo inventory."); return; }

        var door = PromptForDoorInRoom(player);
        if (door is null) return;

        var lockpick = player.Inventory.ItemsCollection
            .FirstOrDefault(i => i.KeyId == Item.LockpickKeyId);
        if (lockpick is null) { Console.WriteLine("\nNo lockpick available."); return; }

        bool ok = player.DisarmTrap(door, lockpick);
        _dbContext.SaveChanges();
        Console.WriteLine(ok
            ? $"\nTrap on {door.Name} disarmed. Lockpick used."
            : $"\nCouldn't disarm — door isn't trapped, already disarmed, or item isn't a lockpick.");
    }

    private Door? PromptForDoorInRoom(Character player)
    {
        var doors = player.Room!.AllDoors.Where(d => d.IsVisible).ToList();
        if (!doors.Any()) { Console.WriteLine("\nNo visible doors here."); return null; }
        Console.WriteLine("\n--- Doors in this room ---");
        foreach (var d in doors)
        {
            var flags = (d.IsLocked ? " [LOCKED]" : "")
                      + (d.IsTrapped && !d.TrapDisarmed ? $" [{d.TrapTypes} TRAP]" : "");
            var other = d.GetOtherRoom(player.Room);
            Console.WriteLine($"  [{d.Id}] {d.Name} → {other.Name}{flags}");
        }
        Console.Write("Door ID: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return null; }
        var door = doors.FirstOrDefault(d => d.Id == id);
        if (door is null) Console.WriteLine("Not in this room.");
        return door;
    }

    // W14 Phase C.4 stretch — Inspect the room (deterministic). Wired
    // from Rooms submenu → 8. Reveals any secret doors connected to the
    // active player's current room.
    private void InspectRoom()
    {
        var player = ResolveActiveOrPrompt("inspect the room with");
        if (player is null) return;
        if (player.Room is null) { Console.WriteLine("\nNot in any room."); return; }

        var revealed = player.InspectForSecretDoors(_dbContext.Doors);
        if (revealed.Count == 0)
        {
            Console.WriteLine($"\n{player.Name} searches {player.Room.Name} carefully but finds nothing hidden.");
            return;
        }

        _dbContext.SaveChanges();
        Console.WriteLine($"\n{player.Name} discovers {revealed.Count} hidden door(s) in {player.Room.Name}:");
        foreach (var d in revealed)
        {
            var other = d.GetOtherRoom(player.Room);
            Console.WriteLine($"  - {d.Name} → {other.Name}");
        }
    }

    private void ListDoors()
    {
        var doors = _dbContext.Doors.ToList();
        if (!doors.Any()) { Console.WriteLine("\nNo doors."); return; }
        Console.WriteLine("\n--- Doors ---");
        foreach (var d in doors)
        {
            var flags = (d.IsLocked ? " [LOCKED]" : "")
                      + (d.IsTrapped && !d.TrapDisarmed ? $" [{d.TrapTypes} TRAP]" : "")
                      + (d.IsSecret ? (d.IsDiscovered ? " [secret-found]" : " [SECRET]") : "");
            Console.WriteLine($"  [{d.Id}] {d.Name}: {d.RoomA.Name} ↔ {d.RoomB.Name}{flags}");
        }
    }

    private Door? PromptDoor(string verb)
    {
        ListDoors();
        Console.Write($"\nDoor ID to {verb}: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return null; }
        var door = _dbContext.Doors.FirstOrDefault(d => d.Id == id);
        if (door is null) Console.WriteLine("Not found.");
        return door;
    }

    private void ToggleDoorLock()
    {
        var door = PromptDoor("toggle");
        if (door is null) return;
        door.IsLocked = !door.IsLocked;
        _dbContext.SaveChanges();
        Console.WriteLine($"Door '{door.Name}' is now {(door.IsLocked ? "LOCKED" : "unlocked")}.");
    }

    // W14 Phase C.4 follow-up — admin edit of every gameplay-relevant
    // Door field. Replaces the need for one-shot SeedC4Demo-style
    // migrations whenever we want to add/test door state via menu UX.
    // Each prompt accepts a blank line to keep the current value, so
    // re-running on a partially-configured door doesn't clobber
    // settings the user wants to preserve.
    private void EditDoor()
    {
        var door = PromptDoor("edit");
        if (door is null) return;

        Console.WriteLine($"\nEditing '{door.Name}' (blank = keep current).");

        Console.Write($"  Name [{door.Name}]: ");
        var nm = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(nm)) door.Name = nm.Trim();

        Console.Write($"  Description [{door.Description}]: ");
        var ds = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(ds)) door.Description = ds.Trim();

        door.IsLocked     = PromptBool("IsLocked",     door.IsLocked);
        door.IsPickable   = PromptBool("IsPickable",   door.IsPickable);
        if (PromptBool("IsTrapped (sets Mechanical)", door.IsTrapped))
            door.TrapTypes = TrapType.Mechanical;
        else
            door.TrapTypes = TrapType.None;
        door.TrapDisarmed = PromptBool("TrapDisarmed", door.TrapDisarmed);
        door.IsSecret     = PromptBool("IsSecret",     door.IsSecret);
        door.IsDiscovered = PromptBool("IsDiscovered", door.IsDiscovered);

        door.TrapDamage = PromptInt("TrapDamage", door.TrapDamage);
        door.UnlockDC   = PromptInt("UnlockDC",   door.UnlockDC);

        Console.Write($"  RequiredKeyId [{door.RequiredKeyId ?? "—"}] (type 'clear' to null it, blank to keep): ");
        var rk = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(rk))
            door.RequiredKeyId = string.Equals(rk.Trim(), "clear", StringComparison.OrdinalIgnoreCase)
                ? null
                : rk.Trim();

        _dbContext.SaveChanges();
        Console.WriteLine($"\nDoor '{door.Name}' updated.");
    }

    private static bool PromptBool(string label, bool current)
    {
        Console.Write($"  {label} [{current}] (y/n, blank=keep): ");
        var raw = Console.ReadLine()?.Trim().ToLowerInvariant();
        if (string.IsNullOrEmpty(raw)) return current;
        if (raw is "y" or "yes" or "true" or "1") return true;
        if (raw is "n" or "no" or "false" or "0") return false;
        return current;
    }

    private static int PromptInt(string label, int current)
    {
        Console.Write($"  {label} [{current}] (blank=keep): ");
        var raw = Console.ReadLine();
        if (string.IsNullOrWhiteSpace(raw)) return current;
        return int.TryParse(raw.Trim(), out var v) ? v : current;
    }

    private void RemoveDoor()
    {
        var door = PromptDoor("remove");
        if (door is null) return;
        _dbContext.RemoveEntity(door);
        _dbContext.SaveChanges();
        Console.WriteLine($"Door '{door.Name}' removed.");
    }

    // -------------------------------------------------------------------------
    // Skills / Abilities / Magic — global definition CRUD + assign-to-character
    // -------------------------------------------------------------------------

    public void SkillsSubmenu()
    {
        while (true)
        {
            Console.WriteLine("\n=== Skills ===");
            Console.WriteLine("  1. List   2. Create   3. Edit   4. Delete   5. Assign to character   0. Back");
            Console.Write("Choice: ");
            switch (Console.ReadLine()?.Trim())
            {
                case "1": ListSkills(); break;
                case "2": CreateSkill(); break;
                case "3": EditSkillDef(); break;
                case "4": DeleteSkillDef(); break;
                case "5": AssignSkillToCharacter(); break;
                case "0": return;
                default: Console.WriteLine("Invalid."); break;
            }
        }
    }

    private void ListSkills()
    {
        var skills = _dbContext.Skills.ToList();
        if (!skills.Any()) { Console.WriteLine("\nNo skills."); return; }
        Console.WriteLine("\n--- Skills ---");
        foreach (var s in skills)
        {
            string sec = s.SecondaryAttribute.HasValue ? s.SecondaryAttribute.ToString()! : "—";
            Console.WriteLine($"  [{s.Id}] {s.Name} (Primary: {s.PrimaryAttribute}, Secondary: {sec})");
        }
    }

    private void CreateSkill()
    {
        Console.Write("Skill name: ");
        var name = Console.ReadLine() ?? "";
        Console.Write("Description: ");
        var desc = Console.ReadLine() ?? "";
        var primary = PromptAttribute("Primary attribute");
        if (primary is null) return;
        Console.Write("Secondary attribute (blank for none): ");
        var secInput = Console.ReadLine()?.Trim();
        CoreAttribute? secondary = null;
        if (!string.IsNullOrEmpty(secInput) && Enum.TryParse<CoreAttribute>(secInput, true, out var sec))
            secondary = sec;

        var skill = new Skill { Name = name, Description = desc, PrimaryAttribute = primary.Value, SecondaryAttribute = secondary };
        _dbContext.AddEntity(skill);
        _dbContext.SaveChanges();
        Console.WriteLine($"Skill '{name}' created (ID {skill.Id}).");
    }

    private Skill? PromptSkill(string verb)
    {
        ListSkills();
        Console.Write($"\nSkill ID to {verb}: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return null; }
        var s = _dbContext.Skills.FirstOrDefault(x => x.Id == id);
        if (s is null) Console.WriteLine("Not found.");
        return s;
    }

    private void EditSkillDef()
    {
        var s = PromptSkill("edit");
        if (s is null) return;
        Console.Write($"Name [{s.Name}] (blank to keep): ");
        var n = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(n)) s.Name = n.Trim();
        Console.Write($"Description [{s.Description}] (blank to keep): ");
        var d = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(d)) s.Description = d.Trim();
        _dbContext.SaveChanges();
        Console.WriteLine("Skill updated.");
    }

    private void DeleteSkillDef()
    {
        var s = PromptSkill("delete");
        if (s is null) return;
        _dbContext.RemoveEntity(s);
        _dbContext.SaveChanges();
        Console.WriteLine("Skill deleted.");
    }

    private void AssignSkillToCharacter()
    {
        var skill = PromptSkill("assign");
        if (skill is null) return;
        var character = ResolveActiveOrPrompt("assign skill to");
        if (character is null) return;
        if (character.CharacterSkills.Any(cs => cs.SkillId == skill.Id))
        {
            Console.WriteLine($"{character.Name} already has {skill.Name}.");
            return;
        }
        Console.Write("Proficiency (integer): ");
        if (!int.TryParse(Console.ReadLine(), out var prof)) { Console.WriteLine("Invalid."); return; }
        var cs = new CharacterSkill { CharacterId = character.Id, SkillId = skill.Id, Proficiency = prof };
        _dbContext.AddEntity(cs);
        _dbContext.SaveChanges();
        Console.WriteLine($"Assigned {skill.Name} (Prof {prof}) to {character.Name}.");
    }

    public void AbilitiesSubmenu()
    {
        while (true)
        {
            Console.WriteLine("\n=== Abilities ===");
            Console.WriteLine("  1. List   2. Create   3. Edit   4. Delete   5. Assign to character   0. Back");
            Console.Write("Choice: ");
            switch (Console.ReadLine()?.Trim())
            {
                case "1": ListAbilities(); break;
                case "2": CreateAbility(); break;
                case "3": EditAbilityDef(); break;
                case "4": DeleteAbilityDef(); break;
                case "5": AssignAbilityToCharacter(); break;
                case "0": return;
                default: Console.WriteLine("Invalid."); break;
            }
        }
    }

    private void ListAbilities()
    {
        var abilities = _dbContext.Abilities.ToList();
        if (!abilities.Any()) { Console.WriteLine("\nNo abilities."); return; }
        Console.WriteLine("\n--- Abilities ---");
        foreach (var a in abilities)
            Console.WriteLine($"  [{a.Id}] {a.Name} ({a.Kind}, Power {a.Power}, Cost {a.StaminaCost} SP, Stat {a.PrimaryStat})");
    }

    private void CreateAbility()
    {
        Console.Write("Ability name: ");
        var name = Console.ReadLine() ?? "";
        Console.Write("Description: ");
        var desc = Console.ReadLine() ?? "";
        Console.Write("Power: ");
        int.TryParse(Console.ReadLine(), out var power);
        Console.Write("Stamina cost: ");
        int.TryParse(Console.ReadLine(), out var cost);
        Console.Write($"Kind ({string.Join("/", Enum.GetNames<AbilityKind>())}): ");
        if (!Enum.TryParse<AbilityKind>(Console.ReadLine(), true, out var kind)) { Console.WriteLine("Invalid kind."); return; }
        var stat = PromptAttribute("Primary stat");
        if (stat is null) return;
        var ab = new Ability { Name = name, Description = desc, Power = power, StaminaCost = cost, Kind = kind, PrimaryStat = stat.Value };
        _dbContext.AddEntity(ab);
        _dbContext.SaveChanges();
        Console.WriteLine($"Ability '{name}' created (ID {ab.Id}).");
    }

    private Ability? PromptAbility(string verb)
    {
        ListAbilities();
        Console.Write($"\nAbility ID to {verb}: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return null; }
        var a = _dbContext.Abilities.FirstOrDefault(x => x.Id == id);
        if (a is null) Console.WriteLine("Not found.");
        return a;
    }

    private void EditAbilityDef()
    {
        var a = PromptAbility("edit");
        if (a is null) return;
        Console.Write($"Name [{a.Name}] (blank to keep): ");
        var n = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(n)) a.Name = n.Trim();
        Console.Write($"Description [{a.Description}] (blank to keep): ");
        var d = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(d)) a.Description = d.Trim();
        Console.Write($"Power [{a.Power}] (blank to keep): ");
        if (int.TryParse(Console.ReadLine(), out var p)) a.Power = p;
        Console.Write($"Stamina cost [{a.StaminaCost}] (blank to keep): ");
        if (int.TryParse(Console.ReadLine(), out var c)) a.StaminaCost = c;
        _dbContext.SaveChanges();
        Console.WriteLine("Ability updated.");
    }

    private void DeleteAbilityDef()
    {
        var a = PromptAbility("delete");
        if (a is null) return;
        _dbContext.RemoveEntity(a);
        _dbContext.SaveChanges();
        Console.WriteLine("Ability deleted.");
    }

    private void AssignAbilityToCharacter()
    {
        var ab = PromptAbility("assign");
        if (ab is null) return;
        var character = ResolveActiveOrPrompt("assign ability to");
        if (character is null) return;
        if (character.Abilities.Any(x => x.Id == ab.Id))
        {
            Console.WriteLine($"{character.Name} already has {ab.Name}.");
            return;
        }
        character.Abilities.Add(ab);
        _dbContext.SaveChanges();
        Console.WriteLine($"Assigned {ab.Name} to {character.Name}.");
    }

    public void MagicSubmenu()
    {
        while (true)
        {
            Console.WriteLine("\n=== Magic ===");
            Console.WriteLine("  1. List   2. Create   3. Edit   4. Delete   5. Assign to character   0. Back");
            Console.Write("Choice: ");
            switch (Console.ReadLine()?.Trim())
            {
                case "1": ListMagic(); break;
                case "2": CreateMagic(); break;
                case "3": EditMagicDef(); break;
                case "4": DeleteMagicDef(); break;
                case "5": AssignMagicToCharacter(); break;
                case "0": return;
                default: Console.WriteLine("Invalid."); break;
            }
        }
    }

    private void ListMagic()
    {
        var magics = _dbContext.Magics.ToList();
        if (!magics.Any()) { Console.WriteLine("\nNo magic defined."); return; }
        Console.WriteLine("\n--- Magic ---");
        foreach (var m in magics)
            Console.WriteLine($"  [{m.Id}] {m.Name} ({m.Element}, {m.Kind}) Power {m.Power}, BitPool {m.BitPoolCost}, Bytes {m.BytePoolCost}, Stat {m.PrimaryStat}");
    }

    private void CreateMagic()
    {
        Console.Write("Magic name: ");
        var name = Console.ReadLine() ?? "";
        Console.Write("Description: ");
        var desc = Console.ReadLine() ?? "";
        Console.Write("Power: ");
        int.TryParse(Console.ReadLine(), out var power);
        Console.Write("BitPool cost: ");
        int.TryParse(Console.ReadLine(), out var bit);
        Console.Write("BytePool cost: ");
        int.TryParse(Console.ReadLine(), out var bytes);
        Console.Write($"Element ({string.Join("/", Enum.GetNames<Element>())}): ");
        if (!Enum.TryParse<Element>(Console.ReadLine(), true, out var element)) { Console.WriteLine("Invalid element."); return; }
        Console.Write($"Kind ({string.Join("/", Enum.GetNames<MagicKind>())}): ");
        if (!Enum.TryParse<MagicKind>(Console.ReadLine(), true, out var kind)) { Console.WriteLine("Invalid kind."); return; }
        var stat = PromptAttribute("Primary stat");
        if (stat is null) return;

        var m = new MagicEntity
        {
            Name = name, Description = desc, Power = power,
            BitPoolCost = bit, BytePoolCost = bytes,
            Element = element, Kind = kind, PrimaryStat = stat.Value
        };
        _dbContext.AddEntity(m);
        _dbContext.SaveChanges();
        Console.WriteLine($"Magic '{name}' created (ID {m.Id}).");
    }

    private MagicEntity? PromptMagic(string verb)
    {
        ListMagic();
        Console.Write($"\nMagic ID to {verb}: ");
        if (!int.TryParse(Console.ReadLine(), out var id)) { Console.WriteLine("Invalid."); return null; }
        var m = _dbContext.Magics.FirstOrDefault(x => x.Id == id);
        if (m is null) Console.WriteLine("Not found.");
        return m;
    }

    private void EditMagicDef()
    {
        var m = PromptMagic("edit");
        if (m is null) return;
        Console.Write($"Name [{m.Name}] (blank to keep): ");
        var n = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(n)) m.Name = n.Trim();
        Console.Write($"Description [{m.Description}] (blank to keep): ");
        var d = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(d)) m.Description = d.Trim();
        Console.Write($"Power [{m.Power}] (blank to keep): ");
        if (int.TryParse(Console.ReadLine(), out var p)) m.Power = p;
        Console.Write($"BitPool cost [{m.BitPoolCost}] (blank to keep): ");
        if (int.TryParse(Console.ReadLine(), out var bp)) m.BitPoolCost = bp;
        Console.Write($"BytePool cost [{m.BytePoolCost}] (blank to keep): ");
        if (int.TryParse(Console.ReadLine(), out var by)) m.BytePoolCost = by;
        _dbContext.SaveChanges();
        Console.WriteLine("Magic updated.");
    }

    private void DeleteMagicDef()
    {
        var m = PromptMagic("delete");
        if (m is null) return;
        _dbContext.RemoveEntity(m);
        _dbContext.SaveChanges();
        Console.WriteLine("Magic deleted.");
    }

    private void AssignMagicToCharacter()
    {
        var m = PromptMagic("assign");
        if (m is null) return;
        var character = ResolveActiveOrPrompt("assign magic to");
        if (character is null) return;
        if (character.Magics.Any(x => x.Id == m.Id))
        {
            Console.WriteLine($"{character.Name} already knows {m.Name}.");
            return;
        }
        character.Magics.Add(m);
        _dbContext.SaveChanges();
        Console.WriteLine($"Assigned {m.Name} to {character.Name}.");
    }

    private static CoreAttribute? PromptAttribute(string label)
    {
        Console.Write($"{label} ({string.Join("/", Enum.GetNames<CoreAttribute>())}): ");
        if (Enum.TryParse<CoreAttribute>(Console.ReadLine(), true, out var attr)) return attr;
        Console.WriteLine("Invalid attribute.");
        return null;
    }

    // -------------------------------------------------------------------------
    // W15 Phase G — LINQ Queries submenu
    // -------------------------------------------------------------------------

    // Ordered list of interactable objects rendered in DrawRoomContents.
    // Letters a,b,c... map to indices 0,1,2... Rebuilt every loop tick.
    private readonly List<object> _roomObjects = new();

    // Rooms the player has set foot in this session (by container ID).
    // Used by DrawMiniMap to distinguish visited (blue) from known (grey).
    private readonly HashSet<int> _visitedRooms = new();

    private void DrawMiniMap(Character player)
    {
        var allRooms = _dbContext.Containers.OfType<Room>()
            .Where(r => r.GridX != null && r.GridY != null)
            .ToList();
        if (!allRooms.Any()) { Console.WriteLine("  (No rooms on grid.)"); return; }

        var doors = _dbContext.Doors.ToList();

        // Known rooms = visited rooms PLUS rooms reachable via a visible door from any visited room.
        var knownIds = new HashSet<int>(_visitedRooms);
        foreach (var vid in _visitedRooms)
            foreach (var d in doors.Where(d => (d.RoomAId == vid || d.RoomBId == vid) && d.IsVisible))
            { knownIds.Add(d.RoomAId); knownIds.Add(d.RoomBId); }

        int minX = allRooms.Min(r => r.GridX!.Value), maxX = allRooms.Max(r => r.GridX!.Value);
        int minY = allRooms.Min(r => r.GridY!.Value), maxY = allRooms.Max(r => r.GridY!.Value);
        int cols = maxX - minX + 1, rows = maxY - minY + 1;

        var grid = allRooms.ToDictionary(r => (r.GridX!.Value - minX, r.GridY!.Value - minY));

        bool HasVisibleDoor(Room? a, Room? b) => a is not null && b is not null &&
            doors.Any(d => d.IsVisible &&
                ((d.RoomAId == a.Id && d.RoomBId == b.Id) || (d.RoomAId == b.Id && d.RoomBId == a.Id)));

        string Cell(Room? r)
        {
            if (r is null || !knownIds.Contains(r.Id)) return " ";
            if (r.Id == player.RoomId) return "[bold red]■[/]";
            if (_visitedRooms.Contains(r.Id))          return "[blue]■[/]";
            return "[grey]□[/]";
        }

        var lines = new List<string>();
        for (int row = 0; row < rows; row++)
        {
            var rLine = new System.Text.StringBuilder();
            var cLine = new System.Text.StringBuilder();

            for (int col = 0; col < cols; col++)
            {
                grid.TryGetValue((col, row),     out var room);
                grid.TryGetValue((col + 1, row), out var rRight);
                grid.TryGetValue((col, row + 1), out var rBelow);

                rLine.Append(Cell(room));

                // Horizontal door connector
                bool hVisible = room is not null && rRight is not null
                    && knownIds.Contains(room.Id) && knownIds.Contains(rRight.Id);
                rLine.Append(hVisible && HasVisibleDoor(room, rRight) ? "─" : " ");

                // Vertical door connector (for connector row)
                bool vVisible = room is not null && rBelow is not null
                    && knownIds.Contains(room.Id) && knownIds.Contains(rBelow.Id);
                cLine.Append(vVisible && HasVisibleDoor(room, rBelow) ? "│" : " ");
                cLine.Append(" ");
            }

            lines.Add(rLine.ToString().TrimEnd());
            if (row < rows - 1)
                lines.Add(cLine.ToString().TrimEnd());
        }

        AnsiConsole.Write(new Panel(string.Join("\n", lines))
        {
            Header = new PanelHeader("[yellow bold] Map [/]"),
            Border = BoxBorder.Rounded,
            Padding = new Padding(2, 1),
        });
        AnsiConsole.MarkupLine("  [bold red]■[/] here  [blue]■[/] visited  [grey]□[/] known  ─│ door");
    }

    public void PlayerLoop()
    {
        var player = _activeCharacter!;
        if (player.Room is null)
        {
            Console.WriteLine("\nCharacter is not placed in any room. Returning to menu.");
            return;
        }

        bool playing = true;
        while (playing && (player.Resources?.Hp ?? 0) > 0)
        {
            if (player.RoomId.HasValue) _visitedRooms.Add(player.RoomId.Value);
            Console.Clear();
            DrawRoomPanel(player);
            DrawRoomContents(player);

            Console.Write("\n  Choice: ");
            var input = Console.ReadLine()?.Trim().ToLower() ?? string.Empty;

            if (input == "q") { playing = false; break; }
            if (input == "i") { InventoryMenu(); continue; }
            if (input == "m") { Console.Clear(); DrawMiniMap(player); _gameUi.PauseAndClear(); continue; }
            if (input == "x") { InspectRoomForSecrets(player); _gameUi.PauseAndClear(); continue; }

            if (int.TryParse(input, out int exitIdx))
            {
                TakeExitByIndex(player, exitIdx);
                continue;
            }

            if (input.Length == 1 && char.IsLetter(input[0]))
            {
                HandleRoomObjectInteraction(player, input[0]);
                continue;
            }

            Console.WriteLine("  Unknown command.");
            _gameUi.PauseAndClear();
        }

        if ((player.Resources?.Hp ?? 0) <= 0)
            Console.WriteLine($"\n  {player.Name} has fallen. Returning to menu.");
    }

    private void DrawRoomPanel(Character player)
    {
        var room = player.Room!;
        int hp    = player.Resources?.Hp    ?? 0;
        int maxHp = player.Resources?.MaxHp ?? 1;
        string hpColor = hp > maxHp * 0.6 ? "green" : hp > maxHp * 0.25 ? "yellow" : "red";
        var hpBar = $"[{hpColor}]HP {hp}/{maxHp}[/]";

        var panel = new Panel($"{hpBar}   [grey]{player.Name} · Lv {player.Level} {player.TypeName}[/]")
        {
            Header = new PanelHeader($"[yellow bold]{room.Name}[/]"),
            Border = BoxBorder.Rounded,
        };
        AnsiConsole.Write(panel);
        AnsiConsole.MarkupLine($"  [italic grey]{room.Description}[/]\n");
    }

    private void DrawRoomContents(Character player)
    {
        var room = player.Room!;

        var exits = room.AllDoors.Where(d => d.IsVisible).ToList();
        var chests = _dbContext.Containers.OfType<Chest>()
            .Where(c => c.RoomId == player.RoomId).ToList();
        var bookshelves = _dbContext.Containers.OfType<Bookshelf>()
            .Where(b => b.RoomId == player.RoomId).ToList();
        var floorItems = room.ItemsCollection.ToList();
        var npcs = room.Characters.Where(c => c.Id != player.Id).ToList();

        // --- Exits ---
        AnsiConsole.MarkupLine("  [bold]Exits:[/]");
        if (exits.Count == 0)
            Console.WriteLine("    (none)");
        for (int i = 0; i < exits.Count; i++)
        {
            var d = exits[i];
            var other = d.GetOtherRoom(room);
            Console.WriteLine($"    [{i + 1}] {d.Name} → {other.Name}");
        }

        // --- Objects (lettered a,b,c…) ---
        _roomObjects.Clear();
        int letterIdx = 0;
        Console.WriteLine();
        AnsiConsole.MarkupLine("  [bold]Here:[/]");
        bool anything = false;

        foreach (var npc in npcs)
        {
            char ltr = (char)('a' + letterIdx++);
            bool dead = (npc.Resources?.Hp ?? 1) <= 0;
            string status = dead
                ? "[grey]defeated[/]"
                : $"[red]HP {npc.Resources?.Hp}/{npc.Resources?.MaxHp}[/]";
            AnsiConsole.MarkupLine($"    [[{ltr}]] {Markup.Escape(npc.Name)} ({Markup.Escape(npc.TypeName)}) — {status}");
            _roomObjects.Add(npc);
            anything = true;
        }
        foreach (var chest in chests)
        {
            char ltr = (char)('a' + letterIdx++);
            AnsiConsole.MarkupLine($"    [[{ltr}]] {Markup.Escape(chest.Name)} [grey](chest)[/]");
            _roomObjects.Add(chest);
            anything = true;
        }
        foreach (var shelf in bookshelves)
        {
            char ltr = (char)('a' + letterIdx++);
            AnsiConsole.MarkupLine($"    [[{ltr}]] [blue]{Markup.Escape(shelf.Name)}[/] (bookshelf)");
            _roomObjects.Add(shelf);
            anything = true;
        }
        foreach (var item in floorItems)
        {
            char ltr = (char)('a' + letterIdx++);
            AnsiConsole.MarkupLine($"    [[{ltr}]] [italic]{Markup.Escape(item.Name)}[/] (on floor)");
            _roomObjects.Add(item);
            anything = true;
        }

        if (!anything)
            Console.WriteLine("    (nothing here)");

        Console.WriteLine("\n  [#] move  [letter] interact  [i] inventory  [m] map  [x] inspect  [q] quit");
    }

    private void TakeExitByIndex(Character player, int exitIdx)
    {
        var exits = player.Room!.AllDoors.Where(d => d.IsVisible).ToList();
        if (exitIdx < 1 || exitIdx > exits.Count)
        {
            Console.WriteLine("  No such exit.");
            return;
        }

        var door = exits[exitIdx - 1];
        if (door.IsLocked)
        {
            Console.WriteLine($"\n  The {door.Name} is locked.");
            Console.Write("  (u)nlock with a key/lockpick? ");
            if (Console.ReadLine()?.Trim().ToLower() == "u")
                TryUnlockTarget(player, door, door.Name);
            _gameUi.PauseAndClear();
            return;
        }

        if (door.IsTrapped && !door.TrapDisarmed)
        {
            door.TrapDisarmed = true;
            if (player.Resources is not null)
                player.Resources.Hp = Math.Max(0, player.Resources.Hp - door.TrapDamage);
            AnsiConsole.MarkupLine($"\n  [red]A {door.TrapTypes} trap fires![/] {Markup.Escape(player.Name)} takes [red]{door.TrapDamage}[/] damage.");
            _gameUi.PauseAndClear();
        }

        var destination = door.GetOtherRoom(player.Room!);
        player.RoomId = destination.Id;
        _dbContext.SaveChanges();
        Console.WriteLine($"\n  {player.Name} passes through {door.Name} into {destination.Name}.");
    }

    private void HandleRoomObjectInteraction(Character player, char letter)
    {
        int idx = letter - 'a';
        if (idx < 0 || idx >= _roomObjects.Count) { Console.WriteLine("  Invalid."); return; }
        var obj = _roomObjects[idx];
        switch (obj)
        {
            case Character npc:    PlayerNpcInteraction(player, npc); break;
            case Chest chest:      PlayerChestInteraction(player, chest); break;
            case Bookshelf shelf:  PlayerBookshelfInteraction(player, shelf); break;
            case Item item:        PlayerFloorItemInteraction(player, item); break;
            default: Console.WriteLine("  Nothing to do."); break;
        }
    }

    private void PlayerFloorItemInteraction(Character player, Item item)
    {
        AnsiConsole.MarkupLine($"\n  [bold]{Markup.Escape(item.Name)}[/] — {Markup.Escape(item.Description)}");
        AnsiConsole.MarkupLine($"  [grey]{item.Value}g · {item.Weight} lb[/]");
        Console.Write("  Pick up? (y/n): ");
        if (Console.ReadLine()?.Trim().ToLower() == "y")
        {
            if (player.TakeItemFrom(player.Room!, item))
            { Console.WriteLine($"  Picked up {item.Name}."); _dbContext.SaveChanges(); }
            else
                Console.WriteLine("  Can't carry that (too heavy or no inventory).");
        }
        _gameUi.PauseAndClear();
    }

    private void PlayerChestInteraction(Character player, Chest chest)
    {
        string state = chest.IsLocked ? "locked" : "unlocked";
        Console.WriteLine($"\n  {chest.Name} [{state}] — {chest.Description}");

        if (chest.IsLocked)
        {
            Console.Write("  (u)nlock / (c)ancel: ");
            if (Console.ReadLine()?.Trim().ToLower() == "u")
                TryUnlockTarget(player, chest, chest.Name);
            _gameUi.PauseAndClear();
            return;
        }

        var result = player.OpenChest(chest);
        if (result == OpenResult.Trapped)
        {
            AnsiConsole.MarkupLine($"\n  [red]A {chest.TrapTypes} trap fires![/] {Markup.Escape(player.Name)} takes [red]{chest.TrapDamage}[/] damage.");
            _dbContext.SaveChanges();
            _gameUi.PauseAndClear();
        }
        else if (result == OpenResult.Locked)
        {
            Console.WriteLine("  Still locked.");
            _gameUi.PauseAndClear();
            return;
        }

        Console.Write("  (l)oot / (c)ancel: ");
        if (Console.ReadLine()?.Trim().ToLower() == "l")
            LootInteractive(player, chest, $"Inside {chest.Name}");
        _dbContext.SaveChanges();
    }

    private void PlayerBookshelfInteraction(Character player, Bookshelf shelf)
    {
        var books = shelf.ItemsCollection.ToList();
        Console.WriteLine($"\n  {shelf.Name}");
        if (!string.IsNullOrWhiteSpace(shelf.Description))
            Console.WriteLine($"  {shelf.Description}");

        if (!books.Any()) { Console.WriteLine("  (empty)"); return; }

        for (int i = 0; i < books.Count; i++)
            Console.WriteLine($"    [{i + 1}] {books[i].Name}");

        Console.Write("  Which # (0 to cancel): ");
        if (!int.TryParse(Console.ReadLine()?.Trim(), out int idx) || idx < 1 || idx > books.Count)
            return;

        var book = books[idx - 1];
        // Tomes have LoreText; other items (seeded as Consumable) use Description.
        string readText = book is Tome t ? t.LoreText : book.Description;

        Console.Write("  (r)ead in place / (t)ake to inventory / (c)ancel: ");
        var act = Console.ReadLine()?.Trim().ToLower();
        if (act == "r")
        {
            Console.WriteLine($"\n=== {book.Name} ===");
            Console.WriteLine(readText);
            Console.WriteLine("===========================");
        }
        else if (act == "t")
        {
            if (player.TakeItemFrom(shelf, book))
            { Console.WriteLine($"  Took {book.Name}."); _dbContext.SaveChanges(); }
            else
                Console.WriteLine("  Can't carry that.");
        }
        _gameUi.PauseAndClear();
    }

    // Tracks whether Mira has already given the cellar-clear reward this session.
    private bool _cellarRewarded = false;

    private void PlayerNpcInteraction(Character player, Character npc)
    {
        bool dead = (npc.Resources?.Hp ?? 1) <= 0;

        if (dead)
        {
            Console.WriteLine($"\n  {Markup.Escape(npc.Name)} — defeated.");
            Console.Write("  (l)oot body / (c)ancel: ");
            var c = Console.ReadLine()?.Trim().ToLower();
            if (c == "l" && npc.Inventory is not null)
                LootInteractive(player, npc.Inventory, $"On {npc.Name}'s body");
            return;
        }

        // Named dialogue dispatch
        switch (npc.Name)
        {
            case "Mira":                 MiraDialogue(player, npc);    return;
            case "Gobby":                GobbyDialogue(player, npc);   return;
            case "Erasmus the Unbound":  ErasmusDialogue(player, npc); return;
        }

        // Generic NPC fallback
        Console.WriteLine($"\n  {Markup.Escape(npc.Name)} — {npc.TypeName}, Lv {npc.Level}");
        Console.WriteLine($"  HP: {npc.Resources?.Hp}/{npc.Resources?.MaxHp}  " +
                          $"ATK: {npc.GetTotalAttack()}  DEF: {npc.GetTotalDefense()}");
        Console.Write("  (f)ight / (e)xamine / (c)ancel: ");
        var choice = Console.ReadLine()?.Trim().ToLower();
        if (choice == "f") PlayerFightNpc(player, npc);
        else if (choice == "e")
            Console.WriteLine($"  {Markup.Escape(npc.Name)} watches you carefully.");
    }

    private void MiraDialogue(Character player, Character mira)
    {
        bool cellarCleared = IsCellarCleared();

        while (true)
        {
            Console.Clear();
            AnsiConsole.MarkupLine("[bold yellow]Mira[/] leans on the bar and gives you a measured look.");
            Console.WriteLine();

            var opts = new List<string>
            {
                "\"What can you tell me about the area?\"",
                "\"Do you have anything for sale?\"",
            };

            if (!cellarCleared)
                opts.Add("\"Something's been making noise in your cellar.\"");
            else if (!_cellarRewarded)
                opts.Add("\"The cellar is clear — I dealt with your rat problem.\"");

            opts.Add("\"Goodbye.\"");

            var pick = AnsiConsole.Prompt(
                new SelectionPrompt<string>().Title("  [grey]You say:[/]").AddChoices(opts));

            if (pick.StartsWith("\"What can you tell"))
            {
                Console.WriteLine();
                AnsiConsole.MarkupLine("  [bold yellow]Mira:[/] \"The Thornwood's been restless lately. Goblins closer");
                AnsiConsole.MarkupLine("  to town than they should be — there's a camp north along the trail.");
                AnsiConsole.MarkupLine("  And stay away from that old chapel further east. Door's been rigged");
                AnsiConsole.MarkupLine("  since before my grandmother's time. Nobody worth trusting goes in there.\"");
                Console.WriteLine();
                AnsiConsole.MarkupLine("  [grey]She pauses, then adds quietly:[/]");
                AnsiConsole.MarkupLine("  [bold yellow]Mira:[/] \"Whatever was sealed beneath that vault — let it stay sealed.\"");
                _gameUi.PauseAndClear();
            }
            else if (pick.StartsWith("\"Do you have anything"))
            {
                MiraShop(player, mira);
            }
            else if (pick.StartsWith("\"Something's been making"))
            {
                Console.WriteLine();
                AnsiConsole.MarkupLine("  [bold yellow]Mira:[/] \"Ha. You noticed that too? Something got in through the old drain.");
                AnsiConsole.MarkupLine("  Big. Knocked over half a barrel of my best stock. If you can clear it out,");
                AnsiConsole.MarkupLine("  I'll make it worth your while.\"");
                _gameUi.PauseAndClear();
                break;
            }
            else if (pick.StartsWith("\"The cellar is clear"))
            {
                Console.WriteLine();
                AnsiConsole.MarkupLine("  [bold yellow]Mira:[/] \"Already? Good. Didn't even hear a scream — you're either");
                AnsiConsole.MarkupLine("  very capable or very quiet. Either way, take this.\"");
                Console.WriteLine();
                AnsiConsole.MarkupLine("  [green]Mira hands you a Healing Potion and a Lockpick.[/]");

                if (player.Inventory is not null)
                {
                    var potion = new ConsoleRpgEntities.Models.Items.Consumable
                    {
                        Name = "Healing Potion",
                        Description = "A ruby flask that warms on the way down. Restores 25 HP.",
                        Value = 30, Weight = 1,
                        Effect = ConsoleRpgEntities.Models.Enums.ConsumableEffect.Heal,
                        Potency = 25
                    };
                    var pick2 = new ConsoleRpgEntities.Models.Items.Consumable
                    {
                        Name = "Lockpick",
                        Description = "A thin wire pick. Breaks on a bad roll.",
                        Value = 15, Weight = 0,
                        KeyId = ConsoleRpgEntities.Models.Items.Item.LockpickKeyId,
                        Effect = ConsoleRpgEntities.Models.Enums.ConsumableEffect.None
                    };
                    player.Inventory.AddItem(potion);
                    player.Inventory.AddItem(pick2);
                    _dbContext.SaveChanges();
                }
                _cellarRewarded = true;
                cellarCleared = true;
                _gameUi.PauseAndClear();
            }
            else // Goodbye
            {
                break;
            }
        }
    }

    private void MiraShop(Character player, Character mira)
    {
        if (mira.Inventory is null || !mira.Inventory.ItemsCollection.Any())
        {
            AnsiConsole.MarkupLine("  [bold yellow]Mira:[/] \"Sold out, I'm afraid. Come back when I've restocked.\"");
            _gameUi.PauseAndClear();
            return;
        }

        while (true)
        {
            Console.Clear();
            AnsiConsole.MarkupLine("[bold yellow]Mira's Shop[/]");
            Console.WriteLine();

            var shopItems = mira.Inventory.ItemsCollection.ToList();
            var shopChoices = shopItems
                .Select(i => $"{Markup.Escape(i.Name)} — {Markup.Escape(i.Description)} [[{i.Value}g]]")
                .Append("Leave shop")
                .ToList();

            var sel = AnsiConsole.Prompt(
                new SelectionPrompt<string>().Title("  [grey]What will you take?[/]").AddChoices(shopChoices));

            if (sel == "Leave shop") break;

            var chosen = shopItems[shopChoices.IndexOf(sel)];
            if (player.PickUp(chosen))
            {
                mira.Inventory.RemoveItem(chosen);
                AnsiConsole.MarkupLine($"  [green]You take {Markup.Escape(chosen.Name)}.[/]");
                _dbContext.SaveChanges();
            }
            else
            {
                AnsiConsole.MarkupLine("  [red]You can't carry that.[/]");
            }

            if (!mira.Inventory.ItemsCollection.Any()) break;
            _gameUi.PauseAndClear();
        }
    }

    private bool IsCellarCleared()
    {
        var rat = _dbContext.Characters.ToList()
            .FirstOrDefault(c => c.Name == "Giant Cellar Rat");
        return rat?.Resources?.Hp <= 0;
    }

    private void GobbyDialogue(Character player, Character gobby)
    {
        Console.Clear();
        AnsiConsole.MarkupLine("[bold green]Gobby[/] spins around, pointing a jagged cleaver at you.");
        Console.WriteLine();
        AnsiConsole.MarkupLine("  [bold green]Gobby:[/] \"Oi! Who dares walk into Gobby's camp? You lost, soft-skin?\"");
        Console.WriteLine();

        var pick = AnsiConsole.Prompt(new SelectionPrompt<string>()
            .Title("  [grey]You say:[/]")
            .AddChoices(
                "\"I'm here to fight.\"",
                "\"I'm just passing through.\"",
                "\"Nice camp you have here.\""
            ));

        Console.WriteLine();
        if (pick.StartsWith("\"I'm here"))
        {
            AnsiConsole.MarkupLine("  [bold green]Gobby:[/] \"Ohoho! Brave words, soft-skin. Gobby loves brave words.");
            AnsiConsole.MarkupLine("  Makes the winning sweeter. COME THEN!\"");
        }
        else if (pick.StartsWith("\"I'm just passing"))
        {
            AnsiConsole.MarkupLine("  [bold green]Gobby:[/] \"Passing THROUGH? Through Gobby's camp?\"");
            AnsiConsole.MarkupLine("  [grey]Gobby's eyes narrow to slits.[/]");
            AnsiConsole.MarkupLine("  [bold green]Gobby:[/] \"Nobody passes through. Gobby ALWAYS gets a toll.\"");
        }
        else
        {
            AnsiConsole.MarkupLine("  [bold green]Gobby:[/] \"...Heh. Gobby does have good taste.\"");
            AnsiConsole.MarkupLine("  [grey]Gobby preens briefly, then his expression hardens.[/]");
            AnsiConsole.MarkupLine("  [bold green]Gobby:[/] \"But now Gobby have YOUR stuff! CHARGE!\"");
        }

        Console.WriteLine();
        _gameUi.PauseAndClear();
        PlayerFightNpc(player, gobby);
    }

    private void ErasmusDialogue(Character player, Character erasmus)
    {
        Console.Clear();
        AnsiConsole.MarkupLine("[bold magenta]The air in the vault shifts. Something stirs.[/]");
        Console.WriteLine();
        System.Threading.Thread.Sleep(800);

        AnsiConsole.MarkupLine("  [bold magenta]Erasmus:[/] \"Do you feel that?\"");
        System.Threading.Thread.Sleep(600);
        AnsiConsole.MarkupLine("  [bold magenta]Erasmus:[/] \"The seal... it [italic]breaks[/].\"");
        System.Threading.Thread.Sleep(800);
        Console.WriteLine();

        AnsiConsole.MarkupLine("  [bold magenta]Erasmus:[/] \"I have waited here for three hundred years, bound by");
        AnsiConsole.MarkupLine("  cowards who feared what I could become. Three centuries of");
        AnsiConsole.MarkupLine("  silence. Three centuries of [bold]patience[/].\"");
        Console.WriteLine();
        System.Threading.Thread.Sleep(1000);

        AnsiConsole.MarkupLine("  [bold magenta]Erasmus:[/] \"And now some wandering fool cracks the seal and walks");
        AnsiConsole.MarkupLine("  in with [italic]mud on their boots[/].\"");
        Console.WriteLine();
        System.Threading.Thread.Sleep(700);

        AnsiConsole.MarkupLine("  A figure rises from the shattered sarcophagus — skeletal,");
        AnsiConsole.MarkupLine("  robed, eyes burning cold blue.");
        Console.WriteLine();
        System.Threading.Thread.Sleep(800);

        AnsiConsole.MarkupLine("  [bold magenta]Erasmus:[/] \"I am [bold white]ERASMUS THE UNBOUND[/] — and I am [bold]free[/].");
        AnsiConsole.MarkupLine("  You... unfortunate soul. You should have left the key");
        AnsiConsole.MarkupLine("  where you found it.\"");
        Console.WriteLine();

        _gameUi.PauseAndClear();
        PlayerFightNpc(player, erasmus);
    }

    private void PlayerFightNpc(Character player, Character npc)
    {
        var rng = new Random();
        AnsiConsole.MarkupLine($"\n  [bold red]⚔ {Markup.Escape(player.Name)} vs. {Markup.Escape(npc.Name)}![/]\n");

        int round = 1;
        bool fled = false;

        while ((player.Resources?.Hp ?? 0) > 0 && (npc.Resources?.Hp ?? 0) > 0)
        {
            // Status header
            AnsiConsole.MarkupLine(
                $"  [bold]Round {round}[/]  " +
                $"[green]Your HP {player.Resources?.Hp}/{player.Resources?.MaxHp}[/]  " +
                $"[yellow]{Markup.Escape(npc.Name)} HP {npc.Resources?.Hp}/{npc.Resources?.MaxHp}[/]");

            // Player action menu
            var choices = new List<string> { "⚔  Attack" };
            var abilities = player.Abilities.Where(a => a.Kind == AbilityKind.Attack).ToList();
            if (abilities.Any()) choices.Add("✦  Ability");
            var magics = player.Magics.Where(m => m.Kind == MagicKind.Attack
                && (player.Resources?.BitPool ?? 0) >= m.BitPoolCost
                && (player.Resources?.BytePool ?? 0) >= m.BytePoolCost).ToList();
            if (magics.Any()) choices.Add("⚡  Magic");
            var consumables = player.Inventory?.ItemsCollection.OfType<Consumable>()
                .Where(c => c.Effect == ConsumableEffect.Heal || c.Effect == ConsumableEffect.Stamina).ToList() ?? new List<Consumable>();
            if (consumables.Any()) choices.Add("🧪  Item");
            choices.Add("🚪  Flee");

            var action = AnsiConsole.Prompt(
                new SelectionPrompt<string>()
                    .Title("  [grey]Your action:[/]")
                    .AddChoices(choices));

            int pDmg = 0;
            if (action.StartsWith("⚔"))
            {
                pDmg = Math.Max(1, player.GetTotalAttack() + rng.Next(1, 7) - npc.GetTotalDefense());
                if (npc.Resources is not null) npc.Resources.Hp = Math.Max(0, npc.Resources.Hp - pDmg);
                AnsiConsole.MarkupLine($"  You strike for [red]{pDmg}[/] damage.");
            }
            else if (action.StartsWith("✦") && abilities.Any())
            {
                var abil = AnsiConsole.Prompt(new SelectionPrompt<string>()
                    .Title("  Choose ability:")
                    .AddChoices(abilities.Select(a => $"{a.Name} (SP {a.StaminaCost}, Power {a.Power})")));
                var chosen = abilities[abilities.FindIndex(a => abil.StartsWith(a.Name))];
                if ((player.Resources?.Sp ?? 0) >= chosen.StaminaCost)
                {
                    if (player.Resources is not null) player.Resources.Sp -= chosen.StaminaCost;
                    pDmg = Math.Max(1, chosen.Power + rng.Next(1, 7) - npc.GetTotalDefense());
                    if (npc.Resources is not null) npc.Resources.Hp = Math.Max(0, npc.Resources.Hp - pDmg);
                    AnsiConsole.MarkupLine($"  [cyan]{Markup.Escape(chosen.Name)}[/] hits for [red]{pDmg}[/] damage.");
                }
                else
                    AnsiConsole.MarkupLine("  [yellow]Not enough Stamina.[/] Turn wasted.");
            }
            else if (action.StartsWith("⚡"))
            {
                if (!magics.Any()) { AnsiConsole.MarkupLine("  No attack magic available."); }
                else
                {
                    var availMagics = magics;
                    var mSel = AnsiConsole.Prompt(new SelectionPrompt<string>()
                        .Title("  Choose spell:")
                        .AddChoices(availMagics.Select(m =>
                        {
                            string cost = m.BitPoolCost > 0 ? $"{m.BitPoolCost} Bits" : $"{m.BytePoolCost} Bytes";
                            return $"{m.Name} ({cost}, Power {m.Power})";
                        })));
                    var mChosen = availMagics[availMagics.FindIndex(m => mSel.StartsWith(m.Name))];
                    bool canCast = (player.Resources?.BitPool ?? 0) >= mChosen.BitPoolCost
                                && (player.Resources?.BytePool ?? 0) >= mChosen.BytePoolCost;
                    if (canCast)
                    {
                        if (player.Resources is not null)
                        {
                            player.Resources.BitPool -= mChosen.BitPoolCost;
                            player.Resources.BytePool -= mChosen.BytePoolCost;
                        }
                        pDmg = Math.Max(1, mChosen.Power + rng.Next(1, 7) - npc.GetTotalDefense());
                        if (npc.Resources is not null) npc.Resources.Hp = Math.Max(0, npc.Resources.Hp - pDmg);
                        AnsiConsole.MarkupLine($"  [magenta]{Markup.Escape(mChosen.Name)}[/] hits for [red]{pDmg}[/] damage.");
                    }
                    else
                    {
                        string poolName = mChosen.BitPoolCost > 0 ? "BitPool" : "BytePool";
                        AnsiConsole.MarkupLine($"  [yellow]Not enough {poolName}.[/] Turn wasted.");
                    }
                }
            }
            else if (action.StartsWith("🧪") && consumables.Any())
            {
                var iSel = AnsiConsole.Prompt(new SelectionPrompt<string>()
                    .Title("  Use which item?")
                    .AddChoices(consumables.Select(c => $"{c.Name} (+{c.Potency} {c.Effect})")));
                var iChosen = consumables[consumables.FindIndex(c => iSel.StartsWith(c.Name))];
                player.UseItem(iChosen);
                AnsiConsole.MarkupLine($"  Used [italic]{Markup.Escape(iChosen.Name)}[/].");
            }
            else if (action.StartsWith("🚪"))
            {
                AnsiConsole.MarkupLine("  You break away and escape!");
                fled = true;
                break;
            }

            if ((npc.Resources?.Hp ?? 0) <= 0) break;

            // NPC attacks back
            int nDmg = Math.Max(1, npc.GetTotalAttack() + rng.Next(1, 7) - player.GetTotalDefense());
            if (player.Resources is not null)
                player.Resources.Hp = Math.Max(0, player.Resources.Hp - nDmg);
            AnsiConsole.MarkupLine(
                $"  {Markup.Escape(npc.Name)} retaliates for [red]{nDmg}[/]. " +
                $"Your HP: [green]{player.Resources?.Hp}[/]/{player.Resources?.MaxHp}");

            round++;
            Console.WriteLine();
        }

        _dbContext.SaveChanges();

        if (fled) return;

        if ((npc.Resources?.Hp ?? 0) <= 0)
        {
            AnsiConsole.MarkupLine($"\n  [green bold]{Markup.Escape(npc.Name)} defeated![/]");
            if (npc.Inventory is not null)
            {
                Console.Write("  Loot body? (y/n): ");
                if (Console.ReadLine()?.Trim().ToLower() == "y")
                    LootInteractive(player, npc.Inventory, $"On {npc.Name}'s body");
            }
        }
        else
        {
            AnsiConsole.MarkupLine("\n  [red bold]You were defeated![/] Resting at 1 HP.");
            if (player.Resources is not null) player.Resources.Hp = 1;
            _dbContext.SaveChanges();
        }
    }

    private void InspectRoomForSecrets(Character player)
    {
        if (player.Room is null) { Console.WriteLine("  Not in a room."); return; }

        var allDoors = player.Room.AllDoors.ToList();
        var found = player.InspectForSecretDoors(allDoors);
        _dbContext.SaveChanges();

        if (found.Count == 0)
            Console.WriteLine("\n  You search the room... nothing hidden here.");
        else
            foreach (var d in found)
                Console.WriteLine($"\n  You discover a hidden passage: {d.Name}!");
    }

    public void QueriesMenu()
    {
        while (true)
        {
            Console.WriteLine("\n=== Queries ===");
            Console.WriteLine("  1. Inventory Audit    (items per container type)");
            Console.WriteLine("  2. Most Dangerous Room (total enemy HP per room)");
            Console.WriteLine("  3. Locked Treasures   (what you can't open yet)");
            Console.WriteLine("  0. Back");
            Console.Write("Choice: ");
            var choice = Console.ReadLine()?.Trim();
            switch (choice)
            {
                case "1": LinqInventoryAudit(); break;
                case "2": LinqMostDangerousRoom(); break;
                case "3": LinqLockedTreasures(); break;
                case "0": return;
                default: Console.WriteLine("Invalid choice."); break;
            }
        }
    }

    // ---- W15 LINQ Query 1: InventoryAudit — GroupBy container type ----
    // Demonstrates Phase E payoff: monster loot now shows as "Inventory",
    // not a separate MonsterLoot bucket. The schema unification is visible.
    private void LinqInventoryAudit()
    {
        var allItems = _dbContext.QueryItems().ToList();

        static string ContainerLabel(Container? c) => c switch
        {
            null        => "Unowned",
            Inventory   => "Inventory",
            Equipment   => "Equipment",
            Chest       => "Chest",
            Room        => "Room (Floor)",
            Bookshelf   => "Bookshelf",
            _           => c.GetType().BaseType?.Name ?? c.GetType().Name
        };

        var groups = allItems
            .GroupBy(i => ContainerLabel(i.Container))
            .Select(g => new { Type = g.Key, Count = g.Count() })
            .OrderByDescending(x => x.Count)
            .ToList();

        Console.WriteLine("\n--- Inventory Audit: items per container type ---");
        if (!groups.Any()) { Console.WriteLine("  (no items in database)"); return; }
        foreach (var g in groups)
            Console.WriteLine($"  {g.Type,-20} {g.Count,4} item(s)");
        Console.WriteLine($"  {"Total",-20} {allItems.Count,4}");
    }

    // ---- W15 LINQ Query 2: MostDangerousRoom — GroupBy room, Sum HP ----
    private void LinqMostDangerousRoom()
    {
        var results = _dbContext.Characters.ToList()
            .Where(c => c.RoomId != null && c.Resources != null)
            .GroupBy(c => c.Room?.Name ?? $"Room #{c.RoomId}")
            .Select(g => new { Room = g.Key, TotalHp = g.Sum(c => c.Resources!.Hp), Count = g.Count() })
            .OrderByDescending(x => x.TotalHp)
            .ToList();

        Console.WriteLine("\n--- Most Dangerous Rooms (total current HP of occupants) ---");
        if (!results.Any()) { Console.WriteLine("  (no characters placed in rooms)"); return; }
        foreach (var r in results)
            Console.WriteLine($"  {r.Room,-25} {r.TotalHp,5} HP  ({r.Count} character(s))");
    }

    // ---- W15 LINQ Query 3: LockedTreasures — ILockable LSP payoff ----
    // Spans Chests, Doors, AND LockedJournals. The same interface means
    // the same filter logic works across all three types — LSP at the query layer.
    private void LinqLockedTreasures()
    {
        var player = ResolveActiveOrPrompt("check locked treasures for");
        if (player is null) return;

        var playerKeyIds = (player.Inventory?.ItemsCollection ?? Enumerable.Empty<Item>())
            .Where(i => i.KeyId != null)
            .Select(i => i.KeyId!)
            .ToHashSet(StringComparer.Ordinal);

        bool CannotOpen(ILockable lockable)
        {
            if (!lockable.IsLocked) return false;
            if (lockable.RequiredKeyId != null) return !playerKeyIds.Contains(lockable.RequiredKeyId);
            return !lockable.IsPickable || !playerKeyIds.Contains(Item.LockpickKeyId);
        }

        var results = new List<(string Kind, string Name, string Note)>();

        foreach (var chest in _dbContext.QueryContainers().OfType<Chest>().ToList())
            if (CannotOpen(chest))
                results.Add(("Chest", chest.Name, chest.RequiredKeyId != null ? $"key '{chest.RequiredKeyId}'" : "lockpick"));

        foreach (var door in _dbContext.Doors.ToList())
            if (CannotOpen(door))
                results.Add(("Door", door.Name, door.RequiredKeyId != null ? $"key '{door.RequiredKeyId}'" : "lockpick"));

        foreach (var journal in _dbContext.QueryItems().OfType<LockedJournal>().ToList())
            if (CannotOpen(journal))
                results.Add(("Journal", journal.Name, journal.RequiredKeyId != null ? $"key '{journal.RequiredKeyId}'" : "lockpick"));

        Console.WriteLine($"\n--- Locked Treasures {player.Name} Cannot Open ({results.Count}) ---");
        if (!results.Any()) { Console.WriteLine("  (you hold keys to everything — impressive)"); return; }
        foreach (var (kind, name, note) in results)
            Console.WriteLine($"  [{kind,-8}] {name,-35} — needs {note}");
    }

    // ── World Reset ───────────────────────────────────────────────────────────
    // Resets all enemies, chests, traps, and Elara's inventory to the original
    // seed state. Safe to run any number of times from the Admin menu.
    public void AdminResetWorld()
    {
        Console.Write("\n  Reset the world to its starting state? All progress will be lost. (y/n): ");
        if (Console.ReadLine()?.Trim().ToLower() != "y") { Console.WriteLine("  Cancelled."); return; }

        // --- 1. Restore enemy NPC resources to full ---
        var enemyNames = new[] { "Gobby", "Giant Cellar Rat", "Risen Acolyte", "Crypt Hound", "Erasmus the Unbound" };
        var enemies = _dbContext.Characters.ToList().Where(c => enemyNames.Contains(c.Name)).ToList();
        foreach (var e in enemies)
        {
            if (e.Resources is null) continue;
            e.Resources.Hp       = e.DeriveMaxHp();
            e.Resources.Sp       = e.DeriveMaxSp();
            e.Resources.BitPool  = e.DeriveMaxBitPool();
            e.Resources.BytePool = e.DeriveMaxBytePool();
        }

        // --- 2. Restore enemy loot inventories ---
        void ClearAndRestock(string npcName, Action<Inventory> restock)
        {
            var npc = _dbContext.Characters.ToList().FirstOrDefault(c => c.Name == npcName);
            if (npc?.Inventory is null) return;
            foreach (var item in npc.Inventory.ItemsCollection.ToList())
                _dbContext.RemoveEntity(item);
            restock(npc.Inventory);
        }

        ClearAndRestock("Gobby", inv =>
        {
            inv.AddItem(new Weapon    { Name = "Goblin Cleaver", Description = "Crude, top-heavy, very enthusiastic.", Value = 35, Weight = 4, AttackPower = 8, WeaponType = WeaponType.Axe, Durability = 20 });
            inv.AddItem(new Consumable { Name = "Lockpick",       Description = "A thin wire pick. Breaks on a bad roll.", Value = 5, Weight = 0, KeyId = Item.LockpickKeyId, Effect = ConsumableEffect.None });
            inv.AddItem(new Consumable { Name = "Lockpick",       Description = "A thin wire pick. Breaks on a bad roll.", Value = 5, Weight = 0, KeyId = Item.LockpickKeyId, Effect = ConsumableEffect.None });
            inv.AddItem(new Consumable { Name = "Healing Potion", Description = "A ruby flask that warms on the way down. Restores 25 HP.", Value = 30, Weight = 1, Effect = ConsumableEffect.Heal, Potency = 25 });
        });
        ClearAndRestock("Giant Cellar Rat", inv =>
            inv.AddItem(new Consumable { Name = "Stamina Draft", Description = "Bitter and fizzy. Restores 20 SP.", Value = 25, Weight = 1, Effect = ConsumableEffect.Stamina, Potency = 20 }));
        ClearAndRestock("Risen Acolyte", inv =>
            inv.AddItem(new Consumable { Name = "Healing Potion", Description = "A ruby flask that warms on the way down. Restores 25 HP.", Value = 30, Weight = 1, Effect = ConsumableEffect.Heal, Potency = 25 }));
        ClearAndRestock("Crypt Hound", inv =>
            inv.AddItem(new Consumable { Name = "Wolf Pelt", Description = "Thick and surprisingly clean. Worth something to a tanner.", Value = 40, Weight = 3, Effect = ConsumableEffect.None }));
        ClearAndRestock("Erasmus the Unbound", inv =>
        {
            inv.AddItem(new Consumable { Name = "Byte Crystal",       Description = "Dense with structured magic. Restores 30 BytePool.", Value = 90, Weight = 1, Effect = ConsumableEffect.BytePool, Potency = 30 });
            inv.AddItem(new Consumable { Name = "Erasmus Manifesto",  Description = "Dense notes in a cramped hand. The last line: 'They think sealing me here ends the matter. Fools. I only need to wait.'", Value = 150, Weight = 1, Effect = ConsumableEffect.None });
        });

        // --- 3. Restore door states ---
        var vaultGate = _dbContext.Doors.ToList().FirstOrDefault(d => d.Name == "Vault Gate");
        if (vaultGate is not null) vaultGate.IsLocked = true;

        var chapelGate = _dbContext.Doors.ToList().FirstOrDefault(d => d.Name == "Chapel Gate");
        if (chapelGate is not null) chapelGate.TrapDisarmed = false;

        // --- 4. Restore chest states and contents ---
        var allChests = _dbContext.Containers.OfType<Chest>().ToList();

        var campCrate = allChests.FirstOrDefault(c => c.Name == "Camp Crate");
        if (campCrate is not null)
        {
            campCrate.IsLocked = true;
            if (!campCrate.ItemsCollection.Any(i => i.KeyId == "vault_key"))
                campCrate.AddItem(new Consumable { Name = "Vault Key", Description = "Heavy iron. Runes etched along the bow — old magic, half-faded.", Value = 200, Weight = 1, KeyId = "vault_key", Effect = ConsumableEffect.None });
        }

        var cellarCask = allChests.FirstOrDefault(c => c.Name == "Cellar Cask");
        if (cellarCask is not null && !cellarCask.ItemsCollection.Any(i => i.Name == "Healing Potion"))
            cellarCask.AddItem(new Consumable { Name = "Healing Potion", Description = "A ruby flask that warms on the way down. Restores 25 HP.", Value = 30, Weight = 1, Effect = ConsumableEffect.Heal, Potency = 25 });

        var altarChest = allChests.FirstOrDefault(c => c.Name == "Altar Chest");
        if (altarChest is not null)
        {
            altarChest.TrapDisarmed = false;
            if (!altarChest.ItemsCollection.Any(i => i.Name == "Bit Crystal"))
                altarChest.AddItem(new Consumable { Name = "Bit Crystal", Description = "A faceted gem humming with raw Bit energy. Restores 30 BitPool.", Value = 60, Weight = 1, Effect = ConsumableEffect.BitPool, Potency = 30 });
        }

        var reliquary = allChests.FirstOrDefault(c => c.Name == "The Sealed Reliquary");
        if (reliquary is not null)
        {
            reliquary.IsLocked     = true;
            reliquary.TrapDisarmed = false;
            if (!reliquary.ItemsCollection.Any(i => i.Name == "Runeblade"))
                reliquary.AddItem(new Weapon    { Name = "Runeblade", Description = "Elven steel etched with dormant runes. Hums faintly in the hand.", Value = 500, Weight = 5, AttackPower = 18, WeaponType = WeaponType.Sword, Durability = 50 });
            if (!reliquary.ItemsCollection.Any(i => i.Name == "Greater Healing Potion"))
                reliquary.AddItem(new Consumable { Name = "Greater Healing Potion", Description = "Thick and golden — restores 60 HP.", Value = 80, Weight = 1, Effect = ConsumableEffect.Heal, Potency = 60 });
        }

        // --- 5. Reset Elara's inventory and equipment to starting kit ---
        var elara = _dbContext.Characters.OfType<Player>().ToList().FirstOrDefault(p => p.Name == "Elara the Bold");
        if (elara is not null)
        {
            // Clear inventory
            foreach (var item in elara.Inventory?.ItemsCollection.ToList() ?? new())
                _dbContext.RemoveEntity(item);

            // Unequip and clear equipment container
            foreach (var slot in elara.EquipmentSlots) { slot.EquippedItemId = null; slot.EquippedItem = null; }
            foreach (var item in elara.Equipment?.ItemsCollection.ToList() ?? new())
                _dbContext.RemoveEntity(item);

            // Starting gear: Iron Sword equipped to MainHand, Leather Vest equipped to Chest
            var sword = new Weapon    { Name = "Iron Sword",   Description = "A reliable blade. Nothing fancy.", Value = 50, Weight = 3, AttackPower = 6, WeaponType = WeaponType.Sword, Durability = 30 };
            var vest  = new Armor     { Name = "Leather Vest", Description = "Worn but protective. Better than nothing.", Value = 40, Weight = 5, DefenseRating = 3, WeightClass = ArmorWeight.Light, Slot = BodySlot.Chest };
            var pot   = new Consumable { Name = "Healing Potion", Description = "A ruby flask that warms on the way down. Restores 25 HP.", Value = 30, Weight = 1, Effect = ConsumableEffect.Heal, Potency = 25 };

            if (elara.Equipment is not null)
            {
                elara.Equipment.AddItem(sword);
                elara.Equipment.AddItem(vest);
                var mainHand = elara.EquipmentSlots.FirstOrDefault(s => (s.Slot & SlotType.MainHand) != 0);
                var chestSlot = elara.EquipmentSlots.FirstOrDefault(s => (s.Slot & SlotType.Chest) != 0);
                if (mainHand  is not null) { mainHand.EquippedItem  = sword; }
                if (chestSlot is not null) { chestSlot.EquippedItem = vest; }
            }
            if (elara.Inventory is not null) elara.Inventory.AddItem(pot);

            // Move back to Inn
            var inn = _dbContext.Containers.OfType<Room>().ToList().FirstOrDefault(r => r.Name == "The Wayward Crow Inn");
            if (inn is not null) elara.RoomId = inn.Id;
        }

        // --- 6. Restore Mira's shop stock ---
        var mira = _dbContext.Characters.ToList().FirstOrDefault(c => c.Name == "Mira");
        if (mira?.Inventory is not null)
        {
            foreach (var item in mira.Inventory.ItemsCollection.ToList())
                _dbContext.RemoveEntity(item);
            mira.Inventory.AddItem(new Consumable { Name = "Healing Potion", Description = "A ruby flask that warms on the way down. Restores 25 HP.", Value = 30, Weight = 1, Effect = ConsumableEffect.Heal, Potency = 25 });
            mira.Inventory.AddItem(new Consumable { Name = "Healing Potion", Description = "A ruby flask that warms on the way down. Restores 25 HP.", Value = 30, Weight = 1, Effect = ConsumableEffect.Heal, Potency = 25 });
            mira.Inventory.AddItem(new Consumable { Name = "Stamina Draft",  Description = "Bitter and fizzy. Restores 20 SP.", Value = 25, Weight = 1, Effect = ConsumableEffect.Stamina, Potency = 20 });
            mira.Inventory.AddItem(new Consumable { Name = "Lockpick",       Description = "A thin wire pick. Breaks on a bad roll.", Value = 15, Weight = 0, KeyId = Item.LockpickKeyId, Effect = ConsumableEffect.None });
        }

        // --- 7. Also restore Thornwood floor herbs ---
        var path = _dbContext.Containers.OfType<Room>().ToList().FirstOrDefault(r => r.Name == "Thornwood Path");
        if (path is not null && !path.ItemsCollection.Any(i => i.Name == "Thornwood Herb"))
        {
            path.AddItem(new Consumable { Name = "Thornwood Herb", Description = "A bitter green leaf used in stamina tinctures. Chew for 10 SP.", Value = 5, Weight = 0, Effect = ConsumableEffect.Stamina, Potency = 10 });
            path.AddItem(new Consumable { Name = "Thornwood Herb", Description = "A bitter green leaf used in stamina tinctures. Chew for 10 SP.", Value = 5, Weight = 0, Effect = ConsumableEffect.Stamina, Potency = 10 });
        }

        // --- Reset visited-room tracking ---
        _visitedRooms.Clear();

        _dbContext.SaveChanges();
        Console.WriteLine("\n  World reset complete. Elara starts at the Inn with basic gear.");
    }
}

// -- small local extension to get the un-proxied item TPH type name --
internal static class ItemTypeNameExtensions
{
    public static string TypeNameForItem(this Item item)
    {
        var t = item.GetType();
        // Walk up proxy chain until we land on something inside ConsoleRpgEntities.Models.Items.
        while (t != null && t.Namespace != "ConsoleRpgEntities.Models.Items")
            t = t.BaseType;
        return t?.Name ?? item.GetType().Name;
    }
}
