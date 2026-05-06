# Mechanics/combat — Combat System

Turn-based combat engine, ability resolution, and item management.

## Files

| File | Purpose |
|---|---|
| `combat.py` | `Fighter` dataclass, `take_turn()`, `hit_check()`, `damage_roll()` |
| `ability_sets.py` | Resolves entity_id to ability list from `data/abilities.json` |
| `spell_sets.py` | Resolves entity_id to spell list from `data/spells.json` |
| `equip.py` | Resolves entity equipment to flat stat mods from `data/items.json` |
| `items.py` | Resolves item templates from `data/items.json`, builds combat bags |
| `abilities.py` | Stat derivation (`derive_stats`), `BaseStats`, `FlatMods`, `Effect` |
| `rules.py` | Combat tuning constants (hit rates, damage caps, regen, cooldowns) |
| `rng.py` | `SimpleRng` — thin random wrapper for combat rolls |

## Data-Driven Design (Session 10)

Abilities and items now load from JSON via the DAO layer:

```python
from Mechanics.combat.ability_sets import get_abilities, get_basic_attack
from Mechanics.combat.spell_sets import get_spells
from Mechanics.combat.equip import resolve_equipment
from Mechanics.combat.items import build_bag

abilities = get_abilities("player")    # From data/abilities.json
spells    = get_spells("player")       # From data/spells.json (cost MP, scale off MAG)
strike    = get_basic_attack()          # Basic attack from JSON
bag       = build_bag("player")         # Inventory from data/entities.json + items.json
equip     = resolve_equipment("player") # Equipment stat mods from data/items.json
```

## Adding Content

- **New ability**: Add to `data/abilities.json`, reference id in entity's abilities array
- **New item**: Add to `data/items.json`, reference id in entity's bag array
- **New spell**: Add to `data/spells.json`, reference id in entity's spells array. Use `cost_mp` and `stat: "MAG"`.
- **New equipment**: Add to `data/items.json` with `type: "weapon"/"armor"`, `slot`, `effects`. Reference in entity's `equipment`.
- No Python code changes needed for new content
