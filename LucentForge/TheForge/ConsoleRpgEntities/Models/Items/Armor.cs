using System.ComponentModel.DataAnnotations.Schema;
using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Items;

public class Armor : DurableItem
{
    public int DefenseRating { get; set; }
    public ArmorWeight WeightClass { get; set; }
    public BodySlot Slot { get; set; }

    [NotMapped]
    public override SlotType? EligibleSlot => Slot switch
    {
        BodySlot.Head => SlotType.Head,
        BodySlot.Chest => SlotType.Chest,
        BodySlot.Legs => SlotType.Legs,
        BodySlot.Feet => SlotType.Feet,
        BodySlot.Hands => SlotType.Hands,
        _ => null
    };
}
