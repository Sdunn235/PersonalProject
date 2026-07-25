"""shell.py — PresentationShell: the pygame view + RuntimeMode machine (R4).

The shell is the swappable *view* over a `SimulationKernel`. It owns everything
pygame: the screen/clock/fonts, the sprite-per-entity map + group, HUD state
(tab index, observation toggle), and the zone-flash countdown. `run(kernel)` is
the driver loop: input → (mode) → `kernel.step(dt, now)` → react to the `SimFrame`
(combat modal, sprite kills, hints, flash) → render.

`RuntimeMode` labels the interaction context, mirroring the `NPCController`
string-keyed state machine one level up. WORLD is the persistent gameplay mode;
the other modes are modal dialogs entered from WORLD. The dialogs are still the
existing blocking sub-loops (behavior-preserving) — the modes formalize *which*
context is active and, for COMBAT, the kernel handoff:
WORLD detects trigger → COMBAT runs `run_combat` → `kernel.resolve_combat` applies
the outcome (model) → shell kills the sprite (view) → WORLD.
"""
from __future__ import annotations

from enum import Enum

# noinspection PyPackageRequirements
import pygame
import settings
from Mechanics.entities.factory import get_sprite_path
from Mechanics.renderer.sprite import EntitySprite
from Mechanics.renderer.save_menu import run_load_menu, run_save_menu
from Mechanics.renderer.pause_menu import run_pause_menu
from Mechanics.renderer.combat_scene import run_combat
from Mechanics.renderer.hud import draw_hud
from Mechanics.renderer.trap_overlay import draw_trap_markers
from Mechanics.renderer.health_bar import draw_stat_bar
from Mechanics.renderer.observation_panel import draw_observation_panel
from Mechanics.observation.run_logger import RunLogger
from Mechanics.combat.casting import convert_amount


class RuntimeMode(Enum):
    """Shell interaction context. WORLD is persistent; the rest are modal dialogs
    entered from WORLD (blocking sub-loops today)."""
    WORLD     = "WORLD"
    COMBAT    = "COMBAT"
    PAUSED    = "PAUSED"
    INVENTORY = "INVENTORY"
    CHEST     = "CHEST"
    SAVE_MENU = "SAVE_MENU"


class PresentationShell:
    """pygame view + input over a headless SimulationKernel."""

    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.screen = pygame.display.set_mode((settings.WINDOW_W, settings.WINDOW_H))
        pygame.display.set_caption("LucentForge — NPC Needs Prototype")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 16)
        self.label_font = pygame.font.SysFont(None, 18)

        self.sprites: dict = {}
        self.sprite_group = pygame.sprite.Group()
        self.hud_index = 0
        self._hud_subjects: list = []
        self.obs_visible = True                 # Heartbeat-6 observation panel ('O')
        self.zone_flash: list = [None]          # Phase 3.4 (room_name, frames_left) | None
        self.mode = RuntimeMode.WORLD
        self.running = True
        self._paused_quit = False               # pause-menu quit saves internally
        self.run_logger = None
        self._kernel = None

        # Keydown dispatch — replaces the event if/elif ladder.
        self._keymap = {
            pygame.K_ESCAPE: self._open_pause,
            pygame.K_TAB:    self._cycle_hud,
            pygame.K_i:      self._open_inventory,
            pygame.K_o:      self._toggle_obs,
            pygame.K_s:      self._open_save,
            pygame.K_e:      self._open_chest,
            pygame.K_c:      self._convert_bits,
        }

    @property
    def session(self):
        """Always the kernel's current session (rebinds on New Game)."""
        return self._kernel.session

    # ── driver loop ─────────────────────────────────────────────────────────────
    def run(self, kernel) -> None:
        self._kernel = kernel
        self._build_sprites()
        self._print_world_banner()
        self._launch_slot_picker()
        self.run_logger = RunLogger(settings.RUN_LOG_DIR)
        self._rebuild_hud_subjects()

        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self._handle_events()
            now = pygame.time.get_ticks() / 1000.0
            frame = kernel.step(dt, now)
            self._orchestrate(frame)
            self.sprite_group.update()   # sync sprites to entity state
            self._react(frame)
            self._render(frame)

        self._shutdown()

    # ── sprite layer ────────────────────────────────────────────────────────────
    def _build_sprites(self) -> None:
        s = self.session
        self.sprites = {}
        for npc, _ in s.npc_list:
            self.sprites[npc.entity_id] = EntitySprite(
                npc, image_path=get_sprite_path(self.ctx, npc.entity_id),
                size=settings.TILE_SIZE - 2)
            print(f"[SPAWN] {npc.name} at ({int(npc.x)}, {int(npc.y)})")
        self.sprites[s.player.entity_id] = EntitySprite(
            s.player, image_path=get_sprite_path(self.ctx, s.player.entity_id),
            size=settings.TILE_SIZE - 2)
        print(f"[SPAWN] Player at ({int(s.player.x)}, {int(s.player.y)})  "
              f"[Arrow keys to move]")
        self.sprite_group = pygame.sprite.Group(*self.sprites.values())

    def _kill_defeated_sprites(self) -> None:
        for npc, _ in self.session.npc_list:
            if npc.entity_id in self.session.defeated_npcs:
                self.sprites[npc.entity_id].kill()

    def _rebuild_hud_subjects(self) -> None:
        self._hud_subjects = [(self.session.player, None, "Player")] + [
            (npc, ctrl, None) for npc, ctrl in self.session.npc_list
        ]
        self.hud_index = 0

    # ── startup ─────────────────────────────────────────────────────────────────
    def _print_world_banner(self) -> None:
        s = self.session
        print(f"\n[WORLD SIM] Heartbeat-1 active | "
              f"Food={s.world_sim.resources.food_total:.0f} | "
              f"Threat={s.world_sim.threat.threat_level:.0f} | "
              f"Town={s.world_sim.town.state.value}")
        print("[MAP] Heartbeat-2 active | River barrier, region zones, bridge crossings")
        print("[H4] Goblin behavior active | Hunger-driven threat, patrol/raid states, proximity fear")
        finite = [x for x in s.sources if x.is_finite]
        print(f"[H5] Resource economy active | {len(finite)} finite sources: "
              + ", ".join(f"{x.label}({x.stock:.0f}/{x.capacity:.0f})" for x in finite))
        print()

    def _launch_slot_picker(self) -> None:
        chosen = run_load_menu(self.screen, self.clock, self.ctx, self.font)
        if chosen is not None:
            data = self.ctx.save_manager.restore(slot_id=chosen)
            if data:
                self._kernel.load(data)
                self._kill_defeated_sprites()
                print(f"[SAVE] Session resumed from slot {chosen}.")
            else:
                print(f"[SAVE] Slot {chosen} empty — starting fresh.")
        else:
            print("[SAVE] New Game — starting fresh.")

    # ── input / modes ───────────────────────────────────────────────────────────
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                handler = self._keymap.get(event.key)
                if handler:
                    handler()

    def _open_pause(self) -> None:
        self.mode = RuntimeMode.PAUSED
        s = self.session
        result = run_pause_menu(
            self.screen, self.clock, self.ctx, self.font,
            s.world_sim, s.sources, s.npc_controllers, s.player, s.player_needs,
            s.defeated_npcs, s.combat_cooldowns,
            inv_svc=s.inv_svc, equip_svc=s.equip_svc, chest_reg=s.chest_reg)
        if result == "quit":
            self._paused_quit = True
            self.running = False
        elif result == "new_game":
            self._kernel.start_new_session()
            self._build_sprites()
            self.zone_flash[0] = None
            self._rebuild_hud_subjects()
            self.run_logger = RunLogger(settings.RUN_LOG_DIR)
        elif result.startswith("load:"):
            slot = int(result.split(":")[1])
            data = self.ctx.save_manager.restore(slot_id=slot)
            if data:
                for npc, _ in self.session.npc_list:
                    self.sprite_group.add(self.sprites[npc.entity_id])
                self._kernel.load(data)
                self._kill_defeated_sprites()
                print(f"[SAVE] Session resumed from slot {slot}.")
        # else "resume" — fall through
        self.mode = RuntimeMode.WORLD

    def _cycle_hud(self) -> None:
        self.hud_index = (self.hud_index + 1) % len(self._hud_subjects)

    def _open_inventory(self) -> None:
        self.mode = RuntimeMode.INVENTORY
        from Mechanics.renderer.inventory_menu import run_inventory_menu
        s = self.session
        run_inventory_menu(self.screen, self.clock, self.ctx, self.font,
                           s.inv_svc, s.equip_svc, s.player)
        self.mode = RuntimeMode.WORLD

    def _toggle_obs(self) -> None:
        self.obs_visible = not self.obs_visible

    def _open_save(self) -> None:
        self.mode = RuntimeMode.SAVE_MENU
        slot = run_save_menu(self.screen, self.clock, self.ctx, self.font)
        if slot is not None:
            self._kernel.save(slot)
        self.mode = RuntimeMode.WORLD

    def _open_chest(self) -> None:
        s = self.session
        pcol = int(s.player.x // settings.TILE_SIZE)
        prow = int(s.player.y // settings.TILE_SIZE)
        adj = None
        for dc, dr in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            adj = next((c for c in s.chest_reg.values()
                        if c.col == pcol + dc and c.row == prow + dr), None)
            if adj:
                break
        if adj:
            self.mode = RuntimeMode.CHEST
            from Mechanics.renderer.chest_menu import run_chest_menu
            from Mechanics.services.outcome import OutcomeResolver
            run_chest_menu(self.screen, self.clock, self.font, adj, s.player,
                           s.inv_svc, s.equip_svc, self.ctx.item_repo, OutcomeResolver())
            self.mode = RuntimeMode.WORLD

    def _convert_bits(self) -> None:
        # Phase 4.5b: out-of-combat Bits->Bytes conversion (§M4).
        p = self.session.player
        b, byt, g = convert_amount(p.bit_pool, p.byte_pool, p.max_byte_pool, p.bit_pool)
        if g > 0:
            p.bit_pool, p.byte_pool = b, byt
            print(f"[CONVERT] {g * 8} Bits -> {g} Bytes  "
                  f"(BP {b}/{p.max_bit_pool}, BYP {byt}/{p.max_byte_pool})")

    # ── per-frame orchestration + reactions ─────────────────────────────────────
    def _orchestrate(self, frame) -> None:
        """Periodic shell policy driven by sim_ticks: status print, autosave, log."""
        s = self.session
        tick = s.world_sim.clock.tick_count
        if frame.sim_ticks > 0 and tick % 30 == 0:
            print(s.world_sim.status_line())
        if (frame.sim_ticks > 0 and settings.AUTOSAVE_INTERVAL > 0
                and tick % settings.AUTOSAVE_INTERVAL == 0):
            self._kernel.save()   # Phase 1.5 autosave (slot 0)
        if frame.sim_ticks > 0 and tick % settings.RUN_LOG_INTERVAL == 0:
            self.run_logger.sample(s.world_sim, s.sources, s.npc_list,
                                   s.defeated_npcs, tick)

    def _react(self, frame) -> None:
        for hint in frame.trap_hints:            # Phase 4.2 (§M8) perception hints
            print(hint)
        if frame.panel_edge:                     # Phase 3.6 edge-triggered panel note
            print(frame.panel_edge)
        if frame.zone_flash is not None:         # Phase 3.4 player room-name flash
            self.zone_flash[0] = (frame.zone_flash, settings.ZONE_LABEL_DURATION)
        if frame.combat_trigger is not None:     # combat handoff (WORLD -> COMBAT)
            self._run_combat(frame.combat_trigger)

    def _run_combat(self, npc) -> None:
        """COMBAT mode: run the modal, report the result to the kernel (model),
        kill the sprite on a win (view), handle game-over."""
        self.mode = RuntimeMode.COMBAT
        s = self.session
        result = run_combat(self.screen, self.clock, self.font, s.player, npc, self.ctx,
                            inv_svc=s.inv_svc, equip_svc=s.equip_svc)
        now = pygame.time.get_ticks() / 1000.0
        died = self._kernel.resolve_combat(npc, result, now)
        if died:
            self.sprites[npc.entity_id].kill()
            print(f"[COMBAT] Player defeated {npc.name}!")
        elif result == "lose":
            print("[COMBAT] Player was defeated — game over.")
            self.running = False
        self.mode = RuntimeMode.WORLD

    # ── render ──────────────────────────────────────────────────────────────────
    def _render(self, frame) -> None:
        s = self.session
        screen = self.screen
        screen.fill(settings.BG_COLOR)
        s.tile_map.draw(screen)
        draw_trap_markers(screen, s.chest_reg, self.font)   # Phase 4.2 (§M8)

        # Source labels (skip those duplicating a zone label; FARM overlaps "Farm").
        _zone_label_names = {"FARM"}
        for src in s.sources:
            if src.label in _zone_label_names:
                continue
            lbl = self.label_font.render(f"[{src.label}]", True, (255, 255, 255))
            screen.blit(lbl, (src.world_x + settings.LEVEL_X - lbl.get_width() // 2,
                              src.world_y + settings.LEVEL_Y - lbl.get_height() // 2))

        # H5: source stock bars for finite sources.
        for src in s.sources:
            if src.is_finite:
                bar_x = src.world_x + settings.LEVEL_X
                bar_y = src.world_y + settings.LEVEL_Y + settings.SOURCE_BAR_OFFSET_Y
                ratio = src.stock / src.capacity if src.capacity > 0 else 1.0
                color = ((68, 206, 27) if ratio > 0.5
                         else (242, 161, 52) if ratio > 0.15
                         else (229, 31, 31))
                draw_stat_bar(screen, bar_x, bar_y, int(src.stock), int(src.capacity),
                              color, (30, 30, 30),
                              width=settings.SOURCE_BAR_WIDTH,
                              height=settings.SOURCE_BAR_HEIGHT)

        self.sprite_group.draw(screen)
        for sprite in self.sprite_group:
            sprite.draw_overlays(screen)

        _e, _ctrl, _lbl = self._hud_subjects[self.hud_index]
        _needs = s.player_needs if _ctrl is None else _ctrl.needs
        _state = _lbl           if _ctrl is None else _ctrl.state
        draw_hud(screen, _e, _needs, _state, self.font, controller=_ctrl)

        if self.obs_visible:
            draw_observation_panel(screen, s.world_sim, s.sources, s.npc_list,
                                   s.defeated_npcs, self.font, player=s.player)

        # Phase 3.4: zone-crossing room-name flash (centered above the tile map).
        if self.zone_flash[0] is not None:
            flash_name, flash_frames = self.zone_flash[0]
            flash_surf = self.font.render(f"[ {flash_name} ]", True, (220, 210, 255))
            flash_x = settings.LEVEL_X + (settings.LEVEL_W - flash_surf.get_width()) // 2
            flash_y = settings.LEVEL_Y - 18
            screen.blit(flash_surf, (flash_x, flash_y))
            self.zone_flash[0] = ((flash_name, flash_frames - 1)
                                  if flash_frames > 1 else None)

        pygame.draw.rect(screen, (80, 80, 100),
                         pygame.Rect(settings.LEVEL_X - 2, settings.LEVEL_Y - 2,
                                     settings.LEVEL_W + 4, settings.LEVEL_H + 4), 2)

        day = s.world_sim.clock.day
        p = s.player
        info_txt = self.font.render(
            f"Day {day:.2f}   HP {p.hp:.0f}/{p.max_hp}"
            f"   SP {p.cycles}/{p.max_cycles}"
            f"   BP {p.bit_pool}/{p.max_bit_pool}"
            f"   BYP {p.byte_pool}/{p.max_byte_pool}",
            True, settings.TEXT_COLOR)
        screen.blit(info_txt, (settings.LEVEL_X, 10))

        pygame.display.flip()

    # ── shutdown ────────────────────────────────────────────────────────────────
    def _shutdown(self) -> None:
        # Phase 1.5: save-on-quit (window-close path; pause-menu quit saved already).
        if settings.SAVE_ON_QUIT and not self._paused_quit:
            self._kernel.save()
        self.run_logger.finalize(self.session.world_sim, self.session.npc_list,
                                 self.session.defeated_npcs)
        pygame.quit()
        print("\n[EXIT] Session ended.")
