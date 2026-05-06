# health_bar.py — HP bar drawn above an entity
# Adapted from Tower Defense health_bar.py
from __future__ import annotations
import pygame


def draw_stat_bar(surface: pygame.Surface, x: float, y: float,
                  value: int, max_value: int,
                  color: tuple, empty_color: tuple,
                  width: int = 24, height: int = 3,
                  offset_y: int = 0) -> None:
    """Compact fixed-color bar for world-map overlays (HP / SP / MP)."""
    if max_value <= 0:
        return
    ratio = max(0.0, value / max_value)
    bg_rect   = pygame.Rect(x - width // 2, y + offset_y, width, height)
    fill_w    = int(width * ratio)
    fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, fill_w, height)
    pygame.draw.rect(surface, empty_color, bg_rect)
    if fill_w > 0:
        pygame.draw.rect(surface, color, fill_rect)
    pygame.draw.rect(surface, (0, 0, 0), bg_rect, 1)


def draw_health_bar(surface: pygame.Surface, x: float, y: float,
                    hp: int, max_hp: int, width: int = 28, height: int = 4,
                    offset_y: int = -18) -> None:
    if max_hp <= 0:
        return
    ratio = max(0.0, hp / max_hp)
    bg_rect  = pygame.Rect(x - width // 2, y + offset_y, width, height)
    fill_w   = int(width * ratio)
    fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, fill_w, height)

    color = (
        (68, 206, 27)  if ratio > 0.6 else
        (242, 161, 52) if ratio > 0.3 else
        (229, 31, 31)
    )

    pygame.draw.rect(surface, (30, 30, 30), bg_rect)
    if fill_w > 0:
        pygame.draw.rect(surface, color, fill_rect)
    pygame.draw.rect(surface, (0, 0, 0), bg_rect, 1)
