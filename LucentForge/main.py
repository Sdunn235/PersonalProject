# main.py — LucentForge PyGame prototype entry point
# Run: python main.py
#
# Thin composition root (Stage 4.6R): build the headless SimulationKernel and the
# pygame PresentationShell, then hand the kernel to the shell's driver loop.
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

# noinspection PyPackageRequirements
import pygame
import settings

from Mechanics.bootstrap import create_game_context
from Mechanics.runtime.kernel import SimulationKernel
from Mechanics.runtime.shell import PresentationShell
from Mechanics.world.tile_map import TileMap


def main():
    pygame.init()

    print("=" * 60)
    print("LucentForge — NPC Needs & Biochem Prototype")
    print(f"Sim day = {settings.SIM_DAY_SECONDS}s  |  FPS={settings.FPS}")
    print(f"Decay rates:  HUNGER={settings.HUNGER_DECAY_RATE:.5f}/tick  "
          f"THIRST={settings.THIRST_DECAY_RATE:.5f}/tick  "
          f"SLEEP={settings.SLEEP_DECAY_RATE:.5f}/tick")
    print("=" * 60)

    # Composition root: services (ctx), world scope (tile_map + sources),
    # the headless kernel (owns the session), and the pygame shell (the view).
    ctx = create_game_context()
    tile_map = TileMap()
    tile_map.load_real_map()
    sources = tile_map.get_need_sources()

    kernel = SimulationKernel.new_session(ctx, tile_map, sources)
    shell = PresentationShell(ctx)
    shell.run(kernel)


if __name__ == "__main__":
    main()
