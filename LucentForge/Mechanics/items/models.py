from __future__ import annotations
from dataclasses import dataclass, field

from .enums import ArmorWeight, BodySlot, ConsumableEffect, SlotType, TrapType, WeaponType, body_slot_to_eligible


@dataclass
class Item:
    id: str
    name: str
    description: str = ""
    value: int = 0          # §A7 economy seed; unit name deferred (§15)
    weight: int = 0         # §4.1 Physique carry budget
    key_id: str | None = None
    container_id: int | None = None   # FK placeholder; populated Phase 2.2

    @property
    def eligible_slots(self) -> SlotType | None:
        return None

    @classmethod
    def from_dict(cls, d: dict) -> Item:
        """Factory — dispatches to concrete subclass based on type/slot fields."""
        item_type = d.get("type", "")
        item_slot = d.get("slot", "")
        if item_type == "weapon":
            return Weapon.from_dict(d)
        if item_type == "armor":
            if item_slot in ("shield", "off_hand"):
                return Shield.from_dict(d)
            return Armor.from_dict(d)
        if item_type == "consumable":
            return Consumable.from_dict(d)
        raise ValueError(f"Unknown item type: {item_type!r}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "weight": self.weight,
            "key_id": self.key_id,
        }


@dataclass
class DurableItem(Item):
    durability: int = 100   # cosmetic Stage 2; decay deferred (§A8)


@dataclass
class Weapon(DurableItem):
    attack_power: int = 0
    resonance: int = 0              # Byte-pattern attunement (terminology map §3.3, §A6)
    weapon_type: WeaponType = WeaponType.SWORD

    @property
    def eligible_slots(self) -> SlotType:
        return SlotType.ANY_HAND    # either hand; dual-wield legal (§A3)

    @classmethod
    def from_dict(cls, d: dict) -> Weapon:
        effects = d.get("effects", {})
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            value=d.get("value", 0),
            weight=d.get("weight", 0),
            key_id=d.get("key_id"),
            durability=d.get("durability", 100),
            attack_power=d.get("attack_power", effects.get("atk", 0)),
            resonance=d.get("resonance", effects.get("mag", 0)),
            weapon_type=WeaponType[d.get("weapon_type", "SWORD").upper()],
        )

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "type": "weapon",
            "durability": self.durability,
            "attack_power": self.attack_power,
            "resonance": self.resonance,
            "weapon_type": self.weapon_type.name,
        }


@dataclass
class Armor(DurableItem):
    defense_rating: int = 0
    resist_rating: int = 0          # §7 elemental proxy; per-element split deferred
    weight_class: ArmorWeight = ArmorWeight.LIGHT
    body_slot: BodySlot = BodySlot.CHEST

    @property
    def eligible_slots(self) -> SlotType:
        return body_slot_to_eligible(self.body_slot)

    @classmethod
    def from_dict(cls, d: dict) -> Armor:
        effects = d.get("effects", {})
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            value=d.get("value", 0),
            weight=d.get("weight", 0),
            key_id=d.get("key_id"),
            durability=d.get("durability", 100),
            defense_rating=d.get("defense_rating", effects.get("def", 0)),
            resist_rating=d.get("resist_rating", effects.get("res", 0)),
            weight_class=ArmorWeight[d.get("weight_class", "LIGHT").upper()],
            body_slot=BodySlot[d.get("body_slot", "CHEST").upper()],
        )

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "type": "armor",
            "durability": self.durability,
            "defense_rating": self.defense_rating,
            "resist_rating": self.resist_rating,
            "weight_class": self.weight_class.name,
            "body_slot": self.body_slot.name,
        }


@dataclass
class Shield(Armor):
    body_slot: BodySlot = BodySlot.OFF_HAND  # overrides Armor default

    @property
    def eligible_slots(self) -> SlotType:
        return SlotType.ANY_HAND    # either hand; pick_slot_for prefers OFF_HAND (§A3)

    @classmethod
    def from_dict(cls, d: dict) -> Shield:
        effects = d.get("effects", {})
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            value=d.get("value", 0),
            weight=d.get("weight", 0),
            key_id=d.get("key_id"),
            durability=d.get("durability", 100),
            defense_rating=d.get("defense_rating", effects.get("def", 0)),
            resist_rating=d.get("resist_rating", effects.get("res", 0)),
            weight_class=ArmorWeight[d.get("weight_class", "LIGHT").upper()],
            body_slot=BodySlot[d.get("body_slot", "OFF_HAND").upper()],
        )

    def to_dict(self) -> dict:
        return {**super().to_dict(), "slot": "shield"}


@dataclass
class Consumable(Item):
    effect: ConsumableEffect = ConsumableEffect.NONE
    potency: int = 0

    @property
    def eligible_slots(self) -> None:
        return None     # consumables have no equipment slot

    @classmethod
    def from_dict(cls, d: dict) -> Consumable:
        effects = d.get("effects", {})
        effect_str = d.get("effect", "NONE").upper()
        potency = d.get("potency", 0)
        # Bridge: infer effect+potency from old effects dict when canonical fields absent
        if effect_str == "NONE" and potency == 0:
            if effects.get("heal"):
                effect_str, potency = "HEAL", effects["heal"]
            elif effects.get("restore_sp"):
                effect_str, potency = "RESTORE_SP", effects["restore_sp"]
            elif effects.get("restore_mp"):
                effect_str, potency = "RESTORE_MP", effects["restore_mp"]
            elif effects.get("restore_bits"):
                effect_str, potency = "RESTORE_BITS", effects["restore_bits"]
            elif effects.get("restore_bytes"):
                effect_str, potency = "RESTORE_BYTES", effects["restore_bytes"]
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            value=d.get("value", 0),
            weight=d.get("weight", 0),
            key_id=d.get("key_id"),
            effect=ConsumableEffect[effect_str],
            potency=potency,
        )

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "type": "consumable",
            "effect": self.effect.name,
            "potency": self.potency,
        }
