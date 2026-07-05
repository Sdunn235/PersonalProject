using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    /// <summary>
    /// W14 Phase C.2 — Door bidirectional + ILockable.
    ///
    /// HAND-EDITED away from the EF-scaffolded version, which mis-inferred
    /// rename targets by matching column TYPE alone:
    ///   SourceRoomId (int) → UnlockDC (int)        ❌ different semantic
    ///   Direction (int enum) → TrapDamage (int)    ❌ different semantic
    /// The data those columns held would have moved to wrong destinations.
    ///
    /// Correct intent:
    ///   - Rename SourceRoomId → RoomAId (preserve FK data; FK metadata
    ///     drops + recreates with the new name).
    ///   - Rename DestinationRoomId → RoomBId (same).
    ///   - Drop Direction column entirely (no longer in the model — the
    ///     bidirectional Door doesn't have an inherent direction; navigation
    ///     uses Door.GetOtherRoom(currentRoom) per GRASP information expert).
    ///   - Add the eight new ILockable + secret-door fields with sensible
    ///     defaults so existing Door rows stay valid.
    ///
    /// Default values (applied to all existing Door rows):
    ///   IsTrapped     = false      no traps until set
    ///   IsPickable    = true       most doors yield to lockpicks
    ///   RequiredKeyId = NULL       no specific key required
    ///   TrapDamage    = 0
    ///   TrapDisarmed  = false
    ///   UnlockDC      = 10         matches Door.cs default
    ///   IsSecret      = false
    ///   IsDiscovered  = true       non-secret doors are always visible
    ///
    /// No directional-pair dedupe needed — Doors table has no seed data,
    /// no rows currently exist (verified before scaffold).
    /// </summary>
    public partial class W14_DoorBidirectionalAndLockable : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // 1. Drop the existing FKs that referenced the soon-renamed columns.
            migrationBuilder.DropForeignKey(
                name: "FK_Doors_Containers_SourceRoomId",
                table: "Doors");

            migrationBuilder.DropForeignKey(
                name: "FK_Doors_Containers_DestinationRoomId",
                table: "Doors");

            migrationBuilder.DropIndex(
                name: "IX_Doors_SourceRoomId",
                table: "Doors");

            // (IX_Doors_DestinationRoomId stays; we'll rename it.)

            // 2. Drop Direction — bidirectional Door doesn't have one canonical
            //    direction; navigation flows through Door.GetOtherRoom(current).
            migrationBuilder.DropColumn(
                name: "Direction",
                table: "Doors");

            // 3. Rename FK columns (preserves data).
            migrationBuilder.RenameColumn(
                name: "SourceRoomId",
                table: "Doors",
                newName: "RoomAId");

            migrationBuilder.RenameColumn(
                name: "DestinationRoomId",
                table: "Doors",
                newName: "RoomBId");

            migrationBuilder.RenameIndex(
                name: "IX_Doors_DestinationRoomId",
                table: "Doors",
                newName: "IX_Doors_RoomBId");

            // 4. Add ILockable contract fields with sensible defaults.
            migrationBuilder.AddColumn<bool>(
                name: "IsTrapped",
                table: "Doors",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "IsPickable",
                table: "Doors",
                type: "bit",
                nullable: false,
                defaultValue: true);

            migrationBuilder.AddColumn<string>(
                name: "RequiredKeyId",
                table: "Doors",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TrapDamage",
                table: "Doors",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<bool>(
                name: "TrapDisarmed",
                table: "Doors",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<int>(
                name: "UnlockDC",
                table: "Doors",
                type: "int",
                nullable: false,
                defaultValue: 10);

            // 5. Add secret-door state.
            migrationBuilder.AddColumn<bool>(
                name: "IsSecret",
                table: "Doors",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "IsDiscovered",
                table: "Doors",
                type: "bit",
                nullable: false,
                defaultValue: true);

            // 6. Rebuild index + FKs with new column names.
            migrationBuilder.CreateIndex(
                name: "IX_Doors_RoomAId",
                table: "Doors",
                column: "RoomAId");

            migrationBuilder.AddForeignKey(
                name: "FK_Doors_Containers_RoomAId",
                table: "Doors",
                column: "RoomAId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Doors_Containers_RoomBId",
                table: "Doors",
                column: "RoomBId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Reverse: drop new FKs, drop new columns, rename Room A/B back
            // to Source/Destination, recreate Direction as int default 0.

            migrationBuilder.DropForeignKey(
                name: "FK_Doors_Containers_RoomAId",
                table: "Doors");

            migrationBuilder.DropForeignKey(
                name: "FK_Doors_Containers_RoomBId",
                table: "Doors");

            migrationBuilder.DropIndex(
                name: "IX_Doors_RoomAId",
                table: "Doors");

            migrationBuilder.DropColumn(name: "IsTrapped", table: "Doors");
            migrationBuilder.DropColumn(name: "IsPickable", table: "Doors");
            migrationBuilder.DropColumn(name: "RequiredKeyId", table: "Doors");
            migrationBuilder.DropColumn(name: "TrapDamage", table: "Doors");
            migrationBuilder.DropColumn(name: "TrapDisarmed", table: "Doors");
            migrationBuilder.DropColumn(name: "UnlockDC", table: "Doors");
            migrationBuilder.DropColumn(name: "IsSecret", table: "Doors");
            migrationBuilder.DropColumn(name: "IsDiscovered", table: "Doors");

            migrationBuilder.RenameColumn(
                name: "RoomAId",
                table: "Doors",
                newName: "SourceRoomId");

            migrationBuilder.RenameColumn(
                name: "RoomBId",
                table: "Doors",
                newName: "DestinationRoomId");

            migrationBuilder.RenameIndex(
                name: "IX_Doors_RoomBId",
                table: "Doors",
                newName: "IX_Doors_DestinationRoomId");

            migrationBuilder.AddColumn<int>(
                name: "Direction",
                table: "Doors",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.CreateIndex(
                name: "IX_Doors_SourceRoomId",
                table: "Doors",
                column: "SourceRoomId");

            migrationBuilder.AddForeignKey(
                name: "FK_Doors_Containers_SourceRoomId",
                table: "Doors",
                column: "SourceRoomId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Doors_Containers_DestinationRoomId",
                table: "Doors",
                column: "DestinationRoomId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }
    }
}
