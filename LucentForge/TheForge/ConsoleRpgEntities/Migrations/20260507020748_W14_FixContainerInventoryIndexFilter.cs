using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ConsoleRpgEntities.Migrations
{
    /// <inheritdoc />
    /// <summary>
    /// W14 Phase B.1 — fixes a latent W12 bug in IX_Containers_Inventory_OwnerCharacterId.
    ///
    /// The W12_InventoryAndSeed migration scaffolded the unique-filtered index with the
    /// WRONG column in its filter clause:
    ///
    ///   column: "Inventory_OwnerCharacterId",            -- correct
    ///   filter: "[OwnerCharacterId] IS NOT NULL"         -- WRONG (refers to a different column)
    ///
    /// In TPH, EF disambiguated the two subclasses' OwnerCharacterId properties by:
    ///   - Equipment rows store the FK in column [OwnerCharacterId]
    ///   - Inventory rows store the FK in column [Inventory_OwnerCharacterId]
    ///
    /// The buggy filter included EVERY Equipment row (their OwnerCharacterId IS NOT NULL)
    /// while their Inventory_OwnerCharacterId is always NULL. With one Equipment row
    /// (Elara only) the unique index tolerated a single NULL key. Once Phase 1.5
    /// (C0020) backfilled Equipment for additional NPCs/Animals, the second NULL
    /// caused: "Cannot insert duplicate key row ... duplicate key value is (NULL)."
    ///
    /// The bug was latent from W12 ship through C0020 because the integrity sweep
    /// only created multiple Equipment rows starting today (2026-05-07) when the
    /// app first ran end-to-end against a multi-character DB.
    ///
    /// Fix: drop the broken index and recreate it with the correct filter
    /// "[Inventory_OwnerCharacterId] IS NOT NULL" so the index only includes
    /// Inventory rows. The companion index IX_Containers_OwnerCharacterId already
    /// uses a correct filter (its column and filter both reference OwnerCharacterId)
    /// and serves the Equipment uniqueness constraint correctly.
    ///
    /// Forward-compatible: W14 will add Room as a 5th Container subclass with no
    /// OwnerCharacterId on either column, so Room rows are naturally excluded
    /// from both indexes.
    /// </summary>
    public partial class W14_FixContainerInventoryIndexFilter : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Containers_Inventory_OwnerCharacterId",
                table: "Containers");

            migrationBuilder.CreateIndex(
                name: "IX_Containers_Inventory_OwnerCharacterId",
                table: "Containers",
                column: "Inventory_OwnerCharacterId",
                unique: true,
                filter: "[Inventory_OwnerCharacterId] IS NOT NULL");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Restore the W12 buggy filter for rollback fidelity. Note: rolling
            // back will reintroduce the multi-NPC startup crash; this Down is
            // for completeness only.
            migrationBuilder.DropIndex(
                name: "IX_Containers_Inventory_OwnerCharacterId",
                table: "Containers");

            migrationBuilder.CreateIndex(
                name: "IX_Containers_Inventory_OwnerCharacterId",
                table: "Containers",
                column: "Inventory_OwnerCharacterId",
                unique: true,
                filter: "[OwnerCharacterId] IS NOT NULL");
        }
    }
}
