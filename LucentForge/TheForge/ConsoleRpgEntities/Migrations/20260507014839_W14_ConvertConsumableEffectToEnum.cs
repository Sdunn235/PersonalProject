using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    /// <summary>
    /// W14 Phase B — converts Consumable.Effect from a free-text nvarchar column
    /// to an int-backed ConsumableEffect enum.
    ///
    /// HAND-EDITED away from the scaffolded `AlterColumn(string -> int)` because
    /// SQL Server cannot directly cast values like 'heal' to int. The safe path
    /// adds a new int column, backfills via CASE on the existing strings, drops
    /// the old column, and renames into place.
    ///
    /// String -> Enum mapping (matches W12_SeedInventoryData.sql + W13_SeedWorldContent.sql):
    ///   'heal'     -> 1 (Heal)
    ///   'stamina'  -> 2 (Stamina)
    ///   'bp'       -> 3 (BitPool)         legacy spelling pre-W14_RenameBpToBitPool
    ///   'bitpool'  -> 3 (BitPool)
    ///   'bytepool' -> 4 (BytePool)
    ///   'keyitem'  -> 0 (None)            type-discriminator overload, removed in Phase C
    ///   'lockpick' -> 0 (None)            type-discriminator overload, removed in Phase C
    ///   anything else / NULL -> 0 (None)
    ///
    /// The ELSE-0 covers non-Consumable rows (Weapons/Armors/Shields) whose
    /// Effect column was always NULL — they get 0 (None) and never read it.
    /// </summary>
    public partial class W14_ConvertConsumableEffectToEnum : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // 1. Add the new int column with a default of 0 (None) so it can
            //    be NOT NULL even before backfill on every existing row.
            migrationBuilder.Sql(@"
                ALTER TABLE [Items]
                ADD [EffectNew] int NOT NULL CONSTRAINT [DF_Items_EffectNew] DEFAULT (0);
            ");

            // 2. Backfill from the legacy string column. Only Consumable rows
            //    had non-null Effect strings; all other discriminators stay 0.
            migrationBuilder.Sql(@"
                UPDATE [Items] SET [EffectNew] = CASE LOWER([Effect])
                    WHEN 'heal'     THEN 1
                    WHEN 'stamina'  THEN 2
                    WHEN 'bp'       THEN 3
                    WHEN 'bitpool'  THEN 3
                    WHEN 'bytepool' THEN 4
                    ELSE 0
                END
                WHERE [ItemType] = 'Consumable';
            ");

            // 3. Drop the legacy string column. The default-constraint on
            //    EffectNew stays in place — that's the new column's identity.
            migrationBuilder.Sql("ALTER TABLE [Items] DROP COLUMN [Effect];");

            // 4. Rename EffectNew -> Effect to match the model property name.
            migrationBuilder.Sql("EXEC sp_rename 'Items.EffectNew', 'Effect', 'COLUMN';");

            // 5. Drop the seed-only default-constraint. The column stays NOT NULL
            //    but going forward EF supplies the value at insert time (the C#
            //    property defaults to ConsumableEffect.None). Leaving the
            //    constraint named DF_Items_EffectNew on a column called Effect
            //    would be a future-reader crisis.
            migrationBuilder.Sql("ALTER TABLE [Items] DROP CONSTRAINT [DF_Items_EffectNew];");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Reverse direction. We map BitPool back to 'bitpool' (current
            // canonical spelling) rather than 'bp' (legacy). Down is best-effort
            // and only used for rollback in dev — historic 'bp'/'keyitem'/
            // 'lockpick' string fidelity is not preserved.
            migrationBuilder.Sql(@"
                ALTER TABLE [Items]
                ADD [EffectOld] nvarchar(max) NULL;
            ");

            migrationBuilder.Sql(@"
                UPDATE [Items] SET [EffectOld] = CASE [Effect]
                    WHEN 1 THEN N'heal'
                    WHEN 2 THEN N'stamina'
                    WHEN 3 THEN N'bitpool'
                    WHEN 4 THEN N'bytepool'
                    ELSE NULL
                END
                WHERE [ItemType] = 'Consumable';
            ");

            // (The DF_Items_EffectNew default-constraint was already dropped in
            // the Up migration's step 5, so don't try to drop it again here.)
            migrationBuilder.Sql("ALTER TABLE [Items] DROP COLUMN [Effect];");
            migrationBuilder.Sql("EXEC sp_rename 'Items.EffectOld', 'Effect', 'COLUMN';");
        }
    }
}
