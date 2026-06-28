# observation_panel.py — Heartbeat-6 world-overview panel.
# Rendered in the free left margin (the per-entity HUD owns the right margin).
# Shows: WORLD (day/town/food/threat), SOURCES (finite stock bars), NPCS
# (per-character state + priority need + target). Toggled by the 'O' key.
from __future__ import annotations
import pygame
import settings
from Mechanics.needs.needs_system import get_priority_need
from Mechanics.renderer.health_bar import draw_stat_bar

_PAD = 8
_LINE = 16


def draw_observation_panel(surface, world_sim, sources, npc_list,
                           defeated, font) -> None:
    px = settings.OBS_PANEL_X
    pw = settings.OBS_PANEL_W
    bar_w = pw - 2 * _PAD
    bar_cx = px + _PAD + bar_w // 2   # draw_stat_bar centers on x

    living = [(n, c) for n, c, _ in npc_list if n.entity_id not in defeated]
    finite = [s for s in sources if s.is_finite]

    n_lines = 6 + 1 + 2 * len(finite) + 1 + len(living) + 2
    panel_h = min(n_lines * _LINE + _PAD * 2, settings.WINDOW_H - 20)

    panel = pygame.Surface((pw, panel_h), pygame.SRCALPHA)
    panel.fill(settings.OBS_PANEL_BG)
    surface.blit(panel, (px, 10))

    x = px + _PAD
    y = 10 + _PAD

    def line(txt, color=settings.OBS_LABEL_COLOR):
        nonlocal y
        surface.blit(font.render(txt, True, color), (x, y))
        y += _LINE

    # --- WORLD ---
    line("- WORLD -", settings.OBS_HEADER_COLOR)
    line(f"Day {world_sim.clock.day:.2f} ({world_sim.clock.time_phase.value})")
    town = world_sim.town.state.value
    line(f"Town: {town.upper()}",
         settings.TOWN_STATE_COLORS.get(town, settings.OBS_LABEL_COLOR))
    line(f"Food: {world_sim.resources.food_total:.0f}")
    threat = world_sim.threat.threat_level
    line(f"Threat: {threat:.0f} ({world_sim.threat.stage.value})")
    threat_color = (settings.COLOR_FINE if threat < settings.THREAT_PASSIVE_MAX
                    else settings.COLOR_WARNING if threat < settings.THREAT_RAIDING_MAX
                    else settings.COLOR_CRITICAL)
    draw_stat_bar(surface, bar_cx, y, int(threat), 100,
                  threat_color, (40, 40, 40), width=bar_w, height=6)
    y += _LINE

    # --- SOURCES ---
    line("- SOURCES -", settings.OBS_HEADER_COLOR)
    for s in finite:
        ratio = s.stock / s.capacity if s.capacity > 0 else 1.0
        color = (settings.COLOR_FINE if ratio > 0.5
                 else settings.COLOR_WARNING if ratio > 0.15
                 else settings.COLOR_CRITICAL)
        line(f"{s.label} {s.stock:.0f}/{s.capacity:.0f}")
        draw_stat_bar(surface, bar_cx, y, int(s.stock), int(s.capacity),
                      color, (40, 40, 40), width=bar_w, height=5)
        y += _LINE

    # --- NPCS ---
    line("- NPCS -", settings.OBS_HEADER_COLOR)
    for npc, ctrl in living:
        pn = get_priority_need(ctrl.needs)
        need_str = f"{pn.label[:4]} {pn.current_value:.0f}" if pn else "ok"
        need_color = pn.zone_color if pn else settings.COLOR_FINE
        target = ctrl.target_source.label if ctrl.target_source else "-"
        surface.blit(font.render(f"{npc.name[:8]} {ctrl.state[:4]}", True,
                                 settings.OBS_LABEL_COLOR), (x, y))
        surface.blit(font.render(f"{need_str} >{target[:5]}", True, need_color),
                     (x + 96, y))
        y += _LINE

    # --- Footer ---
    y += 4
    surface.blit(font.render("[O] hide", True, settings.OBS_HINT_COLOR), (x, y))
