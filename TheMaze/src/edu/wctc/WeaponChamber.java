package edu.wctc;

/**
 * A room containing a weapon that the player can loot.
 * The weapon is critical for succeeding in the final boss encounter.
 * Implements Lootable interface.
 */
public class WeaponChamber extends Room implements Lootable, Interactable {
    private boolean weaponLooted = false;
    private boolean weaponRemovedFromMap = false;

    /**
     * Constructs a WeaponChamber with the given name.
     * @param name the name of the room
     */
    public WeaponChamber(String name) {
        super(name);
    }

    @Override
    public String getSensoryDescription() {
        return "╔════════════════════════════════════════╗\n" +
               "║         YOU ENTER THE ARMORY         ║\n" +
               "╚════════════════════════════════════════╝\n\n" +
               "YOUR QUEST BEGINS\n" +
               "You have been summoned to this cursed place to end an ancient darkness.\n" +
               "The kingdom lies in shadows. A creature of immense power sits upon an\n" +
               "obsidian throne, its very existence draining the life from the world.\n" +
               "To have any hope of victory, you must first find a weapon worthy of the\n" +
               "challenge. This is your first objective.\n\n" +
               "THE ARMORY\n" +
               "Your footsteps echo through the cavernous chamber as you step inside.\n" +
               "The air is thick with the metallic scent of rust and oxidized steel—\n" +
               "centuries of decay all at once assaulting your senses.\n\n" +
               "Dust particles dance in the faint light filtering through cracks in\n" +
               "the stone ceiling. The walls are lined with rotting wooden racks,\n" +
               "from which countless weapons hang in various states of decay.\n\n" +
               "But there—in the center of the chamber, resting on a pristine marble\n" +
               "pedestal—lies a single longsword. Unlike the others, this blade gleams\n" +
               "with an otherworldly polish, its surface unmarred by the ravages of time.\n" +
               "It seems to call to you. This must be what you seek.\n";
    }

    @Override
    public String getShortRoomDescription() {
        return "The armory around you is dusty and ancient, filled with " +
               "countless rusty weapons beyond saving.";
    }

    @Override
    public String getDescription() {
        String grid = layoutGrid != null ? renderGrid() : "[Map not loaded]";
        return "═══════════════════════════════════════\n" +
               "      WEAPON CHAMBER - Armory\n" +
               "═══════════════════════════════════════\n\n" +
               "A dusty armory with scattered weapons on stone pedestals.\n" +
               "The air smells of rust and ancient metal. Sunlight filters\n" +
               "through cracks in the stone walls, illuminating countless\n" +
               "blades and helms covered in centuries of dust.\n\n" +
               "On a central pedestal, you notice a particularly well-preserved\n" +
               "longsword. Its blade still gleams faintly, and its grip looks\n" +
               "firm and reassuring.\n\n" +
               "Room Layout:\n" +
               grid + "\n" +
               "═══════════════════════════════════════\n" +
               "Legend: w=wall, f=floor, W=weapon, p=player, d=door, @=you";
    }

    @Override
    public String interact(Player player) {
        if (!weaponLooted) {
            return "\n═══════════════════════════════════════\n" +
                   "           THE LONGSWORD\n" +
                   "═══════════════════════════════════════\n\n" +
                   "You approach the pedestal and examine the magnificent blade.\n\n" +
                   "The longsword gleams with an ethereal light, as if untouched by\n" +
                   "the passage of centuries. The blade itself is perfectly straight,\n" +
                   "its edges keen and deadly. Intricate runes are etched along the\n" +
                   "fuller, glowing with a faint blue luminescence.\n\n" +
                   "The crossguard is ornate—wrought from pure silver in the shape of\n" +
                   "interlocking dragons. The grip is wrapped in what appears to be\n" +
                   "leather preserved by some ancient magic, feeling supple and warm\n" +
                   "to the touch. The pommel is a perfect sphere of deep blue crystal,\n" +
                   "cool and smooth, subtly pulsing with inner light.\n\n" +
                   "You sense this is no ordinary weapon. It seems to call to you,\n" +
                   "as if yearning to be wielded against the darkness ahead.\n\n" +
                   "⚔️  Use the 'l' command to LOOT the sword and take it with you.\n";
        }
        return "\n✗ You've already taken the longsword. There's nothing more to examine here.";
    }

    @Override
    public String loot(Player player) {
        if (!weaponLooted) {
            player.addToInventory("Iron Longsword");
            player.addToScore(50);
            weaponLooted = true;

            // Remove weapon from map
            if (objectsGrid != null && !weaponRemovedFromMap) {
                for (int i = 0; i < objectsGrid.length; i++) {
                    for (int j = 0; j < objectsGrid[i].length; j++) {
                        if (objectsGrid[i][j] == 'W') {
                            objectsGrid[i][j] = ' ';  // Replace with empty space
                            weaponRemovedFromMap = true;
                            break;
                        }
                    }
                    if (weaponRemovedFromMap) break;
                }
            }

            return "\n★ YOU PICKED UP THE IRON LONGSWORD! ★\n" +
                   "═══════════════════════════════════════\n" +
                   "You grasp the longsword firmly, and it settles into your hands\n" +
                   "as if it was always meant for you to wield. The weight is\n" +
                   "reassuring—heavy enough to strike true, yet balanced enough\n" +
                   "to move with deadly grace.\n\n" +
                   "The runes along the blade flare with brilliant blue light,\n" +
                   "confirming your choice. You feel a surge of confidence.\n" +
                   "Whatever lies ahead, you will face it armed and ready.\n\n" +
                   "You gain 50 points.";
        }
        return "\n✗ You've already taken the weapon from this chamber.";
    }
}

