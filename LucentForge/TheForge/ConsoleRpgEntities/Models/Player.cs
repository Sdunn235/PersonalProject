namespace ConsoleRpgEntities.Models;

// Player is a Character marker type. Inventory/equipment/chest verbs live on the
// Character base class so NPCs and Animals can use them too — the LucentForge
// "anyone can" principle. Player remains distinct via its TPH discriminator
// (used by Race-eligibility checks in AddCharacter/EditIdentity) and any future
// player-only behavior (save game, party leader, etc.).
public class Player : Character
{
}
