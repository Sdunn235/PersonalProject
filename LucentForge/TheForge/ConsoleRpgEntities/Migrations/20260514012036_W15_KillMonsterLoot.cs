using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W15_KillMonsterLoot : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // --- Data migration (must run before structural drops) ---

            // Move items from each MonsterLoot container into the owning NPC's
            // Inventory. Inventory_OwnerCharacterId is EF TPH's disambiguated
            // column name for Inventory.OwnerCharacterId (Equipment uses plain
            // OwnerCharacterId — the W14 B.1 index-filter fix established this).
            migrationBuilder.Sql(@"
                UPDATE Items
                SET ContainerId = Inv.Id
                FROM Items
                JOIN Containers Loot
                    ON Items.ContainerId = Loot.Id
                    AND Loot.ContainerType = 'MonsterLoot'
                JOIN Characters Npc
                    ON Npc.LootId = Loot.Id
                JOIN Containers Inv
                    ON Inv.[Inventory_OwnerCharacterId] = Npc.Id
                    AND Inv.ContainerType = 'Inventory';
            ");

            // Orphaned loot items (MonsterLoot with no NPC.LootId pointing to it)
            // become unowned rather than being silently lost.
            migrationBuilder.Sql(@"
                UPDATE Items
                SET ContainerId = NULL
                FROM Items
                JOIN Containers Loot
                    ON Items.ContainerId = Loot.Id
                    AND Loot.ContainerType = 'MonsterLoot'
                WHERE NOT EXISTS (
                    SELECT 1 FROM Characters Npc WHERE Npc.LootId = Loot.Id
                );
            ");

            // Rename the outcast goblin — his real name is Gobby, not Grubnak.
            // (Grubnak was the tribe's name for him; Gobby is what he calls himself.)
            migrationBuilder.Sql(@"
                UPDATE Characters
                SET Name = 'Gobby'
                WHERE Name = 'Grubnak'
                  AND CharacterType = 'NPC';
            ");

            // Delete all MonsterLoot containers (items already moved above).
            migrationBuilder.Sql(@"
                DELETE FROM Containers WHERE ContainerType = 'MonsterLoot';
            ");

            // --- Structural drops ---

            migrationBuilder.DropForeignKey(
                name: "FK_Characters_Containers_LootId",
                table: "Characters");

            migrationBuilder.DropIndex(
                name: "IX_Characters_LootId",
                table: "Characters");

            migrationBuilder.DropColumn(
                name: "IsLooted",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "LootId",
                table: "Characters");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<bool>(
                name: "IsLooted",
                table: "Containers",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "LootId",
                table: "Characters",
                type: "int",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Characters_LootId",
                table: "Characters",
                column: "LootId",
                unique: true,
                filter: "[LootId] IS NOT NULL");

            migrationBuilder.AddForeignKey(
                name: "FK_Characters_Containers_LootId",
                table: "Characters",
                column: "LootId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.SetNull);
        }
    }
}
