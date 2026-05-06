# turn_result.py — Typed turn result replacing raw dicts
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TurnResult:
    type: str              # "hit" | "miss" | "heal" | "use_item"
    amount: int = 0
    crit: bool = False
    ability: str = ""      # ability id
    ability_name: str = ""
    element: str = "neutral"
    item: str = ""         # item id (for use_item)

    def to_dict(self) -> dict:
        d: dict = {"type": self.type, "amount": self.amount}
        if self.type == "hit":
            d["crit"] = self.crit
            d["ability"] = self.ability
            d["ability_name"] = self.ability_name
            d["element"] = self.element
        elif self.type == "miss":
            d["ability"] = self.ability
            d["ability_name"] = self.ability_name
            d["element"] = self.element
        elif self.type == "heal":
            d["ability"] = self.ability
            d["ability_name"] = self.ability_name
        elif self.type == "use_item":
            d["item"] = self.item
        return d
