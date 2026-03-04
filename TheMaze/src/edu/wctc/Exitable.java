package edu.wctc;

/**
 * Interface for rooms that can be exited from, ending the game.
 * Implementing classes should provide exit mechanics and return descriptive feedback.
 */
public interface Exitable {
    /**
     * Executes the exit action in this room, potentially ending the game.
     * @param player the Player object exiting the room
     * @return a String describing the result of the exit action
     */
    String exit(Player player);
}

