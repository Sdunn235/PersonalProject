using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W15_AddWolf : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "PackSize",
                table: "Characters",
                type: "int",
                nullable: true);

            // --- Seed: Forest Edge room, door, Wolf NPC, and pelt loot ---
            // W15 Phase F3 — proves Phase E works for non-Gobby monsters:
            // the Wolf's loot lives in its Inventory, not a MonsterLoot container.
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                -- 1. Forest Edge room (post-W14 TPH: rooms live in Containers table)
                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'Forest Edge')
                    INSERT INTO Containers (Name, ContainerType, Room_Description)
                    VALUES (N'Forest Edge', 'Room',
                            N'Tall pines press close on both sides. The tree line swallows the light. Something is watching.');

                DECLARE @AntechamberId  INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Room' AND Name = N'Antechamber');
                DECLARE @ForestEdgeId   INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Room' AND Name = N'Forest Edge');

                -- 2. Rough Path door: Antechamber <-> Forest Edge
                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Rough Path')
                AND @AntechamberId IS NOT NULL AND @ForestEdgeId IS NOT NULL
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId,
                                       IsLocked, IsTrapped, IsPickable, RequiredKeyId,
                                       TrapDamage, TrapDisarmed, UnlockDC,
                                       IsSecret, IsDiscovered)
                    VALUES (N'Rough Path',
                            N'A muddy track worn into the earth. Paw prints overlap boot prints.',
                            @AntechamberId, @ForestEdgeId,
                            0, 0, 0, NULL, 0, 0, 0, 0, 1);

                -- 3. Wolf NPC
                IF NOT EXISTS (SELECT 1 FROM Characters WHERE Name = N'Forest Wolf' AND CharacterType = 'Wolf')
                AND @ForestEdgeId IS NOT NULL
                BEGIN
                    INSERT INTO Characters (Name, Level, RoomId, CharacterType, PackSize)
                    VALUES (N'Forest Wolf', 2, @ForestEdgeId, 'Wolf', 3);

                    DECLARE @WolfId INT = SCOPE_IDENTITY();

                    -- Stats (Physique=6 makes it hit a bit harder than the goblin)
                    INSERT INTO Stats (CharacterId, Physique, Constitution, Reflexes, Intuition, Intellect, Linguistic, Luck)
                    VALUES (@WolfId, 6, 5, 7, 3, 1, 0, 2);

                    -- Resources (HP=40, SP=20 — a tough skirmisher)
                    INSERT INTO Resources (CharacterId, Hp, MaxHp, Sp, MaxSp, BitPool, MaxBitPool, BytePool, MaxBytePool)
                    VALUES (@WolfId, 40, 40, 20, 20, 0, 0, 0, 0);

                    -- Inventory (loot lives here — Phase E proof)
                    INSERT INTO Containers (Name, ContainerType, [Inventory_OwnerCharacterId], MaxWeight)
                    VALUES (N'Forest Wolf Inventory', 'Inventory', @WolfId, 50);

                    DECLARE @WolfInvId INT = SCOPE_IDENTITY();

                    -- Raw Pelt loot item
                    INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, Effect, Potency)
                    VALUES (N'Raw Wolf Pelt',
                            N'Thick grey fur, still warm. A tanner would pay well for this.',
                            25, 3, NULL, @WolfInvId, 'Consumable', 0, 0);

                    -- Equipment container (required for integrity sweep; starts empty)
                    INSERT INTO Containers (Name, ContainerType, [OwnerCharacterId])
                    VALUES (N'Forest Wolf Equipment', 'Equipment', @WolfId);
                END
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                -- Remove Wolf loot items first (FK: Items.ContainerId -> Containers.Id)
                DELETE Items
                FROM Items
                JOIN Containers Inv ON Items.ContainerId = Inv.Id
                JOIN Characters W    ON Inv.[Inventory_OwnerCharacterId] = W.Id
                WHERE W.Name = N'Forest Wolf' AND W.CharacterType = 'Wolf';

                -- Remove Wolf containers
                DELETE Containers
                FROM Containers
                JOIN Characters W ON Containers.[Inventory_OwnerCharacterId] = W.Id
                    OR Containers.[OwnerCharacterId] = W.Id
                WHERE W.Name = N'Forest Wolf' AND W.CharacterType = 'Wolf';

                -- Remove Wolf character
                DELETE FROM Characters WHERE Name = N'Forest Wolf' AND CharacterType = 'Wolf';

                -- Remove door and room
                DELETE FROM Doors WHERE Name = N'Rough Path';
                DELETE FROM Containers WHERE ContainerType = 'Room' AND Name = N'Forest Edge';
            ");

            migrationBuilder.DropColumn(
                name: "PackSize",
                table: "Characters");
        }
    }
}
