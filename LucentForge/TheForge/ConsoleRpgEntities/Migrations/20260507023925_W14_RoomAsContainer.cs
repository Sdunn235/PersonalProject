using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    /// <summary>
    /// W14 Phase C.1 — promote Room from a standalone entity to a 5th
    /// Container TPH subclass.
    ///
    /// HAND-EDITED away from the EF-scaffolded version (which would have
    /// DropTable'd Rooms outright, losing all room data and orphaning every
    /// Character.RoomId / Door FK / Chest.RoomId reference).
    ///
    /// Data preservation strategy:
    ///   1. Add Room_Description shadow column to Containers.
    ///   2. Insert each existing Rooms row into Containers as a Room TPH
    ///      discriminator, capturing the old→new id mapping in a #temp
    ///      table via OUTPUT clause on a forced-INSERT MERGE.
    ///   3. Drop the four foreign keys that referenced Rooms.
    ///   4. Update Character.RoomId, Containers.RoomId (Chest's FK to its
    ///      home room), Doors.SourceRoomId, Doors.DestinationRoomId via the
    ///      mapping — every old Room id is replaced by its new Container id.
    ///   5. Drop the now-orphaned Rooms table.
    ///   6. Add the new foreign keys pointing at Containers.
    ///
    /// FK cascade choice: Character.RoomId and Container.RoomId (Chest's
    /// room FK) use NoAction. Combining two SetNull cascades on a
    /// self-referential Containers table triggers SQL Server's "multiple
    /// cascade paths" guard; cleanup is application-side via
    /// GameEngine.RemoveRoom (nulls Character.RoomId, removes Doors,
    /// nulls Chest.RoomId before the actual delete).
    ///
    /// Mapping joins on Name. Antechamber and Vault are the only seeded
    /// rooms and both have unique names; the strategy uses MERGE+OUTPUT
    /// to capture identity-mapped pairs atomically rather than join-on-name
    /// post-hoc.
    /// </summary>
    public partial class W14_RoomAsContainer : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // 1. Shadow column for Room.Description (avoids collision with
            //    Chest.Description; EF disambiguates via the Room_ prefix).
            migrationBuilder.AddColumn<string>(
                name: "Room_Description",
                table: "Containers",
                type: "nvarchar(max)",
                nullable: true);

            // 2. Migrate Rooms → Containers + build old→new id mapping.
            //    The MERGE...ON 1=0 trick forces an INSERT for every row in
            //    the source while letting OUTPUT see both the source's old
            //    Id and the inserted Container's new Id in one statement.
            migrationBuilder.Sql(@"
                CREATE TABLE #RoomMap (OldId int PRIMARY KEY, NewId int NOT NULL);

                MERGE INTO [Containers] AS tgt
                USING [Rooms] AS src
                    ON 1 = 0
                WHEN NOT MATCHED THEN
                    INSERT (ContainerType, Name, Room_Description)
                    VALUES ('Room', src.Name, src.Description)
                OUTPUT src.Id, inserted.Id INTO #RoomMap (OldId, NewId);
            ");

            // 3. Drop the four FKs that referenced Rooms.
            migrationBuilder.DropForeignKey(
                name: "FK_Characters_Rooms_RoomId",
                table: "Characters");

            migrationBuilder.DropForeignKey(
                name: "FK_Containers_Rooms_RoomId",
                table: "Containers");

            migrationBuilder.DropForeignKey(
                name: "FK_Doors_Rooms_DestinationRoomId",
                table: "Doors");

            migrationBuilder.DropForeignKey(
                name: "FK_Doors_Rooms_SourceRoomId",
                table: "Doors");

            // 4. Repoint every FK column via the mapping. This must run
            //    after the FKs are dropped (else the constraints would
            //    fire on every UPDATE) and before the new FKs are added
            //    (else the new constraints would fire here).
            migrationBuilder.Sql(@"
                UPDATE c SET c.RoomId = m.NewId
                FROM [Characters] c
                INNER JOIN #RoomMap m ON c.RoomId = m.OldId;

                UPDATE c SET c.RoomId = m.NewId
                FROM [Containers] c
                INNER JOIN #RoomMap m ON c.RoomId = m.OldId
                WHERE c.ContainerType = 'Chest';

                UPDATE d SET d.SourceRoomId = m.NewId
                FROM [Doors] d
                INNER JOIN #RoomMap m ON d.SourceRoomId = m.OldId;

                UPDATE d SET d.DestinationRoomId = m.NewId
                FROM [Doors] d
                INNER JOIN #RoomMap m ON d.DestinationRoomId = m.OldId;

                DROP TABLE #RoomMap;
            ");

            // 5. Drop the now-empty Rooms table.
            migrationBuilder.DropTable(
                name: "Rooms");

            // 6. Add new FKs pointing at Containers.
            //    Character.RoomId + Container.RoomId use NoAction (default,
            //    no onDelete arg). Doors keep Restrict (already NoAction-
            //    equivalent) for explicit signal.
            migrationBuilder.AddForeignKey(
                name: "FK_Characters_Containers_RoomId",
                table: "Characters",
                column: "RoomId",
                principalTable: "Containers",
                principalColumn: "Id");

            migrationBuilder.AddForeignKey(
                name: "FK_Containers_Containers_RoomId",
                table: "Containers",
                column: "RoomId",
                principalTable: "Containers",
                principalColumn: "Id");

            migrationBuilder.AddForeignKey(
                name: "FK_Doors_Containers_DestinationRoomId",
                table: "Doors",
                column: "DestinationRoomId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Doors_Containers_SourceRoomId",
                table: "Doors",
                column: "SourceRoomId",
                principalTable: "Containers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Reverse: recreate Rooms table, migrate Room rows back out of
            // Containers, repoint FKs to Rooms, restore old SetNull FKs.
            // Best-effort dev rollback.

            migrationBuilder.DropForeignKey(
                name: "FK_Characters_Containers_RoomId",
                table: "Characters");

            migrationBuilder.DropForeignKey(
                name: "FK_Containers_Containers_RoomId",
                table: "Containers");

            migrationBuilder.DropForeignKey(
                name: "FK_Doors_Containers_DestinationRoomId",
                table: "Doors");

            migrationBuilder.DropForeignKey(
                name: "FK_Doors_Containers_SourceRoomId",
                table: "Doors");

            migrationBuilder.CreateTable(
                name: "Rooms",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Rooms", x => x.Id);
                });

            migrationBuilder.Sql(@"
                CREATE TABLE #RoomMap (OldId int PRIMARY KEY, NewId int NOT NULL);

                MERGE INTO [Rooms] AS tgt
                USING (SELECT Id, Name, Room_Description FROM [Containers] WHERE ContainerType = 'Room') AS src
                    ON 1 = 0
                WHEN NOT MATCHED THEN
                    INSERT (Name, Description)
                    VALUES (src.Name, ISNULL(src.Room_Description, ''))
                OUTPUT src.Id, inserted.Id INTO #RoomMap (OldId, NewId);

                UPDATE c SET c.RoomId = m.NewId
                FROM [Characters] c
                INNER JOIN #RoomMap m ON c.RoomId = m.OldId;

                UPDATE c SET c.RoomId = m.NewId
                FROM [Containers] c
                INNER JOIN #RoomMap m ON c.RoomId = m.OldId
                WHERE c.ContainerType = 'Chest';

                UPDATE d SET d.SourceRoomId = m.NewId
                FROM [Doors] d
                INNER JOIN #RoomMap m ON d.SourceRoomId = m.OldId;

                UPDATE d SET d.DestinationRoomId = m.NewId
                FROM [Doors] d
                INNER JOIN #RoomMap m ON d.DestinationRoomId = m.OldId;

                DELETE FROM [Containers] WHERE ContainerType = 'Room';

                DROP TABLE #RoomMap;
            ");

            migrationBuilder.DropColumn(
                name: "Room_Description",
                table: "Containers");

            migrationBuilder.AddForeignKey(
                name: "FK_Characters_Rooms_RoomId",
                table: "Characters",
                column: "RoomId",
                principalTable: "Rooms",
                principalColumn: "Id",
                onDelete: ReferentialAction.SetNull);

            migrationBuilder.AddForeignKey(
                name: "FK_Containers_Rooms_RoomId",
                table: "Containers",
                column: "RoomId",
                principalTable: "Rooms",
                principalColumn: "Id",
                onDelete: ReferentialAction.SetNull);

            migrationBuilder.AddForeignKey(
                name: "FK_Doors_Rooms_DestinationRoomId",
                table: "Doors",
                column: "DestinationRoomId",
                principalTable: "Rooms",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Doors_Rooms_SourceRoomId",
                table: "Doors",
                column: "SourceRoomId",
                principalTable: "Rooms",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }
    }
}
