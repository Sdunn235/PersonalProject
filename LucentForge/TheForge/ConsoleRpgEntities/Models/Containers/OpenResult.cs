namespace ConsoleRpgEntities.Models.Containers;

// W13 — return type for Player.OpenChest. Enum over bool because there are
// more than two outcomes the caller needs to handle distinctly.
public enum OpenResult
{
    Opened,
    Locked,
    Trapped,
    AlreadyOpen
}
