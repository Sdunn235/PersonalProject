# image_utils.py
# Tower Defense Game - Image Utilities Module

import pygame

def load_and_scale_image(path, target_size, fallback_color=(255, 0, 255)):
    """
    Loads an image from the given path and scales it to target_size.
    If the image can't be loaded, returns a placeholder surface filled with fallback_color.
    """
    try:
        if not isinstance(path, str):
            raise FileNotFoundError("Image path is not a valid string.")
        image = pygame.image.load(path).convert_alpha()
        scaled_image = pygame.transform.smoothscale(image, target_size)
        return scaled_image
    except (pygame.error, FileNotFoundError) as e:
        print(f"[WARNING] Image not found: {path} — using fallback placeholder. Error: {e}")
        fallback = pygame.Surface(target_size, pygame.SRCALPHA)
        fallback.fill(fallback_color)
        return fallback


def rotate_image_to_velocity(image: pygame.Surface, velocity: pygame.Vector2) -> pygame.Surface:
    base_direction = pygame.Vector2(1, 0)
    angle = -base_direction.angle_to(velocity)
    return pygame.transform.rotate(image, angle)


def load_directional_frames(sprite_sheet_path, frame_width, frame_height):
    sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
    sheet_width, sheet_height = sprite_sheet.get_size()

    directions = ("down", "left", "right", "up")
    columns = sheet_width // frame_width

    expected_height = frame_height * len(directions)
    assert sheet_height >= expected_height, (
        f"Sprite sheet '{sprite_sheet_path}' is too short: expected {expected_height}px."
    )

    frames_by_direction = {}
    for row_idx, direction in enumerate(directions):
        row_frames = []
        for col_idx in range(columns):
            frame_rect = pygame.Rect(
                col_idx * frame_width,
                row_idx * frame_height,
                frame_width,
                frame_height
            )
            frame = sprite_sheet.subsurface(frame_rect).copy()
            row_frames.append(frame)
        frames_by_direction[direction] = row_frames

    return frames_by_direction


def get_placeholder_color(projectile_type):
    return {
        "arrow": (200, 200, 200),
        "magic": (128, 0, 255),
        "fireball": (255, 80, 0),
        "ice_arrow": (0, 200, 255),
        "fire_arrow": (255, 100, 0),
        "king_buff": (255, 255, 0),
    }.get(projectile_type, (255, 255, 255))
