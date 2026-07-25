"""Mechanics.runtime — application/session lifecycle layer (Stage 4.6R).

Separates the *simulation* (headless, pygame-free) from the *presentation*
(pygame shell). See README.md. Introduced incrementally R1–R6:

- R1  session.py::WorldSession — the pygame-free object graph + new_game()/apply_save().
- R2  kernel.py::SimulationKernel — step(dt) -> SimFrame (the headless line).
- R4  shell.py::PresentationShell — pygame view + RuntimeMode state machine.
"""
