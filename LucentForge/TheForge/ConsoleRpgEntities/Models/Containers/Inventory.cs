namespace ConsoleRpgEntities.Models.Containers;

/// <summary>
/// A character's portable bag. The character's <i>total</i> carrying
/// capacity (Inventory + Equipment combined) lives on
/// <see cref="Character.CanCarry"/> / <see cref="Character.TotalCarriedWeight"/>;
/// this class only exposes the bag-side numbers.
///
/// <para><see cref="MaxWeight"/> is currently used as the character's
/// carry cap (since the int already lives here from W12). Renaming /
/// promoting it to Character is a future cleanup; for now the data
/// stays put and Character.CanCarry interprets it as a total cap.</para>
/// </summary>
public class Inventory : Container
{
    public int? OwnerCharacterId { get; set; }
    public virtual Character? Owner { get; set; }

    /// <summary>The character's total carrying capacity in pounds.
    /// Treated as Character-level by <see cref="Character.CanCarry"/>.</summary>
    public int MaxWeight { get; set; } = 100;

    /// <summary>Weight of items in this bag only (does NOT include
    /// equipped gear). Use <see cref="Character.TotalCarriedWeight"/>
    /// for the encumbrance number.</summary>
    public int CurrentWeight => ItemsCollection.Sum(i => i.Weight);
}
