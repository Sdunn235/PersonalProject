using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Containers;

// W13 — Interface Segregation: anything that can be locked, trapped, or picked.
// Implemented by Chest, Door, and LockedJournal.
//
// W15 Phase H — IsTrapped (single bool) replaced by TrapTypes ([Flags] enum).
// A lock can now have multiple trap mechanisms simultaneously — e.g., Mechanical | Poison.
// IsTrapped is now a computed default implementation: true when TrapTypes != None.
// All callers (TryUnlock, DisarmTrap) that reference ILockable.IsTrapped still work.
public interface ILockable
{
    bool IsLocked { get; set; }
    TrapType TrapTypes { get; set; }
    bool IsTrapped => TrapTypes != TrapType.None;
    bool IsPickable { get; set; }
    string? RequiredKeyId { get; set; }
    int TrapDamage { get; set; }
    bool TrapDisarmed { get; set; }
    int UnlockDC { get; set; }
}
