using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W13_AddChestsAndMonsterLoot : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "KeyId",
                table: "Items",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Description",
                table: "Containers",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsLocked",
                table: "Containers",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsLooted",
                table: "Containers",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsPickable",
                table: "Containers",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsTrapped",
                table: "Containers",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "RequiredKeyId",
                table: "Containers",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "RoomId",
                table: "Containers",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TrapDamage",
                table: "Containers",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "TrapDisarmed",
                table: "Containers",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "UnlockDC",
                table: "Containers",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "LootId",
                table: "Characters",
                type: "int",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Containers_RoomId",
                table: "Containers",
                column: "RoomId");

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

            migrationBuilder.AddForeignKey(
                name: "FK_Containers_Rooms_RoomId",
                table: "Containers",
                column: "RoomId",
                principalTable: "Rooms",
                principalColumn: "Id",
                onDelete: ReferentialAction.SetNull);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Characters_Containers_LootId",
                table: "Characters");

            migrationBuilder.DropForeignKey(
                name: "FK_Containers_Rooms_RoomId",
                table: "Containers");

            migrationBuilder.DropIndex(
                name: "IX_Containers_RoomId",
                table: "Containers");

            migrationBuilder.DropIndex(
                name: "IX_Characters_LootId",
                table: "Characters");

            migrationBuilder.DropColumn(
                name: "KeyId",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "Description",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "IsLocked",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "IsLooted",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "IsPickable",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "IsTrapped",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "RequiredKeyId",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "RoomId",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "TrapDamage",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "TrapDisarmed",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "UnlockDC",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "LootId",
                table: "Characters");
        }
    }
}
