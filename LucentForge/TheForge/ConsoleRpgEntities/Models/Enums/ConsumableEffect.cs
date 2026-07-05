namespace ConsoleRpgEntities.Models.Enums;

/// <summary>
/// Identifies what a <see cref="Items.Consumable"/> does when used.
///
/// Storage: persisted as int (default EF enum convention). Existing string
/// values from W12/W13 seed data are converted by the
/// W14_ConvertConsumableEffectToEnum migration:
///   "heal" -> Heal, "stamina" -> Stamina, "bp"/"bitpool" -> BitPool,
///   "bytepool" -> BytePool, "keyitem"/"lockpick"/anything else -> None.
///
/// Note: <see cref="None"/> is the safe default for rows that are KeyItems
/// or other non-effect-bearing consumables (Iron Lockpicks, dungeon keys).
/// W14 Phase C will extract those into a KeyItem TPH subclass; once that
/// lands, None should disappear from the data set entirely.
/// </summary>
public enum ConsumableEffect
{
    /// <summary>No effect. Used for KeyItem-flagged rows in legacy W12/W13 data
    /// and as a safe default when an Effect string didn't match any case.</summary>
    None = 0,

    /// <summary>Restores HP up to MaxHp. Magnitude = Potency.</summary>
    Heal = 1,

    /// <summary>Restores SP up to MaxSp. Magnitude = Potency.</summary>
    Stamina = 2,

    /// <summary>Restores BitPool up to MaxBitPool. Magnitude = Potency.
    /// Maps from legacy "bp" and "bitpool" strings.</summary>
    BitPool = 3,

    /// <summary>Restores BytePool up to MaxBytePool. Magnitude = Potency.</summary>
    BytePool = 4,
}
