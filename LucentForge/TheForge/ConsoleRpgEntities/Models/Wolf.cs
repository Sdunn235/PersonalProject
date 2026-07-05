namespace ConsoleRpgEntities.Models;

// W15 Phase F3 — Wolf : Npc. PackSize encodes the bible's swarm principle:
// danger is in numbers, not the individual. The seed wolf has PackSize=3
// even though only one NPC row exists — one wolf you can see, two more
// you can't. Proves Phase E works for non-Gobby monsters: loot lives in
// the Wolf's Inventory, not a MonsterLoot container.
public class Wolf : Npc
{
    public int PackSize { get; set; } = 1;
}
