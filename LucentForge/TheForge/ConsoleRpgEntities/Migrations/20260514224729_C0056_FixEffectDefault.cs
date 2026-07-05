using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    /// W14_ConvertConsumableEffectToEnum dropped the DF_Items_EffectNew default constraint
    /// after renaming the column to Effect. This left Effect as int NOT NULL with no default,
    /// so EF TPH inserts of non-Consumable rows (Weapon/Armor) omit the column and SQL Server
    /// rejects the implicit NULL. Re-adding DEFAULT (0) = ConsumableEffect.None fixes it.
    public partial class C0056_FixEffectDefault : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(
                "ALTER TABLE [Items] ADD CONSTRAINT [DF_Items_Effect] DEFAULT (0) FOR [Effect];");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(
                "ALTER TABLE [Items] DROP CONSTRAINT [DF_Items_Effect];");
        }
    }
}
