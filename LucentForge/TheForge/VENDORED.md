# TheForge — Vendored Read-Only Blueprint

**Status: READ ONLY.** Do not modify anything in this directory. It is vendored source
material, same rules as `ReferenceFilesAndCode/` — read, reference, deconstruct, and copy
patterns from it freely; never edit it. (The `README.md` beside this file is the original
graded class document — preserved as-is, it contains the W15 implementation notes and
Design Deviations material.)

## Provenance

Snapshot of the WCTC .NET Frameworks capstone at its final graded commit:

- Original repo: `WCTC-Net-Database/w1-file-i-o-Sdunn235` (GitHub Classroom)
- Vendored at tip: `de5bd22` — **C0057: Finalize CONTRIBUTIONS.md**
- Full C0001–C0057 history archived at: `Sdunn235/TheForge` (private mirror)
- Vendored into LucentForge: 2026-07-05 (Stage 2 planning closeout)

The nested `.git` and `bin/obj/.vs` build artifacts were stripped; this is source only.
It will not build or run from here without a restore — that's intentional. It exists to
be read.

## Role in the Combine Arc

TheForge is the **structural blueprint** for Stages 2–5 of the TheForge → LucentForge
Combine Arc: TPH item/container hierarchies, EquipmentSlot with `[Flags]` slot types,
character item verbs (PickUp/Drop/Equip/Unequip/UseItem/TryUnlock/DisarmTrap),
weight encumbrance, KeyId/lockpick polymorphism.

**Terminology rule (standing, Shawn 2026-07-05):** TheForge is NOT fully aligned to the
LucentForge bible's terminology and mechanics (e.g., BitPool/BytePool vs Bits/Bytes).
The bible is the naming and semantics authority. Every feature imported from here must
pass a reconciliation check against `docs/bible/lucentforge_terminology_map_v_1.md`
before implementation.

## Key reference paths

| Path | What's there |
|---|---|
| `ConsoleRpgEntities/Models/Items/` | Item TPH: Item → DurableItem → Weapon/Armor/Shield; Consumable; KeyId semantics |
| `ConsoleRpgEntities/Models/Containers/` | Container TPH: Inventory/Equipment/Chest/Room/Bookshelf; ILockable |
| `ConsoleRpgEntities/Models/EquipmentSlot.cs` | Slot model with `[Flags]` SlotType |
| `ConsoleRpgEntities/Models/Character.cs` | Equip/Unequip/PickSlotFor/UseItem/TryUnlock/DisarmTrap/CanCarry |
| `ConsoleRpgEntities/Models/Enums/` | SlotType, BodySlot, WeaponType, ArmorWeight, ConsumableEffect, TrapType |
| `ConsoleRpgEntities/Migrations/Scripts/` | SQL seed scripts (W12 starter kit, W13 chest loot) |
