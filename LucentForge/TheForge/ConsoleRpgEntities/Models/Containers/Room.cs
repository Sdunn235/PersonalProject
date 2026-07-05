namespace ConsoleRpgEntities.Models.Containers;

/// <summary>
/// A navigable space in the world. Promoted to a 5th <see cref="Container"/>
/// TPH subclass in W14 Phase C — items on the floor of a room are now stored
/// in the same Items table as items in backpacks, chests, equipment slots, or
/// monster loot, all addressed via <c>Item.ContainerId</c>.
///
/// <para>
/// What Room inherits from <see cref="Container"/>:
/// <list type="bullet">
///   <item><description><c>Id</c> — the canonical room id; FKs from Character.RoomId, Door.RoomAId/RoomBId, Chest.RoomId all point at this.</description></item>
///   <item><description><c>Name</c> — the room's display name (e.g., "Entrance Hall").</description></item>
///   <item><description><c>ItemsCollection</c> — items on the floor of this room.</description></item>
///   <item><description><c>AddItem</c> / <c>RemoveItem</c> — drop/pickup semantics (ContainerId = room.Id, or null on pickup).</description></item>
/// </list>
/// </para>
///
/// <para>
/// What Room owns directly: <see cref="Description"/> (room-specific flavor text;
/// EF disambiguates this from <c>Chest.Description</c> via TPH-shadow column
/// <c>Room_Description</c>), <see cref="Characters"/> (who is here), and
/// <see cref="Doors"/> (passages to neighbors — bidirectional after Phase C.2).
/// </para>
///
/// <para>
/// Pre-Phase-C, Room was a standalone entity in its own <c>Rooms</c> table.
/// The Phase C.1 migration moved each Room row into <c>Containers</c> with
/// <c>ContainerType='Room'</c>, captured an old→new id mapping, repointed
/// the Character.RoomId / Door.SourceRoomId / Door.DestinationRoomId / Chest.RoomId
/// FKs through that mapping, and dropped the standalone <c>Rooms</c> table.
/// </para>
/// </summary>
public class Room : Container
{
    /// <summary>Flavor text describing the room. Stored as TPH-shadow column
    /// <c>Room_Description</c> to avoid colliding with <c>Chest.Description</c>.</summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>Grid column for the mini-map. Null for rooms not yet placed on the grid.</summary>
    public int? GridX { get; set; }

    /// <summary>Grid row for the mini-map. Null for rooms not yet placed on the grid.</summary>
    public int? GridY { get; set; }

    /// <summary>Characters currently located in this room. Maintained via
    /// <c>Character.RoomId</c> back-reference.</summary>
    public virtual ICollection<Character> Characters { get; set; } = new List<Character>();

    /// <summary>Doors where this room is the A endpoint. See also
    /// <see cref="DoorsAsB"/>. EF can't map a single collection to two FKs,
    /// so the relationship is split — consumers usually want
    /// <see cref="AllDoors"/> instead.</summary>
    public virtual ICollection<Door> DoorsAsA { get; set; } = new List<Door>();

    /// <summary>Doors where this room is the B endpoint. See also
    /// <see cref="DoorsAsA"/>.</summary>
    public virtual ICollection<Door> DoorsAsB { get; set; } = new List<Door>();

    /// <summary>All doors connected to this room, regardless of which side.
    /// Use this in display and navigation; the A/B distinction is only
    /// meaningful for the FK relationship.</summary>
    [System.ComponentModel.DataAnnotations.Schema.NotMapped]
    public IEnumerable<Door> AllDoors => DoorsAsA.Concat(DoorsAsB);
}
