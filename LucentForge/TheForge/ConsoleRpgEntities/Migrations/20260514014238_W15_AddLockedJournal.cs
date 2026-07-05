using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W15_AddLockedJournal : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "Content",
                table: "Items",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsLocked",
                table: "Items",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsPickable",
                table: "Items",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsTrapped",
                table: "Items",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "RequiredKeyId",
                table: "Items",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TrapDamage",
                table: "Items",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "TrapDisarmed",
                table: "Items",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "UnlockDC",
                table: "Items",
                type: "int",
                nullable: true);

            // --- Seed: Gobby's Journal in Hidden Alcove ---
            // W15 Phase F1 — LSP demo. The same Dungeon Key that opens the
            // Ornate Rune-Engraved Chest (RequiredKeyId = 'dungeon-main') also
            // opens this journal. TryUnlock(ILockable, Item) handles both with
            // zero code changes — substitution is real.
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                DECLARE @HiddenAlcoveId INT = (
                    SELECT TOP 1 Id FROM Containers
                    WHERE ContainerType = 'Room' AND Name = N'Hidden Alcove'
                );

                IF @HiddenAlcoveId IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM Items WHERE Name = N'Gobby''s Journal')
                    INSERT INTO Items (
                        Name, Description, Value, Weight, KeyId,
                        ContainerId, ItemType,
                        Effect, Potency,
                        Content, IsLocked, IsTrapped, IsPickable,
                        RequiredKeyId, TrapDamage, TrapDisarmed, UnlockDC
                    )
                    VALUES (
                        N'Gobby''s Journal',
                        N'A small battered journal sealed with an iron clasp. The rune on the clasp matches the Dungeon Key.',
                        0, 1, NULL,
                        @HiddenAlcoveId, 'LockedJournal',
                        0, 0,
                        N'Day 1 without the tribe.
They call me deserter. Traitor. Waste of scales.
I call myself free.

The swarm does not think. It only hungers, spreads, and swarms again.
I watched my brothers drown three villages — not for food, not for survival.
For the Warchief''s sport. That is not what we are made for.

We are scouts. Eyes and ears of the deep dark.
We move alone, unseen, unheard. That is our gift.
Swarms are just scouts who forgot what they were.

I have hidden my key here with the chest in the vault.
The chest holds proof of what the Warchief ordered.
If someone finds this: I was not a traitor.
I was the only one paying attention.

— Gobby, the Outcast',
                        1, 0, 0,
                        N'dungeon-main', 0, 0, 99
                    );
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                DELETE FROM Items WHERE Name = N'Gobby''s Journal';
            ");

            migrationBuilder.DropColumn(
                name: "Content",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "IsLocked",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "IsPickable",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "IsTrapped",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "RequiredKeyId",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "TrapDamage",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "TrapDisarmed",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "UnlockDC",
                table: "Items");
        }
    }
}
