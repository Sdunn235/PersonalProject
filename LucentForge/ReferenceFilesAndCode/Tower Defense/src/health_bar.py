# health_bar.py
# Tower Defense Game - Health Bar Module
import pygame
import game_settings

# The HealthBar class will be used to draw a health bar for enemies or towers
class HealthBar:
    def __init__(self, width=32, height=5, border_color=(0, 0, 0), background_color=(100, 100, 100)):
        # Bar dimensions (can scale later based on enemy/tower type)
        self.width = width
        self.height = height

        # Color settings
        self.border_color = border_color         # Outline color
        self.background_color = background_color # Background for empty HP portion

    # This will be called to draw the health bar
    def draw(self, surface, target_rect, current_hp, max_hp, position="top", scale=1.0):
        # Adjust the size of the health bar based on scale
        bar_width = int(self.width * scale)
        bar_height = int(self.height * scale)

        # Calculate the position of the bar
        x = target_rect.centerx - bar_width // 2 # Center the bar horizontally
        if position == "top":
            y = target_rect.top - bar_height - 2 # Slight gap above sprite
        elif position == "bottom":
            y = target_rect.bottom + 2           # Slight gap below sprite
        else:
            y = target_rect.top - bar_height - 2 # Default to top if position is unknown

        # Prevent division errors or drawing bars with broken values
        current_hp = max(0, min(current_hp, max_hp)) # Clamp current HP between 0 and max

        # Draw the background bar (gray or empty part)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, self.background_color, bg_rect)

        # Draw the filled portion if we have valid health
        if max_hp > 0:
            fill_width = int(bar_width * (current_hp / max_hp)) # Scale fill by HP %
            fill_rect = pygame.Rect(x, y, fill_width, bar_height)

            # Calculate HP percent bucket (round down to nearest 10)
            hp_percent = float((current_hp / max_hp) * 100)
            hp_bucket = (hp_percent // 10) * 10

            # Get color from game_settings.hp_color
            hex_color = game_settings.hp_color.get(hp_bucket, "#ffffff") # default to white if not found
            fill_color = self.hex_to_rgb(hex_color)

            pygame.draw.rect(surface, fill_color, fill_rect)

        # Draw the border of the bar
        pygame.draw.rect(surface, self.border_color, bg_rect, 1) # 1 pixel border thickness

    # Helper to convert hex color string to RGB tuple
    def hex_to_rgb(self, hex_string):
        hex_string = hex_string.lstrip('#')
        return tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))