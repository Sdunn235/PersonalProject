namespace ConsoleRpgEntities.Models;

public class Npc : Character
{
    // W15 Phase E: MonsterLoot eliminated. NPC loot lives in the NPC's
    // Inventory (inherited from Character). Inventory is non-null for any
    // NPC created via AddCharacter (integrity sweep auto-creates one).
}
