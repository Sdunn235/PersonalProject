using ConsoleRpgEntities.Helpers;
using Microsoft.EntityFrameworkCore.Migrations;

namespace ConsoleRpgEntities.Migrations;

// Migrations that need to run SQL from a .sql file inherit from this.
// Keeps the `migrationBuilder.Sql(File.ReadAllText(...))` ceremony in one place.
public abstract class BaseMigration : Migration
{
    protected static void RunSqlScript(MigrationBuilder migrationBuilder, string scriptName)
    {
        var sql = MigrationHelper.ReadScript(scriptName);
        migrationBuilder.Sql(sql);
    }
}
