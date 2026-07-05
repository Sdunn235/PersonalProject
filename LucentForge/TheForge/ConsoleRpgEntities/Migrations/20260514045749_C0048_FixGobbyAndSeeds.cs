using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class C0048_FixGobbyAndSeeds : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Gobby (formerly Grubnak) was seeded in W13 without Stats, Resources,
            // Inventory, or Equipment. W15_KillMonsterLoot tried to move his loot to
            // an Inventory that didn't exist, so items went NULL/unowned.
            // Give him a full character setup and fresh gear.
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @GobbyId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Gobby' AND CharacterType = 'NPC');
                IF @GobbyId IS NULL GOTO Done;

                -- Stats (scrappy goblin: quick but fragile)
                IF NOT EXISTS (SELECT 1 FROM Stats WHERE CharacterId = @GobbyId)
                    INSERT INTO Stats (CharacterId, Physique, Constitution, Reflexes, Intuition, Intellect, Linguistic, Luck)
                    VALUES (@GobbyId, 4, 3, 6, 5, 4, 3, 4);

                -- Resources
                IF NOT EXISTS (SELECT 1 FROM Resources WHERE CharacterId = @GobbyId)
                    INSERT INTO Resources (CharacterId, Hp, MaxHp, Sp, MaxSp, BitPool, MaxBitPool, BytePool, MaxBytePool)
                    VALUES (@GobbyId, 29, 29, 19, 19, 40, 40, 22, 22);

                -- Inventory
                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Inventory' AND [Inventory_OwnerCharacterId] = @GobbyId)
                    INSERT INTO Containers (Name, ContainerType, [Inventory_OwnerCharacterId], MaxWeight)
                    VALUES (N'Gobby''s Sack', 'Inventory', @GobbyId, 40);

                DECLARE @InvId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Inventory' AND [Inventory_OwnerCharacterId] = @GobbyId);

                -- Equipment
                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Equipment' AND [OwnerCharacterId] = @GobbyId)
                    INSERT INTO Containers (Name, ContainerType, [OwnerCharacterId])
                    VALUES (N'Gobby''s Gear', 'Equipment', @GobbyId);

                DECLARE @EquipId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Equipment' AND [OwnerCharacterId] = @GobbyId);

                -- EquipmentSlots (power-of-2 values from C0044)
                IF @EquipId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM EquipmentSlots WHERE EquipmentContainerId = @EquipId)
                BEGIN
                    INSERT INTO EquipmentSlots (CharacterId, Slot, EquippedItemId, EquipmentContainerId)
                    SELECT @GobbyId, v.SlotInt, NULL, @EquipId
                    FROM (VALUES (1),(2),(4),(8),(16),(32),(64)) AS v(SlotInt)
                    WHERE NOT EXISTS (
                        SELECT 1 FROM EquipmentSlots WHERE CharacterId = @GobbyId AND EquipmentContainerId = @EquipId AND Slot = v.SlotInt
                    );
                END

                -- Fresh Goblin Cleaver in inventory
                IF @InvId IS NOT NULL AND NOT EXISTS (
                    SELECT 1 FROM Items WHERE Name = N'Goblin Cleaver' AND ContainerId = @InvId
                )
                    INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, AttackPower, WeaponType, Effect, Potency)
                    VALUES (N'Goblin Cleaver', N'Crude, top-heavy, very enthusiastic.', 35, 4, NULL, @InvId, 'Weapon', 8, 1, 0, 0);

                -- Two lockpicks (he's a tinkerer)
                IF @InvId IS NOT NULL AND NOT EXISTS (
                    SELECT 1 FROM Items WHERE Name = N'Lockpick' AND ContainerId = @InvId
                )
                BEGIN
                    INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Lockpick', N'A thin wire pick. Breaks on a bad roll.', 5, 0, N'lockpick', @InvId, 'Consumable', 0, 0);
                    INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Lockpick', N'A thin wire pick. Breaks on a bad roll.', 5, 0, N'lockpick', @InvId, 'Consumable', 0, 0);
                END

                Done:;
            ");

            // Seed Lockpicking skill and link Elara to it (proficiency 2).
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                -- PrimaryAttribute=1=Reflexes, SecondaryAttribute=6=Luck
                IF NOT EXISTS (SELECT 1 FROM Skills WHERE Name = N'Lockpicking')
                    INSERT INTO Skills (Name, Description, PrimaryAttribute, SecondaryAttribute)
                    VALUES (N'Lockpicking', N'Open locks without a key. Reflexes help.', 1, 6);

                DECLARE @LockpickSkillId INT = (SELECT TOP 1 Id FROM Skills WHERE Name = N'Lockpicking');
                DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');

                IF @ElaraId IS NOT NULL AND @LockpickSkillId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM CharacterSkills WHERE CharacterId = @ElaraId AND SkillId = @LockpickSkillId)
                    INSERT INTO CharacterSkills (CharacterId, SkillId, Proficiency)
                    VALUES (@ElaraId, @LockpickSkillId, 2);
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @GobbyId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Gobby' AND CharacterType = 'NPC');
                IF @GobbyId IS NULL GOTO Done;

                DELETE Items FROM Items
                JOIN Containers Inv ON Items.ContainerId = Inv.Id
                WHERE Inv.[Inventory_OwnerCharacterId] = @GobbyId;

                DELETE FROM EquipmentSlots WHERE CharacterId = @GobbyId;
                DELETE FROM Containers WHERE [Inventory_OwnerCharacterId] = @GobbyId OR [OwnerCharacterId] = @GobbyId;
                DELETE FROM Stats WHERE CharacterId = @GobbyId;
                DELETE FROM Resources WHERE CharacterId = @GobbyId;

                Done:;
            ");

            migrationBuilder.Sql(@"
                DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');
                DECLARE @LockpickSkillId INT = (SELECT TOP 1 Id FROM Skills WHERE Name = N'Lockpicking');
                IF @ElaraId IS NOT NULL AND @LockpickSkillId IS NOT NULL
                    DELETE FROM CharacterSkills WHERE CharacterId = @ElaraId AND SkillId = @LockpickSkillId;
                DELETE FROM Skills WHERE Name = N'Lockpicking';
            ");
        }
    }
}
