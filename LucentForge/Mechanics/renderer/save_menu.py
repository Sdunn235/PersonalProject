# save_menu.py — Modal save-slot selection UI (Phase 1.6)
#
# Two public entry points following the combat_scene.py modal sub-loop pattern:
#   run_load_menu  — shown on launch; all 4 slots + New Game row
#   run_save_menu  — shown on S key; manual slots 1-3 only (slot 0 is system-only)
from __future__ import annotations

import pygame
import settings
from Mechanics.data.context import GameContext

# ── Color palette (matches combat_scene.py) ──────────────────────────────────
_BG      = (20, 20, 28)
_BORDER  = (80, 80, 110)
_TEXT    = (240, 240, 240)
_DIM     = (150, 150, 170)
_HEADER  = (200, 200, 230)
_HL_BG   = (255, 210, 60)
_HL_TEXT = (20, 20, 30)
_HINT    = (100, 100, 120)
_DIVIDER = (60, 60, 80)

_TOWN_COLORS = {
    "STABLE":     (68, 206, 27),
    "STRAINED":   (242, 161, 52),
    "COLLAPSING": (229, 31, 31),
}

_SLOT_LABELS = {
    0: "[Autosave]",
    1: "Save Slot 1",
    2: "Save Slot 2",
    3: "Save Slot 3",
}

_W       = 420   # modal width
_ROW_H   = 36    # height per slot row
_PAD     = 12
_TITLE_H = 44    # space from top of modal to first row


def _format_day(tick_count: int) -> str:
    tpd = settings.TICKS_PER_DAY
    return f"Day {tick_count / tpd:.1f}" if tpd > 0 else f"Tick {tick_count}"


def _draw_slot_menu(
    screen: pygame.Surface,
    title: str,
    slot_infos: list[dict | None],
    labels: list[str],
    cursor: int,
    hint: str,
    show_new_game: bool,
    fonts: tuple,
) -> None:
    title_font, slot_font, info_font, hint_font = fonts
    n = len(labels)

    modal_h = _TITLE_H + _PAD + n * _ROW_H
    if show_new_game:
        modal_h += 14 + _ROW_H   # divider gap + New Game row
    modal_h += _PAD + 26          # bottom padding + hint line

    mx = (settings.WINDOW_W - _W) // 2
    my = (settings.WINDOW_H - modal_h) // 2

    pygame.draw.rect(screen, _BG, (mx, my, _W, modal_h))
    pygame.draw.rect(screen, _BORDER, (mx, my, _W, modal_h), 2)

    # Title
    t = title_font.render(title, True, _HEADER)
    screen.blit(t, (mx + (_W - t.get_width()) // 2, my + _PAD))

    y = my + _TITLE_H + _PAD

    # Slot rows
    for i, (label, info) in enumerate(zip(labels, slot_infos)):
        is_sel = (i == cursor)
        row_rect = pygame.Rect(mx + 4, y, _W - 8, _ROW_H - 2)
        if is_sel:
            pygame.draw.rect(screen, _HL_BG, row_rect)

        txt_color = _HL_TEXT if is_sel else _TEXT

        lbl = slot_font.render(label, True, txt_color)
        screen.blit(lbl, (mx + _PAD + 6, y + (_ROW_H - lbl.get_height()) // 2))

        if info is not None:
            tc = _HL_TEXT if is_sel else _TOWN_COLORS.get(info["town_state"], _TEXT)
            meta = info_font.render(
                f"{_format_day(info['tick_count'])}  {info['town_state']}", True, tc
            )
        else:
            meta = info_font.render("— Empty —", True, _HL_TEXT if is_sel else _DIM)

        screen.blit(meta, (mx + _W - meta.get_width() - _PAD, y + (_ROW_H - meta.get_height()) // 2))
        y += _ROW_H

    # New Game row (load menu only)
    if show_new_game:
        new_game_idx = len(labels)
        pygame.draw.line(screen, _DIVIDER, (mx + _PAD, y + 5), (mx + _W - _PAD, y + 5))
        y += 14

        is_sel = (cursor == new_game_idx)
        row_rect = pygame.Rect(mx + 4, y, _W - 8, _ROW_H - 2)
        if is_sel:
            pygame.draw.rect(screen, _HL_BG, row_rect)

        ng = slot_font.render("New Game", True, _HL_TEXT if is_sel else _TEXT)
        screen.blit(ng, (mx + _PAD + 6, y + (_ROW_H - ng.get_height()) // 2))

    # Hint line
    h = hint_font.render(hint, True, _HINT)
    screen.blit(h, (mx + (_W - h.get_width()) // 2, my + modal_h - 22))


def run_load_menu(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    ctx: GameContext,
    font: pygame.font.Font,
) -> int | None:
    """Modal launch menu — all 4 slots plus a New Game row.

    Returns slot_id (0-3) to load, or None for New Game / cancel.
    Selecting an empty slot is treated as New Game.
    """
    all_slot_ids = [0, 1, 2, 3]
    labels = [_SLOT_LABELS[sid] for sid in all_slot_ids]
    slot_infos = ctx.save_manager.list_all_slots(all_slot_ids)
    n_options = len(all_slot_ids) + 1   # 4 slots + New Game
    cursor = 0

    fonts = (
        pygame.font.SysFont(None, 28),
        pygame.font.SysFont(None, 24),
        pygame.font.SysFont(None, 18),
        pygame.font.SysFont(None, 16),
    )

    while True:
        clock.tick(settings.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    cursor = (cursor - 1) % n_options
                elif event.key == pygame.K_DOWN:
                    cursor = (cursor + 1) % n_options
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if cursor == len(all_slot_ids):          # New Game row
                        return None
                    if slot_infos[cursor] is None:           # empty slot → New Game
                        return None
                    return all_slot_ids[cursor]
                elif event.key == pygame.K_ESCAPE:
                    return None

        screen.fill(settings.BG_COLOR)
        _draw_slot_menu(
            screen, "LOAD GAME", slot_infos, labels, cursor,
            "[↑↓] Select    [Enter] Confirm    [Esc] Cancel",
            show_new_game=True, fonts=fonts,
        )
        pygame.display.flip()


def run_save_menu(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    ctx: GameContext,
    font: pygame.font.Font,
) -> int | None:
    """Modal save-slot picker triggered by S key during gameplay.

    Shows only manual slots 1-3; slot 0 is reserved for autosave/quit-save.
    Returns slot_id (1-3) or None if cancelled.
    """
    manual_slot_ids = [1, 2, 3]
    labels = [_SLOT_LABELS[sid] for sid in manual_slot_ids]
    slot_infos = ctx.save_manager.list_all_slots(manual_slot_ids)
    n_options = len(manual_slot_ids)
    cursor = 0

    fonts = (
        pygame.font.SysFont(None, 28),
        pygame.font.SysFont(None, 24),
        pygame.font.SysFont(None, 18),
        pygame.font.SysFont(None, 16),
    )

    while True:
        clock.tick(settings.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    cursor = (cursor - 1) % n_options
                elif event.key == pygame.K_DOWN:
                    cursor = (cursor + 1) % n_options
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return manual_slot_ids[cursor]
                elif event.key == pygame.K_ESCAPE:
                    return None

        screen.fill(settings.BG_COLOR)
        _draw_slot_menu(
            screen, "SAVE GAME", slot_infos, labels, cursor,
            "[↑↓] Select    [Enter] Save    [Esc] Cancel",
            show_new_game=False, fonts=fonts,
        )
        pygame.display.flip()
