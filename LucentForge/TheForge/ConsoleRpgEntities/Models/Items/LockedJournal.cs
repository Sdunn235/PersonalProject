using System.ComponentModel.DataAnnotations.Schema;
using ConsoleRpgEntities.Models.Containers;
using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Items;

// W15 Phase F1 — LSP payoff: a LockedJournal is an Item that also implements
// ILockable. Character.TryUnlock(ILockable, Item) opens it with zero changes
// to the unlock algorithm — same code path as Chest and Door.
//
// W15 Phase H: IsTrapped replaced by TrapTypes ([Flags] TrapType).
public class LockedJournal : Item, ILockable
{
    // Journal-specific content. Readable only when IsLocked == false.
    public string Content { get; set; } = string.Empty;

    // ILockable — same interface as Chest and Door. EF maps these as
    // nullable columns on the Items table (TPH: all items share one table).
    public bool IsLocked { get; set; }
    public TrapType TrapTypes { get; set; }
    [NotMapped] public bool IsTrapped => TrapTypes != TrapType.None;
    public bool IsPickable { get; set; }
    public string? RequiredKeyId { get; set; }
    public int TrapDamage { get; set; }
    public bool TrapDisarmed { get; set; }
    public int UnlockDC { get; set; }
}
