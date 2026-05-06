package edu.wctc;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Utility class for loading CSV map files.
 * Converts CSV grid data into 2D character arrays for room rendering and collision detection.
 */
public class MapLoader {

    /**
     * Loads a CSV map file and converts it to a 2D character array.
     * Empty cells (commas with no value) are represented as spaces.
     *
     * @param filepath the path to the CSV file
     * @return a 2D char array representing the map grid
     * @throws IOException if the file cannot be read
     */
    public static char[][] loadMap(String filepath) throws IOException {
        java.io.File file = new java.io.File(filepath);

        // Try primary path first
        if (!file.exists()) {
            // Try with src/ prefix
            java.io.File srcFile = new java.io.File("src/" + filepath);
            if (srcFile.exists()) {
                file = srcFile;
                filepath = "src/" + filepath;
            }
        }

        if (!file.exists()) {
            throw new IOException("File not found: " + file.getAbsolutePath());
        }

        List<char[]> rows = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] cells = line.split(",");
                char[] row = new char[cells.length];

                for (int i = 0; i < cells.length; i++) {
                    String cell = cells[i].trim();
                    row[i] = cell.isEmpty() ? ' ' : cell.charAt(0);
                }

                rows.add(row);
            }
        }

        return rows.toArray(new char[0][]);
    }

    /**
     * Converts a 2D character array to a formatted string for display.
     *
     * @param grid the 2D char array
     * @return a formatted string representation of the grid
     */
    public static String gridToString(char[][] grid) {
        StringBuilder sb = new StringBuilder();
        for (char[] row : grid) {
            for (char cell : row) {
                sb.append(cell).append(" ");
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    /**
     * Gets the character at a specific position in a grid.
     *
     * @param grid the 2D char array
     * @param row the row index
     * @param col the column index
     * @return the character at that position, or ' ' if out of bounds
     */
    public static char getCellAt(char[][] grid, int row, int col) {
        if (row >= 0 && row < grid.length && col >= 0 && col < grid[0].length) {
            return grid[row][col];
        }
        return ' ';
    }

    /**
     * Finds the position of a character in a grid (first occurrence).
     *
     * @param grid the 2D char array
     * @param target the character to find
     * @return an int array {row, col}, or {-1, -1} if not found
     */
    public static int[] findPosition(char[][] grid, char target) {
        for (int i = 0; i < grid.length; i++) {
            for (int j = 0; j < grid[i].length; j++) {
                if (grid[i][j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{-1, -1};
    }
}

