# game_settings.py
# Tower Defense Game - Game Settings Module
NUM_OF_COLS =18 # Number of columns in the game grid
NUM_OF_ROWS = 18 # Number of rows in the game grid
COL_SIZE = 32 # Size of each cell in the grid
ROW_SIZE = 32 # Size of each cell in the grid
GAME_HEIGHT = NUM_OF_ROWS * ROW_SIZE # Height of the game grid
GAME_WIDTH = NUM_OF_COLS * COL_SIZE # Width of the game grid


fps = 60    # Frames per second
dt = 0 # Delta time (time since last frame)

tick_of_last_enemy_spawn = 0 # Time of the last enemy spawn
enemy_spawn_interval = 500 # Interval between enemy spawns in milliseconds
enemy_wave_size = 10 # Number of enemies in each wave

player_money = 100 # Starting money for the player

hp_color = {}
hp_color[100] = "#44ce1b"  # Green for 100% HP
hp_color[90] = "#bbdb44"   # Light green for 90% HP
hp_color[80] = "#dbd144"   # Yellow for 80% HP
hp_color[70] = "#f7e379"   # Dark yellow for 70% HP
hp_color[60] = "#f7e379"   # Orange for 60% HP
hp_color[50] = "#f7e379"   # Red for 50% HP 
hp_color[40] = "#f7e379"   # Dark red for 40% HP
hp_color[30] = "#f2a134"   # Darker red for 30% HP
hp_color[20] = "#f2a134"   # Very dark red for 20% HP
hp_color[10] = "#e51f1f"   # Almost black for 10%
hp_color[0] = "#e51f1f"    # Black for 0% HP

# To do images for hp variations
# hp_images = {}    
# hp_images = {
#    100: "Tower Defense/src/images/hp/100.png",
#    90: "Tower Defense/src/images/hp/90.png",
#    80: "Tower Defense/src/images/hp/80.png",
#    70: "Tower Defense/src/images/hp/70.png",
#    60: "Tower Defense/src/images/hp/60.png",
#    50: "Tower Defense/src/images/hp/50.png",
#    40: "Tower Defense/src/images/hp/40.png",
#    30: "Tower Defense/src/images/hp/30.png",
#    20: "Tower Defense/src/images/hp/20.png",
#    10: "Tower Defense/src/images/hp/10.png",
#    0: "Tower Defense/src/images/hp/0.png"
#}


# Enemy configuration by type
