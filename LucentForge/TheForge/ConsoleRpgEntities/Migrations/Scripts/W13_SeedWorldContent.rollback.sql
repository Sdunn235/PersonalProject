-- W13_SeedWorldContent.rollback.sql
-- Removes W13 seeded data in reverse FK-dependency order.

SET NOCOUNT ON;

-- 1. Remove items inside W13 containers
DELETE FROM Items WHERE Name IN (
    N'Lesser Healing Draught',
    N'Rusty Dagger',
    N'Silvered Shortsword',
    N'Leather Bracers',
    N'Ember Wand',
    N'Mithril Chainmail',
    N'Elixir of the Wakeful',
    N'Trapmaker''s Dagger',
    N'Antidote',
    N'Goblin Cleaver',
    N'Dungeon Key',
    N'Gobbo''s Stew',
    N'Iron Lockpick #1',
    N'Iron Lockpick #2'
);

-- 2. Unlink Grubnak from his loot, then drop the chests + loot
DECLARE @GrubnakId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Grubnak' AND CharacterType = 'NPC');
IF @GrubnakId IS NOT NULL
    UPDATE Characters SET LootId = NULL WHERE Id = @GrubnakId;

DELETE FROM Containers WHERE ContainerType = 'Chest' AND Name IN (
    N'Weathered Wooden Chest',
    N'Iron-Banded Chest',
    N'Ornate Rune-Engraved Chest',
    N'Dusty Humming Chest'
);

DELETE FROM Containers WHERE ContainerType = 'MonsterLoot' AND Name = N'Grubnak''s Loot';

-- 3. Remove Grubnak (loot already unlinked)
DELETE FROM Characters WHERE Name = N'Grubnak' AND CharacterType = 'NPC';

-- 4. Remove the Lockpicking CharacterSkill + Skill row
DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');
DECLARE @LockpickingSkillId INT = (SELECT TOP 1 Id FROM Skills WHERE Name = N'Lockpicking');
IF @ElaraId IS NOT NULL AND @LockpickingSkillId IS NOT NULL
    DELETE FROM CharacterSkills WHERE CharacterId = @ElaraId AND SkillId = @LockpickingSkillId;

DELETE FROM Skills WHERE Name = N'Lockpicking';

-- 5. Remove the W13 rooms (Elara stays, just clears the FK in next-up the chain)
UPDATE Characters SET RoomId = NULL
    WHERE RoomId IN (SELECT Id FROM Rooms WHERE Name IN (N'Antechamber', N'Vault'));

DELETE FROM Rooms WHERE Name IN (N'Antechamber', N'Vault');
