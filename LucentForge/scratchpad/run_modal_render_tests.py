# run_modal_render_tests.py — what the modal screens show (docs/testing.md "Render"; BACKLOG LF-172).
#
# Pause, inventory, chest, load/save and combat run their own blocking loops with their own fonts, so
# harness/modal.py scripts their input (a couple of frames to draw, then the exit key) and records every
# string they draw. Checks derive from game data where possible (the player's real items, the real
# chest, a real save). Characterization tests (2026-11-19): they pin what each screen shows today, plus
# one behavior from C0056 (Pause -> Load lists only real saves, with no New Game row).
#
#   py scratchpad/run_modal_render_tests.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness.headless import headless_shell, new_kernel, save_frame, step  # noqa: E402
from harness.modal import capture_modal, key  # noqa: E402

import pygame  # noqa: E402
from Mechanics.renderer.chest_menu import run_chest_menu  # noqa: E402
from Mechanics.renderer.combat_scene import run_combat  # noqa: E402
from Mechanics.renderer.inventory_menu import run_inventory_menu  # noqa: E402
from Mechanics.renderer.pause_menu import run_pause_menu  # noqa: E402
from Mechanics.renderer.save_menu import run_load_menu, run_save_menu  # noqa: E402
from Mechanics.services.outcome import OutcomeResolver  # noqa: E402

_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


def has(drawn, fragment: str) -> bool:
    return any(fragment in s for s in drawn)


ESC = [key(pygame.K_ESCAPE)]
print("=" * 64)
print("Modal render tests - pause / inventory / chest / load / save / combat")
print("=" * 64)
ctx, kernel = new_kernel()
shell = headless_shell(ctx, kernel)
step(kernel, 60, shell)
s = kernel.session
F, scr, clk = shell.font, shell.screen, shell.clock

# Pause.
drawn, res = capture_modal(run_pause_menu, scr, clk, ctx, F, s.world_sim, s.sources, s.npc_controllers,
                           s.player, s.player_needs, s.defeated_npcs, s.combat_cooldowns,
                           inv_svc=s.inv_svc, equip_svc=s.equip_svc, chest_reg=s.chest_reg,
                           exit_events=ESC, shell_font=F)
check("pause: titled PAUSED", has(drawn, "PAUSED"))
for opt in ("Resume", "Inventory", "Save", "Load", "New Game", "Quit"):
    check(f"pause: offers {opt}", has(drawn, opt))
check("pause: Esc resumes", res == "resume", repr(res))
save_frame(shell, "10_pause")

# Inventory: shows every item the player actually carries, and their carried weight.
inv = s.inv_svc.get_inventory(s.player.entity_id)
drawn, _ = capture_modal(run_inventory_menu, scr, clk, ctx, F, s.inv_svc, s.equip_svc, s.player,
                         exit_events=ESC, shell_font=F)
check("inventory: titled INVENTORY with an EQUIPPED panel", has(drawn, "INVENTORY") and has(drawn, "EQUIPPED"))
missing = [st.item.name for st in inv.stacks if not has(drawn, st.item.name)]
check(f"inventory: lists every carried item ({len(inv.stacks)})", not missing, f"missing {missing}")
weight = s.inv_svc.carried_weight(s.player.entity_id) + s.equip_svc.equipped_weight(s.player.entity_id)
check(f"inventory: shows the full load, bag + worn gear (§A2), {weight:.1f}", has(drawn, f"Weight {weight:.1f}"))
save_frame(shell, "11_inventory")

# Chest: the real seeded chest; Esc closes; a locked chest offers a way to deal with the lock.
chest = next(iter(s.chest_reg.values()))
drawn, _ = capture_modal(run_chest_menu, scr, clk, F, chest, s.player, s.inv_svc, s.equip_svc,
                         ctx.item_repo, OutcomeResolver(), exit_events=ESC, shell_font=F)
check("chest: draws a menu", len(drawn) >= 2, str(drawn[:6]))
if chest.locked:
    check("chest: a locked chest offers a lock action",
          any(w in s_.lower() for s_ in drawn for w in ("pick", "lock", "key")), str(drawn[:8]))
save_frame(shell, "12_chest")

# Carry load (items addendum §A2: "both inventory (bag items) and equipped items count toward carry
# capacity"). Found by this suite 2026-11-19: the screens agreed with the bible, the take-check didn't.
pid = s.player.entity_id
load = s.inv_svc.carried_weight(pid) + s.equip_svc.equipped_weight(pid)
cap = s.inv_svc.capacity(s.player.stats.STR)
check(f"chest: header shows the full load incl. worn gear ({load:.0f}/{cap:.0f}wt)",
      has(drawn, f"{load:.0f}/{cap:.0f}wt"), str([d for d in drawn if "wt" in d]))
from Mechanics.items.containers import Chest, ItemStack  # noqa: E402
probe = next(st.item for st in s.inv_svc.get_inventory(pid).stacks)
room_in_bag_only = cap - s.inv_svc.carried_weight(pid)
qty = int(room_in_bag_only // probe.weight) if probe.weight > 0 else 0
if qty > 0 and qty * probe.weight > cap - load:
    test_chest = Chest(id="t", col=0, row=0, contents=[ItemStack(probe, qty)])
    took = s.inv_svc.take_from(test_chest, pid, probe, qty, str_stat=s.player.stats.STR,
                               equipped_weight=s.equip_svc.equipped_weight(pid))
    check("take: refuses what fits the bag but not bag + worn gear (§A2)", not took)
else:
    check("take: §A2 over-capacity scenario constructible", False, f"qty={qty}")

# Load at launch: all four slots + a New Game row.
drawn, res = capture_modal(run_load_menu, scr, clk, ctx, F, exit_events=ESC, shell_font=F)
check("load (launch): titled LOAD GAME", has(drawn, "LOAD GAME"))
check("load (launch): offers New Game", has(drawn, "New Game"))
check("load (launch): lists the autosave + three slots",
      has(drawn, "[Autosave]") and all(has(drawn, f"Save Slot {i}") for i in (1, 2, 3)))
check("load (launch): Esc cancels", res is None)

# Pause -> Load (C0056): only real saves, no New Game row.
drawn, _ = capture_modal(run_load_menu, scr, clk, ctx, F, show_new_game=False, saved_only=True,
                         exit_events=ESC, shell_font=F)
check("pause->load with no saves: no New Game row, no empty slots",
      not has(drawn, "New Game") and not has(drawn, "Save Slot"))
with __import__("contextlib").redirect_stdout(__import__("io").StringIO()):
    kernel.save(2)
drawn, _ = capture_modal(run_load_menu, scr, clk, ctx, F, show_new_game=False, saved_only=True,
                         exit_events=ESC, shell_font=F)
check("pause->load after saving slot 2: lists Save Slot 2 only",
      has(drawn, "Save Slot 2") and not has(drawn, "Save Slot 1") and not has(drawn, "Save Slot 3"))
save_frame(shell, "13_load_saved_only")

# Save: three manual slots (no autosave row).
drawn, res = capture_modal(run_save_menu, scr, clk, ctx, F, exit_events=ESC, shell_font=F)
check("save: titled SAVE GAME with slots 1-3", has(drawn, "SAVE GAME")
      and all(has(drawn, f"Save Slot {i}") for i in (1, 2, 3)))
check("save: no autosave row", not has(drawn, "[Autosave]"))
check("save: Esc cancels", res is None)

# Combat: both combatants named, the action menu, and a clean exit (QUIT counts as a loss).
npc = next(e for e, _c in s.npc_list if e.name == "Gruk")
drawn, res = capture_modal(run_combat, scr, clk, F, s.player, npc, ctx, inv_svc=s.inv_svc,
                           equip_svc=s.equip_svc, exit_events=[pygame.event.Event(pygame.QUIT)],
                           shell_font=F)
check("combat: header names both sides", has(drawn, "COMBAT") and has(drawn, s.player.name) and has(drawn, "Gruk"))
for opt in ("Attack", "Abilities", "Spells", "Backpack", "Flee"):
    check(f"combat: action menu offers {opt}", has(drawn, opt))
check("combat: announces the encounter", has(drawn, "Gruk appears"))
check("combat: closing the window ends the fight as a loss", res == "lose", repr(res))
save_frame(shell, "14_combat")

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Modal render tests CLEAN")
