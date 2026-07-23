from __future__ import annotations
# noinspection PyPackageRequirements
import pygame
import settings
from Mechanics.data.context import GameContext
from Mechanics.items.models import Weapon, Armor, Shield, Consumable
from Mechanics.items.enums import BodySlot, ConsumableEffect

_BG      = (20, 20, 28)
_BORDER  = (80, 80, 110)
_HEADER  = (200, 200, 230)
_HL_BG   = (255, 210, 60)
_HL_TEXT = (20, 20, 30)
_TEXT    = (240, 240, 240)
_HINT    = (100, 100, 120)
_GREY    = (80, 80, 90)
_RED     = (220, 60, 60)
_DIM     = (140, 140, 160)

_EQUIP_SLOTS = [
    ("Weapon", "weapon"),
    ("Shield", "shield"),
    ("Head",   "head"),
    ("Armor",  "armor"),
    ("Hands",  "hands"),
    ("Legs",   "legs"),
    ("Feet",   "feet"),
]

_BODY_TO_SLOT: dict[BodySlot, str] = {
    BodySlot.HEAD:  "head",
    BodySlot.CHEST: "armor",
    BodySlot.LEGS:  "legs",
    BodySlot.FEET:  "feet",
    BodySlot.HANDS: "hands",
}


def _slot_for_item(item) -> str | None:
    if isinstance(item, Shield):
        return "shield"
    if isinstance(item, Weapon):
        return "weapon"
    if isinstance(item, Armor):
        return _BODY_TO_SLOT.get(item.body_slot)
    return None


def _apply_consumable(player, effect, potency: int) -> None:
    if effect == ConsumableEffect.HEAL:
        player.heal(potency)
    elif effect == ConsumableEffect.RESTORE_SP:
        player.cycles = min(player.max_cycles, player.cycles + potency)
    elif effect in (ConsumableEffect.RESTORE_MP, ConsumableEffect.RESTORE_BYTES):
        player.byte_pool = min(player.max_byte_pool, player.byte_pool + potency)
    elif effect == ConsumableEffect.RESTORE_BITS:
        player.bit_pool = min(player.max_bit_pool, player.bit_pool + potency)


def _action_unequip(eq_cursor: int, entity_id: str, equip_svc, inv_svc) -> None:
    slot_name = _EQUIP_SLOTS[eq_cursor][1]
    equip_svc.unequip(entity_id, slot_name, inv_svc=inv_svc)


def _action_use_or_equip(stack, player_entity, inv_svc, equip_svc) -> None:
    item = stack.item
    if isinstance(item, Consumable):
        potency = item.potency
        effect = inv_svc.use_consumable(player_entity.entity_id, item.id)
        if effect is not None:
            _apply_consumable(player_entity, effect, potency)
    else:
        slot = _slot_for_item(item)
        if slot and equip_svc:
            inv_svc.remove_item(player_entity.entity_id, item.id)
            equip_svc.equip(player_entity.entity_id, item, slot, inv_svc=inv_svc)


def _draw(screen, W, H, font, panel, eq_cursor, inv_cursor,
          stacks, equip_set, player_entity, inv_svc):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    title_font  = pygame.font.SysFont(None, 30)
    label_font  = pygame.font.SysFont(None, 24)
    hint_font   = pygame.font.SysFont(None, 18)

    ROW_H      = 30
    PANEL_W    = min(W - 40, 620)
    COL_W      = (PANEL_W - 60) // 2
    N_ROWS     = max(len(_EQUIP_SLOTS), len(stacks) + 1)
    PANEL_H    = 60 + N_ROWS * ROW_H + 60
    PANEL_H    = max(PANEL_H, 340)
    px         = (W - PANEL_W) // 2
    py         = (H - PANEL_H) // 2

    pygame.draw.rect(screen, _BG,    (px, py, PANEL_W, PANEL_H), border_radius=8)
    pygame.draw.rect(screen, _BORDER,(px, py, PANEL_W, PANEL_H), width=2, border_radius=8)

    # --- Column positions ---
    left_x  = px + 20
    right_x = px + 20 + COL_W + 20

    # --- Panel headers ---
    eq_col   = _HL_BG if panel == "equip" else _HEADER
    inv_col  = _HL_BG if panel == "inv"   else _HEADER
    eq_head  = title_font.render("EQUIPPED", True, eq_col if panel != "equip" else _HL_TEXT)
    inv_head = title_font.render("INVENTORY", True, inv_col if panel != "inv" else _HL_TEXT)

    if panel == "equip":
        pygame.draw.rect(screen, _HL_BG, (left_x - 4, py + 14, COL_W + 8, 28), border_radius=4)
    if panel == "inv":
        pygame.draw.rect(screen, _HL_BG, (right_x - 4, py + 14, COL_W + 8, 28), border_radius=4)

    screen.blit(eq_head,  (left_x,  py + 18))
    screen.blit(inv_head, (right_x, py + 18))

    row_start_y = py + 54

    # --- Equipped panel ---
    equip_dict: dict[str, object] = {}
    if equip_set:
        for label, slot_key in _EQUIP_SLOTS:
            equip_dict[slot_key] = equip_set.get_slot(slot_key)

    for i, (label, slot_key) in enumerate(_EQUIP_SLOTS):
        row_y  = row_start_y + i * ROW_H
        active = (panel == "equip" and i == eq_cursor)

        if active:
            pygame.draw.rect(screen, _HL_BG,
                             (left_x - 4, row_y - 2, COL_W + 8, ROW_H - 2), border_radius=3)

        item = equip_dict.get(slot_key)
        slot_label = f"{label}:"
        item_label = item.name if item else "(empty)"

        slot_surf = label_font.render(slot_label, True, _HL_TEXT if active else _DIM)
        item_surf = label_font.render(item_label, True, _HL_TEXT if active else (_TEXT if item else _GREY))

        screen.blit(slot_surf, (left_x, row_y + 4))
        screen.blit(item_surf, (left_x + 66, row_y + 4))

    # --- Inventory panel ---
    for i, stack in enumerate(stacks):
        row_y  = row_start_y + i * ROW_H
        active = (panel == "inv" and i == inv_cursor)

        if active:
            pygame.draw.rect(screen, _HL_BG,
                             (right_x - 4, row_y - 2, COL_W + 8, ROW_H - 2), border_radius=3)

        name_text = stack.item.name
        qty_text  = f"×{stack.qty}"
        wt_text   = f"{stack.item.weight * stack.qty:.1f}wt"

        name_surf = label_font.render(name_text, True, _HL_TEXT if active else _TEXT)
        qty_surf  = label_font.render(qty_text,  True, _HL_TEXT if active else _DIM)
        wt_surf   = label_font.render(wt_text,   True, _HL_TEXT if active else _DIM)

        screen.blit(name_surf, (right_x, row_y + 4))
        screen.blit(qty_surf,  (right_x + COL_W - 80, row_y + 4))
        screen.blit(wt_surf,   (right_x + COL_W - 42, row_y + 4))

    # Drop row (greyed, always after last stack)
    drop_row_y = row_start_y + len(stacks) * ROW_H
    drop_surf  = label_font.render("(Drop — Stage 3)", True, _GREY)
    screen.blit(drop_surf, (right_x, drop_row_y + 4))

    # --- Weight footer ---
    if player_entity and inv_svc:
        inv_weight   = inv_svc.get_inventory(player_entity.entity_id)
        inv_w        = inv_weight.total_weight() if inv_weight else 0.0
        equip_w      = sum(i.weight for i in equip_set.all_equipped()) if equip_set else 0.0
        total_w      = inv_w + equip_w
        cap          = settings.CARRY_BASE + settings.CARRY_PER_STR * player_entity.stats.STR
        weight_color = _RED if cap > 0 and total_w / cap >= 0.90 else _TEXT
        weight_text  = f"Weight {total_w:.1f} / {cap:.0f}"
        wt_surf      = label_font.render(weight_text, True, weight_color)
        screen.blit(wt_surf, (px + (PANEL_W - wt_surf.get_width()) // 2,
                               py + PANEL_H - 50))

    # --- Hint ---
    hint = hint_font.render(
        "←→ Panel    ↑↓ Move    ENTER Act    ESC/I Close",
        True, _HINT,
    )
    screen.blit(hint, (px + (PANEL_W - hint.get_width()) // 2, py + PANEL_H - 26))


def run_inventory_menu(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    ctx: GameContext,
    font: pygame.font.Font,
    inv_svc,
    equip_svc=None,
    player_entity=None,
) -> None:
    """Modal inventory/equipment viewer. ESC or I to close."""
    panel      = "equip"
    eq_cursor  = 0
    inv_cursor = 0
    W, H       = screen.get_size()

    while True:
        clock.tick(settings.FPS)

        inv       = inv_svc.get_inventory(player_entity.entity_id) if player_entity else None
        stacks    = list(inv.stacks) if inv else []
        equip_set = (equip_svc.get_equipment(player_entity.entity_id)
                     if equip_svc and player_entity else None)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type != pygame.KEYDOWN:
                continue

            k = event.key
            if k in (pygame.K_ESCAPE, pygame.K_i):
                return
            elif k in (pygame.K_LEFT, pygame.K_a):
                panel = "equip"
            elif k in (pygame.K_RIGHT, pygame.K_d):
                panel = "inv"
            elif k in (pygame.K_UP, pygame.K_w):
                if panel == "equip":
                    eq_cursor = (eq_cursor - 1) % len(_EQUIP_SLOTS)
                else:
                    inv_cursor = (inv_cursor - 1) % max(1, len(stacks) + 1)
            elif k in (pygame.K_DOWN, pygame.K_s):
                if panel == "equip":
                    eq_cursor = (eq_cursor + 1) % len(_EQUIP_SLOTS)
                else:
                    inv_cursor = (inv_cursor + 1) % max(1, len(stacks) + 1)
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if panel == "equip" and equip_set and player_entity:
                    _action_unequip(eq_cursor, player_entity.entity_id, equip_svc, inv_svc)
                elif panel == "inv" and stacks and inv_cursor < len(stacks) and player_entity:
                    _action_use_or_equip(stacks[inv_cursor], player_entity, inv_svc, equip_svc)
                # inv_cursor == len(stacks) → Drop row → no-op

        _draw(screen, W, H, font, panel, eq_cursor, inv_cursor,
              stacks, equip_set, player_entity, inv_svc)
        pygame.display.flip()
