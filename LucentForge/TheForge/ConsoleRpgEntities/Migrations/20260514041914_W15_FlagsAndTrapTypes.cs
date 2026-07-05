using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W15_FlagsAndTrapTypes : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Phase 1: Add TrapTypes columns before dropping IsTrapped
            // so we can migrate existing trap state (IsTrapped=1 → Mechanical=1).

            migrationBuilder.AddColumn<int>(
                name: "TrapTypes",
                table: "Items",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TrapTypes",
                table: "Doors",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "TrapTypes",
                table: "Containers",
                type: "int",
                nullable: true);

            // Phase 2: Migrate IsTrapped bool → TrapType.Mechanical (1) or None (0).
            // LockedJournal rows live in Items; Chest rows live in Containers.

            migrationBuilder.Sql(@"
                UPDATE Items
                SET TrapTypes = CASE WHEN IsTrapped = 1 THEN 1 ELSE 0 END
                WHERE IsTrapped IS NOT NULL;
            ");

            migrationBuilder.Sql(@"
                UPDATE Doors
                SET TrapTypes = CASE WHEN IsTrapped = 1 THEN 1 ELSE 0 END;
            ");

            migrationBuilder.Sql(@"
                UPDATE Containers
                SET TrapTypes = CASE WHEN IsTrapped = 1 THEN 1 ELSE 0 END
                WHERE IsTrapped IS NOT NULL;
            ");

            // Phase 3: Drop the old bool columns now that data is preserved.

            migrationBuilder.DropColumn(
                name: "IsTrapped",
                table: "Items");

            migrationBuilder.DropColumn(
                name: "IsTrapped",
                table: "Doors");

            migrationBuilder.DropColumn(
                name: "IsTrapped",
                table: "Containers");

            // Phase 4: Convert EquipmentSlots.Slot from sequential ints (0–6)
            // to [Flags] power-of-2 values so bitwise & checks work correctly.
            // Old: 0=MainHand,1=OffHand,2=Head,3=Chest,4=Legs,5=Feet,6=Hands
            // New: MainHand=1,OffHand=2,Head=4,Chest=8,Legs=16,Feet=32,Hands=64

            migrationBuilder.Sql(@"
                UPDATE EquipmentSlots
                SET Slot = CASE Slot
                    WHEN 0 THEN 1
                    WHEN 1 THEN 2
                    WHEN 2 THEN 4
                    WHEN 3 THEN 8
                    WHEN 4 THEN 16
                    WHEN 5 THEN 32
                    WHEN 6 THEN 64
                    ELSE Slot
                END;
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Reverse EquipmentSlots.Slot power-of-2 → sequential.
            migrationBuilder.Sql(@"
                UPDATE EquipmentSlots
                SET Slot = CASE Slot
                    WHEN 1  THEN 0
                    WHEN 2  THEN 1
                    WHEN 4  THEN 2
                    WHEN 8  THEN 3
                    WHEN 16 THEN 4
                    WHEN 32 THEN 5
                    WHEN 64 THEN 6
                    ELSE Slot
                END;
            ");

            // Restore IsTrapped columns.
            migrationBuilder.AddColumn<bool>(
                name: "IsTrapped",
                table: "Items",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsTrapped",
                table: "Doors",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "IsTrapped",
                table: "Containers",
                type: "bit",
                nullable: true);

            // Copy TrapTypes !=0 back to IsTrapped=1.
            migrationBuilder.Sql(@"
                UPDATE Items SET IsTrapped = CASE WHEN TrapTypes > 0 THEN 1 ELSE 0 END
                WHERE TrapTypes IS NOT NULL;
            ");
            migrationBuilder.Sql(@"
                UPDATE Doors SET IsTrapped = CASE WHEN TrapTypes > 0 THEN 1 ELSE 0 END;
            ");
            migrationBuilder.Sql(@"
                UPDATE Containers SET IsTrapped = CASE WHEN TrapTypes > 0 THEN 1 ELSE 0 END
                WHERE TrapTypes IS NOT NULL;
            ");

            // Drop TrapTypes columns.
            migrationBuilder.DropColumn(name: "TrapTypes", table: "Items");
            migrationBuilder.DropColumn(name: "TrapTypes", table: "Doors");
            migrationBuilder.DropColumn(name: "TrapTypes", table: "Containers");
        }
    }
}
