-- W12_SeedInventoryData.sql
-- Seeds Races, the reference Player (Elara the Bold), her Stats + Resources,
-- an Inventory + Equipment container pair, starter items, and her EquipmentSlot rows.
--
-- All inserts are guarded by NOT EXISTS checks against stable Names so re-running
-- the migration (or sharing the DB with classmates) won't duplicate data.
--
-- Enum values are stored as ints by EF Core:
--   SlotType:   MainHand=0, OffHand=1, Head=2, Chest=3, Legs=4, Feet=5, Hands=6
--   BodySlot:   Head=0, Chest=1, Legs=2, Feet=3, Hands=4
--   WeaponType: Sword=0, Axe=1, Mace=2, Bow=3, Staff=4, Dagger=5, Spear=6
--   ArmorWeight: Light=0, Medium=1, Heavy=2

SET NOCOUNT ON;

-- =============================================================
-- 1. Races — 3 Playable + 7 Monster (AnimalRace intentionally empty for now)
-- =============================================================
INSERT INTO Races (Name, Description, RaceType)
SELECT v.Name, v.Description, v.RaceType
FROM (VALUES
    (N'Human',    N'Adaptable, balanced, found in every city from Lucent to the frontier.',                     N'Playable'),
    (N'Elf',      N'Long-lived, attuned to the old songs. Common among scholars and scouts.',                   N'Playable'),
    (N'Dwarf',    N'Stone-carvers and smiths. Endure where others break.',                                      N'Playable'),
    (N'Goblin',   N'Small, swift, rarely alone. The true threat is the pack, not the goblin.',                  N'Monster'),
    (N'Orc',      N'Brutal warband raiders. Physically powerful; cunning when led well.',                       N'Monster'),
    (N'Troll',    N'Massive, regenerating. A lone troll can rout a squad.',                                     N'Monster'),
    (N'Mimic',    N'Shapeshifting ambush predator. Often disguised as chests or doors.',                        N'Monster'),
    (N'Slime',    N'Amorphous, splits under blunt force. Common in caves and sewers.',                          N'Monster'),
    (N'Chimera',  N'Patchwork beast — claws, wings, and breath weapon. Alpha monster encounter.',               N'Monster'),
    (N'Kobold',   N'Trap-layers and tunnelers. Weak alone, deadly in their own warrens.',                       N'Monster')
) AS v(Name, Description, RaceType)
WHERE NOT EXISTS (SELECT 1 FROM Races r WHERE r.Name = v.Name);

-- =============================================================
-- 2. Elara the Bold — the reference Player
-- =============================================================
DECLARE @HumanRaceId INT = (SELECT TOP 1 Id FROM Races WHERE Name = N'Human');

IF NOT EXISTS (SELECT 1 FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player')
BEGIN
    INSERT INTO Characters (Name, Level, RaceId, RoomId, CharacterType)
    VALUES (N'Elara the Bold', 1, @HumanRaceId, NULL, 'Player');
END;

DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');

-- Stats
IF NOT EXISTS (SELECT 1 FROM Stats WHERE CharacterId = @ElaraId)
BEGIN
    INSERT INTO Stats (CharacterId, Physique, Reflexes, Constitution, Intellect, Intuition, Linguistic, Luck)
    VALUES (@ElaraId, 8, 7, 7, 5, 6, 5, 5);
END;

-- Resources (derived values: Hp = 50 + Con*5 = 85, Sp = 30+Con*3+Ref*2 = 65, Bp = 20+Intu*4 = 44, BytePool = 10+Intel*3 = 25)
IF NOT EXISTS (SELECT 1 FROM Resources WHERE CharacterId = @ElaraId)
BEGIN
    INSERT INTO Resources (CharacterId, Hp, MaxHp, Sp, MaxSp, Bp, MaxBp, BytePool, MaxBytePool)
    VALUES (@ElaraId, 85, 85, 65, 65, 44, 44, 25, 25);
END;

-- =============================================================
-- 3. Inventory and Equipment containers for Elara
-- =============================================================
IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Inventory' AND Inventory_OwnerCharacterId = @ElaraId)
BEGIN
    INSERT INTO Containers (Name, ContainerType, Inventory_OwnerCharacterId, MaxWeight)
    VALUES (N'Elara''s Pack', 'Inventory', @ElaraId, 100);
END;

IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Equipment' AND OwnerCharacterId = @ElaraId)
BEGIN
    INSERT INTO Containers (Name, ContainerType, OwnerCharacterId, MaxWeight)
    VALUES (N'Elara''s Gear', 'Equipment', @ElaraId, NULL);
END;

DECLARE @InvId INT  = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Inventory' AND Inventory_OwnerCharacterId = @ElaraId);
DECLARE @EquipId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Equipment' AND OwnerCharacterId = @ElaraId);

-- =============================================================
-- 4. Starter items for Elara's Inventory
--    2 Weapons, 2 Armor, 2 Consumables, 1 Key Item
-- =============================================================

-- Weapons
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Rusty Sword' AND ItemType = 'Weapon')
BEGIN
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, ContainerId, ItemType, AttackPower, WeaponType, Durability)
    VALUES (N'Rusty Sword', N'Dented but sharp. Elara''s first blade.', 15, 6, 0, @InvId, 'Weapon', 7, 0, 40);
END;

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Oak Bow' AND ItemType = 'Weapon')
BEGIN
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, ContainerId, ItemType, AttackPower, WeaponType, Durability)
    VALUES (N'Oak Bow', N'A serviceable shortbow. Strings when it rains.', 30, 4, 0, @InvId, 'Weapon', 9, 3, 35);
END;

-- Armor
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Leather Helm' AND ItemType = 'Armor')
BEGIN
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, ContainerId, ItemType, DefenseRating, WeightClass, Slot, Durability)
    VALUES (N'Leather Helm', N'Boiled leather cap, padded lining.', 20, 2, 0, @InvId, 'Armor', 3, 0, 0, 30);
END;

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Leather Tunic' AND ItemType = 'Armor')
BEGIN
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, ContainerId, ItemType, DefenseRating, WeightClass, Slot, Durability)
    VALUES (N'Leather Tunic', N'Flexible chest piece, smells faintly of the tannery.', 40, 5, 0, @InvId, 'Armor', 6, 0, 1, 30);
END;

-- Consumables
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Healing Potion' AND ItemType = 'Consumable')
BEGIN
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Healing Potion', N'Red and bubbling. Restores hit points.', 25, 1, 0, @InvId, 'Consumable', N'heal', 25);
END;

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Stamina Draught' AND ItemType = 'Consumable')
BEGIN
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Stamina Draught', N'Bitter, herbal. Restores stamina.', 20, 1, 0, @InvId, 'Consumable', N'stamina', 20);
END;

-- Key Item (treated as a consumable discriminator row but flagged IsKeyItem; in W12 we keep IsKeyItem as bool)
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Old Brass Key' AND IsKeyItem = 1)
BEGIN
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Old Brass Key', N'Tarnished and heavy. Fits a door nobody remembers.', 0, 1, 1, @InvId, 'Consumable', N'keyitem', 0);
END;

-- =============================================================
-- 5. EquipmentSlot rows for Elara's Equipment container
--    One per SlotType enum value, all empty (EquippedItemId = NULL).
-- =============================================================
INSERT INTO EquipmentSlots (CharacterId, Slot, EquippedItemId, EquipmentContainerId)
SELECT @ElaraId, v.SlotInt, NULL, @EquipId
FROM (VALUES (0),(1),(2),(3),(4),(5),(6)) AS v(SlotInt)
WHERE NOT EXISTS (
    SELECT 1 FROM EquipmentSlots
    WHERE CharacterId = @ElaraId AND EquipmentContainerId = @EquipId AND Slot = v.SlotInt
);
