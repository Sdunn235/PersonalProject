# sprite.py — Pygame sprite wrapper for entities
# Supports colored-circle fallback OR a spritesheet with 4-directional walking animation.
# Sheet layout (all assets in library): 3 cols × 4 rows — down / left / right / up
from __future__ import annotations
import os
import pygame
import settings
from Mechanics.renderer.health_bar import draw_stat_bar

SHEET_COLS = 3
SHEET_ROWS = 4
DIRECTIONS = ("down", "left", "right", "up")
ANIM_SPEED = 0.1   # frame index advance per update tick


def _load_directional_frames(path: str, size: int) -> dict[str, list[pygame.Surface]]:
    """
    Load a sprite sheet (3 cols × 4 rows) and return a dict of direction → frame list.
    Each frame is scaled to size×size.
    Ported from ReferenceFilesAndCode/Tower Defense/src/image_utils.py
    """
    sheet = pygame.image.load(path).convert_alpha()
    sw, sh = sheet.get_size()
    fw = sw // SHEET_COLS
    fh = sh // SHEET_ROWS
    frames: dict[str, list[pygame.Surface]] = {}
    for row_idx, direction in enumerate(DIRECTIONS):
        row_frames = []
        for col_idx in range(SHEET_COLS):
            frame = sheet.subsurface((col_idx * fw, row_idx * fh, fw, fh))
            row_frames.append(pygame.transform.scale(frame, (size, size)))
        frames[direction] = row_frames
    return frames


class EntitySprite(pygame.sprite.Sprite):
    def __init__(self, entity: "Entity",
                 color: tuple[int, int, int] = settings.NPC_COLOR,
                 size: int = settings.TILE_SIZE - 4,
                 image_path: str | None = None):
        super().__init__()
        self.entity = entity
        self.color  = color
        self.size   = size

        self._frames_by_dir: dict[str, list[pygame.Surface]] | None = None
        self.direction   = "down"
        self.anim_index  = 0.0
        self._prev_x     = entity.x
        self._prev_y     = entity.y

        if image_path and os.path.isfile(image_path):
            self._frames_by_dir = _load_directional_frames(image_path, size)
            self.image = self._frames_by_dir["down"][0]
        else:
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            self._redraw_circle()

        self.rect = self.image.get_rect()

    def _redraw_circle(self) -> None:
        self.image.fill((0, 0, 0, 0))
        half = self.size // 2
        pygame.draw.circle(self.image, self.color, (half, half), half)
        pygame.draw.circle(self.image, (0, 0, 0), (half, half), half, 2)

    def update(self) -> None:
        dx = self.entity.x - self._prev_x
        dy = self.entity.y - self._prev_y
        moving = abs(dx) > 0.5 or abs(dy) > 0.5

        if self._frames_by_dir:
            # Determine facing direction from movement vector
            if moving:
                if abs(dx) > abs(dy):
                    self.direction = "right" if dx > 0 else "left"
                else:
                    self.direction = "down" if dy > 0 else "up"
                self.anim_index = (self.anim_index + ANIM_SPEED) % SHEET_COLS
            else:
                self.anim_index = 0.0   # idle — hold first frame

            self.image = self._frames_by_dir[self.direction][int(self.anim_index)]

        self._prev_x = self.entity.x
        self._prev_y = self.entity.y

        self.rect.centerx = int(self.entity.x) + settings.LEVEL_X
        self.rect.centery = int(self.entity.y) + settings.LEVEL_Y

    def draw_overlays(self, surface: pygame.Surface) -> None:
        x = self.entity.x + settings.LEVEL_X
        y = self.entity.y + settings.LEVEL_Y
        # Three stacked bars: HP (red), SP (green), MP (purple)
        draw_stat_bar(surface, x, y, self.entity.hp,     self.entity.max_hp,
                      (229, 31, 31),  (60, 20, 20),  offset_y=-22)
        draw_stat_bar(surface, x, y, self.entity.cycles, self.entity.max_cycles,
                      (68, 206, 27),  (30, 60, 30),  offset_y=-18)
        draw_stat_bar(surface, x, y, self.entity.mp,     self.entity.max_mp,
                      (130, 60, 200), (50, 20, 70),  offset_y=-14)
        font = pygame.font.SysFont(None, 14)
        txt = font.render(self.entity.name, True, settings.TEXT_COLOR)
        surface.blit(txt, (x - txt.get_width() // 2, y - 30))
