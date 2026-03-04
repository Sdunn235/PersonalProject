package edu.wctc;

/**
 * Interface for rooms that can be looted by the player.
 * Implementing classes should provide loot mechanics and return descriptive feedback.
 */
public interface Lootable {
    /**
     * Executes the loot action in this room.
     * @param player the Player object looting the room
     * @return a String describing the result of the loot action
     */
    String loot(Player player);
}

