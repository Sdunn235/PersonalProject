# drive.py — Data-driven drive definitions
# Each drive maps a chemical to a need urgency score.
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Drive:
    name: str
    need_id: str                       # string-based need id
    chemical: str                      # chemical key to read
    base_weight: float = 1.0

    def compute_urgency(self, chemicals, traits) -> float:
        """Return urgency 0.0-1.0 for this drive given current chemical levels."""
        raw = chemicals.get(self.chemical)
        threat_mod = 1.0 + traits.fearfulness * (chemicals.get("pain") + chemicals.get("fear"))
        return min(1.0, raw * self.base_weight * threat_mod)

    @staticmethod
    def from_dict(d: dict) -> Drive:
        """Build a Drive from a needs.json entry."""
        return Drive(
            name=f"{d.get('label', d['id'])} Drive",
            need_id=d["id"],
            chemical=d.get("chemical", d["id"] + "_chem"),
            base_weight=d.get("drive_weight", 1.0),
        )


def make_default_drives() -> list[Drive]:
    """Load drives from needs.json if available, else hardcoded fallback."""
    try:
        from Mechanics.data.dao import Dao
        import os
        needs_path = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "data", "needs.json"))
        if os.path.isfile(needs_path):
            dao = Dao(needs_path)
            return [Drive.from_dict(d) for d in dao.get_all()]
    except Exception:
        pass
    return [
        Drive("Hunger Drive", "hunger", "hunger_chem", base_weight=1.2),
        Drive("Thirst Drive", "thirst", "thirst_chem", base_weight=1.4),
        Drive("Sleep Drive",  "sleep",  "tiredness",   base_weight=0.9),
    ]
