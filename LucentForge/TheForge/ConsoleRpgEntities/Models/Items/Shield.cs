using System.ComponentModel.DataAnnotations.Schema;
using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Items;

// Shields are armor (count toward defense) but live in a hand slot rather than
// a body slot. They may be equipped to MainHand OR OffHand — the equip pipeline
// prefers OffHand and falls back to MainHand. Larger / two-handed shields are a
// future progression concept; today every Shield is one-handed.
public class Shield : Armor
{
    [NotMapped]
    public override SlotType? EligibleSlot => SlotType.OffHand;

    public static bool IsHandSlot(SlotType slot) =>
        slot == SlotType.MainHand || slot == SlotType.OffHand;
}
