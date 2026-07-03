import pygame
import settings
from Mechanics.data.context import GameContext
from Mechanics.renderer.save_menu import run_save_menu

_BG      = (20, 20, 28)
_HEADER  = (200, 200, 230)
_HL_BG   = (255, 210, 60)
_HL_TEXT = (20, 20, 30)
_TEXT    = (240, 240, 240)
_HINT    = (100, 100, 120)

_OPTIONS = ["Resume", "Save", "Quit"]


def run_pause_menu(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    ctx: GameContext,
    font: pygame.font.Font,
    world_sim, sources, controllers, player,
    player_needs, defeated_npcs, combat_cooldowns,
) -> str:
    """
    Modal pause screen. Returns:
      "resume" — player chose Resume or pressed Esc again
      "quit"   — player chose Quit (save-on-quit handled internally)
    """
    cursor = 0
    W, H = screen.get_size()

    while True:
        clock.tick(settings.FPS)

        title_font  = pygame.font.SysFont(None, 36)
        option_font = pygame.font.SysFont(None, 28)
        hint_font   = pygame.font.SysFont(None, 18)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Let main.py post-loop handle the window-close save path
                return "resume"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
                if event.key in (pygame.K_UP, pygame.K_w):
                    cursor = (cursor - 1) % len(_OPTIONS)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    cursor = (cursor + 1) % len(_OPTIONS)
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    choice = _OPTIONS[cursor]
                    if choice == "Resume":
                        return "resume"
                    if choice == "Save":
                        _slot = run_save_menu(screen, clock, ctx, font)
                        if _slot is not None:
                            ctx.save_manager.snapshot(
                                world_sim, sources, controllers,
                                player, player_needs, defeated_npcs,
                                combat_cooldowns, slot_id=_slot,
                            )
                        # fall through — stay in pause menu after save
                    if choice == "Quit":
                        if settings.SAVE_ON_QUIT:
                            ctx.save_manager.snapshot(
                                world_sim, sources, controllers,
                                player, player_needs, defeated_npcs,
                                combat_cooldowns,
                                slot_id=settings.AUTOSAVE_SLOT_ID,
                            )
                        return "quit"

        _draw_pause(screen, W, H, cursor, title_font, option_font, hint_font)
        pygame.display.flip()


def _draw_pause(screen, W, H, cursor, title_font, option_font, hint_font):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    panel_w, panel_h = 320, 220
    px = (W - panel_w) // 2
    py = (H - panel_h) // 2
    pygame.draw.rect(screen, _BG, (px, py, panel_w, panel_h), border_radius=8)
    pygame.draw.rect(screen, (80, 80, 110), (px, py, panel_w, panel_h),
                     width=2, border_radius=8)

    title_surf = title_font.render("PAUSED", True, _HEADER)
    screen.blit(title_surf, (px + (panel_w - title_surf.get_width()) // 2, py + 18))

    for i, label in enumerate(_OPTIONS):
        row_y = py + 70 + i * 38
        if i == cursor:
            pygame.draw.rect(screen, _HL_BG,
                             (px + 20, row_y - 4, panel_w - 40, 32),
                             border_radius=4)
            text_surf = option_font.render(f"▶  {label}", True, _HL_TEXT)
        else:
            text_surf = option_font.render(f"   {label}", True, _TEXT)
        screen.blit(text_surf, (px + 30, row_y))

    hint = hint_font.render(
        "[↑↓] Select    [Enter] OK    [Esc] Resume", True, _HINT
    )
    screen.blit(hint, (px + (panel_w - hint.get_width()) // 2, py + panel_h - 26))
