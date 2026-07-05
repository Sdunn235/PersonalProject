using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W12_InventoryAndSeed : BaseMigration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "ContainerId",
                table: "Items",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "EquipmentContainerId",
                table: "EquipmentSlots",
                type: "int",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "Containers",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ContainerType = table.Column<string>(type: "nvarchar(13)", maxLength: 13, nullable: false),
                    OwnerCharacterId = table.Column<int>(type: "int", nullable: true),
                    Inventory_OwnerCharacterId = table.Column<int>(type: "int", nullable: true),
                    MaxWeight = table.Column<int>(type: "int", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Containers", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Containers_Characters_Inventory_OwnerCharacterId",
                        column: x => x.Inventory_OwnerCharacterId,
                        principalTable: "Characters",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_Containers_Characters_OwnerCharacterId",
                        column: x => x.OwnerCharacterId,
                        principalTable: "Characters",
                        principalColumn: "Id");
                });

            migrationBuilder.CreateIndex(
                name: "IX_Items_ContainerId",
                table: "Items",
                column: "ContainerId");

            migrationBuilder.CreateIndex(
                name: "IX_EquipmentSlots_EquipmentContainerId",
                table: "EquipmentSlots",
                column: "EquipmentContainerId");

            migrationBuilder.CreateIndex(
                name: "IX_Containers_Inventory_OwnerCharacterId",
                table: "Containers",
                column: "Inventory_OwnerCharacterId",
                unique: true,
                filter: "[OwnerCharacterId] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_Containers_OwnerCharacterId",
                table: "Containers",
                column: "OwnerCharacterId",
                unique: true,
                filter: "[OwnerCharacterId] IS NOT NULL");

            migrationBuilder.AddForeignKey(
                name: "FK_EquipmentSlots_Containers_EquipmentContainerId",
                table: "EquipmentSlots",
                column: "EquipmentContainerId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Items_Containers_ContainerId",
                table: "Items",
                column: "ContainerId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.SetNull);

            // W12 seed — runs Races, Elara + Stats/Resources, containers, starter items, equipment slots.
            RunSqlScript(migrationBuilder, "W12_SeedInventoryData.sql");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Tear down seeded rows first, then the schema they depend on.
            RunSqlScript(migrationBuilder, "W12_SeedInventoryData.rollback.sql");

            migrationBuilder.DropForeignKey(
                name: "FK_EquipmentSlots_Containers_EquipmentContainerId",
                table: "EquipmentSlots");

            migrationBuilder.DropForeignKey(
                name: "FK_Items_Containers_ContainerId",
                table: "Items");

            migrationBuilder.DropTable(
                name: "Containers");

            migrationBuilder.DropIndex(
                name: "IX_Items_ContainerId",
                table: "Items");

            migrationBuilder.DropIndex(
                name: "IX_EquipmentSlots_EquipmentContainerId",
                table: "EquipmentSlots");

            migrationBuilder.DropColumn(
                name: "ContainerId",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "EquipmentContainerId",
                table: "EquipmentSlots");
        }
    }
}
