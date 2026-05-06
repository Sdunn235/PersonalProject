# hud.py — HUD: shows entity needs panel with 3-zone bars, threshold markers, HP bar, and state
from __future__ import annotations
import pygame
import settings
from Mechanics.needs.need import Need, NeedZone


_BAR_W  = 110
_BAR_H  = 10
_MARGIN = 8
_PAD    = 6


def draw_hud(surface: pygame.Surface, entity, needs: list[Need],
             state_label: str, font: pygame.font.Font) -> None:
    """
    Draw the needs HUD panel for any entity.
    entity      — any object with .name, .hp, .max_hp
    needs       — list of Need objects
    state_label — display string for the current AI/behavior state
    """
    n_rows  = len(needs) + 2   # needs + HP bar + state label
    panel_h = n_rows * (_BAR_H + _MARGIN + 16) + _PAD * 2 + 32
    panel_w = _BAR_W + 90 + _PAD * 2
    panel_x = settings.LEVEL_X + settings.LEVEL_W + 10
    panel_y = 10

    # Background panel
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((20, 20, 20, 185))
    surface.blit(panel, (panel_x, panel_y))

    y = panel_y + _PAD

    # --- Entity name header ---
    name_txt = font.render(entity.name, True, (220, 220, 240))
    surface.blit(name_txt, (panel_x + _PAD, y))
    y += 16

    # --- Need bars ---
    for need in needs:
        _draw_need_row(surface, font, need, panel_x, y)
        y += 14 + _BAR_H + _MARGIN

    # --- HP bar ---
    y += 4
    hp_pct = max(0.0, entity.hp / entity.max_hp)
    hp_color = (
        (68, 206, 27)  if hp_pct > 0.6 else
        (242, 161, 52) if hp_pct > 0.3 else
        (229, 31, 31)
    )
    hp_lbl = font.render("HP", True, settings.TEXT_COLOR)
    hp_val = font.render(f"{entity.hp:.0f}/{entity.max_hp}", True, settings.TEXT_COLOR)
    surface.blit(hp_lbl, (panel_x + _PAD, y))
    surface.blit(hp_val, (panel_x + _PAD + 20, y))
    y += 14
    bg = pygame.Rect(panel_x + _PAD, y, _BAR_W, _BAR_H)
    fill_w = int(_BAR_W * hp_pct)
    pygame.draw.rect(surface, (40, 40, 40), bg)
    if fill_w > 0:
        pygame.draw.rect(surface, hp_color, pygame.Rect(bg.x, bg.y, fill_w, _BAR_H))
    pygame.draw.rect(surface, (0, 0, 0), bg, 1)
    y += _BAR_H + _MARGIN

    # --- State label ---
    y += 4
    state_txt = font.render(f"State: {state_label}", True, (180, 180, 180))
    surface.blit(state_txt, (panel_x + _PAD, y))
    y += 16

    # --- Tab hint ---
    hint = font.render("[TAB] cycle", True, (100, 100, 120))
    surface.blit(hint, (panel_x + _PAD, y))


def _draw_need_row(surface: pygame.Surface, font: pygame.font.Font,
                   need: Need, px: int, y: int) -> None:
    """Draw one need label, value, and 3-zone bar with two threshold markers."""
    bar_color   = need.zone_color
    label_color = settings.COLOR_CRITICAL if need.zone == NeedZone.CRITICAL else \
                  settings.COLOR_WARNING   if need.zone == NeedZone.WARNING  else \
                  settings.TEXT_COLOR

    lbl = font.render(need.label, True, label_color)
    val = font.render(f"{need.current_value:5.1f}", True, label_color)
    surface.blit(lbl, (px + _PAD, y))
    surface.blit(val, (px + _PAD + 60, y))

    y += 14
    bg_rect   = pygame.Rect(px + _PAD, y, _BAR_W, _BAR_H)
    fill_w    = int(_BAR_W * (need.current_value / 100.0))
    fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, max(0, fill_w), _BAR_H)

    pygame.draw.rect(surface, (40, 40, 40), bg_rect)
    if fill_w > 0:
        pygame.draw.rect(surface, bar_color, fill_rect)

    # Warning threshold marker (orange line)
    wx = px + _PAD + int(_BAR_W * (need.warning_threshold / 100.0))
    pygame.draw.line(surface, settings.COLOR_WARNING,
                     (wx, y), (wx, y + _BAR_H), 2)

    # Critical threshold marker (red line)
    cx = px + _PAD + int(_BAR_W * (need.critical_threshold / 100.0))
    pygame.draw.line(surface, settings.COLOR_CRITICAL,
                     (cx, y), (cx, y + _BAR_H), 2)

    pygame.draw.rect(surface, (0, 0, 0), bg_rect, 1)
