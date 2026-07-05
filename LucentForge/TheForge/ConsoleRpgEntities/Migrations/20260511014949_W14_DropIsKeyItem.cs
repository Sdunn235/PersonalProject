using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    /// <summary>
    /// W14 Phase C.3-lite — drops the redundant Item.IsKeyItem boolean. The
    /// "is this a key" predicate is now Item.KeyId != null. To make that
    /// predicate honest, lockpick rows (which lived as IsKeyItem=1 / KeyId=NULL)
    /// are first backfilled to KeyId = 'lockpick' (the sentinel exposed as
    /// Item.LockpickKeyId in code).
    ///
    /// Before this migration — 3 states encoded in 2 columns:
    ///   IsKeyItem=0, KeyId=*           → not a key
    ///   IsKeyItem=1, KeyId=NULL        → lockpick (generic, consumed on use)
    ///   IsKeyItem=1, KeyId='cellar-key' → specific key
    ///
    /// After — 2 states on 1 column:
    ///   KeyId IS NULL                  → not a key
    ///   KeyId = 'lockpick'             → lockpick
    ///   KeyId = anything else          → specific key
    ///
    /// HAND-EDITED away from the scaffold's bare DropColumn(IsKeyItem) — the
    /// scaffold would have orphaned every lockpick row (KeyId NULL after the
    /// IsKeyItem signal disappears = "not a key" by the new predicate).
    /// The UPDATE must run BEFORE the column drops.
    /// </summary>
    public partial class W14_DropIsKeyItem : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // 1. Convert lockpick rows in place — they were IsKeyItem=1 with
            //    a NULL KeyId. Move their key-ness onto the KeyId column.
            migrationBuilder.Sql(@"
                UPDATE [Items]
                SET [KeyId] = N'lockpick'
                WHERE [IsKeyItem] = 1 AND [KeyId] IS NULL;
            ");

            // 2. Drop the now-redundant boolean. KeyId IS NOT NULL is the
            //    new predicate; the bit column is no longer load-bearing.
            migrationBuilder.DropColumn(
                name: "IsKeyItem",
                table: "Items");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Best-effort dev-only rollback. Restores the pre-migration shape:
            // every row with any KeyId is flagged as a key, and the lockpick
            // sentinel is reverted to the legacy NULL-KeyId representation.

            // 1. Re-add the bit column with a default of 0 so the ALTER can
            //    NOT NULL across every existing row.
            migrationBuilder.AddColumn<bool>(
                name: "IsKeyItem",
                table: "Items",
                type: "bit",
                nullable: false,
                defaultValueSql: "0");

            // 2. Anything with a non-NULL KeyId was a key — lockpick OR
            //    specific. Mark them all as IsKeyItem=1.
            migrationBuilder.Sql(@"
                UPDATE [Items] SET [IsKeyItem] = 1 WHERE [KeyId] IS NOT NULL;
            ");

            // 3. Restore the legacy 'lockpick' = NULL KeyId convention.
            migrationBuilder.Sql(@"
                UPDATE [Items] SET [KeyId] = NULL WHERE [KeyId] = N'lockpick';
            ");
        }
    }
}
