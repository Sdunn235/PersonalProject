# combat_scene.py — Full-screen RPG combat stage
# Takes over the main loop during an encounter, returns "win" / "lose" / "flee".
from __future__ import annotations
import os
from dataclasses import dataclass
import pygame
import settings
from Mechanics.data.context import GameContext
from Mechanics.combat.combat import take_turn
from Mechanics.combat.fighter import build_fighter
from Mechanics.combat.rng import SimpleRng
from Mechanics.combat.ability_sets import get_abilities, get_basic_attack
from Mechanics.combat.spell_sets import get_spells
from Mechanics.combat.equip import resolve_equipment
from Mechanics.combat.items import build_bag
from Mechanics.entities.factory import get_sprite_path

# --- Layout constants ---
FIGHTER_SIZE  = 96           # px for scaled fighter sprite in combat view
LOG_LINES     = 4            # visible lines in the battle log
BAR_W         = 200          # bar width (HP / SP / MP)
BAR_H         = 16
RESULT_PAUSE  = 2000         # ms to show win/lose message before returning

DARK_BG       = (18, 18, 28)
PANEL_COLOR   = (30, 30, 45)
BORDER_COLOR  = (80, 80, 110)
LOG_BG        = (22, 22, 35)
TEXT_WHITE    = (240, 240, 240)
TEXT_DIM      = (150, 150, 170)
MENU_HL       = (255, 210, 60)
MENU_HL_TEXT  = (20, 20, 30)
HP_RED        = (229, 31, 31)
HP_EMPTY      = (60, 20, 20)
STAMINA_GREEN = (68, 206, 27)
STAMINA_EMPTY = (30, 60, 30)
MP_PURPLE     = (130, 60, 200)
MP_EMPTY      = (50, 20, 70)

SHEET_COLS    = 3

# Flee option
_FLEE_OPTION  = {"id": "_flee", "name": "Flee", "kind": "flee", "cost_cycles": 0}

# Top-level ACTIONS menu
_MAIN_OPTIONS = [
    {"id": "_attack",    "name": "Attack",    "kind": "action_attack"},
    {"id": "_abilities", "name": "Abilities", "kind": "action_submenu", "submenu": "abilities"},
    {"id": "_spells",    "name": "Spells",    "kind": "action_submenu", "submenu": "spells"},
    {"id": "_backpack",  "name": "Backpack",  "kind": "action_submenu", "submenu": "backpack"},
    {"id": "_flee",      "name": "Flee",      "kind": "flee"},
]


@dataclass
class _MenuState:
    state: str = "main"   # "main" | "abilities" | "spells" | "backpack"
    main_cursor: int = 0
    sub_cursor:  int = 0


# --- Helpers ---

def _load_fighter_surface(image_path: str | None, size: int,
                          flip: bool = False) -> pygame.Surface | None:
    if not image_path or not os.path.isfile(image_path):
        return None
    sheet = pygame.image.load(image_path).convert_alpha()
    sw, sh = sheet.get_size()
    frame_w = sw // SHEET_COLS
    frame_h = sh // (sh // frame_w)
    frame = sheet.subsurface((0, 0, frame_w, frame_h))
    scaled = pygame.transform.scale(frame, (size, size))
    if flip:
        scaled = pygame.transform.flip(scaled, True, False)
    return scaled


def _hp_color(hp: int, max_hp: int) -> tuple:
    return HP_RED


def _draw_hp_bar(surf: pygame.Surface, x: int, y: int,
                 hp: int, max_hp: int, label: str, font: pygame.font.Font):
    ratio = hp / max(1, max_hp)
    fill  = int(BAR_W * ratio)
    pygame.draw.rect(surf, HP_EMPTY,              (x, y, BAR_W, BAR_H))
    pygame.draw.rect(surf, _hp_color(hp, max_hp), (x, y, fill,  BAR_H))
    pygame.draw.rect(surf, BORDER_COLOR,          (x, y, BAR_W, BAR_H), 1)
    txt = font.render(f"{label}  {hp}/{max_hp}", True, TEXT_WHITE)
    surf.blit(txt, (x + 4, y + (BAR_H - txt.get_height()) // 2))


def _draw_stamina_bar(surf: pygame.Surface, x: int, y: int,
                      cycles: int, max_cycles: int, font: pygame.font.Font):
    ratio = cycles / max(1, max_cycles)
    fill  = int(BAR_W * ratio)
    pygame.draw.rect(surf, STAMINA_EMPTY,  (x, y, BAR_W, BAR_H))
    pygame.draw.rect(surf, STAMINA_GREEN, (x, y, fill,  BAR_H))
    pygame.draw.rect(surf, BORDER_COLOR,  (x, y, BAR_W, BAR_H), 1)
    txt = font.render(f"SP  {cycles}/{max_cycles}", True, TEXT_WHITE)
    surf.blit(txt, (x + 4, y + (BAR_H - txt.get_height()) // 2))


def _draw_mp_bar(surf: pygame.Surface, x: int, y: int,
                 mp: int, max_mp: int, font: pygame.font.Font):
    ratio = mp / max(1, max_mp)
    fill  = int(BAR_W * ratio)
    pygame.draw.rect(surf, MP_EMPTY,  (x, y, BAR_W, BAR_H))
    pygame.draw.rect(surf, MP_PURPLE, (x, y, fill,  BAR_H))
    pygame.draw.rect(surf, BORDER_COLOR, (x, y, BAR_W, BAR_H), 1)
    txt = font.render(f"MP  {mp}/{max_mp}", True, TEXT_WHITE)
    surf.blit(txt, (x + 4, y + (BAR_H - txt.get_height()) // 2))


def _result_to_log(result: dict, attacker_name: str, defender_name: str) -> str:
    t  = result["type"]
    ab = result.get("ability_name", "")
    prefix = f"uses {ab} — " if ab and ab not in ("Basic", "_basic") else ""
    if t == "hit":
        crit = " CRITICAL!" if result.get("crit") else ""
        return f"{attacker_name} {prefix}hits {defender_name} for {result['amount']}{crit}"
    if t == "miss":
        return f"{attacker_name} {prefix}misses!"
    if t == "heal":
        return f"{attacker_name} {prefix}heals {result['amount']} HP"
    if t == "use_item":
        return f"{attacker_name} uses item, heals {result['amount']} HP"
    return f"{attacker_name} acts"


def _get_sub_items(state: str, pf: Fighter) -> list[dict]:
    """Return the row list for the active submenu. First row is always Back."""
    back = {"kind": "back", "label": "\u2190 Back"}
    if state == "abilities":
        rows = [back]
        for ab in (pf.abilities or []):
            rows.append({"kind": "ability", "label": ab["name"], "ability": ab})
        return rows
    if state == "spells":
        rows = [back]
        for sp in (pf.spells or []):
            rows.append({"kind": "spell", "label": sp["name"], "spell": sp})
        if not pf.spells:
            rows.append({"kind": "empty", "label": "(No spells learned)"})
        return rows
    if state == "backpack":
        rows = [back]
        for st in pf.bag:
            rows.append({"kind": "use_item",
                         "label": f"{st.item['name']}  x{st.qty}", "stack": st})
        if not pf.bag:
            rows.append({"kind": "empty", "label": "(Empty)"})
        return rows
    return [back]


def _use_item(stack, pf: Fighter, log: list[str]) -> None:
    """Apply item effects to pf and append result message to log."""
    item = stack.item
    msgs = []
    if item.get("heal", 0) > 0:
        before = pf.hp
        pf.hp = min(pf.max_hp, pf.hp + item["heal"])
        msgs.append(f"restored {pf.hp - before} HP")
    if item.get("restore_sp", 0) > 0:
        pf.cycles = min(pf.max_cycles, pf.cycles + item["restore_sp"])
        msgs.append(f"restored {item['restore_sp']} SP")
    if item.get("restore_mp", 0) > 0:
        pf.mp = min(pf.max_mp, pf.mp + item["restore_mp"])
        msgs.append(f"restored {item['restore_mp']} MP")
    stack.qty -= 1
    if stack.qty <= 0:
        try:
            pf.bag.remove(stack)
        except ValueError:
            pass
    effect_str = ", ".join(msgs) if msgs else "no effect"
    log.append(f"You use {item['name']} — {effect_str}!")


# --- Main entry point ---

def run_combat(screen: pygame.Surface, clock: pygame.time.Clock,
               font: pygame.font.Font,
               player_entity, npc_entity,
               ctx: GameContext) -> str:
    """
    Runs the full-screen combat stage.
    Returns "win", "lose", or "flee".
    """
    pygame.display.set_caption(f"LucentForge — Combat: Player vs {npc_entity.name}")

    # Build fighters from entity data
    player_fighter = build_fighter(
        name       = "Player",
        hp         = int(player_entity.hp),
        max_hp     = int(player_entity.max_hp),
        stats      = player_entity.stats,
        is_enemy   = False,
        cycles     = player_entity.cycles,
        max_cycles = player_entity.max_cycles,
        mp         = player_entity.mp,
        max_mp     = player_entity.max_mp,
    )
    npc_fighter = build_fighter(
        name       = npc_entity.name,
        hp         = int(npc_entity.hp),
        max_hp     = int(npc_entity.max_hp),
        stats      = npc_entity.stats,
        is_enemy   = True,
        cycles     = npc_entity.cycles,
        max_cycles = npc_entity.max_cycles,
        mp         = npc_entity.mp,
        max_mp     = npc_entity.max_mp,
    )

    # Attach ability sets
    player_fighter.abilities = get_abilities(ctx, player_entity.entity_id)
    npc_fighter.abilities    = get_abilities(ctx, npc_entity.entity_id)

    # Attach spell sets
    player_fighter.spells = get_spells(ctx, player_entity.entity_id)
    npc_fighter.spells    = get_spells(ctx, npc_entity.entity_id)

    # Resolve equipment -> weapon dict for damage_roll
    player_equip = resolve_equipment(ctx, player_entity.entity_id)
    npc_equip    = resolve_equipment(ctx, npc_entity.entity_id)
    player_fighter.weapon = player_equip if player_equip else None
    npc_fighter.weapon    = npc_equip if npc_equip else None

    # Starter inventory — loaded from entities.json bag field
    player_fighter.bag = build_bag(ctx, player_entity.entity_id)

    # Lazy-load the basic attack ability
    attack_ability = get_basic_attack(ctx)

    menu = _MenuState()
    rng  = SimpleRng()

    # Load fighter visuals — sprite paths from entities.json
    player_img = _load_fighter_surface(
        get_sprite_path(ctx, player_entity.entity_id), FIGHTER_SIZE, flip=False)
    npc_img    = _load_fighter_surface(
        get_sprite_path(ctx, npc_entity.entity_id), FIGHTER_SIZE, flip=True)

    # Fonts
    title_font  = pygame.font.SysFont(None, 28)
    ui_font     = pygame.font.SysFont(None, 20)
    log_font    = pygame.font.SysFont(None, 18)
    menu_font   = pygame.font.SysFont(None, 24)

    W, H = screen.get_size()

    # Load combat background
    _bg_path = os.path.join("assets", "images", "level01.png")
    if os.path.isfile(_bg_path):
        bg_surf = pygame.image.load(_bg_path).convert()
        bg_surf = pygame.transform.scale(bg_surf, (W, H))
    else:
        bg_surf = None

    # Battle log
    log: list[str] = [f"A wild {npc_entity.name} appears!"]

    # Turn state
    player_turn = True
    waiting_for_input = True

    def _sync_entities_and_return(outcome: str) -> str:
        player_entity.hp     = float(player_fighter.hp)
        player_entity.cycles = player_fighter.cycles
        player_entity.mp     = player_fighter.mp
        npc_entity.hp        = float(npc_fighter.hp)
        npc_entity.cycles    = npc_fighter.cycles
        npc_entity.mp        = npc_fighter.mp
        pygame.display.set_caption("LucentForge — NPC Needs Prototype")
        return outcome

    while True:
        clock.tick(settings.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return _sync_entities_and_return("lose")

            if event.type == pygame.KEYDOWN and player_turn and waiting_for_input:

                # --- Main menu ---
                if menu.state == "main":
                    if event.key == pygame.K_UP:
                        menu.main_cursor = (menu.main_cursor - 1) % len(_MAIN_OPTIONS)
                    elif event.key == pygame.K_DOWN:
                        menu.main_cursor = (menu.main_cursor + 1) % len(_MAIN_OPTIONS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                        chosen = _MAIN_OPTIONS[menu.main_cursor]

                        if chosen["kind"] == "flee":
                            log.append("You flee from battle!")
                            _draw_combat(screen, W, H, player_fighter, npc_fighter,
                                         player_img, npc_img, log, player_turn,
                                         title_font, ui_font, log_font, menu_font,
                                         npc_entity.name, waiting_for_input,
                                         bg_surf, menu, attack_ability)
                            pygame.display.flip()
                            pygame.time.wait(800)
                            return _sync_entities_and_return("flee")

                        elif chosen["kind"] == "action_attack":
                            if player_fighter.cycles >= attack_ability["cost_cycles"]:
                                res = take_turn(player_fighter, npc_fighter, rng,
                                                forced_ability=attack_ability)
                                log.append(_result_to_log(res, "You", npc_entity.name))
                                waiting_for_input = False
                            else:
                                log.append("Not enough SP to attack!")

                        elif chosen["kind"] == "action_submenu":
                            menu.state      = chosen["submenu"]
                            menu.sub_cursor = 0

                # --- Submenus ---
                else:
                    sub_items = _get_sub_items(menu.state, player_fighter)
                    if event.key == pygame.K_UP:
                        menu.sub_cursor = (menu.sub_cursor - 1) % len(sub_items)
                    elif event.key == pygame.K_DOWN:
                        menu.sub_cursor = (menu.sub_cursor + 1) % len(sub_items)
                    elif event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        menu.state = "main"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                        row = sub_items[menu.sub_cursor]
                        if row["kind"] == "back":
                            menu.state = "main"
                        elif row["kind"] == "ability":
                            ab = row["ability"]
                            if player_fighter.cycles >= ab.get("cost_cycles", 0):
                                res = take_turn(player_fighter, npc_fighter, rng,
                                                forced_ability=ab)
                                log.append(_result_to_log(res, "You", npc_entity.name))
                                waiting_for_input = False
                                menu.state = "main"
                            else:
                                log.append(f"Not enough SP for {ab['name']}!")
                        elif row["kind"] == "spell":
                            sp = row["spell"]
                            if player_fighter.mp >= sp.get("cost_mp", 0):
                                res = take_turn(player_fighter, npc_fighter, rng,
                                                forced_ability=sp)
                                log.append(_result_to_log(res, "You", npc_entity.name))
                                waiting_for_input = False
                                menu.state = "main"
                            else:
                                log.append(f"Not enough MP for {sp['name']}!")
                        elif row["kind"] == "use_item":
                            _use_item(row["stack"], player_fighter, log)
                            waiting_for_input = False
                            menu.state = "main"
                        # "empty" rows do nothing

        # After player action — check NPC HP, then enemy turn
        if not waiting_for_input and player_turn:
            if npc_fighter.hp <= 0:
                log.append(f"{npc_entity.name} is defeated!")
                _draw_combat(screen, W, H, player_fighter, npc_fighter,
                             player_img, npc_img, log, player_turn,
                             title_font, ui_font, log_font, menu_font,
                             npc_entity.name, waiting_for_input, bg_surf,
                             menu, attack_ability)
                _draw_result(screen, W, H, "Victory!", (80, 220, 80), title_font)
                pygame.display.flip()
                pygame.time.wait(RESULT_PAUSE)
                return _sync_entities_and_return("win")

            # Enemy turn
            player_turn = False
            res = take_turn(npc_fighter, player_fighter, rng)
            log.append(_result_to_log(res, npc_entity.name, "You"))

            if player_fighter.hp <= 0:
                log.append("You have been defeated!")
                _draw_combat(screen, W, H, player_fighter, npc_fighter,
                             player_img, npc_img, log, player_turn,
                             title_font, ui_font, log_font, menu_font,
                             npc_entity.name, waiting_for_input, bg_surf,
                             menu, attack_ability)
                _draw_result(screen, W, H, "Defeated!", (220, 60, 60), title_font)
                pygame.display.flip()
                pygame.time.wait(RESULT_PAUSE)
                return _sync_entities_and_return("lose")

            # Back to player
            player_turn = True
            waiting_for_input = True

        # Draw
        _draw_combat(screen, W, H, player_fighter, npc_fighter,
                     player_img, npc_img, log, player_turn,
                     title_font, ui_font, log_font, menu_font,
                     npc_entity.name, waiting_for_input, bg_surf,
                     menu, attack_ability)
        pygame.display.flip()


def _draw_combat(screen, W, H,
                 pf: Fighter, nf: Fighter,
                 player_img, npc_img,
                 log: list[str], player_turn: bool,
                 title_font, ui_font, log_font, menu_font,
                 npc_name: str, waiting: bool,
                 bg_surf=None,
                 menu: _MenuState = None,
                 attack_ability: dict | None = None):

    if bg_surf is not None:
        screen.blit(bg_surf, (0, 0))
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 180))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill(DARK_BG)

    # --- Title bar (y=6) ---
    title = title_font.render(f"COMBAT  —  Player  vs  {npc_name}", True, TEXT_WHITE)
    screen.blit(title, (W // 2 - title.get_width() // 2, 6))

    # --- Fighter positions (y=36) ---
    sprite_y = 36
    player_x = W // 4 - FIGHTER_SIZE // 2
    npc_x    = 3 * W // 4 - FIGHTER_SIZE // 2

    if player_img:
        screen.blit(player_img, (player_x, sprite_y))
    else:
        pygame.draw.rect(screen, settings.PLAYER_COLOR,
                         (player_x, sprite_y, FIGHTER_SIZE, FIGHTER_SIZE))

    if npc_img:
        screen.blit(npc_img, (npc_x, sprite_y))
    else:
        pygame.draw.rect(screen, settings.NPC_COLOR,
                         (npc_x, sprite_y, FIGHTER_SIZE, FIGHTER_SIZE))

    # --- HP bars (y=152, label y=134) ---
    bar_y = sprite_y + FIGHTER_SIZE + 20
    _draw_hp_bar(screen, player_x, bar_y, pf.hp, pf.max_hp, "HP", ui_font)
    _draw_hp_bar(screen, npc_x,    bar_y, nf.hp, nf.max_hp, "HP", ui_font)

    # --- SP bars (y=172) ---
    sp_y = bar_y + BAR_H + 4
    _draw_stamina_bar(screen, player_x, sp_y, pf.cycles, pf.max_cycles, ui_font)
    _draw_stamina_bar(screen, npc_x,    sp_y, nf.cycles, nf.max_cycles, ui_font)

    # --- MP bars (y=192) ---
    mp_y = sp_y + BAR_H + 4
    _draw_mp_bar(screen, player_x, mp_y, pf.mp, pf.max_mp, ui_font)
    _draw_mp_bar(screen, npc_x,    mp_y, nf.mp, nf.max_mp, ui_font)

    # --- Battle log panel (y~214) ---
    log_y = mp_y + BAR_H + 14
    log_h = LOG_LINES * 19 + 14
    log_rect = pygame.Rect(20, log_y, W - 40, log_h)
    pygame.draw.rect(screen, LOG_BG, log_rect)
    pygame.draw.rect(screen, BORDER_COLOR, log_rect, 1)

    visible = log[-LOG_LINES:]
    for i, line in enumerate(visible):
        color = TEXT_WHITE if i == len(visible) - 1 else TEXT_DIM
        txt = log_font.render(f"> {line}", True, color)
        screen.blit(txt, (log_rect.x + 8, log_rect.y + 7 + i * 19))

    # --- Action menu ---
    menu_top = log_y + log_h + 10

    if player_turn and waiting and menu is not None:
        item_h  = 24
        panel_w = 220
        panel_x = W // 2 - panel_w // 2

        if menu.state == "main":
            _draw_main_menu(screen, panel_x, menu_top, panel_w, item_h,
                            pf, menu, menu_font, ui_font, attack_ability)
        else:
            _draw_sub_menu(screen, panel_x, menu_top, panel_w, item_h,
                           pf, menu, menu_font, ui_font)

    elif not player_turn or not waiting:
        wait_txt = menu_font.render("Enemy is acting...", True, TEXT_DIM)
        screen.blit(wait_txt, (W // 2 - wait_txt.get_width() // 2, menu_top + 8))


def _draw_main_menu(screen, panel_x, panel_y, panel_w, item_h,
                    pf: Fighter, menu: _MenuState, menu_font, ui_font,
                    attack_ability: dict | None = None):
    """Draw the top-level ACTIONS panel."""
    header = menu_font.render("ACTIONS", True, TEXT_DIM)
    screen.blit(header, (panel_x + 4, panel_y - 20))

    panel_h = len(_MAIN_OPTIONS) * item_h + 10
    pygame.draw.rect(screen, PANEL_COLOR,  (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, BORDER_COLOR, (panel_x, panel_y, panel_w, panel_h), 1)

    any_ability_affordable = any(
        pf.cycles >= ab.get("cost_cycles", 0)
        for ab in (pf.abilities or [])
    )

    atk = attack_ability or {"cost_cycles": 0}

    for i, opt in enumerate(_MAIN_OPTIONS):
        is_sel   = (i == menu.main_cursor)
        row_rect = pygame.Rect(panel_x + 2, panel_y + 5 + i * item_h, panel_w - 4, item_h - 2)
        if is_sel:
            pygame.draw.rect(screen, MENU_HL, row_rect)

        # Cost / submenu indicator
        if opt["kind"] == "action_attack":
            cost_str  = f"  ({atk['cost_cycles']} SP)"
            affordable = pf.cycles >= atk["cost_cycles"]
        elif opt["kind"] == "action_submenu":
            cost_str = "  \u203a"
            sub = opt["submenu"]
            if sub == "abilities":
                affordable = any_ability_affordable
            elif sub == "spells":
                affordable = any(
                    pf.mp >= sp.get("cost_mp", 0)
                    for sp in (pf.spells or [])
                )
            elif sub == "backpack":
                affordable = bool(pf.bag)
            else:
                affordable = True
        else:  # flee
            cost_str  = ""
            affordable = True

        text_color = MENU_HL_TEXT if is_sel else (TEXT_WHITE if affordable else TEXT_DIM)
        label = menu_font.render(f"  {opt['name']}{cost_str}", True, text_color)
        screen.blit(label, (panel_x + 4, panel_y + 7 + i * item_h))

    hint = ui_font.render("Up/Down   Enter", True, TEXT_DIM)
    screen.blit(hint, (panel_x, panel_y + panel_h + 6))


def _draw_sub_menu(screen, panel_x, panel_y, panel_w, item_h,
                   pf: Fighter, menu: _MenuState, menu_font, ui_font):
    """Draw a submenu (abilities / spells / backpack)."""
    header_name = menu.state.upper()
    header = menu_font.render(header_name, True, TEXT_DIM)
    screen.blit(header, (panel_x + 4, panel_y - 20))

    sub_items = _get_sub_items(menu.state, pf)
    panel_h   = len(sub_items) * item_h + 10
    pygame.draw.rect(screen, PANEL_COLOR,  (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, BORDER_COLOR, (panel_x, panel_y, panel_w, panel_h), 1)

    for i, row in enumerate(sub_items):
        is_sel   = (i == menu.sub_cursor)
        row_rect = pygame.Rect(panel_x + 2, panel_y + 5 + i * item_h, panel_w - 4, item_h - 2)
        if is_sel:
            pygame.draw.rect(screen, MENU_HL, row_rect)

        if row["kind"] == "ability":
            ab       = row["ability"]
            cost     = ab.get("cost_cycles", 0)
            cost_str = f"  (SP: {cost})" if cost > 0 else ""
            affordable = pf.cycles >= cost
            text_color = MENU_HL_TEXT if is_sel else (TEXT_WHITE if affordable else TEXT_DIM)
            label = menu_font.render(f"  {row['label']}{cost_str}", True, text_color)
        elif row["kind"] == "spell":
            sp       = row["spell"]
            cost_mp  = sp.get("cost_mp", 0)
            cost_str = f"  (MP: {cost_mp})" if cost_mp > 0 else ""
            affordable = pf.mp >= cost_mp
            text_color = MENU_HL_TEXT if is_sel else (TEXT_WHITE if affordable else TEXT_DIM)
            label = menu_font.render(f"  {row['label']}{cost_str}", True, text_color)
        else:
            text_color = MENU_HL_TEXT if is_sel else TEXT_DIM
            label = menu_font.render(f"  {row['label']}", True, text_color)

        screen.blit(label, (panel_x + 4, panel_y + 7 + i * item_h))

    hint = ui_font.render("Up/Down   Enter   ESC=Back", True, TEXT_DIM)
    screen.blit(hint, (panel_x, panel_y + panel_h + 6))


def _draw_result(screen, W, H, message: str, color: tuple, font: pygame.font.Font):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))
    txt = font.render(message, True, color)
    screen.blit(txt, (W // 2 - txt.get_width() // 2,
                      H // 2 - txt.get_height() // 2))
