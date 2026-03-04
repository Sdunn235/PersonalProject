package edu.wctc;

/**
 * Abstract base class for all rooms in the maze.
 * Manages room connections and provides methods for room interaction.
 * Supports loading room layouts from CSV files.
 */
public abstract class Room {
    private String name;
    private Room north;
    private Room south;
    private Room east;
    private Room west;
    private Room up;
    private Room down;

    // CSV grid data for room layout - public for GUI rendering
    public char[][] layoutGrid;
    public char[][] objectsGrid;
    public char[][] collisionGrid;

    // Player position in the room
    public int playerRow;
    public int playerCol;

    // Track first-time entry for sensory descriptions
    private boolean hasBeenEntered = false;

    /**
     * Constructs a Room with a given name.
     * All directional connections are initially null.
     * @param name the name of the room
     */
    public Room(String name) {
        this.name = name;
        this.north = null;
        this.south = null;
        this.east = null;
        this.west = null;
        this.up = null;
        this.down = null;
        this.layoutGrid = null;
        this.objectsGrid = null;
        this.collisionGrid = null;
        this.playerRow = -1;
        this.playerCol = -1;
        this.hasBeenEntered = false;
    }

    /**
     * Loads CSV map files for this room.
     * @param layoutPath path to layout.csv
     * @param objectsPath path to objects.csv
     * @param collisionPath path to collision.csv
     * @throws java.io.IOException if files cannot be read
     */
    public void loadMaps(String layoutPath, String objectsPath, String collisionPath) throws java.io.IOException {
        this.layoutGrid = MapLoader.loadMap(layoutPath);
        this.objectsGrid = MapLoader.loadMap(objectsPath);
        this.collisionGrid = MapLoader.loadMap(collisionPath);

        // Find player starting position
        int[] playerPos = MapLoader.findPosition(objectsGrid, 'p');
        this.playerRow = playerPos[0];
        this.playerCol = playerPos[1];
    }

    /**
     * Abstract method to get the room description.
     * Subclasses must provide a description of the room.
     * @return a String describing the room
     */
    public abstract String getDescription();

    /**
     * Renders the room's grid for display.
     * Overlays objects on top of layout based on priority.
     * @return formatted grid string
     */
    protected String renderGrid() {
        if (layoutGrid == null || layoutGrid.length == 0) {
            return "[Map not loaded]";
        }

        StringBuilder sb = new StringBuilder();

        // Top border
        sb.append("┌");
        for (int i = 0; i < layoutGrid[0].length; i++) {
            sb.append("──┬");
        }
        sb.setLength(sb.length() - 1);  // Remove last ┬
        sb.append("┐\n");

        // Grid rows
        for (int i = 0; i < layoutGrid.length; i++) {
            sb.append("│");
            for (int j = 0; j < layoutGrid[i].length; j++) {
                char cell;

                // Show player sprite if at this position
                if (i == playerRow && j == playerCol) {
                    cell = '@';  // Player placeholder
                }
                // Show object if present and not empty
                else if (j < objectsGrid[i].length && objectsGrid[i][j] != ' ') {
                    cell = objectsGrid[i][j];
                }
                // Otherwise show layout
                else {
                    cell = layoutGrid[i][j];
                }

                sb.append(" ").append(cell).append("│");
            }
            sb.append("\n");
        }

        // Bottom border
        sb.append("└");
        for (int i = 0; i < layoutGrid[0].length; i++) {
            sb.append("──┴");
        }
        sb.setLength(sb.length() - 1);  // Remove last ┴
        sb.append("┘");

        return sb.toString();
    }

    /**
     * Gets an adjoining room in the specified direction.
     * @param direction the direction ('n', 's', 'e', 'w', 'u', 'd')
     * @return the Room in that direction, or null if there is none
     */
    public Room getAdjoiningRoom(char direction) {
        return switch (direction) {
            case 'n' -> north;
            case 's' -> south;
            case 'e' -> east;
            case 'w' -> west;
            case 'u' -> up;
            case 'd' -> down;
            default -> null;
        };
    }

    /**
     * Gets a formatted string of all valid exit directions from this room.
     * @return a String listing all available directions
     */
    public String getExits() {
        StringBuilder sb = new StringBuilder("You can move:");
        boolean hasExits = false;

        if (north != null) {
            sb.append(" north");
            hasExits = true;
        }
        if (south != null) {
            sb.append(hasExits ? "," : "").append(" south");
            hasExits = true;
        }
        if (east != null) {
            sb.append(hasExits ? "," : "").append(" east");
            hasExits = true;
        }
        if (west != null) {
            sb.append(hasExits ? "," : "").append(" west");
            hasExits = true;
        }
        if (up != null) {
            sb.append(hasExits ? "," : "").append(" up");
            hasExits = true;
        }
        if (down != null) {
            sb.append(hasExits ? "," : "").append(" down");
            hasExits = true;
        }

        if (!hasExits) {
            return "You are trapped with no exits!";
        }
        return sb.append(".").toString();
    }

    /**
     * Gets the name of this room.
     * @return the room's name
     */
    public String getName() {
        return name;
    }

    /**
     * Checks if a given direction has a valid exit.
     * @param direction the direction to check ('n', 's', 'e', 'w', 'u', 'd')
     * @return true if there is a room in that direction, false otherwise
     */
    public boolean isValidDirection(char direction) {
        return getAdjoiningRoom(direction) != null;
    }

    /**
     * Sets the room to the north.
     * @param room the Room to connect to the north
     */
    public void setNorth(Room room) {
        this.north = room;
    }

    /**
     * Sets the room to the south.
     * @param room the Room to connect to the south
     */
    public void setSouth(Room room) {
        this.south = room;
    }

    /**
     * Sets the room to the east.
     * @param room the Room to connect to the east
     */
    public void setEast(Room room) {
        this.east = room;
    }

    /**
     * Sets the room to the west.
     * @param room the Room to connect to the west
     */
    public void setWest(Room room) {
        this.west = room;
    }

    /**
     * Sets the room above (up).
     * @param room the Room to connect above
     */
    public void setUp(Room room) {
        this.up = room;
    }

    /**
     * Sets the room below (down).
     * @param room the Room to connect below
     */
    public void setDown(Room room) {
        this.down = room;
    }

    /**
     * Checks if this is the player's first time entering the room.
     * @return true if this is the first entry, false otherwise
     */
    public boolean isFirstEntry() {
        return !hasBeenEntered;
    }

    /**
     * Marks this room as having been entered by the player.
     * Called when the player moves into the room.
     */
    public void markAsEntered() {
        this.hasBeenEntered = true;
    }

    /**
     * Gets the sensory description for first-time room entry.
     * Default implementation returns empty string; subclasses can override.
     * @return sensory description or empty string
     */
    public String getSensoryDescription() {
        return "";
    }

    /**
     * Gets a short version of the room description for non-interactable interactions.
     * Default implementation returns empty string; subclasses can override.
     * @return abbreviated room description
     */
    public String getShortRoomDescription() {
        return "";
    }
}

