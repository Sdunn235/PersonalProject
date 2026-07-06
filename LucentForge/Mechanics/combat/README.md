# Mechanics/combat/

Core combat engine: turn processing, damage resolution, stat derivation, fighter model.

## Removed in Phase 2.4 (C0016)

- **`equip.py`** — deleted. `resolve_equipment()` read equipment from the raw `effects` dict,
  causing armor `defense_rating` to never reach damage mitigation. Equipment stat mods now
  come from `EquipmentService.gear_mods()` (`Mechanics/services/equipment_service.py`).
  Entity innate DEF/RES passed as a baseline `FlatMods` entry before gear mods.

- **`items.py`** — deleted. `build_bag()` read from the entity blob, bypassing persistent
  inventory entirely — NPC bags were dead code. Bags now come from
  `InventoryService.get_inventory()` (`Mechanics/services/inventory_service.py`).
  Item consumption persists via `_flush_combat_bag()` in `combat_scene.py` at combat end.

## Key files

| File | Role |
|---|---|
| `abilities.py` | `BaseStats`, `FlatMods`, `Stats`, `derive_stats()` |
| `fighter.py` | `Fighter` dataclass, `CombatLoadout`, `build_fighter()` |
| `combat.py` | Facade — `take_turn()` delegates to `TurnProcessor` |
| `turn_processor.py` | Turn logic — ability/spell/item/flee resolution |
| `damage_resolver.py` | Damage and hit calculations |
| `action_selector.py` | NPC action selection heuristics |
| `rng.py` | `SimpleRng` — thin random wrapper |
| `rules.py` | Numeric constants (thresholds, caps, cooldowns) |
