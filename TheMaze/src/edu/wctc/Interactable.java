package edu.wctc;

/**
 * Interface for rooms that can be interacted with by the player.
 * Implementing classes should provide interaction mechanics and return descriptive feedback.
 */
public interface Interactable {
    /**
     * Executes the interact action in this room.
     * @param player the Player object interacting with the room
     * @return a String describing the result of the interaction
     */
    String interact(Player player);
}

