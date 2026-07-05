using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W15_AddGridCoordinates : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "GridX",
                table: "Containers",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "GridY",
                table: "Containers",
                type: "int",
                nullable: true);

            // Seed grid positions for the 5 known rooms.
            // Layout (X=col left-to-right, Y=row top-to-bottom):
            //         col0          col1           col2
            // row0             Forest Edge
            // row1  Anc. Lib   Antechamber   Hidden Alcove
            // row2             Vault
            migrationBuilder.Sql(@"
                UPDATE Containers SET GridX = 1, GridY = 0
                WHERE ContainerType = 'Room' AND Name = N'Forest Edge';

                UPDATE Containers SET GridX = 0, GridY = 1
                WHERE ContainerType = 'Room' AND Name = N'Ancient Library';

                UPDATE Containers SET GridX = 1, GridY = 1
                WHERE ContainerType = 'Room' AND Name = N'Antechamber';

                UPDATE Containers SET GridX = 2, GridY = 1
                WHERE ContainerType = 'Room' AND Name = N'Hidden Alcove';

                UPDATE Containers SET GridX = 1, GridY = 2
                WHERE ContainerType = 'Room' AND Name = N'Vault';
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "GridX",
                table: "Containers");

            migrationBuilder.DropColumn(
                name: "GridY",
                table: "Containers");
        }
    }
}
