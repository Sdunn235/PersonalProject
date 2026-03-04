package edu.wctc;

/**
 * Represents the game world and manages game state.
 * Contains all rooms, the player, and handles navigation and interactions.
 */
public class Maze {
    private Room currentRoom;
    private Player player;
    private boolean isFinished;
    private SagesChamber sagesChamber;
    private String lastEntranceNarrative = "";  // Track entrance narrative for GUI

    /**
     * Constructs a Maze and initializes all rooms and connections.
     * Sets the player's starting room and initial state.
     * Loads CSV map data for each room.
     */
    public Maze() throws java.io.IOException {
        this.player = new Player();
        this.isFinished = false;

        // Create all rooms
        WeaponChamber weaponChamber = new WeaponChamber("Weapon Chamber");
        sagesChamber = new SagesChamber("Sage's Chamber");
        BossChamber bossChamber = new BossChamber("Boss Chamber");

        // Load CSV maps for each room from compiled directory
        String basePath = "edu/wctc/maps/";

        try {
            weaponChamber.loadMaps(
                basePath + "WeaponChamber/layout.csv",
                basePath + "WeaponChamber/objects.csv",
                basePath + "WeaponChamber/collision.csv"
            );

            sagesChamber.loadMaps(
                basePath + "SagesChamber/layout.csv",
                basePath + "SagesChamber/objects.csv",
                basePath + "SagesChamber/collision.csv"
            );

            bossChamber.loadMaps(
                basePath + "BossChamber/layout.csv",
                basePath + "BossChamber/objects.csv",
                basePath + "BossChamber/collision.csv"
            );
        } catch (java.io.IOException e) {
            // Maps will display as [Map not loaded] if files cannot be found
            // Game is still fully playable in text mode
        }

        // Set sage reference for boss encounter
        bossChamber.setSageReference(sagesChamber);

        // Set room connections
        // Weapon Chamber connections
        weaponChamber.setEast(sagesChamber);

        // Sage's Chamber connections
        sagesChamber.setWest(weaponChamber);
        sagesChamber.setEast(bossChamber);

        // Boss Chamber connections
        bossChamber.setWest(sagesChamber);

        // Set player's starting room and mark as entered
        this.currentRoom = weaponChamber;
        this.currentRoom.markAsEntered();
    }

    /**
     * Attempts to move the player in the specified direction.
     * @param direction the direction to move ('n', 's', 'e', 'w', 'u', 'd')
     * @return true if the move was successful, false otherwise
     */
    public boolean move(char direction) {
        if (currentRoom.isValidDirection(direction)) {
            currentRoom = currentRoom.getAdjoiningRoom(direction);

            // Generate entrance narrative for first entry
            if (currentRoom.isFirstEntry()) {
                lastEntranceNarrative = currentRoom.getSensoryDescription();
                currentRoom.markAsEntered();
            } else {
                lastEntranceNarrative = "";
            }

            return true;
        }
        return false;
    }

    /**
     * Attempts to exit the current room.
     * If the room is exitable, triggers the exit logic (potentially ending the game).
     * @return a String describing the result of the exit attempt
     */
    public String exitCurrentRoom() {
        if (currentRoom instanceof Exitable) {
            String result = ((Exitable) currentRoom).exit(player);
            isFinished = true;
            return result;
        }
        // Not a boss room - show message that there's no one to fight here
        return "✗ There is no one here who deserves your wrath.";
    }

    /**
     * Attempts to interact with the current room.
     * If the room is interactable, triggers the interaction logic.
     * @return a String describing the result of the interaction
     */
    public String interactWithCurrentRoom() {
        if (currentRoom instanceof Interactable) {
            return ((Interactable) currentRoom).interact(player);
        }
        return "✗ There is nothing to interact with in this room.";
    }

    /**
     * Attempts to loot the current room.
     * If the room is lootable, triggers the loot logic.
     * @return a String describing the result of the loot attempt
     */
    public String lootCurrentRoom() {
        if (currentRoom instanceof Lootable) {
            return ((Lootable) currentRoom).loot(player);
        }
        return "✗ There is nothing to loot in this room.";
    }

    /**
     * Gets the player's current score.
     * @return the score as an integer
     */
    public int getPlayerScore() {
        return player.getScore();
    }

    /**
     * Gets the player's current inventory.
     * @return a formatted string of the player's inventory
     */
    public String getPlayerInventory() {
        return player.getInventory();
    }

    /**
     * Gets the description of the current room.
     * @return the room description as a String
     */
    public String getCurrentRoomDescription() {
        return currentRoom.getDescription();
    }

    /**
     * Gets the available exits from the current room.
     * @return a formatted string of available exits
     */
    public String getCurrentRoomExits() {
        return currentRoom.getExits();
    }

    /**
     * Checks if the game is finished.
     * @return true if the game has ended, false otherwise
     */
    public boolean isFinished() {
        return isFinished;
    }

    /**
     * Gets the name of the current room.
     * @return the current room's name
     */
    public String getCurrentRoomName() {
        return currentRoom.getName();
    }

    /**
     * Gets the current room object (for GUI access to grid data).
     * @return the current Room
     */
    public Room getCurrentRoom() {
        return currentRoom;
    }

    /**
     * Sets the finished state of the game.
     * @param finished true to end the game, false otherwise
     */
    public void setFinished(boolean finished) {
        this.isFinished = finished;
    }

    /**
     * Gets the entrance narrative for the current room (sensory description).
     * Returns empty string if not first entry.
     * @return the sensory description or empty string
     */
    public String getLastEntranceNarrative() {
        return lastEntranceNarrative;
    }

    /**
     * Gets the starting room entrance narrative for the initial game state.
     * @return the starting sensory description
     */
    public String getStartingEntranceNarrative() {
        return currentRoom.getSensoryDescription();
    }
}

