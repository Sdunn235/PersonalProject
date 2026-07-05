from __future__ import annotations
from dataclasses import dataclass, field
from Mechanics.items.models import Item


@dataclass
class ItemStack:
    item: Item
    qty: int = 1


@dataclass
class Inventory:
    owner_id: str
    stacks: list[ItemStack] = field(default_factory=list)

    def find_stack(self, item_id: str) -> ItemStack | None:
        return next((s for s in self.stacks if s.item.id == item_id), None)

    def add(self, item: Item, qty: int = 1) -> None:
        existing = self.find_stack(item.id)
        if existing:
            existing.qty += qty
        else:
            self.stacks.append(ItemStack(item, qty))

    def remove(self, item_id: str, qty: int = 1) -> bool:
        stack = self.find_stack(item_id)
        if stack is None or stack.qty < qty:
            return False
        stack.qty -= qty
        if stack.qty == 0:
            self.stacks.remove(stack)
        return True

    def total_weight(self) -> float:
        return sum(s.item.weight * s.qty for s in self.stacks)

    def to_list(self) -> list[dict]:
        return [{"item_id": s.item.id, "qty": s.qty} for s in self.stacks]


@dataclass
class EquipmentSet:
    owner_id: str
    slots: dict[str, Item] = field(default_factory=dict)

    def get_slot(self, slot_name: str) -> Item | None:
        return self.slots.get(slot_name)

    def put_slot(self, slot_name: str, item: Item) -> Item | None:
        displaced = self.slots.get(slot_name)
        self.slots[slot_name] = item
        return displaced

    def clear_slot(self, slot_name: str) -> Item | None:
        return self.slots.pop(slot_name, None)

    def all_equipped(self) -> list[Item]:
        return list(self.slots.values())

    def to_dict(self) -> dict[str, str]:
        return {slot: item.id for slot, item in self.slots.items()}
