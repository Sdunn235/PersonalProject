using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W14_RenameBpToBitPool : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.RenameColumn(
                name: "MaxBp",
                table: "Resources",
                newName: "MaxBitPool");

            migrationBuilder.RenameColumn(
                name: "Bp",
                table: "Resources",
                newName: "BitPool");

            migrationBuilder.RenameColumn(
                name: "BpCost",
                table: "Magics",
                newName: "BitPoolCost");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.RenameColumn(
                name: "MaxBitPool",
                table: "Resources",
                newName: "MaxBp");

            migrationBuilder.RenameColumn(
                name: "BitPool",
                table: "Resources",
                newName: "Bp");

            migrationBuilder.RenameColumn(
                name: "BitPoolCost",
                table: "Magics",
                newName: "BpCost");
        }
    }
}
