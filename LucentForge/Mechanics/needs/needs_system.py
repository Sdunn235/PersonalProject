# needs_system.py — NPC needs loop (generic over string need_ids)
from __future__ import annotations
from .need import Need, NeedZone
import settings


HP_REGEN_RATE      = 1.0
STAMINA_REGEN_RATE = 5.0


def update_needs(needs: list[Need], is_sleeping: bool = False) -> None:
    """Tick each need down by its decay_rate.
    During sleep, non-sleep needs decay at their sleep_decay_mult rate.
    """
    for need in needs:
        rate = need.decay_rate
        if is_sleeping and need.need_id != "sleep":
            rate *= need.sleep_decay_mult
        need.current_value = max(0.0, need.current_value - rate)


def sort_needs_by_urgency(needs: list[Need]) -> list[Need]:
    """Sort ascending by current_value (lowest = most urgent first)."""
    arr = list(needs)
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j].current_value > arr[j + 1].current_value:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def get_priority_need(needs: list[Need]) -> Need | None:
    """Returns the most urgent need in WARNING or CRITICAL zone, or None."""
    sorted_needs = sort_needs_by_urgency(needs)
    for need in sorted_needs:
        if need.is_urgent:
            return need
    return None


def fill_need(need: Need, dt: float, source=None) -> bool:
    """Increase need value at source. Uses source-specific rates when available.

    For finite sources, consumes stock — may return less fill if depleted.
    Returns True when fully satisfied (need >= 100).
    """
    if source is not None:
        # Source-aware fill: use source's satisfaction_amount + interaction_time
        fill_per_second = source.satisfaction_amount / (settings.FPS * source.interaction_time)
        fill_amount = fill_per_second * dt * 60
        if source.is_finite:
            fill_amount = source.consume(fill_amount)
        need.current_value = min(100.0, need.current_value + fill_amount)
    else:
        # Backward compat: generic fill_rate (no source context)
        need.current_value = min(100.0, need.current_value + need.fill_rate * dt * 60)
    return need.current_value >= 100.0


def apply_regen(needs: list[Need], entity, dt: float) -> tuple[float, float]:
    """Regen HP and stamina when ALL needs are FINE."""
    if any(n.is_urgent for n in needs):
        return 0.0, 0.0

    hp_gained = HP_REGEN_RATE * dt
    entity.hp = min(entity.max_hp, entity.hp + hp_gained)

    stamina_gained = 0.0
    if hasattr(entity, "cycles"):
        stamina_gained = STAMINA_REGEN_RATE * dt
        entity._stamina_accum = getattr(entity, '_stamina_accum', 0.0) + stamina_gained
        if entity._stamina_accum >= 1.0:
            add = int(entity._stamina_accum)
            entity.cycles = min(entity.max_cycles, entity.cycles + add)
            entity._stamina_accum -= add

    return hp_gained, stamina_gained


def apply_health_drain(needs: list[Need], entity, dt: float) -> float:
    """Drain HP for any need at zero."""
    total_drain = 0.0
    for need in needs:
        if need.is_zero:
            drain = need.hp_drain_rate * dt
            entity.hp = max(0, entity.hp - drain)
            total_drain += drain
    return total_drain
