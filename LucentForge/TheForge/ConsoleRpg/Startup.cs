using ConsoleRpg.Services;
using ConsoleRpg.UI;
using ConsoleRpgEntities.Data;

namespace ConsoleRpg;

public static class Startup
{
    public static IGameUi GameUi { get; private set; } = null!;
    public static GameEngine GameEngine { get; private set; } = null!;

    public static void Initialize()
    {
        GameUi = new ConsoleGameUi();
        IContext dbContext = new GameContext();
        GameEngine = new GameEngine(dbContext, GameUi);
        GameEngine.EnsureCharacterIntegrity();
    }
}
