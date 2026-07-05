namespace ConsoleRpgEntities.Helpers;

// Resolves a SQL script from the Migrations/Scripts folder so migrations
// can execute hand-written SQL (seed data, data fix-ups, etc.).
public static class MigrationHelper
{
    public static string ReadScript(string scriptName)
    {
        var baseDir = AppContext.BaseDirectory;
        var path = Path.Combine(baseDir, "Migrations", "Scripts", scriptName);

        if (!File.Exists(path))
            throw new FileNotFoundException(
                $"Migration script not found. Expected at: {path}. " +
                "Ensure the .sql file has CopyToOutputDirectory=PreserveNewest in ConsoleRpgEntities.csproj.");

        return File.ReadAllText(path);
    }
}
