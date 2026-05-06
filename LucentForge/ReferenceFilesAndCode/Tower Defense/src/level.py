# level.py
# Tower Defense Game - Level Class Module
import csv
import pygame
import game_settings

class Level():
    def __init__(self):
        self.background = None

        # Initialize tile grids
        self.blocked_tiles = [[False for _ in range(game_settings.NUM_OF_COLS)] for _ in range(game_settings.NUM_OF_ROWS)]
        self.path_tiles = [[False for _ in range(game_settings.NUM_OF_COLS)] for _ in range(game_settings.NUM_OF_ROWS)]

        self.enemy_waypoints = []  # List of enemy waypoints

    def get_grid_from_csv(self, path_to_csv):
        with open(path_to_csv, "r") as file:
            grid = list(csv.reader(file))
        return grid

    def add_cell_to_tiles(self, cell, tiles):
        tiles[cell[1]][cell[0]] = True  # Note: [row][col]

    def add_grid_to_tiles(self, grid_to_add, tiles):
        for row in range(len(tiles)):
            for col in range(len(tiles[row])):
                grid_value = int(grid_to_add[row][col])
                if grid_value >= 0:
                    tiles[row][col] = True

    def add_grid_to_path_tiles(self, grid_to_add):
        for row in range(len(self.path_tiles)):
            for col in range(len(self.path_tiles[row])):
                grid_value = int(grid_to_add[row][col])
                if grid_value >= 0:
                    self.path_tiles[row][col] = True

    def create_waypoint_vector(self, waypoints):
        for waypoint in waypoints:
            x = waypoint[0] * game_settings.COL_SIZE + game_settings.COL_SIZE // 2
            y = waypoint[1] * game_settings.ROW_SIZE + game_settings.ROW_SIZE // 2
            self.enemy_waypoints.append(pygame.Vector2(x, y))

    def print_grid(self):
        for row in range(len(self.blocked_tiles)):
            for col in range(len(self.blocked_tiles[row])):
                print(f"{self.blocked_tiles[row][col]} ", end="\t")
            print()
