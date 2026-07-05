using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    public partial class W13_SeedWorldContent : BaseMigration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Seeds chests in rooms, Grubnak the Goblin + his MonsterLoot,
            // the Lockpicking Skill row + Elara's CharacterSkill proficiency,
            // and the items inside both containers.
            RunSqlScript(migrationBuilder, "W13_SeedWorldContent.sql");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            RunSqlScript(migrationBuilder, "W13_SeedWorldContent.rollback.sql");
        }
    }
}
