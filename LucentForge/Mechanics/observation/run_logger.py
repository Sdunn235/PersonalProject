# run_logger.py — Heartbeat-6 run-log: CSV record of world + NPC state over a run,
# plus an emergence summary written at the end. The point of Heartbeat-6 is to
# *prove* emergence over time, not just observe it live in the panel.
from __future__ import annotations
import csv
import os
from datetime import datetime


class RunLogger:
    """Records world + per-NPC state to CSV every sample, and writes an
    emergence summary when the run ends.

    Two CSVs per run under logs/run_<timestamp>/:
      - world.csv : one row per sample (day, food, threat, stage, town, stocks)
      - npcs.csv  : one row per living NPC per sample (state, need, target, hp)
    """

    _TOWN_SEVERITY = {"stable": 0, "strained": 1, "collapsing": 2}

    def __init__(self, base_dir: str = "logs"):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(base_dir, f"run_{stamp}")
        os.makedirs(self.run_dir, exist_ok=True)

        self._world_f = open(os.path.join(self.run_dir, "world.csv"),
                             "w", newline="", encoding="utf-8")
        self._npc_f = open(os.path.join(self.run_dir, "npcs.csv"),
                           "w", newline="", encoding="utf-8")
        self._world_w = csv.writer(self._world_f)
        self._npc_w = csv.writer(self._npc_f)

        self._world_w.writerow(["tick", "day", "phase", "food_total",
                                "threat", "stage", "town", "sources"])
        self._npc_w.writerow(["tick", "name", "subtype", "state",
                              "priority_need", "need_value", "zone",
                              "target", "hp",
                              "room", "aff_score", "comfort", "stress",
                              "best_region", "best_region_pref", "relocating"])

        # Accumulated run stats for the summary
        self._samples = 0
        self._min_food = float("inf")
        self._peak_threat = 0.0
        self._worst_town = "stable"
        self._raid_count = 0
        self._prev_goblin_state: dict[str, str] = {}
        self._closed = False

    def sample(self, world_sim, sources, npc_list, defeated, tick: int) -> None:
        from Mechanics.needs.needs_system import get_priority_need

        food = world_sim.resources.food_total
        threat = world_sim.threat.threat_level
        stage = world_sim.threat.stage.value
        town = world_sim.town.state.value
        day = world_sim.clock.day
        phase = world_sim.clock.time_phase.value

        src_str = ";".join(f"{s.label}:{s.stock:.0f}/{s.capacity:.0f}"
                           for s in sources if s.is_finite)
        self._world_w.writerow([tick, f"{day:.3f}", phase, f"{food:.1f}",
                                f"{threat:.1f}", stage, town, src_str])

        for npc, ctrl, _ in npc_list:
            if npc.entity_id in defeated:
                continue
            pn = get_priority_need(ctrl.needs)
            target = ctrl.target_source.label if ctrl.target_source else ""
            room = world_sim.zone_tracker._current_rooms.get(npc.name)
            best = getattr(ctrl, "best_region", None)
            self._npc_w.writerow([
                tick, npc.name, npc.subtype, ctrl.state,
                pn.label if pn else "",
                f"{pn.current_value:.1f}" if pn else "",
                pn.zone.value if pn else "FINE",
                target, f"{npc.hp:.0f}",
                room.name if room else "",
                f"{getattr(ctrl, 'affinity_comfort', 0.0):+.2f}",
                f"{ctrl.brain.chemicals.get('comfort'):.3f}",
                f"{ctrl.brain.chemicals.get('stress'):.3f}",
                best[0] if best else "",
                f"{best[1]:+.2f}" if best else "",
                getattr(ctrl, "relocate_target_region", None) or "",
            ])

            # Raid count: goblin transition into RAIDING
            if npc.subtype == "goblin":
                prev = self._prev_goblin_state.get(npc.entity_id)
                if ctrl.state == "RAIDING" and prev != "RAIDING":
                    self._raid_count += 1
                self._prev_goblin_state[npc.entity_id] = ctrl.state

        # Roll up stats
        self._samples += 1
        self._min_food = min(self._min_food, food)
        self._peak_threat = max(self._peak_threat, threat)
        if (self._TOWN_SEVERITY.get(town, 0)
                > self._TOWN_SEVERITY.get(self._worst_town, 0)):
            self._worst_town = town

    def finalize(self, world_sim, npc_list, defeated) -> None:
        if self._closed:
            return
        from Mechanics.needs.needs_system import get_priority_need

        lines = ["=" * 52,
                 "LucentForge - Heartbeat-6 Run Summary",
                 "=" * 52,
                 f"Samples:      {self._samples}",
                 f"Sim days:     {world_sim.clock.day:.2f}",
                 f"Min food:     {self._min_food:.0f}" if self._samples else "Min food:     n/a",
                 f"Peak threat:  {self._peak_threat:.1f}",
                 f"Worst town:   {self._worst_town}",
                 f"Goblin raids: {self._raid_count}",
                 "-" * 52,
                 "Final NPC state:"]
        for npc, ctrl, _ in npc_list:
            if npc.entity_id in defeated:
                lines.append(f"  {npc.name:10} DEFEATED")
                continue
            pn = get_priority_need(ctrl.needs)
            need_str = (f"{pn.label} {pn.current_value:.0f} ({pn.zone.value})"
                        if pn else "all FINE")
            lines.append(f"  {npc.name:10} {ctrl.state:11} hp={npc.hp:.0f}  need={need_str}")
        summary = "\n".join(lines)

        print("\n" + summary)
        with open(os.path.join(self.run_dir, "summary.txt"), "w",
                  encoding="utf-8") as f:
            f.write(summary + "\n")

        self._world_f.close()
        self._npc_f.close()
        self._closed = True
        print(f"\n[RUN-LOG] Saved to {self.run_dir}")
