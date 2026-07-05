namespace ConsoleRpgEntities.Models.Enums;

// W15 Phase H — [Flags] enum for equipment slot eligibility.
// Teacher earlier hint: "EquipmentSlot eligibility (head/body/legs) is the
// canonical [Flags] candidate." With power-of-2 values, an item can be
// eligible for multiple slots — e.g., a dagger can equip MainHand | OffHand.
// The bitwise check in Character.PickSlotFor() replaces the old equality check.
//
// Migration W15_FlagsAndTrapTypes converts old sequential DB values (0=MainHand,
// 1=OffHand, ...) to the new power-of-2 values in EquipmentSlots.Slot.
[Flags]
public enum SlotType
{
    None     = 0,
    MainHand = 1 << 0,
    OffHand  = 1 << 1,
    Head     = 1 << 2,
    Chest    = 1 << 3,
    Legs     = 1 << 4,
    Feet     = 1 << 5,
    Hands    = 1 << 6,
    AnyHand  = MainHand | OffHand,
}
