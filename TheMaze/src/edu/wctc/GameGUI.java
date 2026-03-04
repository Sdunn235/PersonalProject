package edu.wctc;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.Timer;

/**
 * GameGUI - Swing-based GUI for The Maze game.
 * Uses Java Swing (no external libraries needed) for maximum compatibility.
 * Renders the game with colors, buttons, and a visual grid.
 */
public class GameGUI extends JFrame {

    private Maze maze;
    private JTextPane narrativeArea;
    private JLabel roomLabel;
    private JLabel scoreLabel;
    private JLabel inventoryLabel;
    private JPanel mapPanel;
    private JButton[] directionButtons = new JButton[4];  // N, S, E, W only (no U/D)
    private JButton[] actionButtons = new JButton[5];

    // Player position tracking
    private int playerRow = 5;  // Starting position (center-ish)
    private int playerCol = 5;
    private String lastRoomName = "";  // Track room changes

    private static final int TILE_SIZE = 35;
    private static final int GRID_WIDTH = 12;
    private static final int GRID_HEIGHT = 12;

    // Colors
    private static final Color WALL_COLOR = new Color(51, 51, 51);
    private static final Color FLOOR_COLOR = new Color(136, 136, 136);
    private static final Color PLAYER_COLOR = new Color(255, 215, 0);
    private static final Color WEAPON_COLOR = new Color(255, 99, 71);
    private static final Color NPC_COLOR = new Color(65, 105, 225);
    private static final Color DOOR_COLOR = new Color(50, 205, 50);
    private static final Color EXIT_COLOR = new Color(255, 20, 147);
    private static final Color BG_COLOR = new Color(26, 26, 26);
    private static final Color TEXT_COLOR = new Color(200, 200, 200);

    public GameGUI() {
        try {
            maze = new Maze();
            setupUI();
            updateDisplay();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void setupUI() {
        setTitle("🏰 THE MAZE - Dungeon Adventure");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 900);
        setLocationRelativeTo(null);
        setBackground(BG_COLOR);

        // Main container
        JPanel mainPanel = new JPanel(new BorderLayout(15, 15));
        mainPanel.setBackground(BG_COLOR);
        mainPanel.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));

        // TOP: Title and Stats
        mainPanel.add(createTopPanel(), BorderLayout.NORTH);

        // CENTER: Map and Narrative
        mainPanel.add(createCenterPanel(), BorderLayout.CENTER);

        // BOTTOM: Controls
        mainPanel.add(createBottomPanel(), BorderLayout.SOUTH);

        add(mainPanel);
        setVisible(true);

        // Display starting room's sensory narrative AFTER UI is visible
        // Use Timer to ensure it appears at the end of initial text
        Timer startTimer = new Timer(500, e -> {
            String startingNarrative = maze.getStartingEntranceNarrative();
            if (!startingNarrative.isEmpty()) {
                appendSensoryNarrative(startingNarrative);
            }
        });
        startTimer.setRepeats(false);
        startTimer.start();
    }

    private JPanel createTopPanel() {
        JPanel topPanel = new JPanel(new BorderLayout(10, 10));
        topPanel.setBackground(new Color(42, 42, 42));
        topPanel.setBorder(BorderFactory.createMatteBorder(0, 0, 2, 0, new Color(68, 68, 68)));
        topPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Title
        JLabel titleLabel = new JLabel("⚔️ THE MAZE GAME ⚔️");
        titleLabel.setFont(new Font("Arial", Font.BOLD, 28));
        titleLabel.setForeground(new Color(255, 215, 0));

        // Room name
        roomLabel = new JLabel("Starting Adventure...");
        roomLabel.setFont(new Font("Arial", Font.BOLD, 18));
        roomLabel.setForeground(new Color(135, 206, 235));

        // Stats
        scoreLabel = new JLabel("Score: 0");
        scoreLabel.setFont(new Font("Arial", Font.BOLD, 14));
        scoreLabel.setForeground(new Color(144, 238, 144));

        inventoryLabel = new JLabel("Inventory: Empty");
        inventoryLabel.setFont(new Font("Arial", Font.BOLD, 14));
        inventoryLabel.setForeground(new Color(255, 182, 193));

        JPanel statsPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 30, 5));
        statsPanel.setBackground(new Color(42, 42, 42));
        statsPanel.add(scoreLabel);
        statsPanel.add(inventoryLabel);

        JPanel leftPanel = new JPanel(new BorderLayout(10, 10));
        leftPanel.setBackground(new Color(42, 42, 42));
        leftPanel.add(titleLabel, BorderLayout.NORTH);
        leftPanel.add(roomLabel, BorderLayout.CENTER);
        leftPanel.add(statsPanel, BorderLayout.SOUTH);

        topPanel.add(leftPanel, BorderLayout.CENTER);
        return topPanel;
    }

    private JPanel createCenterPanel() {
        JPanel centerPanel = new JPanel(new BorderLayout(15, 0));
        centerPanel.setBackground(BG_COLOR);

        // LEFT: Map display
        mapPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                drawMap(g);
            }
        };
        mapPanel.setBackground(new Color(34, 34, 34));
        mapPanel.setBorder(BorderFactory.createLineBorder(new Color(68, 68, 68), 2));
        mapPanel.setPreferredSize(new Dimension(TILE_SIZE * GRID_WIDTH + 20, TILE_SIZE * GRID_HEIGHT + 20));

        // RIGHT: Narrative area
        JPanel narrativePanel = new JPanel(new BorderLayout(10, 10));
        narrativePanel.setBackground(new Color(34, 34, 34));
        narrativePanel.setBorder(BorderFactory.createLineBorder(new Color(68, 68, 68), 2));

        JLabel narrativeTitle = new JLabel("📖 Story & Events");
        narrativeTitle.setFont(new Font("Arial", Font.BOLD, 14));
        narrativeTitle.setForeground(new Color(255, 215, 0));

        narrativeArea = new JTextPane();
        narrativeArea.setEditable(false);
        narrativeArea.setBackground(new Color(26, 26, 26));
        narrativeArea.setFont(new Font("Courier New", Font.PLAIN, 12));
        narrativeArea.setText("Welcome to The Maze!\n\n" +
                            "Your quest:\n1. Find and loot the weapon\n2. Talk to the Sage for knowledge\n3. Defeat the Boss\n\n" +
                            "Good luck, adventurer!\n\n");

        JScrollPane scrollPane = new JScrollPane(narrativeArea);
        scrollPane.getViewport().setBackground(new Color(26, 26, 26));

        narrativePanel.add(narrativeTitle, BorderLayout.NORTH);
        narrativePanel.add(scrollPane, BorderLayout.CENTER);

        centerPanel.add(mapPanel, BorderLayout.WEST);
        centerPanel.add(narrativePanel, BorderLayout.CENTER);

        return centerPanel;
    }

    private JPanel createBottomPanel() {
        JPanel bottomPanel = new JPanel(new BorderLayout(20, 15));
        bottomPanel.setBackground(new Color(42, 42, 42));
        bottomPanel.setBorder(BorderFactory.createMatteBorder(2, 0, 0, 0, new Color(68, 68, 68)));

        // Movement controls
        JPanel movementPanel = createMovementPanel();

        // Action controls
        JPanel actionPanel = createActionPanel();

        bottomPanel.add(movementPanel, BorderLayout.WEST);
        bottomPanel.add(actionPanel, BorderLayout.CENTER);

        return bottomPanel;
    }

    private JPanel createMovementPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(new Color(26, 26, 26));
        panel.setBorder(BorderFactory.createLineBorder(new Color(68, 68, 68), 1));
        panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Title at top
        JLabel titleLabel = new JLabel("D-Pad Movement");
        titleLabel.setFont(new Font("Arial", Font.BOLD, 12));
        titleLabel.setForeground(new Color(255, 215, 0));
        panel.add(titleLabel, BorderLayout.NORTH);

        // D-Pad grid in center - SIMPLIFIED: Only N, S, E, W (no U/D)
        JPanel dpadPanel = new JPanel(new GridBagLayout());
        dpadPanel.setBackground(new Color(26, 26, 26));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);

        // NORTH (top center)
        gbc.gridx = 1;
        gbc.gridy = 0;
        directionButtons[0] = createButton("↑ N", 'n');
        dpadPanel.add(directionButtons[0], gbc);

        // WEST (left), SOUTH (center), EAST (right)
        gbc.gridx = 0;
        gbc.gridy = 1;
        directionButtons[1] = createButton("← W", 'w');
        dpadPanel.add(directionButtons[1], gbc);

        gbc.gridx = 1;
        gbc.gridy = 1;
        directionButtons[3] = createButton("↓ S", 's');
        dpadPanel.add(directionButtons[3], gbc);

        gbc.gridx = 2;
        gbc.gridy = 1;
        directionButtons[2] = createButton("E →", 'e');
        dpadPanel.add(directionButtons[2], gbc);

        // Note: No Up/Down buttons - use stairs/ladder interaction to change maps

        panel.add(dpadPanel, BorderLayout.CENTER);
        return panel;
    }

    private JPanel createActionPanel() {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        panel.setBackground(new Color(26, 26, 26));
        panel.setBorder(BorderFactory.createLineBorder(new Color(68, 68, 68), 1));

        actionButtons[0] = createActionButton("💬 Interact", () -> {
            // Check if there's a door adjacent to the player (N/S/E/W)
            Room currentRoom = maze.getCurrentRoom();
            int doorRow = -1;
            int doorCol = -1;

            if (currentRoom != null && currentRoom.layoutGrid != null) {
                // Check all 4 directions for a door
                int[][] directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}}; // N, S, W, E
                for (int[] dir : directions) {
                    int checkRow = playerRow + dir[0];
                    int checkCol = playerCol + dir[1];

                    if (checkRow >= 0 && checkRow < GRID_HEIGHT &&
                        checkCol >= 0 && checkCol < GRID_WIDTH) {
                        char cellContent = currentRoom.layoutGrid[checkRow][checkCol];
                        if (cellContent == 'd') {
                            doorRow = checkRow;
                            doorCol = checkCol;
                            break;
                        }
                    }
                }
            }

            // If door found adjacent, transition to next room
            if (doorRow >= 0 && doorCol >= 0) {
                appendNarrative("You walk through the door...");

                // Determine which direction to go based on door location
                char directionToMove = 'e';  // Default to east

                if (currentRoom != null && currentRoom.layoutGrid != null) {
                    // Check which side the door is on
                    if (doorCol == 0) {
                        directionToMove = 'w';  // Door on left wall, go west
                    } else if (doorCol == GRID_WIDTH - 1) {
                        directionToMove = 'e';  // Door on right wall, go east
                    }
                }

                boolean moved = maze.move(directionToMove);

                if (moved) {
                    appendNarrative("You enter the next room.");

                    // Display sensory narrative if first entry
                    String entranceNarrative = maze.getLastEntranceNarrative();
                    if (!entranceNarrative.isEmpty()) {
                        appendSensoryNarrative(entranceNarrative);
                    }

                    // After transition, position player at the corresponding door in new room
                    Room newRoom = maze.getCurrentRoom();
                    if (newRoom != null && newRoom.layoutGrid != null) {
                        // Find the door in the new room's layout and position player next to it
                        for (int i = 0; i < GRID_HEIGHT; i++) {
                            for (int j = 0; j < GRID_WIDTH; j++) {
                                if (newRoom.layoutGrid[i][j] == 'd') {
                                    // Place player next to the door in the same row
                                    if (j == 0) {
                                        playerCol = 1;  // Door on left wall, stand right of it
                                    } else if (j == GRID_WIDTH - 1) {
                                        playerCol = GRID_WIDTH - 2;  // Door on right wall, stand left of it
                                    }
                                    playerRow = i;  // Same row as door
                                    lastRoomName = newRoom.getName();  // Update room tracker
                                    updateDisplay();
                                    return;
                                }
                            }
                        }
                    }
                } else {
                    appendNarrative("The door is locked!");
                }
                updateDisplay();
            } else {
                // Otherwise, normal interaction
                String result = maze.interactWithCurrentRoom();

                // Use appropriate color based on interaction type
                if (result.contains("LONGSWORD") || result.contains("sword")) {
                    appendItemNarrative(result);
                } else if (result.contains("CREATURE") || result.contains("BOSS") || result.contains("Sage")) {
                    appendBossNarrative(result);
                } else {
                    appendNarrative(result);
                }
                updateDisplay();
            }
        });

        actionButtons[1] = createActionButton("💰 Loot", () -> {
            String result = maze.lootCurrentRoom();

            // Use gold color for loot success
            if (result.contains("picked up")) {
                appendItemNarrative(result);
            } else {
                appendNarrative(result);
            }
            updateDisplay();
        });

        actionButtons[2] = createActionButton("🎒 Inventory", () -> {
            appendNarrative(maze.getPlayerInventory());
        });

        actionButtons[3] = createActionButton("⚔️ FIGHT", () -> {
            String result = maze.exitCurrentRoom();

            // Use colored narratives for boss fight outcomes
            if (result.contains("VICTORY")) {
                appendNarrativeWithColor(result, new Color(144, 238, 144));  // Green for victory
            } else if (result.contains("DEFEAT") || result.contains("GAME OVER")) {
                appendNarrativeWithColor(result, new Color(255, 99, 71));  // Red for defeat
            } else if (result.contains("CREATURE") || result.contains("Sage speaks")) {
                appendBossNarrative(result);
            } else {
                appendNarrative(result);
            }

            updateDisplay();
            if (maze.isFinished()) {
                showGameOver();
            }
        });

        actionButtons[4] = createActionButton("❌ Quit", () -> {
            System.exit(0);
        });

        for (JButton btn : actionButtons) {
            panel.add(btn);
        }

        return panel;
    }

    private JButton createButton(String label, char direction) {
        JButton btn = new JButton(label);
        btn.setFont(new Font("Arial", Font.BOLD, 11));
        btn.setPreferredSize(new Dimension(70, 50));
        btn.setBackground(new Color(0, 102, 204));
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

        btn.addActionListener(e -> {
            // Move player in the grid ONLY - NO room transitions from direction buttons
            boolean moved = movePlayerOnGrid(direction);

            if (moved) {
                appendNarrative("✓ You move " + getDirectionName(direction) + ".");
            } else {
                appendNarrative("✗ You cannot move in that direction.");
            }
            updateDisplay();
        });

        btn.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                btn.setBackground(new Color(0, 136, 255));
            }
            public void mouseExited(java.awt.event.MouseEvent evt) {
                btn.setBackground(new Color(0, 102, 204));
            }
        });

        return btn;
    }

    /**
     * Move the player icon on the current grid.
     * @param direction the direction to move (n/s/e/w only)
     * @return true if move was valid, false otherwise
     */
    private boolean movePlayerOnGrid(char direction) {
        int newRow = playerRow;
        int newCol = playerCol;

        switch (direction) {
            case 'n': newRow--; break;  // North = up
            case 's': newRow++; break;  // South = down
            case 'w': newCol--; break;  // West = left
            case 'e': newCol++; break;  // East = right
            default: return false;
        }

        // Check bounds
        if (newRow < 0 || newRow >= GRID_HEIGHT || newCol < 0 || newCol >= GRID_WIDTH) {
            return false;
        }

        // Check collision (assuming we have access to current room's collision grid)
        char[][] collision = getCurrentRoomCollisionGrid();
        if (collision != null && collision[newRow][newCol] == '1') {
            return false;  // Wall or obstacle
        }

        // Move successful - update player position
        playerRow = newRow;
        playerCol = newCol;
        return true;
    }

    /**
     * Get the collision grid for the current room.
     */
    private char[][] getCurrentRoomCollisionGrid() {
        try {
            Room currentRoom = maze.getCurrentRoom();
            if (currentRoom != null && currentRoom.collisionGrid != null) {
                return currentRoom.collisionGrid;
            }
        } catch (Exception e) {
            // If we can't access collision grid, allow movement
        }
        return null;
    }

    private JButton createActionButton(String label, Runnable action) {
        JButton btn = new JButton(label);
        btn.setFont(new Font("Arial", Font.BOLD, 11));
        btn.setPreferredSize(new Dimension(110, 40));
        btn.setBackground(new Color(204, 102, 0));
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

        btn.addActionListener(e -> action.run());

        btn.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                btn.setBackground(new Color(255, 136, 0));
            }
            public void mouseExited(java.awt.event.MouseEvent evt) {
                btn.setBackground(new Color(204, 102, 0));
            }
        });

        return btn;
    }

    private void drawMap(Graphics g) {
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        char[][] layout = getCurrentRoomLayout();

        int startX = 10;
        int startY = 10;

        for (int row = 0; row < GRID_HEIGHT; row++) {
            for (int col = 0; col < GRID_WIDTH; col++) {
                int x = startX + col * TILE_SIZE;
                int y = startY + row * TILE_SIZE;

                drawTile(g2, x, y, layout[row][col]);
            }
        }

        // Grid lines
        g2.setColor(new Color(68, 68, 68));
        g2.setStroke(new BasicStroke(0.5f));
        for (int i = 0; i <= GRID_WIDTH; i++) {
            g2.drawLine(startX + i * TILE_SIZE, startY, startX + i * TILE_SIZE, startY + GRID_HEIGHT * TILE_SIZE);
        }
        for (int i = 0; i <= GRID_HEIGHT; i++) {
            g2.drawLine(startX, startY + i * TILE_SIZE, startX + GRID_WIDTH * TILE_SIZE, startY + i * TILE_SIZE);
        }
    }

    private void drawTile(Graphics2D g, int x, int y, char cellType) {
        switch (cellType) {
            case 'w':
                g.setColor(WALL_COLOR);
                g.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                break;
            case 'f':
                g.setColor(FLOOR_COLOR);
                g.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                break;
            case '@':
                g.setColor(PLAYER_COLOR);
                g.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                g.setColor(Color.BLACK);
                g.setFont(new Font("Arial", Font.BOLD, 18));
                g.drawString("@", x + 12, y + 24);
                break;
            case 'W':
                g.setColor(WEAPON_COLOR);
                g.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                g.setColor(Color.WHITE);
                g.setFont(new Font("Arial", Font.BOLD, 14));
                g.drawString("W", x + 12, y + 22);
                break;
            case 'n':
                g.setColor(NPC_COLOR);
                g.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                g.setColor(Color.WHITE);
                g.setFont(new Font("Arial", Font.BOLD, 14));
                g.drawString("n", x + 13, y + 22);
                break;
            case 'd':
                g.setColor(DOOR_COLOR);
                g.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                g.setColor(Color.BLACK);
                g.setFont(new Font("Arial", Font.BOLD, 14));
                g.drawString("d", x + 13, y + 22);
                break;
            case 'e':
                g.setColor(EXIT_COLOR);
                g.fillRect(x, y, TILE_SIZE, TILE_SIZE);
                g.setColor(Color.WHITE);
                g.setFont(new Font("Arial", Font.BOLD, 14));
                g.drawString("e", x + 13, y + 22);
                break;
            default:
                g.setColor(FLOOR_COLOR);
                g.fillRect(x, y, TILE_SIZE, TILE_SIZE);
        }
    }

    private char[][] getCurrentRoomLayout() {
        try {
            Room currentRoom = maze.getCurrentRoom();
            if (currentRoom == null) {
                return createDefaultLayout();
            }

            // Use the actual CSV layout from the room
            if (currentRoom.layoutGrid != null) {
                // Create a copy to avoid modifying the original
                char[][] displayGrid = new char[GRID_HEIGHT][GRID_WIDTH];

                // Copy layout
                for (int i = 0; i < Math.min(GRID_HEIGHT, currentRoom.layoutGrid.length); i++) {
                    for (int j = 0; j < Math.min(GRID_WIDTH, currentRoom.layoutGrid[i].length); j++) {
                        displayGrid[i][j] = currentRoom.layoutGrid[i][j];
                    }
                }

                // Overlay objects if available
                if (currentRoom.objectsGrid != null) {
                    for (int i = 0; i < Math.min(GRID_HEIGHT, currentRoom.objectsGrid.length); i++) {
                        for (int j = 0; j < Math.min(GRID_WIDTH, currentRoom.objectsGrid[i].length); j++) {
                            char obj = currentRoom.objectsGrid[i][j];
                            if (obj != ' ') {
                                displayGrid[i][j] = obj;
                            }
                        }
                    }
                }

                // Place player at tracked position
                if (playerRow >= 0 && playerRow < GRID_HEIGHT &&
                    playerCol >= 0 && playerCol < GRID_WIDTH) {
                    displayGrid[playerRow][playerCol] = '@';
                }

                return displayGrid;
            }
        } catch (Exception e) {
            System.err.println("Error loading room layout: " + e.getMessage());
        }

        return createDefaultLayout();
    }

    /**
     * Create a default layout if none is available.
     */
    private char[][] createDefaultLayout() {
        char[][] layout = new char[GRID_HEIGHT][GRID_WIDTH];

        for (int i = 0; i < GRID_HEIGHT; i++) {
            for (int j = 0; j < GRID_WIDTH; j++) {
                if (i == 0 || i == GRID_HEIGHT - 1 || j == 0 || j == GRID_WIDTH - 1) {
                    layout[i][j] = 'w';
                } else {
                    layout[i][j] = 'f';
                }
            }
        }

        // Place player
        layout[playerRow][playerCol] = '@';

        return layout;
    }

    private void updateDisplay() {
        String currentRoomName = maze.getCurrentRoom().getName();

        // Check if room changed
        if (!currentRoomName.equals(lastRoomName)) {
            // Room changed - reset player position to spawn point
            lastRoomName = currentRoomName;
            Room currentRoom = maze.getCurrentRoom();
            if (currentRoom != null && currentRoom.objectsGrid != null) {
                // Look for player spawn position 'p' in objects grid
                boolean foundPlayer = false;
                for (int i = 0; i < currentRoom.objectsGrid.length && !foundPlayer; i++) {
                    for (int j = 0; j < currentRoom.objectsGrid[i].length && !foundPlayer; j++) {
                        if (currentRoom.objectsGrid[i][j] == 'p') {
                            playerRow = i;
                            playerCol = j;
                            foundPlayer = true;
                        }
                    }
                }
                // If no 'p' marker, center player
                if (!foundPlayer) {
                    playerRow = GRID_HEIGHT / 2;
                    playerCol = GRID_WIDTH / 2;
                }
            }
        }

        roomLabel.setText("📍 " + currentRoomName);
        scoreLabel.setText("⭐ Score: " + maze.getPlayerScore());
        inventoryLabel.setText("🎒 Inventory: " + (maze.getPlayerInventory().equals("Inventory: Empty") ? "Empty" : maze.getPlayerInventory()));

        mapPanel.repaint();
    }

    private void appendNarrative(String text) {
        appendNarrativeWithColor(text, new Color(144, 238, 144));  // Default green
    }

    private void appendNarrativeWithColor(String text, Color color) {
        try {
            javax.swing.text.SimpleAttributeSet attrs = new javax.swing.text.SimpleAttributeSet();
            javax.swing.text.StyleConstants.setForeground(attrs, color);
            narrativeArea.getDocument().insertString(narrativeArea.getDocument().getLength(), "\n" + text, attrs);
            narrativeArea.setCaretPosition(narrativeArea.getDocument().getLength());
        } catch (Exception e) {
            System.err.println("Error appending narrative: " + e.getMessage());
        }
    }

    private void appendSensoryNarrative(String text) {
        appendNarrativeWithColor(text, new Color(135, 206, 235));  // Cyan for sensory
    }

    private void appendItemNarrative(String text) {
        appendNarrativeWithColor(text, new Color(255, 215, 0));  // Gold for items
    }

    private void appendBossNarrative(String text) {
        appendNarrativeWithColor(text, new Color(255, 99, 71));  // Red for danger
    }

    private void showGameOver() {
        appendNarrativeWithColor("════════════════════════════════════════", new Color(255, 215, 0));
        appendNarrativeWithColor("🎮 GAME OVER", new Color(255, 215, 0));
        appendNarrativeWithColor("📊 Final Score: " + maze.getPlayerScore(), new Color(255, 215, 0));
        appendNarrativeWithColor("════════════════════════════════════════", new Color(255, 215, 0));
    }

    private String getDirectionName(char direction) {
        return switch (direction) {
            case 'n' -> "north";
            case 's' -> "south";
            case 'e' -> "east";
            case 'w' -> "west";
            default -> "unknown";
        };
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new GameGUI());
    }
}

