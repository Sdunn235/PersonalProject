using ConsoleRpgEntities.Models.Enums;
using ConsoleRpgEntities.Models.Items;

namespace ConsoleRpgEntities.Models.Containers;

public class Equipment : Container
{
    public int? OwnerCharacterId { get; set; }
    public virtual Character? Owner { get; set; }

    public virtual ICollection<EquipmentSlot> Slots { get; set; } = new List<EquipmentSlot>();

    // W13 invariant: a Container subclass enforces a rule its base doesn't know about.
    // Adapted to W12's slot-based design: an item is equippable iff it has an
    // EligibleSlot AND a matching slot exists and is empty.
    //
    // Shield exception: shields are valid in MainHand OR OffHand. Either being
    // empty satisfies the precondition.
    public bool CanEquip(Item item)
    {
        if (item is Shield)
        {
            return Slots.Any(s =>
                Shield.IsHandSlot(s.Slot) && s.EquippedItemId == null);
        }

        if (item.EligibleSlot is not SlotType slot) return false;
        var matching = Slots.FirstOrDefault(s => s.Slot == slot);
        return matching != null && matching.EquippedItemId == null;
    }
}
