"""chest_menu.py — Phase 2.7 interactive chest/lock/trap/loot modal (E key)."""
from __future__ import annotations
import pygame
import settings
from Mechanics.services.outcome import OutcomeCheck, OutcomeResolver, Degree, attribute_term

_BG       = (20,  20,  28)
_BORDER   = (80,  80, 110)
_TEXT     = (240, 240, 240)
_DIM      = (100, 100, 120)
_HL_BG    = (255, 210,  60)
_HL_TEXT  = (20,  20,  30)
_HINT     = (100, 100, 120)
_GREEN    = (68,  206,  27)
_ORANGE   = (242, 161,  52)
_RED      = (220,  60,  60)
_MSG_OK   = (130, 210, 130)
_MSG_FAIL = (220, 130, 130)

_W      = 420
_ROW_H  = 36
_PAD    = 12
_TITLE_H = 44


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fire_trap(chest, player) -> str:
    dmg = chest.trap_damage
    player.hp = max(1, player.hp - dmg)
    print(f"[TRAP] {chest.id} fired — {dmg} dmg, player HP now {player.hp}")
    return dmg


def _build_options(chest, player, inv_svc, item_repo) -> list[tuple[str, bool, str]]:
    """Return list of (label, enabled, action_key) for the current chest state."""
    options: list[tuple[str, bool, str]] = []

    if chest.locked:
        if chest.required_key_id:
            key_item = item_repo.find_by_id(chest.required_key_id)
            key_name = key_item.name if key_item else chest.required_key_id
            inv = inv_svc.get_inventory(player.entity_id)
            has_key = bool(inv and inv.find_stack(chest.required_key_id))
            options.append((f"Use {key_name}", has_key, "use_key"))
        else:
            inv = inv_svc.get_inventory(player.entity_id)
            has_pick = bool(inv and inv.find_stack("lockpick"))
            options.append(("Pick Lock (Lockpick)", has_pick, "pick_lock"))
        options.append(("Leave", True, "leave"))

    elif chest.is_trapped:
        options.append(("Disarm Trap", True, "disarm"))
        options.append(("Open Anyway", True, "open_anyway"))
        options.append(("Leave", True, "leave"))

    else:
        if chest.contents:
            for stack in chest.contents:
                wt = stack.item.weight
                lbl = f"Take {stack.item.name}  [{wt:.0f}wt]  (x{stack.qty})"
                options.append((lbl, True, f"take:{stack.item.id}"))
            options.append(("Take All", True, "take_all"))
        else:
            options.append(("(Chest is empty)", False, "empty"))
        options.append(("Leave", True, "leave"))

    return options


def _execute(action: str, chest, player, inv_svc, item_repo,
             resolver: OutcomeResolver) -> tuple[str, bool]:
    """Perform action. Returns (message, success)."""

    # --- Use specific key ---
    if action == "use_key":
        key_item = item_repo.find_by_id(chest.required_key_id)
        key_name = key_item.name if key_item else chest.required_key_id
        inv_svc.remove_item(player.entity_id, chest.required_key_id, 1)
        chest.locked = False
        if not chest.is_trapped:
            chest.is_opened = True
        return (f"{key_name} used — lock opened.", True)

    # --- Pick lock ---
    if action == "pick_lock":
        check = OutcomeCheck(
            base_value=settings.LOCKPICK_BASE_VALUE,
            difficulty=chest.lock_dc,
            attributes=attribute_term(player.attributes, "reflexes"),
        )
        result = resolver.resolve(check)

        if result.degree == Degree.CRITICAL_SUCCESS:
            chest.locked = False
            chest.is_trapped = False
            chest.is_opened = True
            return ("Critical success! Lock picked and trap disarmed.", True)

        if result.degree == Degree.SUCCESS:
            chest.locked = False
            if not chest.is_trapped:
                chest.is_opened = True
            return ("Lock picked.", True)

        if result.degree == Degree.FAILURE:
            inv_svc.remove_item(player.entity_id, "lockpick", 1)
            return ("Lockpick broke. Try again.", False)

        # CRITICAL_FAILURE
        inv_svc.remove_item(player.entity_id, "lockpick", 1)
        if chest.is_trapped:
            dmg = _fire_trap(chest, player)
            chest.is_trapped = False
            chest.locked = False
            chest.is_opened = True
            return (f"Lockpick snapped — trap triggered! {dmg} dmg (HP floored at 1).", False)
        return ("Lockpick snapped badly. Lock holds.", False)

    # --- Disarm trap ---
    if action == "disarm":
        check = OutcomeCheck(
            base_value=0,
            difficulty=settings.TRAP_DISARM_DC,
            attributes=attribute_term(player.attributes, "reflexes"),
        )
        result = resolver.resolve(check)
        if result.success:
            chest.is_trapped = False
            chest.is_opened = True
            return ("Trap disarmed.", True)
        dmg = _fire_trap(chest, player)
        chest.is_trapped = False
        chest.is_opened = True
        return (f"Disarm failed — trap triggered! {dmg} dmg (HP floored at 1).", False)

    # --- Open anyway ---
    if action == "open_anyway":
        dmg = _fire_trap(chest, player)
        chest.is_trapped = False
        chest.is_opened = True
        return (f"Trap triggered! {dmg} dmg (HP floored at 1).", False)

    # --- Take one item ---
    if action.startswith("take:"):
        item_id = action[5:]
        stack = next((s for s in chest.contents if s.item.id == item_id), None)
        if stack is None:
            return ("Item no longer in chest.", False)
        ok = inv_svc.take_from(chest, player.entity_id, stack.item, 1,
                               str_stat=player.stats.STR)
        chest.is_opened = True
        if ok:
            return (f"Took {stack.item.name}.", True)
        return ("Too heavy!", False)

    # --- Take all ---
    if action == "take_all":
        taken: list[str] = []
        skipped: list[str] = []
        for stack in list(chest.contents):
            ok = inv_svc.take_from(chest, player.entity_id, stack.item, stack.qty,
                                   str_stat=player.stats.STR)
            chest.is_opened = True
            if ok:
                taken.append(stack.item.name)
            else:
                skipped.append(stack.item.name)
        if taken and not skipped:
            return ("Took everything.", True)
        if taken:
            return (f"Took {', '.join(taken)}. Too heavy for the rest.", True)
        return ("Too heavy to take anything!", False)

    return ("", True)


def _draw_panel(screen: pygame.Surface, font: pygame.font.Font,
                chest, player, inv_svc,
                options: list[tuple[str, bool, str]],
                cursor: int, msg: str, msg_ok: bool) -> None:
    n = len(options)
    msg_rows = 1 if msg else 0
    modal_h = _TITLE_H + n * _ROW_H + _PAD * 3 + msg_rows * _ROW_H

    sw, sh = screen.get_size()
    mx = (sw - _W) // 2
    my = (sh - modal_h) // 2

    # Dim overlay
    dim = pygame.Surface((sw, sh), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 150))
    screen.blit(dim, (0, 0))

    # Panel
    pygame.draw.rect(screen, _BG,     (mx, my, _W, modal_h), border_radius=4)
    pygame.draw.rect(screen, _BORDER, (mx, my, _W, modal_h), 1, border_radius=4)

    # Title
    chest_name = chest.id.replace("_", " ").title()
    title_surf = font.render(f"[ {chest_name} ]", True, (200, 200, 240))
    screen.blit(title_surf, (mx + _PAD, my + _PAD))

    # Status badge
    if chest.locked:
        badge_txt, badge_col = "LOCKED", _RED
    elif chest.is_trapped:
        badge_txt, badge_col = "TRAPPED!", _ORANGE
    else:
        badge_txt, badge_col = "OPEN", _GREEN
    badge_surf = font.render(badge_txt, True, badge_col)
    screen.blit(badge_surf, (mx + _W - badge_surf.get_width() - _PAD, my + _PAD))

    # Player weight info
    if hasattr(player, "stats"):
        carried = inv_svc.carried_weight(player.entity_id)
        cap     = inv_svc.capacity(player.stats.STR)
        wt_txt  = font.render(f"{carried:.0f}/{cap:.0f}wt", True, _HINT)
        screen.blit(wt_txt, (mx + _W - wt_txt.get_width() - _PAD, my + _TITLE_H - wt_txt.get_height() - 2))

    # Options
    y = my + _TITLE_H
    for i, (lbl, enabled, _action) in enumerate(options):
        row_rect = pygame.Rect(mx + 2, y, _W - 4, _ROW_H)
        if i == cursor:
            pygame.draw.rect(screen, _HL_BG, row_rect, border_radius=3)
            color = _HL_TEXT
        else:
            color = _TEXT if enabled else _DIM
        txt_surf = font.render(lbl, True, color)
        screen.blit(txt_surf, (mx + _PAD, y + (_ROW_H - txt_surf.get_height()) // 2))
        y += _ROW_H

    # Message
    if msg:
        msg_color = _MSG_OK if msg_ok else _MSG_FAIL
        msg_surf = font.render(msg, True, msg_color)
        screen.blit(msg_surf, (mx + _PAD, y + (_PAD // 2)))

    # Hint line
    hint_y = my + modal_h - font.get_height() - 4
    hint_surf = font.render("↑↓ Navigate   ENTER Select   ESC / E Close", True, _HINT)
    # Draw hint at bottom-right so it doesn't overlap msg
    screen.blit(hint_surf,
                (mx + _W - hint_surf.get_width() - _PAD, hint_y))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_chest_menu(screen: pygame.Surface, clock: pygame.time.Clock,
                   font: pygame.font.Font, chest, player,
                   inv_svc, equip_svc, item_repo,
                   resolver: OutcomeResolver) -> None:
    """Block until player closes the chest menu. Mutates chest in place."""
    cursor  = 0
    msg     = ""
    msg_ok  = True

    while True:
        clock.tick(settings.FPS)
        options = _build_options(chest, player, inv_svc, item_repo)
        n = max(len(options), 1)
        cursor = min(cursor, n - 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_e):
                    return
                elif event.key == pygame.K_UP:
                    cursor = (cursor - 1) % n
                elif event.key == pygame.K_DOWN:
                    cursor = (cursor + 1) % n
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    lbl, enabled, action = options[cursor]
                    if action == "leave":
                        return
                    if action == "empty":
                        continue
                    if enabled:
                        prev_locked  = chest.locked
                        prev_trapped = chest.is_trapped
                        msg, msg_ok = _execute(
                            action, chest, player, inv_svc, item_repo, resolver
                        )
                        # Reset cursor when chest state changes
                        if chest.locked != prev_locked or chest.is_trapped != prev_trapped:
                            cursor = 0
                    else:
                        msg    = "You don't have what's needed."
                        msg_ok = False

        _draw_panel(screen, font, chest, player, inv_svc, options, cursor, msg, msg_ok)
        pygame.display.flip()
