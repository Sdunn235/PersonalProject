using System.ComponentModel.DataAnnotations.Schema;
using ConsoleRpgEntities.Models.Containers;
using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Items;

public abstract class Item
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public int Value { get; set; }
    public int Weight { get; set; }
    // W14 Phase C.3-lite — single-column key-ness predicate. Was a 3-state
    // encoding (IsKeyItem bool + nullable KeyId); collapsed to 2 states on
    // KeyId alone:
    //   null              → not a key (Weapon/Armor/Shield/Consumable)
    //   LockpickKeyId     → generic lockpick (consumed on use against pickable locks)
    //   anything else     → specific key matching a lock's RequiredKeyId
    public const string LockpickKeyId = "lockpick";
    public string? KeyId { get; set; }

    // W12: every item lives in at most one container. Nullable so items can float
    // (e.g., orphaned during a move, or dropped in a room before W14 rooms-as-containers).
    public int? ContainerId { get; set; }
    public virtual Container? Container { get; set; }

    // W13: derived equip-slot eligibility. Consumables and key items return
    // null (not equippable). Weapon/Armor override. NotMapped — derived.
    [NotMapped]
    public virtual SlotType? EligibleSlot => null;
}
