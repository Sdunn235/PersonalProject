namespace ConsoleRpgEntities.Models.Items;

// W15 Phase F2 — lore item. Readable from a Bookshelf in a Room.
// LoreText surfaces world-building content (Bits/Bytes magic, Gobby's tribe
// account, world cosmology). Reading requires no key — knowledge is free.
public class Tome : Item
{
    public string LoreText { get; set; } = string.Empty;
}
