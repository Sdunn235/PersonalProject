package edu.wctc;

/**
 * A room containing a wise sage who provides knowledge about the upcoming boss.
 * The player can interact with the sage multiple times, each interaction providing
 * additional insight and increasing their chances of success in the final battle.
 * Implements Interactable interface.
 */
public class SagesChamber extends Room implements Interactable {
    private int interactionCount = 0;
    private final String[] dialogues = {
        "The creature ahead feeds on fear. Knowledge is your shield. Take time to prepare yourself mentally.",

        "I sense a weakness... its left flank is vulnerable. Strike there with conviction when the moment comes.",

        "You are as prepared as you can be. Go now, and reclaim your kingdom. May fortune favor the brave."
    };

    /**
     * Constructs a SagesChamber with the given name.
     * @param name the name of the room
     */
    public SagesChamber(String name) {
        super(name);
    }

    @Override
    public String getSensoryDescription() {
        return "╔════════════════════════════════════════╗\n" +
               "║      YOU ENTER THE SAGE'S CHAMBER    ║\n" +
               "╚════════════════════════════════════════╝\n\n" +
               "YOUR SECOND OBJECTIVE\n" +
               "You have obtained a weapon, but weaponry alone will not be enough.\n" +
               "The creature is ancient and powerful beyond measure. You must seek\n" +
               "knowledge if you hope to find its weakness. An old sage dwells in this\n" +
               "place, said to possess wisdom that spans millennia. Every word they\n" +
               "speak could be the difference between victory and death.\n\n" +
               "THE LIBRARY\n" +
               "The moment you step through the doorway, the air transforms.\n" +
               "The oppressive coldness of the stone corridors yields to a warm,\n" +
               "almost inviting atmosphere. The scent of ancient paper and herbs\n" +
               "fills your lungs—sage, lavender, and something you cannot quite place.\n\n" +
               "Your eyes adjust to softer lighting. Countless candles flicker\n" +
               "throughout the chamber, casting dancing shadows across towering shelves\n" +
               "laden with books, scrolls, and artifacts of immense age.\n\n" +
               "In the center of the chamber, a robed figure sits in perfect stillness\n" +
               "upon a stone bench. Their presence radiates calm—an island of serenity\n" +
               "in a sea of chaos. Ancient eyes open slowly as they sense your presence.\n" +
               "You sense that this being possesses knowledge that may prove crucial\n" +
               "to your survival. They motion for you to speak with them.\n";
    }

    @Override
    public String getShortRoomDescription() {
        return "The library is vast and filled with ancient knowledge, " +
               "though the sage sits in silent meditation.";
    }

    @Override
    public String getDescription() {
        String grid = layoutGrid != null ? renderGrid() : "[Map not loaded]";
        return "═══════════════════════════════════════\n" +
               "     SAGE'S CHAMBER - Ancient Library\n" +
               "═══════════════════════════════════════\n\n" +
               "An ancient library filled with dusty scrolls and crumbling tomes.\n" +
               "The walls are lined with shelves carved from dark wood, their\n" +
               "contents spanning centuries of accumulated knowledge.\n\n" +
               "In the center sits a robed figure on a stone bench, eyes closed\n" +
               "in deep meditation. The figure's presence radiates calm wisdom\n" +
               "and an aura of serene knowledge.\n\n" +
               "Room Layout:\n" +
               grid + "\n" +
               "═══════════════════════════════════════\n" +
               "Legend: w=wall, f=floor, n=NPC sage, p=player, d=door, @=you";
    }

    @Override
    public String interact(Player player) {
        if (interactionCount < dialogues.length) {
            String dialogue = dialogues[interactionCount];
            interactionCount++;
            player.addToScore(25);
            return "\n📜 Sage speaks:\n" +
                   "  \"" + dialogue + "\"\n" +
                   "  You gain 25 points.";
        }
        return "\n✗ The sage meditates silently. You've learned all they have to teach.";
    }

    /**
     * Gets the current interaction count.
     * Used for calculating success probability in the boss encounter.
     * @return the number of times the sage has been interacted with
     */
    public int getInteractionCount() {
        return interactionCount;
    }
}

