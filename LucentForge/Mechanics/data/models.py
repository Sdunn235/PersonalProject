# models.py — Typed data models replacing raw dicts
# Mirrors RPGDatabaseManager's Player, Item, MonsterBase models
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AbilityDef:
    id: str
    name: str
    kind: str                          # "attack" | "heal"
    category: str = "ability"          # "basic" | "ability" | "spell"
    power: float = 1.0
    amount_pct: float = 0.0            # heal % of max HP
    cost_cycles: int = 0
    cost_mp: int = 0
    element: str = "neutral"
    stat: str = "STR"                  # "STR" | "MAG"
    description: str = ""

    @staticmethod
    def from_dict(d: dict) -> AbilityDef:
        return AbilityDef(
            id=d["id"], name=d["name"], kind=d["kind"],
            category=d.get("category", "ability"),
            power=d.get("power", 1.0),
            amount_pct=d.get("amount_pct", 0.0),
            cost_cycles=d.get("cost_cycles", 0),
            cost_mp=d.get("cost_mp", 0),
            element=d.get("element", "neutral"),
            stat=d.get("stat", "STR"),
            description=d.get("description", ""),
        )

    def to_dict(self) -> dict:
        d: dict = {"id": self.id, "name": self.name, "kind": self.kind,
                    "category": self.category}
        if self.kind == "attack":
            d["power"] = self.power
            d["element"] = self.element
        if self.kind == "heal":
            d["amount_pct"] = self.amount_pct
        if self.cost_cycles:
            d["cost_cycles"] = self.cost_cycles
        if self.cost_mp:
            d["cost_mp"] = self.cost_mp
        if self.stat != "STR":
            d["stat"] = self.stat
        return d


@dataclass
class ItemDef:
    id: str
    name: str
    type: str                          # "weapon" | "armor" | "consumable"
    slot: str = ""                     # "weapon" | "armor" | "shield" | ""
    effects: dict = field(default_factory=dict)
    description: str = ""

    @staticmethod
    def from_dict(d: dict) -> ItemDef:
        return ItemDef(
            id=d["id"], name=d["name"], type=d["type"],
            slot=d.get("slot", ""),
            effects=dict(d.get("effects", {})),
            description=d.get("description", ""),
        )

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "type": self.type,
                "slot": self.slot, "effects": self.effects,
                "description": self.description}


@dataclass
class EntityDef:
    id: str
    name: str
    type: str                          # "player" | "npc"
    subtype: str = "human"             # "human" | "goblin" | "dragon"
    level: int = 1
    character_class: str = ""
    hp: int = 100
    max_hp: int = 100
    stats: dict = field(default_factory=dict)
    traits: dict = field(default_factory=dict)
    cycles: dict = field(default_factory=dict)
    mp: dict = field(default_factory=dict)
    spawn: dict = field(default_factory=dict)
    sprite: str = ""
    is_enemy: bool = True
    abilities: list[str] = field(default_factory=list)
    spells: list[str] = field(default_factory=list)
    equipment: dict = field(default_factory=dict)
    bag: list[dict] = field(default_factory=list)
    resistances: dict = field(default_factory=dict)
    fire_damage: int = 0

    @staticmethod
    def from_dict(d: dict) -> EntityDef:
        return EntityDef(
            id=d["id"], name=d["name"], type=d["type"],
            subtype=d.get("subtype", "human"),
            level=d.get("level", 1),
            character_class=d.get("character_class", ""),
            hp=d.get("hp", 100), max_hp=d.get("max_hp", 100),
            stats=dict(d.get("stats", {})),
            traits=dict(d.get("traits", {})),
            cycles=dict(d.get("cycles", {})),
            mp=dict(d.get("mp", {})),
            spawn=dict(d.get("spawn", {})),
            sprite=d.get("sprite", ""),
            is_enemy=d.get("is_enemy", True),
            abilities=list(d.get("abilities", [])),
            spells=list(d.get("spells", [])),
            equipment=dict(d.get("equipment", {})),
            bag=list(d.get("bag", [])),
            resistances=dict(d.get("resistances", {})),
            fire_damage=d.get("fire_damage", 0),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "type": self.type,
            "subtype": self.subtype, "level": self.level,
            "character_class": self.character_class,
            "hp": self.hp, "max_hp": self.max_hp,
            "stats": self.stats, "traits": self.traits,
            "cycles": self.cycles, "mp": self.mp,
            "spawn": self.spawn, "sprite": self.sprite,
            "is_enemy": self.is_enemy,
            "abilities": self.abilities, "spells": self.spells,
            "equipment": self.equipment, "bag": self.bag,
        }
