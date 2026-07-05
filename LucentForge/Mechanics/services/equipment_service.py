from __future__ import annotations
from Mechanics.items.containers import EquipmentSet
from Mechanics.items.models import Armor, Item, Weapon
from Mechanics.items.repos import IItemRepository


class EquipmentService:
    """Facade over all entity EquipmentSet objects. Keyed by entity_id."""

    def __init__(self, item_repo: IItemRepository) -> None:
        self._item_repo = item_repo
        self._equipment: dict[str, EquipmentSet] = {}

    def register(self, entity_id: str, equip_set: EquipmentSet) -> None:
        self._equipment[entity_id] = equip_set

    def get_equipment(self, entity_id: str) -> EquipmentSet | None:
        return self._equipment.get(entity_id)

    def equip(self, entity_id: str, item: Item, slot_name: str,
              inv_svc=None) -> Item | None:
        """Place item in slot. Returns displaced item. If inv_svc given, displaced item
        goes back to inventory automatically."""
        equip_set = self._equipment.get(entity_id)
        if equip_set is None:
            return None
        displaced = equip_set.put_slot(slot_name, item)
        if displaced is not None and inv_svc is not None:
            inv_svc.add_item(entity_id, displaced)
        return displaced

    def unequip(self, entity_id: str, slot_name: str, inv_svc=None) -> Item | None:
        """Remove item from slot. If inv_svc given, adds to inventory."""
        equip_set = self._equipment.get(entity_id)
        if equip_set is None:
            return None
        item = equip_set.clear_slot(slot_name)
        if item is not None and inv_svc is not None:
            inv_svc.add_item(entity_id, item)
        return item

    def gear_mods(self, entity_id: str) -> dict[str, int]:
        """Combined stat mods from equipped items (canonical fields).
        Phase 2.4 replaces resolve_equipment() with this."""
        equip_set = self._equipment.get(entity_id)
        if equip_set is None:
            return {}
        mods: dict[str, int] = {}
        for item in equip_set.all_equipped():
            if isinstance(item, Weapon):
                mods["atk"] = mods.get("atk", 0) + item.attack_power
                if item.resonance:
                    mods["mag"] = mods.get("mag", 0) + item.resonance
            elif isinstance(item, Armor):
                if item.defense_rating:
                    mods["def"] = mods.get("def", 0) + item.defense_rating
                if item.resist_rating:
                    mods["res"] = mods.get("res", 0) + item.resist_rating
        return mods

    def weapon_profile(self, entity_id: str) -> Item | None:
        equip_set = self._equipment.get(entity_id)
        if equip_set is None:
            return None
        return equip_set.get_slot("weapon")

    def serialize_all(self) -> dict[str, dict[str, str]]:
        return {eid: es.to_dict() for eid, es in self._equipment.items()}
