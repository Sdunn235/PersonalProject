using ConsoleRpg;

Startup.Initialize();
Startup.GameUi.DisplayWelcome();

bool running = true;
while (running)
{
    string mode = Startup.GameUi.GetModeChoice();

    if (mode == "0")
    {
        running = false;
        break;
    }

    if (mode == "p")
    {
        Startup.GameEngine.SelectCharacter();
        if (Startup.GameEngine.HasActiveCharacter)
            Startup.GameEngine.PlayerLoop();
    }
    else if (mode == "a")
    {
        bool adminRunning = true;
        while (adminRunning)
        {
            string choice = Startup.GameUi.GetMenuChoice(Startup.GameEngine.ActiveCharacterLabel);
            switch (choice)
            {
                case "1": Startup.GameEngine.CharactersSubmenu(); break;
                case "2": Startup.GameEngine.ItemsSubmenu(); break;
                case "3": Startup.GameEngine.RoomsSubmenu(); break;
                case "4": Startup.GameEngine.SkillsSubmenu(); break;
                case "5": Startup.GameEngine.AbilitiesSubmenu(); break;
                case "6": Startup.GameEngine.MagicSubmenu(); break;
                case "7": Startup.GameEngine.InventoryMenu(); break;
                case "8": Startup.GameEngine.ChestMenu(); break;
                case "9": Startup.GameEngine.BookshelfMenu(); break;
                case "q": Startup.GameEngine.QueriesMenu(); break;
                case "r": Startup.GameEngine.AdminResetWorld(); break;
                case "0":
                    adminRunning = false;
                    break;
                default:
                    Startup.GameUi.DisplayMessage("Invalid choice. Please try again.");
                    break;
            }

            if (adminRunning)
                Startup.GameUi.PauseAndClear();
        }
    }
}
