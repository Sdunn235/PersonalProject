using ConsoleRpgEntities.Models.Enums;

namespace ConsoleRpgEntities.Models.Items;

/// <summary>
/// A single-use Item that produces an effect when consumed by a Character.
///
/// Effect/Potency contract:
///   - <see cref="Effect"/> identifies WHICH resource is restored (or None).
///   - <see cref="Potency"/> is the magnitude added to that resource. The
///     restoration is clamped at the resource's max (e.g., heal can't push
///     HP past MaxHp).
///   - Consumption: an item is removed from the user's Inventory only when
///     a real effect was applied. <see cref="ConsumableEffect.None"/> rows
///     do not consume on use (this fixes the W12/W13 silent-fail bug where
///     unrecognized effect strings still removed the item).
///
/// W14 Phase B refactor: <see cref="Effect"/> was previously a free-text
/// string ("heal", "stamina", "bp"/"bitpool", "bytepool", "keyitem",
/// "lockpick") which mixed effect semantics with type-discriminator
/// semantics. Promoting to an enum eliminated the magic-string smell and
/// the silent-fail bug; the type-discriminator overload (KeyItem,
/// Lockpick) will be removed in Phase C via a KeyItem TPH subclass.
/// </summary>
public class Consumable : Item
{
    /// <summary>Which resource this consumable restores. Defaults to None.</summary>
    public ConsumableEffect Effect { get; set; } = ConsumableEffect.None;

    /// <summary>Amount restored to the resource named by <see cref="Effect"/>.
    /// Clamped at the resource's max during use. Zero or negative values are
    /// allowed but produce no observable change.</summary>
    public int Potency { get; set; }
}
