# The Maze - Dark Fantasy Dungeon Crawler

A Java-based game where players explore a multi-room dungeon, collect weapons, gather knowledge from NPCs, and face a final boss encounter. Success depends on strategic preparation and a bit of luck!

## Quick Start

### How to Run

**Option 1: Using the Launcher Script (Easiest)**
```bash
RUN_GAME.bat
# Choose [1] for GUI version
```

**Option 2: From Command Line**
```bash
javac -d . src/edu/wctc/*.java
java edu.wctc.GameGUI
```

**Option 3: Console Version (No GUI)**
```bash
java edu.wctc.Main
```

## Game Overview

### Your Quest
1. **Weapon Chamber**: Find and loot the Iron Longsword (+50 points)
2. **Sage's Chamber**: Talk to the Sage for knowledge (up to 3 times, +25 each)
3. **Boss Chamber**: Face the final challenge (+500 points if successful)

### Success Rates
- **No weapon**: 0% (automatic loss)
- **Weapon only**: 50% success
- **Weapon + 1 sage talk**: 65% success
- **Weapon + 2 sage talks**: 80% success
- **Weapon + 3 sage talks**: 95% success ⭐

## Controls

### Movement (D-Pad Style)
```
    ↑ N
 ← W   ↓ S  → E
```
- Click directional buttons to move one cell at a time
- Walls block movement
- Doors transition between rooms

### Actions
- **💬 Interact**: Talk to NPCs
- **💰 Loot**: Pick up items
- **🎒 Inventory**: View what you're carrying
- **🚪 Exit Room**: Leave room / battle boss
- **❌ Quit**: Close game

## Project Structure

```
The Maze/
├── src/edu/wctc/
│   ├── *.java              (12 Java source files)
│   ├── maps/               (CSV map data)
│   │   ├── WeaponChamber/
│   │   ├── SagesChamber/
│   │   └── BossChamber/
│   └── images/             (Sprite assets)
├── RUN_GAME.bat           (Launcher)
└── README.md              (This file)
```

## Architecture

### Classes
- **Maze.java**: Game engine and state manager
- **Room.java**: Abstract base class for rooms
- **Player.java**: Score and inventory tracking
- **Main.java**: Console version driver
- **GameGUI.java**: JavaFX GUI implementation
- **MapLoader.java**: CSV file reader

### Room Implementations
- **WeaponChamber**: Lootable (get the weapon)
- **SagesChamber**: Interactable (gather knowledge)
- **BossChamber**: Exitable (final challenge)

### Interfaces
- **Lootable**: `loot(Player): String`
- **Interactable**: `interact(Player): String`
- **Exitable**: `exit(Player): String`

## Requirements Met

✅ 3 Interfaces (Lootable, Interactable, Exitable)  
✅ 4 Core Classes (Room, Player, Maze, Main)  
✅ 3+ Concrete Room Classes  
✅ 10 Game Commands (n/s/e/w/i/l/x/v)  
✅ GUI Implementation (Swing)  
✅ CSV-Based Map System  
✅ Proper OOP Design  

## Features

- **Grid-Based Movement**: 12×12 room layouts with collision detection
- **Color-Coded GUI**: Professional dark theme with intuitive controls
- **Interactive Objects**: Weapons, NPCs, exits placed on map grids
- **Probabilistic Outcomes**: Boss battle success depends on preparation
- **Replayability**: Random outcomes ensure multiple playthroughs
- **Score Tracking**: Accumulate points through strategic decisions

## Technologies

- **Language**: Java 8+
- **GUI**: Java Swing (no external dependencies)
- **Data Format**: CSV files for room layouts
- **Build**: Standard Java compilation (javac)

## Game Loop

1. Display current room description and map
2. Show available exits and current score
3. Accept player command (movement or action)
4. Process command and update game state
5. Return feedback to player
6. Repeat until game is finished

## File Format: CSV Maps

Each room has 3 CSV files:

**layout.csv** - Terrain layer
```
w = wall (blocks movement)
f = floor (walkable)
d = door (transition to next room)
```

**objects.csv** - Game objects
```
p = player spawn point
W = weapon (lootable)
n = NPC (interactable)
e = exit (battle point)
```

**collision.csv** - Movement validation
```
1 = blocked
0 = passable
```

## Gameplay Tips

- **Speed Run**: Get weapon, skip sage, fight boss (50% odds)
- **Safe Run**: Get weapon, talk to sage 3x, fight boss (95% odds)
- **Strategic**: Plan your route before starting
- **Replayability**: Try different approaches for variety

## License

This is a school assignment for WCTC (Wisconsin Colleges Teaching Consortium).

---

**Status**: Complete and Ready for Submission  
**Last Updated**: February 8, 2026

