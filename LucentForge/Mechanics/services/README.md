# Mechanics/services/

Service layer for LucentForge. Facades over the domain model. All services are stateful registries
keyed by `entity_id`. They are created in `bootstrap.py` and held by `main.py` — not stored on
`GameContext` (data-only per decision 13 of the Stage 2 master plan).

## Modules

| File | Contents |
|---|---|
| `__init__.py` | Protocol interfaces: `ICombatService`, `INeedsService`, `IEntityFactory`, `IInventoryService`, `IEquipmentService` |
| `inventory_service.py` | `InventoryService` — per-entity bag management, consumable use, weight/capacity |
| `equipment_service.py` | `EquipmentService` — per-entity slot management, stat mods, equip/unequip |
| `outcome.py` | `OutcomeResolver` — §12.2 bounded-variance outcome check engine (lock/trap/skill checks) |

## Architecture

Services are created via `bootstrap.create_item_services(ctx)` at new-game time or rebuilt via
`bootstrap.rebuild_item_services(save_data, ...)` after a save-load. Both functions seed services
from the `entities.json` bag/equipment definitions or saved bag column respectively.

Services do NOT import from each other at module level. `equip()`/`unequip()` accept an optional
`inv_svc` parameter to avoid circular imports while still auto-returning displaced items to inventory.

## Stage 2 Integration

| Phase | What happens |
|---|---|
| **2.3 (this)** | InventoryService + EquipmentService wired. Starting kits seeded. Bag persisted to entity_state via m0004. |
| **2.4** | Combat refactor: `resolve_equipment()` replaced by `EquipmentService.gear_mods()`. `build_bag()` replaced by `InventoryService`. |
| **2.5** | Inventory UI modal driven by these services. Drop/loot/trade actions wired. |

## Bible References

- `§A1` — Items as capability grants (equip / use / carry / take)
- `§A2` — Carry as bodily budget (`CARRY_BASE + 2×STR`)
- `§A3` — Slot doctrine and equip/unequip rules
- `§A5` — Outcome resolution for item interactions (outcome.py implementation)
