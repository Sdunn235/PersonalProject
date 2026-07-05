using ConsoleRpgEntities.Models.Abilities;
using ConsoleRpgEntities.Models.Containers;
using ConsoleRpgEntities.Models.Enums;
using ConsoleRpgEntities.Models.Items;
using ConsoleRpgEntities.Models.Magic;
using ConsoleRpgEntities.Models.Races;
using ConsoleRpgEntities.Models.Skills;

namespace ConsoleRpgEntities.Models;

public abstract class Character
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public int Level { get; set; }

    public int? RoomId { get; set; }
    public virtual Room? Room { get; set; }

    public int? RaceId { get; set; }
    public virtual Race? Race { get; set; }

    public virtual Stats? Stats { get; set; }
    public virtual Resources? Resources { get; set; }

    // W12: each character owns at most one Inventory and one Equipment container.
    // Nullable — a character can exist before getting a backpack or equipped gear.
    public virtual Inventory? Inventory { get; set; }
    public virtual Equipment? Equipment { get; set; }

    public virtual ICollection<EquipmentSlot> EquipmentSlots { get; set; } = new List<EquipmentSlot>();

    public virtual ICollection<Ability> Abilities { get; set; } = new List<Ability>();
    public virtual ICollection<Magic.Magic> Magics { get; set; } = new List<Magic.Magic>();
    public virtual ICollection<CharacterSkill> CharacterSkills { get; set; } = new List<CharacterSkill>();

    // --- Derivation helpers (bible §5: resources are derived from stats) ---

    public int DeriveMaxHp() => 50 + (Stats?.Constitution ?? 0) * 5;
    public int DeriveMaxSp() => 30 + (Stats?.Constitution ?? 0) * 3 + (Stats?.Reflexes ?? 0) * 2;
    public int DeriveMaxBitPool() => 20 + (Stats?.Intuition ?? 0) * 4;
    public int DeriveMaxBytePool() => 10 + (Stats?.Intellect ?? 0) * 3;

    // --- Combat helpers ---

    public int GetTotalAttack()
    {
        int baseAttack = Stats?.Physique ?? 0;
        int weaponBonus = EquipmentSlots
            .Where(s => s.EquippedItem is Weapon)
            .Sum(s => ((Weapon)s.EquippedItem!).AttackPower);
        return baseAttack + weaponBonus;
    }

    public int GetTotalDefense()
    {
        int baseDef = Stats?.Constitution ?? 0;
        int armorBonus = EquipmentSlots
            .Where(s => s.EquippedItem is Armor)
            .Sum(s => ((Armor)s.EquippedItem!).DefenseRating);
        return baseDef + armorBonus;
    }

    // W12: un-proxy a lazy-loaded entity so GetType().Name returns "Player" not "PlayerProxy".
    public string TypeName => GetType().BaseType?.Name ?? GetType().Name;

    // -------------------------------------------------------------------------
    // Inventory / Equipment / Chest verbs (W12 + W13).
    // Promoted from Player to Character in Phase 1.5: NPCs and Animals get the
    // same capabilities. All operations mutate state in memory; caller is
    // responsible for SaveChanges().
    // -------------------------------------------------------------------------

    // Single shared d20 source for skill rolls (lockpicking, etc.).
    private static readonly Random _rng = new();

    /// <summary>
    /// Total weight a character is currently carrying — the sum of items in
    /// their Inventory bag PLUS items in their Equipment slots. Worn gear
    /// counts against carrying capacity by every standard RPG model.
    ///
    /// <para>Pre-fix (W12/W13): only Inventory was counted, so a character
    /// could equip 50-lb plate + 30-lb greatsword and their bag still
    /// reported empty.</para>
    /// </summary>
    public int TotalCarriedWeight()
    {
        int inv = Inventory?.ItemsCollection.Sum(i => i.Weight) ?? 0;
        int eq = Equipment?.ItemsCollection.Sum(i => i.Weight) ?? 0;
        return inv + eq;
    }

    /// <summary>
    /// True if this character can carry an additional <paramref name="additionalWeight"/>
    /// pounds without exceeding their carrying capacity (currently stored
    /// as <see cref="Inventory.MaxWeight"/> — semantically the character's
    /// total carry cap, not just the bag's volume).
    ///
    /// <para>Use this for any "can I take this item?" check; it accounts
    /// for both worn and bagged weight. Replaces the bag-only
    /// <c>Inventory.CanFit</c>.</para>
    /// </summary>
    public bool CanCarry(int additionalWeight)
    {
        if (Inventory is null) return false;
        return TotalCarriedWeight() + additionalWeight <= Inventory.MaxWeight;
    }

    public bool PickUp(Item item)
    {
        if (Inventory is null) return false;
        if (!CanCarry(item.Weight)) return false;

        Inventory.AddItem(item);
        return true;
    }

    public void Drop(Item item)
    {
        if (Inventory is not null && Inventory.ItemsCollection.Contains(item))
            Inventory.RemoveItem(item);
        else
            item.ContainerId = null;
    }

    public bool Equip(Item item)
    {
        if (Equipment is null) return false;

        var slot = PickSlotFor(item);
        if (slot is null) return false;

        Inventory?.ItemsCollection.Remove(item);
        Equipment.AddItem(item);
        slot.EquippedItemId = item.Id;
        slot.EquippedItem = item;
        return true;
    }

    public void Unequip(Item item)
    {
        if (Equipment is null) return;

        var slot = Equipment.Slots.FirstOrDefault(s => s.EquippedItemId == item.Id);
        if (slot is not null)
        {
            slot.EquippedItemId = null;
            slot.EquippedItem = null;
        }

        Equipment.ItemsCollection.Remove(item);
        Inventory?.AddItem(item);
    }

    public void UseItem(Consumable item)
    {
        if (Resources is null) return;

        // W14 Phase B: switch on the typed Effect enum (was: switch on lowered
        // string). The 'applied' flag fixes a W12/W13 bug where unrecognized
        // effect strings ("keyitem"/"lockpick"/typos) silently consumed the
        // item without doing anything. With the enum, only real effects can
        // be selected at compile time AND the consume step now requires a
        // successful application.
        var applied = false;
        switch (item.Effect)
        {
            case ConsumableEffect.Heal:
                Resources.Hp = Math.Min(Resources.MaxHp, Resources.Hp + item.Potency);
                applied = true;
                break;
            case ConsumableEffect.Stamina:
                Resources.Sp = Math.Min(Resources.MaxSp, Resources.Sp + item.Potency);
                applied = true;
                break;
            case ConsumableEffect.BitPool:
                Resources.BitPool = Math.Min(Resources.MaxBitPool, Resources.BitPool + item.Potency);
                applied = true;
                break;
            case ConsumableEffect.BytePool:
                Resources.BytePool = Math.Min(Resources.MaxBytePool, Resources.BytePool + item.Potency);
                applied = true;
                break;
            case ConsumableEffect.None:
                // Non-effect-bearing rows (KeyItems, lockpicks pre-Phase-C).
                // Don't consume — the item is a physical object, not a potion.
                break;
        }

        if (applied)
            Inventory?.RemoveItem(item);
    }

    private EquipmentSlot? PickSlotFor(Item item)
    {
        if (Equipment is null) return null;

        // Shield first — it's a subclass of Armor, so the Armor case below would
        // otherwise route it to BodySlot.Hands (wrong: shields use a hand slot).
        // W15 Phase H: bitwise & instead of == because SlotType is now [Flags].
        if (item is Shield)
        {
            return Equipment.Slots.FirstOrDefault(s =>
                       (s.Slot & Enums.SlotType.OffHand) != 0 && s.EquippedItemId is null)
                ?? Equipment.Slots.FirstOrDefault(s =>
                       (s.Slot & Enums.SlotType.MainHand) != 0 && s.EquippedItemId is null);
        }

        return item switch
        {
            Weapon => Equipment.Slots.FirstOrDefault(s =>
                (s.Slot & Enums.SlotType.MainHand) != 0 && s.EquippedItemId is null),
            Armor armor => Equipment.Slots.FirstOrDefault(s =>
                (s.Slot & BodySlotToSlotType(armor.Slot)) != 0 && s.EquippedItemId is null),
            _ => null
        };
    }

    private static Enums.SlotType BodySlotToSlotType(Enums.BodySlot body) => body switch
    {
        Enums.BodySlot.Head => Enums.SlotType.Head,
        Enums.BodySlot.Chest => Enums.SlotType.Chest,
        Enums.BodySlot.Legs => Enums.SlotType.Legs,
        Enums.BodySlot.Feet => Enums.SlotType.Feet,
        Enums.BodySlot.Hands => Enums.SlotType.Hands,
        _ => Enums.SlotType.Chest
    };

    // -- W13 chest & loot verbs --

    public OpenResult OpenChest(Chest chest)
    {
        if (chest is null) throw new ArgumentNullException(nameof(chest));

        if (!chest.IsLocked && (chest.IsTrapped && !chest.TrapDisarmed))
        {
            chest.TrapDisarmed = true;
            if (Resources is not null)
                Resources.Hp = Math.Max(0, Resources.Hp - chest.TrapDamage);
            return OpenResult.Trapped;
        }

        if (chest.IsLocked)
            return OpenResult.Locked;

        return OpenResult.Opened;
    }

    // W14 Phase C.4 — LSP refactor: target is ILockable, not Chest. Door
    // implements the same interface (Phase C.2), so the identical algorithm
    // unlocks chests AND doors AND any future ILockable with zero
    // duplication. The method body uses only ILockable members.
    public bool TryUnlock(ILockable target, Item key)
    {
        if (target is null) throw new ArgumentNullException(nameof(target));
        if (key is null) throw new ArgumentNullException(nameof(key));
        if (key.KeyId is null) return false;          // not a key at all
        if (!target.IsLocked) return true;

        if (key.KeyId == Item.LockpickKeyId)
        {
            // Lockpick branch.
            // Can't even try (needs a real key, or lock is unpickable) — tool not consumed.
            if (!target.IsPickable || target.RequiredKeyId is not null)
                return false;

            int reflexes = Stats?.Reflexes ?? 0;
            int proficiency = CharacterSkills
                .FirstOrDefault(cs => cs.Skill?.Name == "Lockpicking")?.Proficiency ?? 0;
            int roll = _rng.Next(1, 21); // d20
            int total = roll + reflexes + proficiency;

            if (total >= target.UnlockDC)
            {
                target.IsLocked = false;
                return true; // Success — lockpick survives
            }
            Inventory?.RemoveItem(key); // Failure — lockpick broke
            return false;
        }

        // Specific key branch.
        if (target.RequiredKeyId is null) return false;
        if (string.Equals(key.KeyId, target.RequiredKeyId, StringComparison.Ordinal))
        {
            target.IsLocked = false;
            return true;
        }
        return false;
    }

    // W14 Phase C.4 — same LSP shift. Disarm works on any ILockable; the
    // host (Chest, Door, …) is irrelevant to the algorithm.
    public bool DisarmTrap(ILockable target, Item lockpick)
    {
        if (target is null) throw new ArgumentNullException(nameof(target));
        if (lockpick is null) throw new ArgumentNullException(nameof(lockpick));
        if (lockpick.KeyId != Item.LockpickKeyId) return false;
        if (!target.IsTrapped || target.TrapDisarmed) return false;

        target.TrapDisarmed = true;
        Inventory?.RemoveItem(lockpick);
        return true;
    }

    // W14 Phase C.4 / stretch — deterministic secret-door inspection.
    // Looks at the supplied door collection, picks doors connected to this
    // character's current room that are still IsSecret AND !IsDiscovered,
    // marks them discovered, and returns the list of newly-revealed doors.
    // Caller is responsible for SaveChanges() on the context.
    public IReadOnlyList<Door> InspectForSecretDoors(IEnumerable<Door> doors)
    {
        if (doors is null) throw new ArgumentNullException(nameof(doors));
        if (Room is null) return Array.Empty<Door>();

        var discovered = doors
            .Where(d => d.IsSecret && !d.IsDiscovered)
            .Where(d => d.RoomAId == Room.Id || d.RoomBId == Room.Id)
            .ToList();

        foreach (var d in discovered) d.IsDiscovered = true;
        return discovered;
    }

    /// <summary>
    /// Move a single item from any container into this character's inventory.
    /// Returns true if the item was taken; false if the inventory can't fit
    /// the item, the source doesn't contain it, or this character has no
    /// inventory.
    ///
    /// <para>This is the generic primitive for *all* "I'm taking that
    /// thing" actions — looting chests, looting bodies, picking items off
    /// the floor of a room (W14), or any future container type. The UX
    /// (interactive picker, batch "take all," etc.) is built on top of
    /// this in <c>GameEngine</c>; the model just knows how to move one
    /// item at a time and refuse if the move would violate a constraint.</para>
    /// </summary>
    public bool TakeItemFrom(Container source, Item item)
    {
        if (source is null) throw new ArgumentNullException(nameof(source));
        if (item is null) throw new ArgumentNullException(nameof(item));
        if (Inventory is null) return false;
        if (!source.ItemsCollection.Contains(item)) return false;
        if (!CanCarry(item.Weight)) return false;

        source.RemoveItem(item);
        Inventory.AddItem(item);
        return true;
    }
}
