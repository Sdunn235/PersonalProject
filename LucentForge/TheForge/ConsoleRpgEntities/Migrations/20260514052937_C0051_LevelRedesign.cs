using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class C0051_LevelRedesign : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // ── Step 1: Tear down old seed rooms and their dependents ──────────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                UPDATE Characters SET RoomId = NULL
                WHERE RoomId IN (
                    SELECT Id FROM Containers
                    WHERE ContainerType = 'Room'
                    AND Name IN (N'Forest Edge', N'Ancient Library', N'Antechamber', N'Hidden Alcove', N'Vault')
                );

                DECLARE @OldRoomIds TABLE (Id INT);
                INSERT INTO @OldRoomIds
                SELECT Id FROM Containers
                WHERE ContainerType = 'Room'
                AND Name IN (N'Forest Edge', N'Ancient Library', N'Antechamber', N'Hidden Alcove', N'Vault');

                DELETE FROM Items WHERE ContainerId IN (
                    SELECT Id FROM Containers
                    WHERE RoomId IN (SELECT Id FROM @OldRoomIds)
                       OR [Bookshelf_RoomId] IN (SELECT Id FROM @OldRoomIds)
                );
                DELETE FROM Items WHERE ContainerId IN (SELECT Id FROM @OldRoomIds);
                -- Chests reference old rooms via RoomId; Bookshelves via Bookshelf_RoomId (EF TPH disambiguation)
                DELETE FROM Containers WHERE RoomId          IN (SELECT Id FROM @OldRoomIds);
                DELETE FROM Containers WHERE [Bookshelf_RoomId] IN (SELECT Id FROM @OldRoomIds);
                DELETE FROM Doors
                WHERE RoomAId IN (SELECT Id FROM @OldRoomIds)
                   OR RoomBId IN (SELECT Id FROM @OldRoomIds);
                DELETE FROM Containers
                WHERE ContainerType = 'Room'
                AND Name IN (N'Forest Edge', N'Ancient Library', N'Antechamber', N'Hidden Alcove', N'Vault');
            ");

            // ── Step 2: Seed 7 new rooms ───────────────────────────────────────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'The Wayward Crow Inn')
                    INSERT INTO Containers (Name, ContainerType, [Room_Description], GridX, GridY)
                    VALUES (N'The Wayward Crow Inn', 'Room',
                            N'A warm, low-ceilinged inn that smells of pine smoke and stew. The innkeeper, Mira, watches you from behind the bar with sharp, appraising eyes.',
                            1, 0);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'Inn Cellar')
                    INSERT INTO Containers (Name, ContainerType, [Room_Description], GridX, GridY)
                    VALUES (N'Inn Cellar', 'Room',
                            N'Rough stone walls, barrels of ale, and the unmistakable skittering of something alive in the dark.',
                            0, 0);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'Thornwood Path')
                    INSERT INTO Containers (Name, ContainerType, [Room_Description], GridX, GridY)
                    VALUES (N'Thornwood Path', 'Room',
                            N'A narrow dirt track winding through twisted trees. The air is cooler here, and the inn behind you feels very far away.',
                            1, 1);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'Goblin Camp')
                    INSERT INTO Containers (Name, ContainerType, [Room_Description], GridX, GridY)
                    VALUES (N'Goblin Camp', 'Room',
                            N'Crude lean-tos, charred firepits, and the faint reek of goblin. Someone has been here — and recently.',
                            0, 2);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'Ruined Chapel')
                    INSERT INTO Containers (Name, ContainerType, [Room_Description], GridX, GridY)
                    VALUES (N'Ruined Chapel', 'Room',
                            N'A crumbling shrine to a forgotten order. Pews are overturned, the altar defaced. Shelves of old texts line the far wall.',
                            2, 2);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'Crypt Entrance')
                    INSERT INTO Containers (Name, ContainerType, [Room_Description], GridX, GridY)
                    VALUES (N'Crypt Entrance', 'Room',
                            N'Stone steps descend into suffocating dark. The air here has no smell — just cold, empty silence.',
                            2, 3);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'The Sealed Vault')
                    INSERT INTO Containers (Name, ContainerType, [Room_Description], GridX, GridY)
                    VALUES (N'The Sealed Vault', 'Room',
                            N'A vast circular chamber. Ancient runes ring the floor. At the centre, a cracked stone sarcophagus — its lid shattered from within.',
                            2, 4);
            ");

            // ── Step 3: Seed Doors ─────────────────────────────────────────────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                DECLARE @InnId    INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'The Wayward Crow Inn');
                DECLARE @CellarId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Inn Cellar');
                DECLARE @PathId   INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Thornwood Path');
                DECLARE @CampId   INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Goblin Camp');
                DECLARE @ChapelId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Ruined Chapel');
                DECLARE @CryptId  INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Crypt Entrance');
                DECLARE @VaultId  INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'The Sealed Vault');

                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Cellar Hatch')
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId, IsLocked, IsPickable, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, IsSecret, IsDiscovered)
                    VALUES (N'Cellar Hatch', N'A heavy wooden hatch in the floor of the inn.', @InnId, @CellarId, 0, 1, 0, 0, 0, 10, 0, 1);

                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Inn Front Door')
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId, IsLocked, IsPickable, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, IsSecret, IsDiscovered)
                    VALUES (N'Inn Front Door', N'A sturdy oak door. The forest begins just beyond.', @InnId, @PathId, 0, 1, 0, 0, 0, 10, 0, 1);

                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Forest Trail North')
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId, IsLocked, IsPickable, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, IsSecret, IsDiscovered)
                    VALUES (N'Forest Trail North', N'A narrow path leading deeper into the Thornwood.', @PathId, @CampId, 0, 1, 0, 0, 0, 10, 0, 1);

                -- Chapel gate has a Mechanical trap (TrapTypes=1, damage=8)
                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Chapel Gate')
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId, IsLocked, IsPickable, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, IsSecret, IsDiscovered)
                    VALUES (N'Chapel Gate', N'Iron-banded timber gates. A faint smell of rust and old blood.', @PathId, @ChapelId, 0, 1, 1, 8, 0, 10, 0, 1);

                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Crypt Door')
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId, IsLocked, IsPickable, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, IsSecret, IsDiscovered)
                    VALUES (N'Crypt Door', N'A low stone arch with steps descending into darkness.', @ChapelId, @CryptId, 0, 1, 0, 0, 0, 10, 0, 1);

                -- Vault gate: locked, not pickable, requires vault_key
                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Vault Gate')
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId, IsLocked, IsPickable, RequiredKeyId, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, IsSecret, IsDiscovered)
                    VALUES (N'Vault Gate', N'A massive iron door, sealed with ancient runes. The keyhole glows faintly.', @CryptId, @VaultId, 1, 0, N'vault_key', 0, 0, 0, 20, 0, 1);
            ");

            // ── Step 4: Seed Mira (innkeeper / shop NPC) ──────────────────────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                DECLARE @InnId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'The Wayward Crow Inn');

                IF NOT EXISTS (SELECT 1 FROM Characters WHERE Name = N'Mira' AND CharacterType = 'NPC')
                    INSERT INTO Characters (Name, Level, CharacterType, RoomId)
                    VALUES (N'Mira', 5, 'NPC', @InnId);

                DECLARE @MiraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Mira' AND CharacterType = 'NPC');

                IF NOT EXISTS (SELECT 1 FROM Stats WHERE CharacterId = @MiraId)
                    INSERT INTO Stats (CharacterId, Physique, Constitution, Reflexes, Intuition, Intellect, Linguistic, Luck)
                    VALUES (@MiraId, 4, 6, 5, 6, 5, 6, 4);

                IF NOT EXISTS (SELECT 1 FROM Resources WHERE CharacterId = @MiraId)
                    INSERT INTO Resources (CharacterId, Hp, MaxHp, Sp, MaxSp, BitPool, MaxBitPool, BytePool, MaxBytePool)
                    VALUES (@MiraId, 80, 80, 48, 48, 44, 44, 25, 25);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @MiraId)
                    INSERT INTO Containers (Name, ContainerType, [Inventory_OwnerCharacterId], MaxWeight)
                    VALUES (N'Mira''s Stock', 'Inventory', @MiraId, 100);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @MiraId)
                    INSERT INTO Containers (Name, ContainerType, [OwnerCharacterId])
                    VALUES (N'Mira''s Gear', 'Equipment', @MiraId);

                DECLARE @MiraInvId  INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Inventory'  AND [Inventory_OwnerCharacterId] = @MiraId);
                DECLARE @MiraEquipId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId]           = @MiraId);

                IF @MiraEquipId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM EquipmentSlots WHERE EquipmentContainerId = @MiraEquipId)
                    INSERT INTO EquipmentSlots (CharacterId, Slot, EquippedItemId, EquipmentContainerId)
                    SELECT @MiraId, v.SlotInt, NULL, @MiraEquipId
                    FROM (VALUES (1),(2),(4),(8),(16),(32),(64)) AS v(SlotInt);

                -- Shop stock: 2x Healing Potion, 1x Stamina Draft, 1x Lockpick
                IF @MiraInvId IS NOT NULL
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Healing Potion' AND ContainerId=@MiraInvId)
                    BEGIN
                        INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Healing Potion', N'A ruby flask that warms on the way down. Restores 25 HP.', 30, 1, @MiraInvId, 'Consumable', 1, 25);
                        INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Healing Potion', N'A ruby flask that warms on the way down. Restores 25 HP.', 30, 1, @MiraInvId, 'Consumable', 1, 25);
                    END
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Stamina Draft' AND ContainerId=@MiraInvId)
                        INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Stamina Draft', N'Bitter and fizzy. Restores 20 SP.', 25, 1, @MiraInvId, 'Consumable', 2, 20);
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Lockpick' AND ContainerId=@MiraInvId)
                        INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Lockpick', N'A thin wire pick. Breaks on a bad roll.', 15, 0, N'lockpick', @MiraInvId, 'Consumable', 0, 0);
                END
            ");

            // ── Step 5: Move Gobby to Goblin Camp ────────────────────────────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @CampId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Goblin Camp');
                UPDATE Characters SET RoomId = @CampId WHERE Name = N'Gobby' AND CharacterType = 'NPC';
            ");

            // ── Step 6: Vault Key in Gobby's camp crate; potion in Gobby's loot ──
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @CampId    INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Goblin Camp');
                DECLARE @GobbyId   INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Gobby' AND CharacterType = 'NPC');
                DECLARE @GobbyInvId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @GobbyId);

                -- Camp Crate (locked, pickable, DC 12)
                IF @CampId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Chest' AND Name=N'Camp Crate' AND RoomId=@CampId)
                    INSERT INTO Containers (Name, ContainerType, RoomId, IsLocked, IsPickable, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, MaxWeight)
                    VALUES (N'Camp Crate', 'Chest', @CampId, 1, 1, 0, 0, 0, 12, 30);

                DECLARE @CrateId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Chest' AND Name=N'Camp Crate' AND RoomId=@CampId);
                IF @CrateId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Vault Key' AND ContainerId=@CrateId)
                    INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Vault Key', N'Heavy iron. Runes etched along the bow — old magic, half-faded.', 200, 1, N'vault_key', @CrateId, 'Consumable', 0, 0);

                IF @GobbyInvId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Healing Potion' AND ContainerId=@GobbyInvId)
                    INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Healing Potion', N'A ruby flask that warms on the way down. Restores 25 HP.', 30, 1, @GobbyInvId, 'Consumable', 1, 25);
            ");

            // ── Step 7: Seed Inn Cellar (Rat + Cask chest) ────────────────────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @CellarId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Inn Cellar');

                IF NOT EXISTS (SELECT 1 FROM Characters WHERE Name = N'Giant Cellar Rat' AND CharacterType = 'NPC')
                    INSERT INTO Characters (Name, Level, CharacterType, RoomId)
                    VALUES (N'Giant Cellar Rat', 1, 'NPC', @CellarId);

                DECLARE @RatId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Giant Cellar Rat' AND CharacterType = 'NPC');

                IF NOT EXISTS (SELECT 1 FROM Stats WHERE CharacterId = @RatId)
                    INSERT INTO Stats (CharacterId, Physique, Constitution, Reflexes, Intuition, Intellect, Linguistic, Luck)
                    VALUES (@RatId, 3, 2, 7, 2, 1, 1, 4);

                IF NOT EXISTS (SELECT 1 FROM Resources WHERE CharacterId = @RatId)
                    INSERT INTO Resources (CharacterId, Hp, MaxHp, Sp, MaxSp, BitPool, MaxBitPool, BytePool, MaxBytePool)
                    VALUES (@RatId, 22, 22, 16, 16, 28, 28, 13, 13);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @RatId)
                    INSERT INTO Containers (Name, ContainerType, [Inventory_OwnerCharacterId], MaxWeight)
                    VALUES (N'Rat Scraps', 'Inventory', @RatId, 10);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @RatId)
                    INSERT INTO Containers (Name, ContainerType, [OwnerCharacterId])
                    VALUES (N'Rat Body', 'Equipment', @RatId);

                DECLARE @RatEquipId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @RatId);
                IF @RatEquipId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM EquipmentSlots WHERE EquipmentContainerId = @RatEquipId)
                    INSERT INTO EquipmentSlots (CharacterId, Slot, EquippedItemId, EquipmentContainerId)
                    SELECT @RatId, v.SlotInt, NULL, @RatEquipId
                    FROM (VALUES (1),(2),(4),(8),(16),(32),(64)) AS v(SlotInt);

                DECLARE @RatInvId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @RatId);
                IF @RatInvId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Items WHERE ContainerId=@RatInvId)
                    INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Stamina Draft', N'Bitter and fizzy. Restores 20 SP.', 25, 1, @RatInvId, 'Consumable', 2, 20);

                -- Cellar Cask (unlocked)
                IF @CellarId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Chest' AND Name=N'Cellar Cask' AND RoomId=@CellarId)
                    INSERT INTO Containers (Name, ContainerType, RoomId, IsLocked, IsPickable, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, MaxWeight)
                    VALUES (N'Cellar Cask', 'Chest', @CellarId, 0, 1, 0, 0, 0, 10, 20);

                DECLARE @CaskId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Chest' AND Name=N'Cellar Cask' AND RoomId=@CellarId);
                IF @CaskId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Healing Potion' AND ContainerId=@CaskId)
                    INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Healing Potion', N'A ruby flask that warms on the way down. Restores 25 HP.', 30, 1, @CaskId, 'Consumable', 1, 25);
            ");

            // ── Step 8: Thornwood floor items ─────────────────────────────────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @PathId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Thornwood Path');
                IF @PathId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Thornwood Herb' AND ContainerId=@PathId)
                BEGIN
                    INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Thornwood Herb', N'A bitter green leaf used in stamina tinctures. Chew for 10 SP.', 5, 0, @PathId, 'Consumable', 2, 10);
                    INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Thornwood Herb', N'A bitter green leaf used in stamina tinctures. Chew for 10 SP.', 5, 0, @PathId, 'Consumable', 2, 10);
                END
            ");

            // ── Step 9: Ruined Chapel (Undead + Bookshelf + Poison chest) ─────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @ChapelId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Ruined Chapel');

                IF @ChapelId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Bookshelf' AND Name=N'Chapel Shelves' AND [Bookshelf_RoomId]=@ChapelId)
                    INSERT INTO Containers (Name, ContainerType, [Bookshelf_RoomId], MaxWeight)
                    VALUES (N'Chapel Shelves', 'Bookshelf', @ChapelId, 50);

                DECLARE @ShelfId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Bookshelf' AND Name=N'Chapel Shelves' AND [Bookshelf_RoomId]=@ChapelId);
                IF @ShelfId IS NOT NULL
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Tome of the Sealed Ones' AND ContainerId=@ShelfId)
                        INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Tome of the Sealed Ones',
                                N'A cracked leather volume. The last entry reads: ''The Conclave sealed Erasmus the Unbound beneath the vault in year 743 — may the lock hold until the world forgets his name.''',
                                80, 2, @ShelfId, 'Consumable', 0, 0);
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Herbalist''s Notes' AND ContainerId=@ShelfId)
                        INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Herbalist''s Notes',
                                N'Field notes on Thornwood flora. On Thornwood Herb: ''Chew raw for a burst of stamina. Tastes awful.''',
                                15, 1, @ShelfId, 'Consumable', 0, 0);
                END

                IF NOT EXISTS (SELECT 1 FROM Characters WHERE Name = N'Risen Acolyte' AND CharacterType = 'NPC')
                    INSERT INTO Characters (Name, Level, CharacterType, RoomId)
                    VALUES (N'Risen Acolyte', 3, 'NPC', @ChapelId);

                DECLARE @UndeadId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Risen Acolyte' AND CharacterType = 'NPC');

                IF NOT EXISTS (SELECT 1 FROM Stats WHERE CharacterId = @UndeadId)
                    INSERT INTO Stats (CharacterId, Physique, Constitution, Reflexes, Intuition, Intellect, Linguistic, Luck)
                    VALUES (@UndeadId, 7, 5, 2, 3, 2, 1, 2);

                IF NOT EXISTS (SELECT 1 FROM Resources WHERE CharacterId = @UndeadId)
                    INSERT INTO Resources (CharacterId, Hp, MaxHp, Sp, MaxSp, BitPool, MaxBitPool, BytePool, MaxBytePool)
                    VALUES (@UndeadId, 75, 75, 45, 45, 32, 32, 16, 16);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @UndeadId)
                    INSERT INTO Containers (Name, ContainerType, [Inventory_OwnerCharacterId], MaxWeight)
                    VALUES (N'Acolyte Remains', 'Inventory', @UndeadId, 30);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @UndeadId)
                    INSERT INTO Containers (Name, ContainerType, [OwnerCharacterId])
                    VALUES (N'Acolyte Gear', 'Equipment', @UndeadId);

                DECLARE @UndeadEquipId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @UndeadId);
                IF @UndeadEquipId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM EquipmentSlots WHERE EquipmentContainerId = @UndeadEquipId)
                    INSERT INTO EquipmentSlots (CharacterId, Slot, EquippedItemId, EquipmentContainerId)
                    SELECT @UndeadId, v.SlotInt, NULL, @UndeadEquipId
                    FROM (VALUES (1),(2),(4),(8),(16),(32),(64)) AS v(SlotInt);

                DECLARE @UndeadInvId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @UndeadId);
                IF @UndeadInvId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Items WHERE ContainerId=@UndeadInvId)
                    INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Healing Potion', N'A ruby flask that warms on the way down. Restores 25 HP.', 30, 1, @UndeadInvId, 'Consumable', 1, 25);

                -- Altar Chest: unlocked but Poison-trapped (TrapTypes=4, damage=12)
                IF @ChapelId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Chest' AND Name=N'Altar Chest' AND RoomId=@ChapelId)
                    INSERT INTO Containers (Name, ContainerType, RoomId, IsLocked, IsPickable, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, MaxWeight)
                    VALUES (N'Altar Chest', 'Chest', @ChapelId, 0, 1, 4, 12, 0, 10, 25);

                DECLARE @AltarChestId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Chest' AND Name=N'Altar Chest' AND RoomId=@ChapelId);
                IF @AltarChestId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Items WHERE ContainerId=@AltarChestId)
                    INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Bit Crystal', N'A faceted gem humming with raw Bit energy. Restores 30 BitPool.', 60, 1, @AltarChestId, 'Consumable', 3, 30);
                    -- ConsumableEffect.BitPool = 3
            ");

            // ── Step 10: Crypt Entrance (Crypt Hound wolf) ────────────────────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @CryptId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'Crypt Entrance');

                IF NOT EXISTS (SELECT 1 FROM Characters WHERE Name = N'Crypt Hound' AND CharacterType = 'Wolf')
                    INSERT INTO Characters (Name, Level, CharacterType, RoomId, PackSize)
                    VALUES (N'Crypt Hound', 3, 'Wolf', @CryptId, 2);

                DECLARE @WolfId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Crypt Hound' AND CharacterType = 'Wolf');

                IF NOT EXISTS (SELECT 1 FROM Stats WHERE CharacterId = @WolfId)
                    INSERT INTO Stats (CharacterId, Physique, Constitution, Reflexes, Intuition, Intellect, Linguistic, Luck)
                    VALUES (@WolfId, 6, 4, 8, 4, 2, 1, 5);

                IF NOT EXISTS (SELECT 1 FROM Resources WHERE CharacterId = @WolfId)
                    INSERT INTO Resources (CharacterId, Hp, MaxHp, Sp, MaxSp, BitPool, MaxBitPool, BytePool, MaxBytePool)
                    VALUES (@WolfId, 70, 70, 44, 44, 36, 36, 16, 16);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @WolfId)
                    INSERT INTO Containers (Name, ContainerType, [Inventory_OwnerCharacterId], MaxWeight)
                    VALUES (N'Wolf Pelt and Bones', 'Inventory', @WolfId, 20);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @WolfId)
                    INSERT INTO Containers (Name, ContainerType, [OwnerCharacterId])
                    VALUES (N'Wolf Body', 'Equipment', @WolfId);

                DECLARE @WolfEquipId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @WolfId);
                IF @WolfEquipId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM EquipmentSlots WHERE EquipmentContainerId = @WolfEquipId)
                    INSERT INTO EquipmentSlots (CharacterId, Slot, EquippedItemId, EquipmentContainerId)
                    SELECT @WolfId, v.SlotInt, NULL, @WolfEquipId
                    FROM (VALUES (1),(2),(4),(8),(16),(32),(64)) AS v(SlotInt);

                DECLARE @WolfInvId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @WolfId);
                IF @WolfInvId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Items WHERE ContainerId=@WolfInvId)
                    INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Wolf Pelt', N'Thick and surprisingly clean. Worth something to a tanner.', 40, 3, @WolfInvId, 'Consumable', 0, 0);
            ");

            // ── Step 11: The Sealed Vault (Erasmus boss + Reliquary chest) ─────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @VaultId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'The Sealed Vault');

                IF NOT EXISTS (SELECT 1 FROM Characters WHERE Name = N'Erasmus the Unbound' AND CharacterType = 'NPC')
                    INSERT INTO Characters (Name, Level, CharacterType, RoomId)
                    VALUES (N'Erasmus the Unbound', 8, 'NPC', @VaultId);

                DECLARE @BossId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Erasmus the Unbound' AND CharacterType = 'NPC');

                IF NOT EXISTS (SELECT 1 FROM Stats WHERE CharacterId = @BossId)
                    INSERT INTO Stats (CharacterId, Physique, Constitution, Reflexes, Intuition, Intellect, Linguistic, Luck)
                    VALUES (@BossId, 6, 8, 5, 9, 10, 7, 6);

                IF NOT EXISTS (SELECT 1 FROM Resources WHERE CharacterId = @BossId)
                    INSERT INTO Resources (CharacterId, Hp, MaxHp, Sp, MaxSp, BitPool, MaxBitPool, BytePool, MaxBytePool)
                    VALUES (@BossId, 120, 120, 60, 60, 56, 56, 40, 40);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @BossId)
                    INSERT INTO Containers (Name, ContainerType, [Inventory_OwnerCharacterId], MaxWeight)
                    VALUES (N'Erasmus Hoard', 'Inventory', @BossId, 60);

                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @BossId)
                    INSERT INTO Containers (Name, ContainerType, [OwnerCharacterId])
                    VALUES (N'Erasmus Robes', 'Equipment', @BossId);

                DECLARE @BossEquipId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Equipment' AND [OwnerCharacterId] = @BossId);
                IF @BossEquipId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM EquipmentSlots WHERE EquipmentContainerId = @BossEquipId)
                    INSERT INTO EquipmentSlots (CharacterId, Slot, EquippedItemId, EquipmentContainerId)
                    SELECT @BossId, v.SlotInt, NULL, @BossEquipId
                    FROM (VALUES (1),(2),(4),(8),(16),(32),(64)) AS v(SlotInt);

                DECLARE @BossInvId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Inventory' AND [Inventory_OwnerCharacterId] = @BossId);
                IF @BossInvId IS NOT NULL
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Byte Crystal' AND ContainerId=@BossInvId)
                        INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Byte Crystal', N'Dense with structured magic. Restores 30 BytePool.', 90, 1, @BossInvId, 'Consumable', 4, 30);
                        -- ConsumableEffect.BytePool = 4
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Erasmus Manifesto' AND ContainerId=@BossInvId)
                        INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Erasmus Manifesto',
                                N'Dense notes in a cramped hand. The last line: ''They think sealing me here ends the matter. Fools. I only need to wait.''',
                                150, 1, @BossInvId, 'Consumable', 0, 0);
                END

                -- Boss Chest: locked, not pickable, Electric-trapped (TrapTypes=8, damage=20)
                IF @VaultId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType='Chest' AND Name=N'The Sealed Reliquary' AND RoomId=@VaultId)
                    INSERT INTO Containers (Name, ContainerType, RoomId, IsLocked, IsPickable, RequiredKeyId, TrapTypes, TrapDamage, TrapDisarmed, UnlockDC, MaxWeight)
                    VALUES (N'The Sealed Reliquary', 'Chest', @VaultId, 1, 0, N'vault_key', 8, 20, 0, 20, 50);

                DECLARE @ReliquaryId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Chest' AND Name=N'The Sealed Reliquary' AND RoomId=@VaultId);
                IF @ReliquaryId IS NOT NULL
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Runeblade' AND ContainerId=@ReliquaryId)
                        INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, AttackPower, WeaponType, Effect, Potency)
                        VALUES (N'Runeblade', N'Elven steel etched with dormant runes. Hums faintly in the hand.', 500, 5, NULL, @ReliquaryId, 'Weapon', 18, 1, 0, 0);
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name=N'Greater Healing Potion' AND ContainerId=@ReliquaryId)
                        INSERT INTO Items (Name, Description, Value, Weight, ContainerId, ItemType, Effect, Potency)
                        VALUES (N'Greater Healing Potion', N'Thick and golden — restores 60 HP.', 80, 1, @ReliquaryId, 'Consumable', 1, 60);
                END

                -- Erasmus uses Byte Bolt
                DECLARE @ByteBoltId INT = (SELECT TOP 1 Id FROM Magics WHERE Name = N'Byte Bolt');
                IF @BossId IS NOT NULL AND @ByteBoltId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM CharacterMagic WHERE MagicsId = @ByteBoltId AND CharactersId = @BossId)
                    INSERT INTO CharacterMagic (MagicsId, CharactersId) VALUES (@ByteBoltId, @BossId);
            ");

            // ── Step 12: Set Elara's starting room to The Wayward Crow Inn ─────────
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @InnId   INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType='Room' AND Name=N'The Wayward Crow Inn');
                DECLARE @ElaraId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Elara the Bold' AND CharacterType = 'Player');
                IF @ElaraId IS NOT NULL AND @InnId IS NOT NULL
                    UPDATE Characters SET RoomId = @InnId WHERE Id = @ElaraId;
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                -- Null room pointers before removing rooms
                UPDATE Characters SET RoomId = NULL
                WHERE RoomId IN (
                    SELECT Id FROM Containers WHERE ContainerType = 'Room'
                    AND Name IN (
                        N'The Wayward Crow Inn', N'Inn Cellar', N'Thornwood Path',
                        N'Goblin Camp', N'Ruined Chapel', N'Crypt Entrance', N'The Sealed Vault'
                    )
                );

                -- Remove Erasmus
                DECLARE @BossId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Erasmus the Unbound' AND CharacterType = 'NPC');
                IF @BossId IS NOT NULL
                BEGIN
                    DELETE FROM CharacterMagic WHERE CharactersId = @BossId;
                    DELETE Items FROM Items JOIN Containers C ON Items.ContainerId = C.Id WHERE C.[Inventory_OwnerCharacterId] = @BossId;
                    DELETE FROM EquipmentSlots WHERE CharacterId = @BossId;
                    DELETE FROM Containers WHERE [Inventory_OwnerCharacterId] = @BossId OR [OwnerCharacterId] = @BossId;
                    DELETE FROM Stats WHERE CharacterId = @BossId;
                    DELETE FROM Resources WHERE CharacterId = @BossId;
                    DELETE FROM Characters WHERE Id = @BossId;
                END

                -- Remove other seeded NPCs
                DECLARE @NpcIds TABLE (Id INT);
                INSERT INTO @NpcIds
                SELECT Id FROM Characters
                WHERE Name IN (N'Mira', N'Giant Cellar Rat', N'Risen Acolyte', N'Crypt Hound');

                DELETE Items FROM Items JOIN Containers C ON Items.ContainerId = C.Id
                WHERE C.[Inventory_OwnerCharacterId] IN (SELECT Id FROM @NpcIds);
                DELETE FROM EquipmentSlots WHERE CharacterId IN (SELECT Id FROM @NpcIds);
                DELETE FROM Containers WHERE [Inventory_OwnerCharacterId] IN (SELECT Id FROM @NpcIds) OR [OwnerCharacterId] IN (SELECT Id FROM @NpcIds);
                DELETE FROM Stats WHERE CharacterId IN (SELECT Id FROM @NpcIds);
                DELETE FROM Resources WHERE CharacterId IN (SELECT Id FROM @NpcIds);
                DELETE FROM Characters WHERE Id IN (SELECT Id FROM @NpcIds);

                -- Remove room child containers and their items
                DECLARE @NewRoomIds TABLE (Id INT);
                INSERT INTO @NewRoomIds
                SELECT Id FROM Containers WHERE ContainerType = 'Room'
                AND Name IN (
                    N'The Wayward Crow Inn', N'Inn Cellar', N'Thornwood Path',
                    N'Goblin Camp', N'Ruined Chapel', N'Crypt Entrance', N'The Sealed Vault'
                );

                DELETE FROM Items WHERE ContainerId IN (
                    SELECT Id FROM Containers
                    WHERE RoomId              IN (SELECT Id FROM @NewRoomIds)
                       OR [Bookshelf_RoomId] IN (SELECT Id FROM @NewRoomIds)
                );
                DELETE FROM Items WHERE ContainerId IN (SELECT Id FROM @NewRoomIds);
                DELETE FROM Containers WHERE RoomId              IN (SELECT Id FROM @NewRoomIds);
                DELETE FROM Containers WHERE [Bookshelf_RoomId] IN (SELECT Id FROM @NewRoomIds);
                DELETE FROM Doors WHERE RoomAId IN (SELECT Id FROM @NewRoomIds) OR RoomBId IN (SELECT Id FROM @NewRoomIds);
                DELETE FROM Containers WHERE Id IN (SELECT Id FROM @NewRoomIds);

                -- Gobby loses his room assignment
                UPDATE Characters SET RoomId = NULL WHERE Name = N'Gobby' AND CharacterType = 'NPC';
            ");
        }
    }
}
