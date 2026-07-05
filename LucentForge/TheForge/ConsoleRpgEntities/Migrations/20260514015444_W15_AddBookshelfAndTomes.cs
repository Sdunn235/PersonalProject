using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W15_AddBookshelfAndTomes : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "LoreText",
                table: "Items",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Bookshelf_Description",
                table: "Containers",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "Bookshelf_RoomId",
                table: "Containers",
                type: "int",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Containers_Bookshelf_RoomId",
                table: "Containers",
                column: "Bookshelf_RoomId");

            migrationBuilder.AddForeignKey(
                name: "FK_Containers_Containers_Bookshelf_RoomId",
                table: "Containers",
                column: "Bookshelf_RoomId",
                principalTable: "Containers",
                principalColumn: "Id");

            // --- Seed: Ancient Library room, door, bookshelf, and three tomes ---
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                -- 1. New room: Ancient Library
                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'Ancient Library')
                    INSERT INTO Containers (Name, ContainerType, Room_Description)
                    VALUES (N'Ancient Library', 'Room',
                            N'Tall shelves line every wall, heavy with dust and knowledge. The air smells of old ink and cold stone.');

                DECLARE @AntechamberId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Room' AND Name = N'Antechamber');
                DECLARE @AncientLibId  INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Room' AND Name = N'Ancient Library');

                -- 2. Stone Archway door: Antechamber <-> Ancient Library (not secret, not locked)
                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Stone Archway')
                AND @AntechamberId IS NOT NULL AND @AncientLibId IS NOT NULL
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId,
                                       IsLocked, IsTrapped, IsPickable, RequiredKeyId,
                                       TrapDamage, TrapDisarmed, UnlockDC,
                                       IsSecret, IsDiscovered)
                    VALUES (N'Stone Archway',
                            N'A broad stone archway worn smooth by age. The room beyond smells of old books.',
                            @AntechamberId, @AncientLibId,
                            0, 0, 0, NULL, 0, 0, 0, 0, 1);

                -- 3. Bookshelf in Ancient Library
                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Bookshelf' AND Name = N'Carved Oak Shelf')
                AND @AncientLibId IS NOT NULL
                    INSERT INTO Containers (Name, ContainerType, Bookshelf_Description, Bookshelf_RoomId)
                    VALUES (N'Carved Oak Shelf', 'Bookshelf',
                            N'Rows of tomes, some cracked and faded. A few look recently disturbed.',
                            @AncientLibId);

                DECLARE @ShelfId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Bookshelf' AND Name = N'Carved Oak Shelf');

                -- 4. Tomes (Effect=0/Potency=0 satisfy the NOT NULL constraint shared across Items TPH)
                IF @ShelfId IS NOT NULL
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'LucentForge Codex, Vol. I')
                        INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, Effect, Potency, LoreText)
                        VALUES (
                            N'LucentForge Codex, Vol. I',
                            N'A slim primer bound in grey leather. The cover bears two nested spirals.',
                            50, 2, NULL, @ShelfId, 'Tome', 0, 0,
                            N'The world runs on something older than fire.
Scholars call it the Source — layered beneath stone and root, it pulses in two frequencies: Bits and Bytes.

Bits are sharp, precise, destructive. A Bit-struck flame burns cold.
Bytes are slow, patient, constructive. A Byte-wrought ward outlasts any wall.

Neither is good nor evil. Each is a hammer looking for a nail.
The art is knowing which one to swing.

— Excerpt from a primer on Source-wielding, attributed to the Founders'
                        );

                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'On the Outcast')
                        INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, Effect, Potency, LoreText)
                        VALUES (
                            N'On the Outcast',
                            N'A thin official record, sealed with a wax mark in the shape of a thorn-cluster.',
                            10, 1, NULL, @ShelfId, 'Tome', 0, 0,
                            N'Let the record show:

Grubnak of the Sharp Eye was a scout of the Blackthorn Swarm.
On the night of the third raid, he abandoned his post.
Three clutchmates were taken because the flank was unwatched.

He calls himself free. We have heard he has taken another name for himself.
Names do not change what a creature is.
He will always be Grubnak to us.

He stole from the Warchief''s table and fled into the dungeon dark.
If found, he is to be returned. Alive is preferred. Not required.

This account is sealed by the Warchief''s mark.'
                        );

                    IF NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'A Brief History of the Wilds')
                        INSERT INTO Items (Name, Description, Value, Weight, KeyId, ContainerId, ItemType, Effect, Potency, LoreText)
                        VALUES (
                            N'A Brief History of the Wilds',
                            N'A thick volume with a cracked spine. The first third is water-damaged beyond reading.',
                            30, 3, NULL, @ShelfId, 'Tome', 0, 0,
                            N'The Wilds were not always wild.

Before the Fracture, these forests were tended — paths marked,
rivers named, settlements spaced a day''s walk apart.
Something broke the order. No one living remembers what.

What remains: creatures that should not be this far inland,
ruins that predate the oldest maps, and an unsettling quiet
that deepens the further you walk from the last road.

The scholars say the Forge still burns beneath it all.
They have not yet agreed on what it is forging.'
                        );
                END
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                DELETE FROM Items WHERE Name IN (
                    N'LucentForge Codex, Vol. I',
                    N'On the Outcast',
                    N'A Brief History of the Wilds'
                );
                DELETE FROM Containers WHERE ContainerType = 'Bookshelf' AND Name = N'Carved Oak Shelf';
                DELETE FROM Doors WHERE Name = N'Stone Archway';
                DELETE FROM Containers WHERE ContainerType = 'Room' AND Name = N'Ancient Library';
            ");

            migrationBuilder.DropForeignKey(
                name: "FK_Containers_Containers_Bookshelf_RoomId",
                table: "Containers");

            migrationBuilder.DropIndex(
                name: "IX_Containers_Bookshelf_RoomId",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "LoreText",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "Bookshelf_Description",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "Bookshelf_RoomId",
                table: "Containers");
        }
    }
}
