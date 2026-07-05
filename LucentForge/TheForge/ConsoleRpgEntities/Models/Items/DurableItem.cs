namespace ConsoleRpgEntities.Models.Items;

// Abstract intermediate TPH layer: items that have durability (Weapons and Armor).
// Renamed from "Equipment" in W12 to avoid collision with the Equipment container subclass.
public abstract class DurableItem : Item
{
    public int Durability { get; set; }
}
