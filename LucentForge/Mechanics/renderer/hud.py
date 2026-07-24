# hud.py — HUD: shows entity needs panel with 3-zone bars, threshold markers, HP bar, and state
from __future__ import annotations
# noinspection PyPackageRequirements
import pygame
import settings
from Mechanics.needs.need import Need, NeedZone

_BAR_W  = 110
_BAR_H  = 10
_MARGIN = 8
_PAD    = 6
_LINE   = 15

# Biochem section chemicals and display labels (in order)
_CHEM_ROWS = [
    ("comfort",        "Comfort",  settings.COLOR_FINE),
    ("stress",         "Stress",   settings.COLOR_CRITICAL),
    ("affinity_strain","Strain",   (200, 80, 200)),
    ("pain",           "Pain",     settings.COLOR_CRITICAL),
    ("fear",           "Fear",     settings.COLOR_WARNING),
]


def draw_hud(surface: pygame.Surface, entity, needs: list[Need],
             state_label: str, font: pygame.font.Font,
             controller=None) -> None:
    """
    Draw the needs HUD panel for any entity.
    entity      — any object with .name, .hp, .max_hp
    needs       — list of Need objects
    state_label — display string for the current AI/behavior state
    controller  — optional NpcController; when provided, adds biochem detail section
    """
    biochem_rows = (len(_CHEM_ROWS) + 4) if controller is not None else 0
    n_rows  = len(needs) + 2   # needs + HP bar + state label
    panel_h = (n_rows * (_BAR_H + _MARGIN + 16) + _PAD * 2 + 32
               + biochem_rows * _LINE + (_PAD if biochem_rows else 0))
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

    # --- Biochem detail (NPC only — controller required) ---
    if controller is not None:
        brain = controller.brain
        chem  = brain.chemicals

        y += 4
        surface.blit(font.render("- BIOCHEM -", True, (200, 200, 230)), (panel_x + _PAD, y))
        y += _LINE

        # Reactive chemicals
        for key, label, hi_color in _CHEM_ROWS:
            val = chem.get(key)
            color = hi_color if val > 0.05 else (100, 100, 120)
            txt = font.render(f"{label:<8} {val:.3f}", True, color)
            surface.blit(txt, (panel_x + _PAD, y))
            y += _LINE

        y += 4
        # Drive urgencies
        surface.blit(font.render("- DRIVES -", True, (200, 200, 230)), (panel_x + _PAD, y))
        y += _LINE
        for drive in brain.drives:
            urgency = drive.compute_urgency(chem, brain.traits)
            u_color = (settings.COLOR_CRITICAL if urgency > 0.7
                       else settings.COLOR_WARNING if urgency > 0.4
                       else (100, 100, 120))
            txt = font.render(f"{drive.need_id:<8} {urgency:.3f}", True, u_color)
            surface.blit(txt, (panel_x + _PAD, y))
            y += _LINE

        y += 4
        # Affinity + memory
        aff_score = getattr(controller, "affinity_comfort", 0.0)
        aff_color = (settings.COLOR_FINE     if aff_score > 0.05
                     else settings.COLOR_CRITICAL if aff_score < -0.05
                     else (100, 100, 120))
        surface.blit(font.render(f"Aff score {aff_score:+.2f}", True, aff_color),
                     (panel_x + _PAD, y))
        y += _LINE
        best = getattr(controller, "memory", None)
        best = best.best_region() if best else None
        if best:
            surface.blit(font.render(f"Best rgn  {best[1]:+.2f}", True, (130, 130, 160)),
                         (panel_x + _PAD, y))
            y += _LINE

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
