# npc_logger.py — Observer for zone changes and tick logging
from __future__ import annotations
from Mechanics.needs.need import Need, NeedZone
import settings


class NeedZoneLogger:
    """Observes need zone transitions and logs them."""

    def __init__(self, needs: list[Need], npc_name: str = "???"):
        self._npc_name = npc_name
        self._prev_zones: dict[str, NeedZone] = {
            n.need_id: NeedZone.FINE for n in needs
        }

    def check_zone_changes(self, needs: list[Need]) -> None:
        _severity = {NeedZone.FINE: 0, NeedZone.WARNING: 1, NeedZone.CRITICAL: 2}
        for need in needs:
            prev = self._prev_zones.get(need.need_id, NeedZone.FINE)
            curr = need.zone
            if curr != prev:
                direction = "v" if _severity[curr] > _severity[prev] else "^"
                print(f"[ZONE {direction}] {self._npc_name}: {need.label} "
                      f"{prev.value} -> {curr.value} ({need.current_value:.1f})")
                self._prev_zones[need.need_id] = curr

    def log_needs(self, needs: list[Need], npc, state_name: str, tick: int) -> None:
        parts = []
        for n in needs:
            color_tag = {"FINE": "", "WARNING": "!", "CRITICAL": "!!"}[n.zone.value]
            parts.append(f"{n.label}={n.current_value:.1f}{color_tag}")
        hp_str = f"HP={npc.hp:.0f}"
        print(f"[TICK {tick:>6}]  {'  '.join(parts)}  {hp_str}  state={state_name}")
