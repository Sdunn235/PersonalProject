# trap_overlay.py — world-space markers for perceived traps (§M8).
from __future__ import annotations
import pygame
import settings

_MARK_COLOR = (230, 60, 60)
_BACK_COLOR = (20, 20, 24)


def draw_trap_markers(surface: pygame.Surface, chest_reg: dict,
                      font: pygame.font.Font) -> None:
    """Draw a red '!' above every chest whose trap the player has perceived and
    which is still trapped + unopened. The visual half of the §M8 reveal."""
    ts = settings.TILE_SIZE
    for chest in chest_reg.values():
        if not (chest.is_trapped and chest.trap_perceived and not chest.is_opened):
            continue
        cx = chest.col * ts + ts // 2
        cy = chest.row * ts + ts // 2
        glyph = font.render("!", True, _MARK_COLOR)
        rect = glyph.get_rect(center=(cx, cy - ts // 4))
        pygame.draw.rect(surface, _BACK_COLOR, rect.inflate(6, 2))
        surface.blit(glyph, rect)
