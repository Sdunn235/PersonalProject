"""commands.py — semantic input Commands for the shell (Stage 4.6R / R5).

A `Command` is a named intent ("open the pause menu"), decoupled from the physical
key that triggers it. The shell translates a pygame event into a `Command`
(`handle_event`) and then runs it (`execute`). This extends the codebase's existing
"menu returns an action string" convention (e.g. pause_menu -> "resume"/"load:N")
up to the top-level input layer, and buys two things:

- **Remap** — the physical-key -> Command binding is data (`DEFAULT_KEY_BINDINGS`);
  copy and edit it to rebind without touching handler logic.
- **Replay / headless tests** — a Command sequence can be fed to `shell.execute()`
  directly, exercising input handling with no pygame key events.
"""
from enum import Enum

# noinspection PyPackageRequirements
import pygame


class Command(Enum):
    """Top-level player intents the shell knows how to run."""
    QUIT       = "QUIT"        # window close
    PAUSE      = "PAUSE"       # open the pause menu
    CYCLE_HUD  = "CYCLE_HUD"   # tab through HUD subjects
    INVENTORY  = "INVENTORY"   # open the inventory modal
    TOGGLE_OBS = "TOGGLE_OBS"  # toggle the observation panel
    SAVE       = "SAVE"        # open the save-slot menu
    CHEST      = "CHEST"       # interact with an adjacent chest
    CONVERT    = "CONVERT"     # rest: convert Bits -> Bytes (§M4)
    PAUSE_SIM  = "PAUSE_SIM"   # Glass Box: freeze/unfreeze the simulation
    STEP_SIM   = "STEP_SIM"    # Glass Box: advance one sim tick while frozen
    INSPECT    = "INSPECT"     # Glass Box: toggle the deep mind inspector


# Default physical-key -> Command bindings. Remappable: copy this dict, edit the
# keys, and hand it to PresentationShell (or mutate shell._bindings).
DEFAULT_KEY_BINDINGS = {
    pygame.K_ESCAPE: Command.PAUSE,
    pygame.K_TAB:    Command.CYCLE_HUD,
    pygame.K_i:      Command.INVENTORY,
    pygame.K_o:      Command.TOGGLE_OBS,
    pygame.K_s:      Command.SAVE,
    pygame.K_e:      Command.CHEST,
    pygame.K_c:      Command.CONVERT,
    pygame.K_p:      Command.PAUSE_SIM,   # freeze/unfreeze the sim (Glass Box)
    pygame.K_PERIOD: Command.STEP_SIM,    # step one tick while frozen
    pygame.K_v:      Command.INSPECT,     # toggle the deep mind inspector
}
