"""kernel.py — SimulationKernel: the headless-authoritative simulation line (R2).

`SimulationKernel` owns a `WorldSession` + `GameContext` and advances the world
with **no pygame attached**. `step(dt, now)` senses (elapsed time + player intent,
already applied to the player controller by the shell), thinks (world tick + AI +
physiology), and returns a `SimFrame` — the small set of *events* the presentation
shell reacts to (run the combat modal, print hints, kill sprites, flash zones).

This is the headless line: `step()` performs no rendering, no persistence, no
console I/O. Periodic orchestration (autosave, run-log sampling, status prints)
stays in the shell, driven by `SimFrame.sim_ticks`. Combat is *detected* here and
*run* by the shell (the modal is a blocking pygame call); on a win the shell
applies the defeat back onto the session.

`now` is wall-clock seconds (the shell passes `pygame.time.get_ticks() / 1000`),
kept as a plain parameter so the kernel never imports pygame.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import settings
from Mechanics.runtime.session import HOME_PANEL, WorldSession
from Mechanics.needs.needs_system import apply_health_drain, apply_regen, update_needs
from Mechanics.services.perception import perceive_traps
from Mechanics.ai.proximity import update_proximity_fear
from Mechanics.world.world_coord import PanelEdge

COMBAT_TRIGGER_DIST = settings.TILE_SIZE * 1.2
COMBAT_COOLDOWN = 4.0


@dataclass
class SimFrame:
    """Events from one kernel.step() for the presentation shell to react to."""

    sim_ticks: int = 0                              # ticks advanced this frame
    combat_trigger: object | None = None            # entity to fight (shell runs modal)
    trap_hints: list = field(default_factory=list)  # [str] perception hints to print
    panel_edge: str | None = None                   # [PANEL] edge message, or None
    zone_flash: str | None = None                   # room name the PLAYER entered, or None
    panel_changed: tuple | None = None              # (panel_x, panel_y) the player just entered


class SimulationKernel:
    """Owns the WorldSession + GameContext; advances the sim with no pygame."""

    def __init__(self, ctx, session: WorldSession) -> None:
        self.ctx = ctx
        self.session = session
        self._last_at_edge: PanelEdge | None = None  # edge-triggered panel detection

    # ── lifecycle (wraps R1 / bootstrap primitives) ─────────────────────────────
    @classmethod
    def new_session(cls, ctx, tile_map, sources) -> "SimulationKernel":
        """Build a kernel around a fresh session."""
        return cls(ctx, WorldSession.new_game(ctx, tile_map, sources))

    def start_new_session(self) -> None:
        """New Game: rebuild a fresh session in place, reusing world-scope
        tile_map + sources (not recreated). Resets edge-trigger state."""
        home = self.session.panel_maps.get(HOME_PANEL, self.session.tile_map)
        self.session = WorldSession.new_game(self.ctx, home, self.session.sources)
        self.ctx.current_panel = HOME_PANEL
        self._last_at_edge = None

    def load(self, save_data) -> None:
        """Patch the current session in place from restore() data."""
        self.session.apply_save(save_data, self.ctx)

    def resolve_combat(self, entity, result: str, now: float) -> bool:
        """Apply a combat outcome to the session (model side of the handoff, R4).
        Records the cooldown; on a win marks the entity defeated. Returns True if
        the entity died so the shell can kill its sprite (view side)."""
        self.session.combat_cooldowns[entity.entity_id] = now
        if result == "win":
            self.session.defeated_npcs.add(entity.entity_id)
            return True
        return False

    def save(self, slot_id: int = 0) -> None:
        """Snapshot the current session to a slot."""
        self.ctx.save_manager.snapshot_session(self.session, slot_id=slot_id)

    # ── the headless line ───────────────────────────────────────────────────────
    def step(self, dt: float, now: float) -> SimFrame:
        s = self.session
        frame = SimFrame()

        # Threat escalation input: average living-goblin hunger (H4).
        living_count = len(s.npc_list) - len(s.defeated_npcs)
        goblin_hungers = []
        for npc_e, npc_c in s.npc_list:
            if npc_e.entity_id not in s.defeated_npcs and npc_e.subtype == "goblin":
                h = next((n for n in npc_c.needs if n.need_id == "hunger"), None)
                if h:
                    goblin_hungers.append(h.current_value / 100.0)
        avg_goblin_hunger = (sum(goblin_hungers) / len(goblin_hungers)
                             if goblin_hungers else 1.0)

        frame.sim_ticks = s.world_sim.tick(dt, living_count, avg_goblin_hunger)

        # Glass Box A3: stamp the current tick so sim-side event appends timestamp.
        from Mechanics.observation.event_log import EVENTS
        EVENTS.set_tick(s.world_sim.clock.tick_count)

        # Zone crossing detection: fires the wired sim-side observers (logging +
        # zone AI) and returns the events. The player's crossing becomes a UI
        # SimFrame event (zone_flash) for the shell — Model/View split (R3).
        # Each panel's entities are checked against that panel's map and rooms (Arc B).
        if frame.sim_ticks > 0:
            by_panel: dict = {}
            for e in [e for e, _ in s.npc_list if e.entity_id not in s.defeated_npcs] + [s.player]:
                by_panel.setdefault(s.panel_of(e), []).append(e)
            events = []
            for panel, group in by_panel.items():
                events += s.world_sim.zone_tracker.check_and_fire(
                    group, s.map_for(panel), self.ctx.rooms, panel[0], panel[1],
                    s.world_sim.clock.tick_count,
                )
            for ev in events:
                if ev.entity_name == s.player.name:
                    frame.zone_flash = ev.to_room.name if ev.to_room else "Unknown"
                    break

        # Occupancy + proximity fear / contested sources (H4).
        all_entities = (
            [e for e, _ in s.npc_list if e.entity_id not in s.defeated_npcs]
            + [s.player]
        )
        # Occupancy is per panel: nobody blocks a tile on a panel they are not on (Arc B).
        occupied_by = {e.entity_id: (s.panel_of(e), s.tile_map.world_to_grid(e.x, e.y))
                       for e in all_entities}
        contested = update_proximity_fear(s.npc_list, s.defeated_npcs)

        # NPC decision + physiology.
        for npc_entity, npc_ctrl in s.npc_list:
            if npc_entity.entity_id not in s.defeated_npcs:
                here = s.panel_of(npc_entity)
                others = {pos for eid, (panel, pos) in occupied_by.items()
                          if eid != npc_entity.entity_id and panel == here}
                npc_ctrl.contested_sources = contested
                npc_ctrl.update(dt, occupied_tiles=others)
                apply_health_drain(npc_ctrl.needs, npc_entity, dt)
                apply_regen(npc_ctrl.needs, npc_entity, dt)
                npc_entity.update(dt)

        # Player physiology (controller intent already applied by the shell).
        s.player_controller.update(dt)
        s.player.update(dt)
        update_needs(s.player_needs)
        apply_health_drain(s.player_needs, s.player, dt)
        apply_regen(s.player_needs, s.player, dt)

        # Passive Intuition trap perception (§M8) — returned, printed by the shell.
        frame.trap_hints = list(perceive_traps(s.player, s.chests_on(s.player_panel)))

        # Panel edges: cross into a defined neighbour, else report the edge once (edge-triggered).
        frame.panel_changed = self._cross_panel_edge()
        frame.panel_edge = self._detect_panel_edge()
        frame.combat_trigger = self._detect_combat(now)
        return frame

    # ── detection helpers ───────────────────────────────────────────────────────
    def _player_edge(self) -> PanelEdge | None:
        """The panel edge the player stands on, if any."""
        s = self.session
        pcol = int(s.player.x // settings.TILE_SIZE)
        prow = int(s.player.y // settings.TILE_SIZE)
        if prow <= 0:
            return PanelEdge.NORTH
        if prow >= settings.ROWS - 1:
            return PanelEdge.SOUTH
        if pcol <= 0:
            return PanelEdge.WEST
        if pcol >= settings.COLS - 1:
            return PanelEdge.EAST
        return None

    # Outward direction of each edge (intent sign that means "keep going off this edge").
    _OUTWARD = {PanelEdge.NORTH: (0, -1), PanelEdge.SOUTH: (0, 1),
                PanelEdge.WEST: (-1, 0), PanelEdge.EAST: (1, 0)}

    def _cross_panel_edge(self) -> tuple | None:
        """The player on an edge, pushing outward, with a neighbour defined there, steps onto the
        neighbour's facing edge in the same column (or row). Returns the new panel, or None.
        Refused if the arrival tile is blocked (the edge contract EC2 says it never is)."""
        s = self.session
        edge = self._player_edge()
        if edge is None:
            return None
        ox, oy = self._OUTWARD[edge]
        ix, iy = s.player_controller.move_intent
        if not ((ox and ix * ox > 0) or (oy and iy * oy > 0)):
            return None
        px, py = s.player_panel
        if not self.ctx.panel_loader.can_transition(px, py, edge):
            return None
        target = (px + ox, py + oy)
        tile = settings.TILE_SIZE
        col = int(s.player.x // tile) if ox == 0 else (settings.COLS - 1 if ox < 0 else 0)
        row = int(s.player.y // tile) if oy == 0 else (settings.ROWS - 1 if oy < 0 else 0)
        if s.map_for(target).is_blocked(col, row):
            return None
        s.player.x, s.player.y = col * tile + tile / 2, row * tile + tile / 2
        s.enter_panel(target, self.ctx)
        self._last_at_edge = self._player_edge()
        return target

    def _detect_panel_edge(self) -> str | None:
        """Edge-triggered: return a [PANEL] message once per new edge entry with no neighbour."""
        edge_now = self._player_edge()
        msg = None
        if edge_now is not None and edge_now is not self._last_at_edge:
            px, py = self.session.player_panel
            if not self.ctx.panel_loader.can_transition(px, py, edge_now):
                msg = (f"[PANEL] Player at {edge_now.value.lower()} edge of "
                       f"Panel({px},{py}) — no adjacent panel defined.")
        self._last_at_edge = edge_now
        return msg

    def _detect_combat(self, now: float):
        """First living NPC within trigger distance past its cooldown, or None."""
        s = self.session
        for npc_entity, _ in s.npc_list:
            if npc_entity.entity_id in s.defeated_npcs:
                continue
            if s.panel_of(npc_entity) != s.player_panel:
                continue                             # nothing reaches across a panel edge
            since_last = now - s.combat_cooldowns.get(npc_entity.entity_id, -999)
            if since_last < COMBAT_COOLDOWN:
                continue
            dist = math.hypot(s.player.x - npc_entity.x, s.player.y - npc_entity.y)
            if dist < COMBAT_TRIGGER_DIST:
                return npc_entity
        return None
