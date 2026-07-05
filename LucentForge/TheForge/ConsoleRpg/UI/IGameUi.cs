namespace ConsoleRpg.UI;

public interface IGameUi
{
    void DisplayWelcome();
    string GetModeChoice();
    string GetMenuChoice();
    string GetMenuChoice(string? activeLabel);
    void DisplayMessage(string message);
    void PauseAndClear();
}
