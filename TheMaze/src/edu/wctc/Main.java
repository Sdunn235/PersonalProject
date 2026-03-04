package edu.wctc;

import java.util.Scanner;

/**
 * Main driver class for the Maze game.
 * Handles the game loop, user input, and display of game state.
 */
public class Main {
    public static void main(String[] args) {
        try {
            Maze maze = new Maze();
            Scanner scanner = new Scanner(System.in);

            System.out.println("\n╔════════════════════════════════════════╗");
            System.out.println("║       WELCOME TO THE MAZE GAME        ║");
            System.out.println("║    A Dark Fantasy Dungeon Crawler     ║");
            System.out.println("╚════════════════════════════════════════╝\n");

            System.out.println("Commands:");
            System.out.println("  Movement: n(north), s(south), e(east), w(west), u(up), d(down)");
            System.out.println("  Actions:  i(interact), l(loot), x(exit), v(inventory)");
            System.out.println("  Quit:     q");
            System.out.println("════════════════════════════════════════\n");

            while (!maze.isFinished()) {
                // Display current state
                System.out.println("\n" + maze.getCurrentRoomDescription());
                System.out.println("\nCurrent Room: " + maze.getCurrentRoomName());
                System.out.println(maze.getCurrentRoomExits());
                System.out.println("Score: " + maze.getPlayerScore());

                // Get input
                System.out.print("\nEnter command: ");
                String input = scanner.nextLine().trim().toLowerCase();

                if (input.isEmpty()) {
                    System.out.println("✗ Please enter a valid command.");
                    continue;
                }

                char command = input.charAt(0);
                String result = "";

                // Process command
                switch (command) {
                    case 'n':
                    case 's':
                    case 'e':
                    case 'w':
                    case 'u':
                    case 'd':
                        boolean moved = maze.move(command);
                        if (moved) {
                            result = "→ You move in that direction.";
                        } else {
                            result = "✗ You cannot go that way.";
                        }
                        break;
                    case 'i':
                        result = maze.interactWithCurrentRoom();
                        break;
                    case 'l':
                        result = maze.lootCurrentRoom();
                        break;
                    case 'x':
                        result = maze.exitCurrentRoom();
                        break;
                    case 'v':
                        result = "\n" + maze.getPlayerInventory();
                        break;
                    case 'q':
                        System.out.println("\n✗ You have abandoned the maze. Thanks for playing!");
                        scanner.close();
                        return;
                    default:
                        result = "✗ Unknown command. Try n, s, e, w, u, d, i, l, x, v, or q.";
                }

                System.out.println(result);
            }

            // Game finished
            System.out.println("\n════════════════════════════════════════");
            System.out.println("Final Score: " + maze.getPlayerScore());
            System.out.println("════════════════════════════════════════\n");
            scanner.close();
        } catch (java.io.IOException e) {
            System.err.println("Error loading game resources: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
