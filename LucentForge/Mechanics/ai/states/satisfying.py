# satisfying.py — SatisfyingState: fill need at source
from __future__ import annotations
import math
from Mechanics.needs.need import NeedZone
from Mechanics.needs.needs_system import fill_need
from Mechanics.ai.interpreter import interpret_outcome
import settings


class SatisfyingState:
    name = "SATISFYING"

    def enter(self, controller) -> None:
        pass

    def update(self, controller, dt: float) -> None:
        if controller.target_source is None:
            controller._set_state("IDLE")
            return

        need = next((n for n in controller.needs
                     if n.need_id == controller.target_source.need_id), None)
        if need is None:
            controller._set_state("IDLE")
            return

        # Only interrupt if another need is CRITICAL AND lower than current
        critical_override = next(
            (n for n in controller.needs
             if n.zone == NeedZone.CRITICAL
             and n.need_id != controller.target_source.need_id
             and n.current_value < need.current_value),
            None
        )
        if critical_override:
            print(f"[INTERRUPT] {controller.npc.name}: {critical_override.label} ({critical_override.current_value:.1f}) "
                  f"more critical than {need.label} ({need.current_value:.1f}) -- re-routing")
            controller.target_source = None
            controller._set_state("IDLE")
            return

        done = fill_need(need, dt, source=controller.target_source)

        # H5: source ran out mid-fill — NPC must find another source
        if (not done
                and controller.target_source is not None
                and controller.target_source.is_finite
                and controller.target_source.stock <= 0):
            print(f"[DEPLETED] {controller.npc.name}: {controller.target_source.label} "
                  f"ran out while eating ({need.label} at {need.current_value:.1f})")
            controller.target_source = None
            controller._set_state("IDLE")
            return

        if done:
            # Interpret outcome and record memory (Heartbeat-3)
            start_x, start_y = controller._decision_start_pos
            distance = math.hypot(controller.npc.x - start_x,
                                  controller.npc.y - start_y)
            quality = interpret_outcome(
                need_zone_at_decision=controller._decision_need_zone or NeedZone.WARNING,
                distance_traveled=distance,
                was_interrupted=controller._was_interrupted,
                traits=controller.brain.traits,
            )
            controller.memory.record_outcome(
                source_label=controller.target_source.label,
                need_id=controller.target_source.need_id,
                quality_score=quality,
                tick=controller._tick,
            )
            # Trait drift based on outcome quality (Heartbeat-3)
            drift = settings.TRAIT_DRIFT_AMOUNT
            if quality >= 0.7:
                controller.brain.traits.drift("curiosity", drift * 0.5)
            elif quality <= 0.3:
                controller.brain.traits.drift("fearfulness", drift)
                controller.brain.traits.drift("curiosity", -drift * 0.3)

            stock_info = ""
            if controller.target_source.is_finite:
                stock_info = (f", stock={controller.target_source.stock:.0f}"
                              f"/{controller.target_source.capacity:.0f}")
            print(f"[DONE] {controller.npc.name}: {need.label} satisfied "
                  f"(quality={quality:.2f}, "
                  f"mem={controller.memory.get_source_preference(controller.target_source.label):.2f}"
                  f"{stock_info})")
            controller.target_source = None
            controller._last_need_log = None
            controller._set_state("IDLE")
