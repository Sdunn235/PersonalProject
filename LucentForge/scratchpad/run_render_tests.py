# run_render_tests.py — what the player SEES, asserted headlessly (docs/testing.md "Render").
#
# Replaces the live checks Shawn ran at the window for fatigue (2026-11-17/18) and strain
# (2026-11-19): a real PresentationShell renders full world frames off-screen and a SpyFont
# records every string drawn. Each check names the live check it replaces. A negative control
# proves the assertions aren't vacuous. Frames are saved to logs/screens/latest/ as evidence.
#
#   py scratchpad/run_render_tests.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness.headless import (controller_of, headless_shell, new_kernel,  # noqa: E402
                              render_text, save_frame, step)

import settings  # noqa: E402
from Mechanics.biochem.receptor import apply_perceived_pulls  # noqa: E402
from Mechanics.runtime.commands import Command  # noqa: E402

_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


def has(drawn, fragment: str) -> bool:
    return any(fragment in s for s in drawn)


def lines_with(drawn, fragment: str) -> list[str]:
    return [s for s in drawn if fragment in s]


print("=" * 64)
print("Render tests - what the world frame draws (HUD / O panel / V inspector)")
print("=" * 64)

ctx, kernel = new_kernel()
shell = headless_shell(ctx, kernel)
step(kernel, 120, shell)                      # two seconds of play so sprites/HUD settle

gruk, elara = controller_of(kernel, "Gruk"), controller_of(kernel, "Elara")


def quiet_chems(ctrl):
    for key in ("fatigue", "affinity_strain"):
        ctrl.brain.chemicals.set(key, 0.0)
    ctrl.relocate_target_region = None


# --- Negative control: nobody fatigued or strained -> no such suffix anywhere on screen. ---
for _ent, _ctrl in kernel.session.npc_list:
    quiet_chems(_ctrl)
apply_perceived_pulls(elara.needs, elara.brain.chemicals, elara.brain.traits)
drawn = render_text(shell, subject="Gruk")
check("control: panel shows no fatigue suffix when fatigue is 0",
      not any(s.strip().startswith("f0.") for s in drawn))
drawn = render_text(shell, subject="Elara", inspect=True)
check("control: inspector shows no actual>felt need when nothing pulls",
      not any(">" in s and ("Sleep" in s or "Hunger" in s or "Thirst" in s) for s in drawn))

# --- Live check 'fatigue visible' (2026-11-17/18), now automated. ---
gruk.brain.chemicals.set("fatigue", 0.42)
gruk.brain.chemicals.set("affinity_strain", 0.0)
drawn = render_text(shell, subject="Gruk")
check("HUD shows a Fatigue row with the value for the TAB-selected NPC",
      has(drawn, "Fatigue  0.420"), "; ".join(lines_with(drawn, "Fatigue")))
check("O panel shows Gruk's fatigue suffix f0.42", any(s.strip() == "f0.42" for s in drawn),
      "; ".join(s for s in drawn if s.strip().startswith(("f0", "s0"))))
save_frame(shell, "01_fatigue_hud_panel")

# --- Live check 'strain visible, takes priority in the suffix' (2026-11-19). ---
elara.brain.chemicals.set("affinity_strain", 0.30)
elara.brain.chemicals.set("fatigue", 0.20)
drawn = render_text(shell, subject="Elara")
check("O panel shows strain (s0.30) ahead of fatigue for Elara",
      any(s.strip() == "s0.30" for s in drawn) and not any(s.strip() == "f0.20" for s in drawn))
check("HUD shows a Strain row with the value", has(drawn, "Strain   0.300"),
      "; ".join(lines_with(drawn, "Strain")))

# --- Live check 'inspector: 4 decimals + actual>felt needs' (2026-11-18/19). ---
elara.brain.chemicals.set("fatigue", 0.6)
elara.brain.chemicals.set("affinity_strain", 0.0)
sleep = next(n for n in elara.needs if n.need_id == "sleep")
sleep.current_value = 58.0
apply_perceived_pulls(elara.needs, elara.brain.chemicals, elara.brain.traits)
expected_felt = 58.0 - 0.6 * settings.FATIGUE_PULL_FRACTION * (100.0 - sleep.warning_threshold)
drawn = render_text(shell, subject="Elara", inspect=True)
check("inspector shows fatigue to 4 decimals", has(drawn, "fatigue  0.6000"),
      "; ".join(lines_with(drawn, "fatigue")))
check(f"inspector shows sleep as actual>felt (58.0>{expected_felt:.0f}) with the perceived zone",
      any(f"58.0>{expected_felt:.0f}" in s and "WARNING" in s for s in drawn),
      "; ".join(lines_with(drawn, "58.0")))
save_frame(shell, "02_inspector_elara_fatigued")

# --- Live check 'P freeze, . steps, , rewinds — values visibly move' (Glass Box + 4 decimals). ---
quiet_chems(gruk)
step(kernel, 600, shell)                      # Gruk patrols: fatigue builds for 10 s
shell.execute(Command.PAUSE_SIM)
check("P freezes the sim", shell._paused_sim)
tick0 = kernel.session.world_sim.clock.tick_count
fat0 = gruk.brain.chemicals.get("fatigue")
for _ in range(settings.FPS):                 # one sim tick of frames, as the live loop would
    shell.execute(Command.STEP_SIM)
    if shell._step_once:
        shell._step_once = False
        with __import__("contextlib").redirect_stdout(__import__("io").StringIO()):
            shell._advance_one_tick(0.0)
        break
tick1 = kernel.session.world_sim.clock.tick_count
fat1 = gruk.brain.chemicals.get("fatigue")
check(". advances exactly one sim tick", tick1 == tick0 + 1, f"{tick0}->{tick1}")
check(". visibly moves Gruk's fatigue in the inspector's 4th decimal",
      f"{fat0:.4f}" != f"{fat1:.4f}", f"{fat0:.6f} -> {fat1:.6f}")
with __import__("contextlib").redirect_stdout(__import__("io").StringIO()):
    shell.execute(Command.REWIND)
check(", steps the sim back one tick", kernel.session.world_sim.clock.tick_count == tick0,
      f"now {kernel.session.world_sim.clock.tick_count}, expected {tick0}")
drawn = render_text(shell, subject="Gruk", inspect=True)
save_frame(shell, "03_inspector_gruk_after_rewind")

print("=" * 64)
print(f"Screens saved to {os.path.relpath(os.path.join('logs', 'screens', 'latest'))}")
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Render tests CLEAN")
