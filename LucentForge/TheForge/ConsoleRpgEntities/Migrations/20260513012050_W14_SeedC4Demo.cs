using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    /// <summary>
    /// W14 Phase C.4 demo seed. The W12/W13 seed shipped a 2-room world
    /// (Antechamber + Vault) with a single unlocked, untrapped, non-secret
    /// door between them — fine for chest demos, but no door in the world
    /// ever exercised the door-side of C.4's LSP refactor. This migration
    /// plants the minimum demo content so every C.4 path is verifiable
    /// from a fresh clone.
    ///
    /// Adds:
    ///   * 1 new room: Hidden Alcove (Container row, ContainerType='Room')
    ///   * 1 new door: Hidden Tapestry (Antechamber ↔ Hidden Alcove,
    ///     IsSecret=1, IsDiscovered=0) — exercises InspectForSecretDoors
    ///
    /// Modifies the existing Solid Oak Door (Antechamber ↔ Vault) in place
    /// to:
    ///   * IsLocked   = 1, IsPickable = 1, UnlockDC = 10  (lockpick path)
    ///   * IsTrapped  = 1, TrapDamage  = 8                 (trap path)
    ///
    /// This single door exercises every chest-shape behavior on a door:
    /// lockpick unlock, trap fire on first traverse, DisarmTrap before
    /// traverse.
    ///
    /// Idempotent — inserts are guarded by name-keyed lookups. Down
    /// restores the pre-C.4 state of the Oak Door and removes the new
    /// room + door.
    /// </summary>
    public partial class W14_SeedC4Demo : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                -- 1. New room: Hidden Alcove (Container TPH row).
                --    Room_Description carries the prose (EF auto-renamed to
                --    avoid colliding with Chest.Description on the shared
                --    Containers table).
                IF NOT EXISTS (SELECT 1 FROM Containers WHERE ContainerType = 'Room' AND Name = N'Hidden Alcove')
                    INSERT INTO Containers (Name, ContainerType, Room_Description)
                    VALUES (N'Hidden Alcove', 'Room',
                            N'A dust-choked alcove behind a tapestry. Cobwebs hang undisturbed in the corners.');

                DECLARE @AntechamberId  INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Room' AND Name = N'Antechamber');
                DECLARE @HiddenAlcoveId INT = (SELECT TOP 1 Id FROM Containers WHERE ContainerType = 'Room' AND Name = N'Hidden Alcove');

                -- 2. New secret door: Hidden Tapestry. Not locked, not trapped —
                --    the secret-door discovery flow is what we exercise here.
                --    Once InspectForSecretDoors flips IsDiscovered, traversal
                --    is free.
                IF NOT EXISTS (SELECT 1 FROM Doors WHERE Name = N'Hidden Tapestry')
                    INSERT INTO Doors (Name, Description, RoomAId, RoomBId,
                                       IsLocked, IsTrapped, IsPickable, RequiredKeyId,
                                       TrapDamage, TrapDisarmed, UnlockDC,
                                       IsSecret, IsDiscovered)
                    VALUES (N'Hidden Tapestry',
                            N'A faded wall tapestry. Behind it, a passage you would not have found unless you looked.',
                            @AntechamberId, @HiddenAlcoveId,
                            0, 0, 1, NULL,
                            0, 0, 10,
                            1, 0);

                -- 3. Upgrade the existing Solid Oak Door in place: lock it,
                --    make it pickable, trap it. One door, three C.4 demo paths.
                UPDATE Doors
                   SET IsLocked   = 1,
                       IsPickable = 1,
                       UnlockDC   = 10,
                       IsTrapped  = 1,
                       TrapDamage = 8
                 WHERE Name = N'Solid Oak Door';
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Best-effort, dev-only rollback.
            //   1. Revert the Oak Door to its pre-C.4 baseline (unlocked,
            //      untrapped). IsPickable=1 stays true — that was its state
            //      pre-C.4 too, so leaving it alone is the honest rollback.
            //   2. Drop the new secret door.
            //   3. Drop the new Hidden Alcove room. No FK orphans expected —
            //      nothing else is seeded into it by Up.
            migrationBuilder.Sql(@"
                SET NOCOUNT ON;

                UPDATE Doors
                   SET IsLocked     = 0,
                       IsTrapped    = 0,
                       TrapDamage   = 0,
                       TrapDisarmed = 0,
                       UnlockDC     = 10
                 WHERE Name = N'Solid Oak Door';

                DELETE FROM Doors WHERE Name = N'Hidden Tapestry';

                DELETE FROM Containers
                 WHERE ContainerType = 'Room' AND Name = N'Hidden Alcove';
            ");
        }
    }
}
