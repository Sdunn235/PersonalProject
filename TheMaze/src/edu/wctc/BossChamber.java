package edu.wctc;

import java.util.Random;

/**
 * The final room of the maze containing a powerful creature.
 * The player must exit this room to end the game. Success depends on preparation
 * (having the weapon and consulting the sage for increased success probability).
 * Implements Exitable interface.
 */
public class BossChamber extends Room implements Exitable, Interactable {
    private SagesChamber sageReference;
    private boolean bossEncounterStarted = false;

    /**
     * Constructs a BossChamber with the given name.
     * @param name the name of the room
     */
    public BossChamber(String name) {
        super(name);
    }

    /**
     * Sets a reference to the sage's chamber for interaction count tracking.
     * @param sage the SagesChamber instance
     */
    public void setSageReference(SagesChamber sage) {
        this.sageReference = sage;
    }

    @Override
    public String getSensoryDescription() {
        return "╔════════════════════════════════════════╗\n" +
               "║     YOU ENTER THE BOSS CHAMBER      ║\n" +
               "╚════════════════════════════════════════╝\n\n" +
               "YOUR FINAL OBJECTIVE\n" +
               "Everything has led to this moment. You have obtained a weapon of power.\n" +
               "You have sought counsel from the ancient sage. Now comes the true test\n" +
               "of your worth. Ahead waits the creature that has plagued this realm for\n" +
               "centuries. You must defeat it, or the kingdom will perish in endless night.\n" +
               "Steel yourself. This is the moment of reckoning.\n\n" +
               "THE OBSIDIAN THRONE ROOM\n" +
               "The moment you cross the threshold, reality itself seems to warp.\n" +
               "A bone-chilling cold washes over you, so intense it steals your breath.\n" +
               "Your breath mists in the frigid air as an overwhelming sense of dread\n" +
               "coils around your heart like serpents.\n\n" +
               "The chamber before you is vast and oppressive. Towering walls of\n" +
               "obsidian black stone stretch upward, their surfaces gleaming with an\n" +
               "unnatural sheen that reflects no light—absorbs it, swallows it whole.\n" +
               "The very darkness seems alive, writhing at the edges of your vision.\n\n" +
               "In the far distance, atop a throne of twisted bone and shadow,\n" +
               "something moves. Something ancient. Something furious.\n\n" +
               "Red eyes—terrible, burning eyes—ignite in the darkness like portals\n" +
               "to perdition. You feel its gaze fall upon you, and you know with\n" +
               "absolute certainty that your journey has led to this moment.\n\n" +
               "There is no turning back now.\n";
    }

    @Override
    public String getShortRoomDescription() {
        return "The obsidian throne room stretches before you, its darkness " +
               "oppressive and suffocating.";
    }

    @Override
    public String getDescription() {
        String grid = layoutGrid != null ? renderGrid() : "[Map not loaded]";
        return "═══════════════════════════════════════\n" +
               "    BOSS CHAMBER - Obsidian Throne\n" +
               "═══════════════════════════════════════\n\n" +
               "A massive obsidian throne room stretches before you.\n" +
               "The walls gleam with an unnatural black sheen, reflecting\n" +
               "the faint red glow emanating from the far end of the chamber.\n\n" +
               "Atop a towering throne sits an ancient creature of immense\n" +
               "power. Its eyes burn with crimson fire, and an aura of\n" +
               "menacing darkness radiates from its form.\n\n" +
               "This is your final test. The creature turns to regard you,\n" +
               "as if acknowledging your arrival for the first time.\n\n" +
               "⚔️  TO FACE THE BOSS: Click the [⚔️ FIGHT] button ⚔️\n\n" +
               "Room Layout:\n" +
               grid + "\n" +
               "═══════════════════════════════════════\n" +
               "Legend: w=wall, f=floor, e=exit, d=door, p=player, @=you";
    }

    @Override
    public String interact(Player player) {
        if (!bossEncounterStarted) {
            bossEncounterStarted = true;
            return generateBossDescription(player);
        }
        return "\n⚠️  The creature watches you with consuming hatred. Its form\n" +
               "radiates an oppressive aura of power and malevolence.\n" +
               "There is only one path forward: face it in combat.\n\n" +
               "He looks at you to make your move. (Click FIGHT Now)\n";
    }

    /**
     * Generates a detailed description of the boss encounter.
     * Includes intimidating dialogue and sensory details.
     */
    private String generateBossDescription(Player player) {
        return "\n╔════════════════════════════════════════╗\n" +
               "║      THE CREATURE ON THE THRONE      ║\n" +
               "╚════════════════════════════════════════╝\n\n" +
               "You step forward, drawing closer to the throne. With each footfall,\n" +
               "the shadow deepens, the cold intensifies, until you can scarcely feel\n" +
               "your limbs.\n\n" +
               "The creature rises—terrible and vast. Its form is barely corporeal,\n" +
               "more shadow and flame than flesh. Where it stands, reality bends and\n" +
               "warps. The very air crackles with ancient malice.\n\n" +
               "When it speaks, its voice is like the grinding of continents, like\n" +
               "the death screams of stars:\n\n" +
               "     \"SO... AT LAST THE KINGDOM SENDS A CHAMPION.\n" +
               "      HOW AMUSING. HOW PITIFUL.\n" +
               "      I HAVE WAITED EONS FOR ONE BRAVE OR FOOLISH ENOUGH TO STAND\n" +
               "      BEFORE ME. YOUR DEFIANCE CHANGES NOTHING. YOUR END IS WRITTEN\n" +
               "      IN THE VERY FABRIC OF FATE.\n" +
               "      LET US END THIS... AND YOUR SUFFERING.\"\n\n" +
               "The creature spreads massive wings of pure darkness, blocking out all\n" +
               "remaining light. You stand alone in the abyss, facing a power that\n" +
               "seems utterly insurmountable.\n\n" +
               "Only one thing remains: the battle.\n\n" +
               "He looks at you to make your move. (Click FIGHT Now)\n";
    }

    @Override
    public String exit(Player player) {
        int successChance = calculateSuccessChance(player);
        Random random = new Random();
        int roll = random.nextInt(100);

        if (roll < successChance) {
            player.addToScore(500);
            return generateVictoryNarrative(player, successChance);
        } else {
            return generateDefeatNarrative(player, successChance);
        }
    }

    /**
     * Generates a victory narrative based on player preparation.
     */
    private String generateVictoryNarrative(Player player, int chance) {
        StringBuilder narrative = new StringBuilder();
        narrative.append("\n╔════════════════════════════════════════╗\n");
        narrative.append("║          ⚔️  VICTORY!  ⚔️           ║\n");
        narrative.append("╚════════════════════════════════════════╝\n\n");

        // Determine narrative based on preparation level
        if (player.hasItem("Iron Longsword")) {
            narrative.append("With the longsword raised before you, its runes blazing with\n" +
                           "sacred blue light, you charge forward. The weapon feels alive\n" +
                           "in your hands, responding to your will as if it were part of\n" +
                           "your very being.\n\n");
        }

        int sageCount = sageReference != null ? sageReference.getInteractionCount() : 0;

        if (sageCount >= 3) {
            narrative.append("Your mind is clear, sharpened by the sage's wisdom. Each word\n" +
                           "spoken has woven itself into your strategy. As the creature\n" +
                           "lunges, you remember: 'Its left flank is vulnerable.'\n\n" +
                           "You pivot with impossible grace, your blade finding the opening\n" +
                           "the sage revealed. The creature roars—a sound of ancient rage\n" +
                           "and agony.\n\n");
        } else if (sageCount >= 1) {
            narrative.append("The sage's words echo in your mind, bolstering your courage.\n" +
                           "With newfound determination, you face the creature's assault.\n" +
                           "Your blade meets its darkness again and again, each strike\n" +
                           "pushing back the shadows.\n\n");
        } else {
            narrative.append("With courage born of desperation, you throw yourself forward.\n" +
                           "The creature's power is immense, but your determination is\n" +
                           "greater. Again and again your blade finds purchase, chipping\n" +
                           "away at the darkness.\n\n");
        }

        narrative.append("The creature's form begins to unravel. It screams—a wail of\n" +
                       "fury that shakes the very foundations of reality. Its essence\n" +
                       "tears apart, dissipating into nothingness.\n\n" +
                       "The obsidian walls crack and crumble. Blinding light floods\n" +
                       "through the fissures. The curse—ancient and terrible—breaks\n" +
                       "at last.\n\n" +
                       "The kingdom is saved. The darkness has been banished.\n" +
                       "The world is reborn in light.\n\n" +
                       "═══════════════════════════════════════\n" +
                       "FINAL SCORE: " + player.getScore() + " points\n" +
                       "═══════════════════════════════════════\n" +
                       "You have triumphed against impossible odds!\n");

        return narrative.toString();
    }

    /**
     * Generates a defeat narrative based on player preparation level.
     */
    private String generateDefeatNarrative(Player player, int chance) {
        StringBuilder narrative = new StringBuilder();
        narrative.append("\n╔════════════════════════════════════════╗\n");
        narrative.append("║         💀  DEFEAT  💀              ║\n");
        narrative.append("╚════════════════════════════════════════╝\n\n");

        int sageCount = sageReference != null ? sageReference.getInteractionCount() : 0;
        boolean hasWeapon = player.hasItem("Iron Longsword");

        if (!hasWeapon) {
            narrative.append("Without a weapon, you charge the creature in desperation.\n" +
                           "It swats you aside as if you were an insect. Your courage\n" +
                           "is admirable, but ultimately meaningless against such power.\n\n" +
                           "The creature's shadow envelops you. Your screams fade into\n" +
                           "eternal darkness.\n\n");
        } else if (sageCount == 0) {
            narrative.append("You raise your blade, and the creature laughs—a sound like\n" +
                           "the death of worlds. It moves with terrifying speed.\n" +
                           "Your sword, though well-forged, feels inadequate against\n" +
                           "such ancient power.\n\n" +
                           "Blow after blow you trade with the creature, but you lack\n" +
                           "the knowledge to find its weakness. Slowly, relentlessly,\n" +
                           "the creature overwhelms you.\n\n" +
                           "As darkness claims you, you realize: knowledge itself is\n" +
                           "as important as steel.\n\n");
        } else {
            narrative.append("You fight with skill and determination, your sword gleaming\n" +
                           "in the darkness. The sage's wisdom guides your strikes, and\n" +
                           "for a moment, you believe victory is possible.\n\n" +
                           "But the creature's power is too great. For every wound you\n" +
                           "inflict, it returns two. The battle rages on, but the outcome\n" +
                           "was written before you began.\n\n" +
                           "As you feel your strength waning, you realize that perhaps\n" +
                           "greater preparation was needed. Perhaps this curse was never\n" +
                           "meant to be broken...\n\n");
        }

        narrative.append("═══════════════════════════════════════\n" +
                       "GAME OVER\n" +
                       "Final Score: " + player.getScore() + " points\n" +
                       "═══════════════════════════════════════\n" +
                       "The darkness endures. But you may try again...\n");

        return narrative.toString();
    }

    /**
     * Calculates the success probability based on player preparation.
     * @param player the player attempting to exit
     * @return the success chance as a percentage (0-95)
     */
    private int calculateSuccessChance(Player player) {
        int chance = 0;

        // Base: 0% (automatic failure without weapon)
        if (!player.hasItem("Iron Longsword")) {
            return 0;
        }

        // With weapon: 50%
        chance = 50;

        // Each sage interaction adds 15% (max 3 interactions = +45%)
        if (sageReference != null) {
            int sageInteractions = sageReference.getInteractionCount();
            chance += (sageInteractions * 15);
        }

        // Cap at 95%
        return Math.min(chance, 95);
    }
}

