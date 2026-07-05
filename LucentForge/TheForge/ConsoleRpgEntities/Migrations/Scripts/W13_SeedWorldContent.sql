-- W13_SeedWorldContent.sql
-- Seeds the W13 chest/loot world content:
--   * Two rooms (Antechamber, Vault) so chests have somewhere to live
--   * Four chests with varied lock/trap/pick state
--   * Grubnak the Goblin (NPC) with a MonsterLoot container
--   * Items inside both kinds of containers
--   * The "Lockpicking" Skill row + Elara's CharacterSkill proficiency
--     (LucentForge integration: Player.TryUnlock uses this)
--
-- Idempotent — every insert is guarded by NOT EXISTS keyed on stable Names.
--
-- Enum values stored as ints by EF Core:
--   CoreAttribute: Physique=0, Reflexes=1, Constitution=2, Intellect=3,
--                  Intuition=4, Linguistic=5, Luck=6
--   WeaponType:    Sword=0, Axe=1, Mace=2, Bow=3, Staff=4, Dagger=5, Spear=6
--   BodySlot:      Head=0, Chest=1, Legs=2, Feet=3, Hands=4
--   ArmorWeight:   Light=0, Medium=1, Heavy=2

SET NOCOUNT ON;

-- =============================================================
-- 1. Rooms
-- =============================================================
IF NOT EXISTS (SELECT 1 FROM Rooms WHERE Name = N'Antechamber')
    INSERT INTO Rooms (Name, Description) VALUES
        (N'Antechamber', N'A dim, dust-coated entry hall. Footprints suggest recent passage.');

IF NOT EXISTS (SELECT 1 FROM Rooms WHERE Name = N'Vault')
    INSERT INTO Rooms (Name, Description) VALUES
        (N'Vault', N'Cold stone walls. The air smells faintly of old iron and ozone.');

DECLARE @RoomAntechamberId INT = (SELECT TOP 1 Id FROM Rooms WHERE Name = N'Antechamber');
DECLARE @RoomVaultId       INT = (SELECT TOP 1 Id FROM Rooms WHERE Name = N'Vault');

-- Place Elara in the Antechamber if she has no room yet.
DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');
IF @ElaraId IS NOT NULL
    UPDATE Characters SET RoomId = @RoomAntechamberId WHERE Id = @ElaraId AND RoomId IS NULL;

-- =============================================================
-- 2. Lockpicking skill (LucentForge integration anchor)
-- =============================================================
IF NOT EXISTS (SELECT 1 FROM Skills WHERE Name = N'Lockpicking')
    INSERT INTO Skills (Name, Description, PrimaryAttribute, SecondaryAttribute) VALUES
        (N'Lockpicking', N'Manipulating tumblers and wards with picks and patience.', 1, NULL); -- Reflexes=1

DECLARE @LockpickingSkillId INT = (SELECT TOP 1 Id FROM Skills WHERE Name = N'Lockpicking');

-- Elara starts with a modest Lockpicking proficiency (LF integration demo).
IF @ElaraId IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM CharacterSkills WHERE CharacterId = @ElaraId AND SkillId = @LockpickingSkillId
)
    INSERT INTO CharacterSkills (CharacterId, SkillId, Proficiency) VALUES (@ElaraId, @LockpickingSkillId, 3);

-- =============================================================
-- 3. Chests — Container TPH discriminator 'Chest'
-- =============================================================
-- Containers schema relevant columns:
--   Name, ContainerType, Description, IsLocked, IsTrapped, IsPickable,
--   RequiredKeyId, TrapDamage, TrapDisarmed, UnlockDC, RoomId, MaxWeight,
--   OwnerCharacterId, Inventory_OwnerCharacterId, IsLooted

IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Chest' AND Name = N'Weathered Wooden Chest')
    INSERT INTO Containers (Name, ContainerType, Description, IsLocked, IsTrapped, IsPickable, RequiredKeyId, TrapDamage, TrapDisarmed, UnlockDC, RoomId)
    VALUES (N'Weathered Wooden Chest', 'Chest', N'Splintered planks bound with rusted bands.', 0, 0, 1, NULL, 0, 0, 0, @RoomAntechamberId);

IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Chest' AND Name = N'Iron-Banded Chest')
    INSERT INTO Containers (Name, ContainerType, Description, IsLocked, IsTrapped, IsPickable, RequiredKeyId, TrapDamage, TrapDisarmed, UnlockDC, RoomId)
    VALUES (N'Iron-Banded Chest', 'Chest', N'Heavy oak with iron straps. The lock is an old pin tumbler.', 1, 0, 1, NULL, 0, 0, 12, @RoomAntechamberId);

IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Chest' AND Name = N'Ornate Rune-Engraved Chest')
    INSERT INTO Containers (Name, ContainerType, Description, IsLocked, IsTrapped, IsPickable, RequiredKeyId, TrapDamage, TrapDisarmed, UnlockDC, RoomId)
    VALUES (N'Ornate Rune-Engraved Chest', 'Chest', N'Silver runes catch lantern-light. Only the right key turns these wards.', 1, 0, 0, N'dungeon-main', 0, 0, 99, @RoomVaultId);

IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Chest' AND Name = N'Dusty Humming Chest')
    INSERT INTO Containers (Name, ContainerType, Description, IsLocked, IsTrapped, IsPickable, RequiredKeyId, TrapDamage, TrapDisarmed, UnlockDC, RoomId)
    VALUES (N'Dusty Humming Chest', 'Chest', N'A faint hum from inside. The lid trembles.', 0, 1, 1, NULL, 8, 0, 0, @RoomVaultId);

DECLARE @ChestWoodId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Chest' AND Name = N'Weathered Wooden Chest');
DECLARE @ChestIronId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Chest' AND Name = N'Iron-Banded Chest');
DECLARE @ChestOrnateId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Chest' AND Name = N'Ornate Rune-Engraved Chest');
DECLARE @ChestHummingId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Chest' AND Name = N'Dusty Humming Chest');

-- =============================================================
-- 4. Chest contents
-- =============================================================
-- Wooden: minor potion + rusty dagger
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Lesser Healing Draught')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Lesser Healing Draught', N'A weak red liquid. Better than nothing.', 10, 1, 0, NULL, @ChestWoodId, 'Consumable', N'heal', 12);

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Rusty Dagger')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, AttackPower, WeaponType, Durability)
    VALUES (N'Rusty Dagger', N'Short, pitted, but balanced.', 8, 2, 0, NULL, @ChestWoodId, 'Weapon', 4, 5, 20);

-- Iron-Banded: silvered shortsword + leather bracers (Hands armor)
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Silvered Shortsword')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, AttackPower, WeaponType, Durability)
    VALUES (N'Silvered Shortsword', N'Polished blade, faintly etched.', 65, 4, 0, NULL, @ChestIronId, 'Weapon', 11, 0, 50);

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Leather Bracers')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, DefenseRating, WeightClass, Slot, Durability)
    VALUES (N'Leather Bracers', N'Wraps for the forearms.', 25, 1, 0, NULL, @ChestIronId, 'Armor', 4, 0, 4, 30); -- BodySlot.Hands=4

-- Ornate Rune-Engraved: ember wand + mithril chainmail + elixir
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Ember Wand')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, AttackPower, WeaponType, Durability)
    VALUES (N'Ember Wand', N'A polished hawthorn wand humming with heat.', 180, 1, 0, NULL, @ChestOrnateId, 'Weapon', 14, 4, 60); -- Staff=4

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Mithril Chainmail')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, DefenseRating, WeightClass, Slot, Durability)
    VALUES (N'Mithril Chainmail', N'Light yet impossibly tough. Worth a small fortune.', 500, 8, 0, NULL, @ChestOrnateId, 'Armor', 14, 1, 1, 80); -- Medium, Chest

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Elixir of the Wakeful')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Elixir of the Wakeful', N'Restores byte-pool. Tastes of static.', 90, 1, 0, NULL, @ChestOrnateId, 'Consumable', N'bytepool', 15);

-- Dusty Humming (trapped): trapmaker's dagger + antidote
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Trapmaker''s Dagger')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, AttackPower, WeaponType, Durability)
    VALUES (N'Trapmaker''s Dagger', N'A precision blade for tinkering with snares.', 120, 1, 0, NULL, @ChestHummingId, 'Weapon', 6, 5, 40);

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Antidote')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Antidote', N'Bitter green liquid. Restores a small amount of health.', 30, 1, 0, NULL, @ChestHummingId, 'Consumable', N'heal', 18);

-- =============================================================
-- 5. Grubnak the Goblin + his MonsterLoot
-- =============================================================
DECLARE @GoblinRaceId INT = (SELECT TOP 1 Id FROM Races WHERE Name = N'Goblin');

IF @GoblinRaceId IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM Characters WHERE Name = N'Grubnak' AND CharacterType = 'NPC'
)
    INSERT INTO Characters (Name, Level, RaceId, RoomId, CharacterType)
    VALUES (N'Grubnak', 2, @GoblinRaceId, @RoomVaultId, 'NPC');

DECLARE @GrubnakId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Grubnak' AND CharacterType = 'NPC');

-- Grubnak's MonsterLoot container (treated as already-defeated per W13 cosmetic-loot decision)
IF @GrubnakId IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM Containers WHERE ContainerType = 'MonsterLoot' AND Name = N'Grubnak''s Loot'
)
    INSERT INTO Containers (Name, ContainerType, Description, IsLooted)
    VALUES (N'Grubnak''s Loot', 'MonsterLoot', N'A loosely bound sack tied to the goblin''s belt.', 0);

DECLARE @GrubnakLootId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'MonsterLoot' AND Name = N'Grubnak''s Loot');

-- Wire NPC → MonsterLoot if not already linked.
IF @GrubnakId IS NOT NULL AND @GrubnakLootId IS NOT NULL
    UPDATE Characters SET LootId = @GrubnakLootId WHERE Id = @GrubnakId AND LootId IS NULL;

-- Grubnak's drops: cleaver, dungeon key, gobbo's stew
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Goblin Cleaver')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, AttackPower, WeaponType, Durability)
    VALUES (N'Goblin Cleaver', N'Crude, top-heavy, very enthusiastic.', 35, 4, 0, NULL, @GrubnakLootId, 'Weapon', 8, 1, 25); -- Axe=1

-- Specific key (KeyId = 'dungeon-main') — opens the Ornate Rune-Engraved Chest.
IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Dungeon Key')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Dungeon Key', N'A heavy iron key with deep notches and a faint rune.', 0, 1, 1, N'dungeon-main', @GrubnakLootId, 'Consumable', N'keyitem', 0);

IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Gobbo''s Stew')
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Gobbo''s Stew', N'Brown, lumpy, smells of mushrooms. Restores stamina.', 12, 1, 0, NULL, @GrubnakLootId, 'Consumable', N'stamina', 14);

-- =============================================================
-- 6. Lockpick — give Elara two so she can practice on Chest 4 and disarm a trap.
-- =============================================================
DECLARE @ElaraInvId INT = (SELECT TOP 1 Id FROM Containers
                           WHERE ContainerType = 'Inventory' AND Inventory_OwnerCharacterId = @ElaraId);

IF @ElaraInvId IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM Items WHERE Name = N'Iron Lockpick #1'
)
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Iron Lockpick #1', N'A bent steel pick. Single-use; breaks if the lock fights back.', 5, 1, 1, NULL, @ElaraInvId, 'Consumable', N'lockpick', 0);

IF @ElaraInvId IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM Items WHERE Name = N'Iron Lockpick #2'
)
    INSERT INTO Items (Name, Description, Value, Weight, IsKeyItem, KeyId, ContainerId, ItemType, Effect, Potency)
    VALUES (N'Iron Lockpick #2', N'Spare pick. Slightly thicker.', 5, 1, 1, NULL, @ElaraInvId, 'Consumable', N'lockpick', 0);
