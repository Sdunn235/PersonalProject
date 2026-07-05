using System.ComponentModel.DataAnnotations.Schema;
using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Containers;

// W13 — A Container subclass that adds lock/trap/pick state.
// Two interfaces: IItemContainer (via Container) AND ILockable (state-based gating).
// Lives in a Room (nullable so chests can be created before placement).
//
// W15 Phase H: IsTrapped (bool) replaced by TrapTypes ([Flags] TrapType).
// IsTrapped is now computed — true when TrapTypes != None.
public class Chest : Container, ILockable
{
    public string Description { get; set; } = string.Empty;

    // ILockable
    public bool IsLocked { get; set; }
    public TrapType TrapTypes { get; set; }
    [NotMapped] public bool IsTrapped => TrapTypes != TrapType.None;
    public bool IsPickable { get; set; } = true;
    public string? RequiredKeyId { get; set; }
    public int TrapDamage { get; set; }
    public bool TrapDisarmed { get; set; }

    // LucentForge integration — DC for the lockpick skill check
    public int UnlockDC { get; set; }

    public int? RoomId { get; set; }
    public virtual Room? Room { get; set; }
}
