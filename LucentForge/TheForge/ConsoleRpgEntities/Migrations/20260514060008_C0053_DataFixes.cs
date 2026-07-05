using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class C0053_DataFixes : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // ── Fix 1: Gobby HP reset ─────────────────────────────────────────────
            // Gobby was killed in a prior test session; his HP persisted as 0.
            // Restore to full so he appears alive in Goblin Camp.
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;
                DECLARE @GobbyId INT = (SELECT TOP 1 Id FROM Characters WHERE Name = N'Gobby' AND CharacterType = 'NPC');
                IF @GobbyId IS NOT NULL
                    UPDATE Resources SET Hp = MaxHp WHERE CharacterId = @GobbyId;
            ");

            // ── Fix 2: Grid coordinate redesign ──────────────────────────────────
            // Original layout had diagonal connections (Camp/Chapel diagonal from Path).
            // New layout makes all door connections orthogonal (H or V only):
            //
            //   col0     col1     col2
            //   row0:  Cellar   Inn
            //   row1:  Camp     Path    Chapel
            //   row2:                   Crypt
            //   row3:                   Vault
            //
            // Inn-Cellar: horizontal ✓   Inn-Path: vertical ✓
            // Path-Camp: horizontal ✓    Path-Chapel: horizontal ✓
            // Chapel-Crypt: vertical ✓   Crypt-Vault: vertical ✓
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                UPDATE Containers SET GridX = 0, GridY = 0
                WHERE ContainerType = 'Room' AND Name = N'Inn Cellar';

                UPDATE Containers SET GridX = 1, GridY = 0
                WHERE ContainerType = 'Room' AND Name = N'The Wayward Crow Inn';

                UPDATE Containers SET GridX = 0, GridY = 1
                WHERE ContainerType = 'Room' AND Name = N'Goblin Camp';

                UPDATE Containers SET GridX = 1, GridY = 1
                WHERE ContainerType = 'Room' AND Name = N'Thornwood Path';

                UPDATE Containers SET GridX = 2, GridY = 1
                WHERE ContainerType = 'Room' AND Name = N'Ruined Chapel';

                UPDATE Containers SET GridX = 2, GridY = 2
                WHERE ContainerType = 'Room' AND Name = N'Crypt Entrance';

                UPDATE Containers SET GridX = 2, GridY = 3
                WHERE ContainerType = 'Room' AND Name = N'The Sealed Vault';
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Restore original grid coordinates (diagonal layout) on rollback.
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                UPDATE Containers SET GridX = 0, GridY = 0
                WHERE ContainerType = 'Room' AND Name = N'Inn Cellar';

                UPDATE Containers SET GridX = 1, GridY = 0
                WHERE ContainerType = 'Room' AND Name = N'The Wayward Crow Inn';

                UPDATE Containers SET GridX = 0, GridY = 2
                WHERE ContainerType = 'Room' AND Name = N'Goblin Camp';

                UPDATE Containers SET GridX = 1, GridY = 1
                WHERE ContainerType = 'Room' AND Name = N'Thornwood Path';

                UPDATE Containers SET GridX = 2, GridY = 2
                WHERE ContainerType = 'Room' AND Name = N'Ruined Chapel';

                UPDATE Containers SET GridX = 2, GridY = 3
                WHERE ContainerType = 'Room' AND Name = N'Crypt Entrance';

                UPDATE Containers SET GridX = 2, GridY = 4
                WHERE ContainerType = 'Room' AND Name = N'The Sealed Vault';
            ");
        }
    }
}
