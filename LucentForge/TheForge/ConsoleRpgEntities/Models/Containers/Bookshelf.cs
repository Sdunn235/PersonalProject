namespace ConsoleRpgEntities.Models.Containers;

// W15 Phase F2 — informational container. Holds Tomes (lore items).
// Follows the Chest pattern: lives in a Room via a nullable RoomId FK.
// Tome-only content is enforced at the UX layer, not the DB layer,
// so the TPH schema stays clean.
public class Bookshelf : Container
{
    public string Description { get; set; } = string.Empty;

    public int? RoomId { get; set; }
    public virtual Room? Room { get; set; }
}
