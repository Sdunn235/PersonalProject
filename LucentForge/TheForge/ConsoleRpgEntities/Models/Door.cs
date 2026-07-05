using System.ComponentModel.DataAnnotations.Schema;
using ConsoleRpgEntities.Models.Containers;
using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models;

/// <summary>
/// A passage between two rooms. After W14 Phase C.2, Door is bidirectional —
/// one row per passage, with two endpoints <see cref="RoomA"/> and <see cref="RoomB"/>.
/// The door doesn't have an inherent direction; navigation is relative to the
/// character's current room.
///
/// <para>
/// <b>Information expert (GRASP):</b> the Door knows its own endpoints, so it
/// answers "which room is on the other side from where I am now?" via
/// <see cref="GetOtherRoom"/>. <c>MovePlayer</c> hands the door the current
/// room and asks; the door does the lookup. No <c>Direction</c> enum needed.
/// </para>
///
/// <para>
/// <b>Liskov Substitution (Phase C.4):</b> Door implements <see cref="ILockable"/>,
/// the same interface chests use. After Phase C.4, <c>Character.TryUnlock</c>
/// takes <c>ILockable</c> instead of <c>Chest</c>, and the same algorithm
/// unlocks chests and doors with zero duplication.
/// </para>
///
/// <para>
/// Pre-Phase-C.2, Door was directional with <c>SourceRoomId</c>/<c>DestinationRoomId</c>/
/// <c>Direction</c> — two rows per bidirectional passage. The W14 refactor
/// renamed the FK columns, dropped <c>Direction</c>, added the full
/// <see cref="ILockable"/> field set plus secret-door state.
/// </para>
/// </summary>
public class Door : ILockable
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;

    /// <summary>One of the two rooms this door connects.</summary>
    public int RoomAId { get; set; }
    public virtual Room RoomA { get; set; } = null!;

    /// <summary>The other room this door connects.</summary>
    public int RoomBId { get; set; }
    public virtual Room RoomB { get; set; } = null!;

    // --- ILockable contract (shared with Chest and LockedJournal) ---
    // W15 Phase H: IsTrapped replaced by TrapTypes ([Flags] TrapType).
    public bool IsLocked { get; set; }
    public TrapType TrapTypes { get; set; }
    [NotMapped] public bool IsTrapped => TrapTypes != TrapType.None;
    public bool IsPickable { get; set; } = true;
    public string? RequiredKeyId { get; set; }
    public int TrapDamage { get; set; }
    public bool TrapDisarmed { get; set; }
    public int UnlockDC { get; set; } = 10;

    // --- W14 stretch goal: secret doors ---
    /// <summary>If true, the door is hidden until a successful inspection
    /// flips <see cref="IsDiscovered"/>. Per data integrity: the door row
    /// always exists with both endpoints set; only its visibility is gated.</summary>
    public bool IsSecret { get; set; }

    /// <summary>Whether a secret door has been found. Always true for non-secret
    /// doors. Combined with <see cref="IsSecret"/> via the helper below.</summary>
    public bool IsDiscovered { get; set; } = true;

    /// <summary>True when the door is visible in normal listings.
    /// Non-secret doors are always visible; secret doors are visible only
    /// after discovery.</summary>
    [NotMapped]
    public bool IsVisible => !IsSecret || IsDiscovered;

    /// <summary>
    /// Given the room a character is currently in, return the room on the
    /// other side of this door. Throws if <paramref name="currentRoom"/> is
    /// not one of this door's endpoints — that's an invariant violation,
    /// not a runtime case to handle gracefully.
    /// </summary>
    public Room GetOtherRoom(Room currentRoom)
    {
        if (currentRoom.Id == RoomAId) return RoomB;
        if (currentRoom.Id == RoomBId) return RoomA;
        throw new InvalidOperationException(
            $"Door {Id} '{Name}' connects rooms {RoomAId} and {RoomBId}, " +
            $"but was asked for the 'other side' of room {currentRoom.Id}.");
    }
}
