from __future__ import annotations
from typing import Protocol, runtime_checkable

from .models import Armor, Consumable, Item, Shield, Weapon


@runtime_checkable
class IItemRepository(Protocol):
    def find_by_id(self, item_id: str) -> Item | None: ...
    def find_all(self) -> list[Item]: ...
    def find_weapons(self) -> list[Weapon]: ...
    def find_armor(self) -> list[Armor]: ...
    def find_consumables(self) -> list[Consumable]: ...


class ItemRepository:
    """Typed item access over the existing SqliteDao.

    Wraps ctx.items (SqliteDao returning raw dicts) and hydrates to typed
    Item subclasses via Item.from_dict(). Callers that still need raw dicts
    (resolve_equipment, get_item_as_combat) should use ctx.items directly
    until Phase 2.4.
    """

    def __init__(self, dao) -> None:
        self._dao = dao  # SqliteDao — untyped to avoid circular import

    def find_by_id(self, item_id: str) -> Item | None:
        raw = self._dao.get_by_id(item_id)
        return Item.from_dict(raw) if raw is not None else None

    def find_all(self) -> list[Item]:
        return [Item.from_dict(r) for r in self._dao.get_all()]

    def find_weapons(self) -> list[Weapon]:
        return [i for i in self.find_all() if isinstance(i, Weapon)]

    def find_armor(self) -> list[Armor]:
        return [i for i in self.find_all() if isinstance(i, Armor)]

    def find_consumables(self) -> list[Consumable]:
        return [i for i in self.find_all() if isinstance(i, Consumable)]
