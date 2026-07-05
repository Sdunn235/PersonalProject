# Mechanics/items/

Domain model package for items and equipment. Stage 2 of the TheForge Combine Arc.

## Modules

| File | Contents |
|---|---|
| `enums.py` | `SlotType`, `BodySlot`, `WeaponType`, `ArmorWeight`, `ConsumableEffect`, `TrapType`, `body_slot_to_eligible()` |
| `models.py` | `Item`, `DurableItem`, `Weapon`, `Armor`, `Shield`, `Consumable` |
| `__init__.py` | Flat re-export of all enums and model classes |

## Class Hierarchy

```
Item
├── DurableItem
│   ├── Weapon      — attack_power, resonance, weapon_type; eligible_slots = ANY_HAND
│   └── Armor       — defense_rating, resist_rating, weight_class, body_slot; eligible_slots = body_slot_to_eligible()
│       └── Shield  — body_slot defaults OFF_HAND; eligible_slots = ANY_HAND
└── Consumable      — effect (ConsumableEffect), potency; eligible_slots = None
```

## Design Contracts

- `Item.from_dict(d)` is a **factory** — it dispatches to the correct concrete class based on `d["type"]` and `d["slot"]`.
- Each concrete `from_dict()` is a **bridge adapter**: reads new canonical fields first, falls back to the old `effects` dict for backward compatibility with current `items.json`. The bridge is removed in Phase 2.2 when the seed data is updated.
- `eligible_slots` is a `@property`, not a stored field. It is computed from the item's type and `body_slot` at read time.
- `to_dict()` outputs the new canonical format (flat named fields, no `effects` nesting).

## Stage 2 Integration

| Phase | What happens |
|---|---|
| **2.1 (this package)** | Enums and model classes defined. No callers wired yet. |
| **2.2** | Migration m0003, new schema. `items.json` updated to canonical format. `from_dict()` bridge no longer needed. |
| **2.3** | Repository and service layers. `ItemService` uses these types. `ItemDef` in `data/models.py` retired. |
| **2.4** | Combat refactor. `resolve_equipment()`, `get_item_as_combat()`, `fighter.weapon` all updated to use typed models instead of flat dicts. Known armor-DEF defect fixed. |
| **2.5** | Inventory UI modal using these types. |

## Bible References

- `§A1` — Items as capability grants (equip / use / carry / take)
- `§A2` — Carry as bodily budget (`weight` field; capacity = 20 + 2×STR)
- `§A3` — Slot doctrine (`SlotType` flags, dual-wield, `pick_slot_for` algorithm)
- `§A6` — `resonance` on Weapon = intrinsic Byte-attunement (distinct from arcane focus §6.6)
- `§A7` — `value` field planted; unit name deferred to §15
- `§A8` — `durability` field exists; decay mechanics deferred
- Terminology map: `docs/bible/lucentforge_terminology_map_v_1.md`
