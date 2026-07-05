from __future__ import annotations
import settings
from Mechanics.items.containers import Inventory, ItemStack
from Mechanics.items.enums import ConsumableEffect
from Mechanics.items.models import Consumable, Item


class InventoryService:
    """Facade over all entity Inventory objects. Stateful registry keyed by entity_id."""

    def __init__(self) -> None:
        self._inventories: dict[str, Inventory] = {}

    def register(self, entity_id: str, inventory: Inventory) -> None:
        self._inventories[entity_id] = inventory

    def get_inventory(self, entity_id: str) -> Inventory | None:
        return self._inventories.get(entity_id)

    def add_item(self, entity_id: str, item: Item, qty: int = 1) -> bool:
        inv = self._inventories.get(entity_id)
        if inv is None:
            return False
        inv.add(item, qty)
        return True

    def remove_item(self, entity_id: str, item_id: str, qty: int = 1) -> bool:
        inv = self._inventories.get(entity_id)
        if inv is None:
            return False
        return inv.remove(item_id, qty)

    def use_consumable(self, entity_id: str, item_id: str) -> ConsumableEffect | None:
        """Consume one use of item_id. Returns effect type; caller applies it to entity stats."""
        inv = self._inventories.get(entity_id)
        if inv is None:
            return None
        stack = inv.find_stack(item_id)
        if stack is None or not isinstance(stack.item, Consumable):
            return None
        effect = stack.item.effect
        inv.remove(item_id, 1)
        return effect

    def carried_weight(self, entity_id: str) -> float:
        inv = self._inventories.get(entity_id)
        return inv.total_weight() if inv else 0.0

    def capacity(self, str_stat: int) -> float:
        return float(settings.CARRY_BASE + settings.CARRY_PER_STR * str_stat)

    def is_encumbered(self, entity_id: str, str_stat: int) -> bool:
        return self.carried_weight(entity_id) > self.capacity(str_stat)

    def serialize_all(self) -> dict[str, list]:
        return {eid: inv.to_list() for eid, inv in self._inventories.items()}
