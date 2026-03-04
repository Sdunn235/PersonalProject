package edu.wctc;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents the player in the maze game.
 * Tracks the player's score and inventory.
 */
public class Player {
    private int score;
    private List<String> inventory;

    /**
     * Constructs a Player with an initial score of 0 and empty inventory.
     */
    public Player() {
        this.score = 0;
        this.inventory = new ArrayList<>();
    }

    /**
     * Adds an item to the player's inventory.
     * @param item the name of the item to add
     */
    public void addToInventory(String item) {
        inventory.add(item);
    }

    /**
     * Adds points to the player's score.
     * @param points the number of points to add
     */
    public void addToScore(int points) {
        score += points;
    }

    /**
     * Returns the player's current inventory as a formatted string.
     * @return a string representation of the inventory, or a message if empty
     */
    public String getInventory() {
        if (inventory.isEmpty()) {
            return "Your inventory is empty.";
        }
        StringBuilder sb = new StringBuilder("Inventory:\n");
        for (int i = 0; i < inventory.size(); i++) {
            sb.append("  ").append(i + 1).append(". ").append(inventory.get(i)).append("\n");
        }
        return sb.toString();
    }

    /**
     * Returns the player's current score.
     * @return the score as an integer
     */
    public int getScore() {
        return score;
    }

    /**
     * Checks if the player has a specific item in their inventory.
     * @param item the name of the item to check for
     * @return true if the item is in the inventory, false otherwise
     */
    public boolean hasItem(String item) {
        return inventory.contains(item);
    }
}

