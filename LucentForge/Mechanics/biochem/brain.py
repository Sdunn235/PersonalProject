# brain.py — Decision layer: chemicals + drives + traits -> priority need
from __future__ import annotations
from Mechanics.biochem.chemical import Chemicals
from Mechanics.biochem.drive import Drive, make_default_drives
from Mechanics.entities.traits import Traits
from Mechanics.needs.need import Need


class Brain:
    def __init__(self, traits: Traits):
        self.chemicals: Chemicals = Chemicals()
        self.traits: Traits = traits
        self.drives: list[Drive] = make_default_drives()

    def tick(self, needs: list[Need]) -> None:
        """Update chemical state from current needs. Call once per frame."""
        self.chemicals.tick(needs)

    def get_priority_need_id(self, needs: list[Need]) -> str | None:
        """Returns the need_id with highest urgency, or None."""
        scores: dict[str, float] = {}
        for drive in self.drives:
            urgency = drive.compute_urgency(self.chemicals, self.traits)
            if urgency > 0.0:
                scores[drive.need_id] = urgency

        if not scores:
            return None

        for need in needs:
            if need.need_id in scores and not need.is_urgent:
                scores[need.need_id] *= (1.0 - self.traits.curiosity * 0.3)

        return max(scores, key=scores.__getitem__)

    def chem_summary(self) -> str:
        d = self.chemicals.as_dict()
        return " | ".join(f"{k}={v:.3f}" for k, v in d.items())
