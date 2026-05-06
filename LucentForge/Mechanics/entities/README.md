# Mechanics/entities — Entity Definitions & Factory

Entity base classes, stat/trait dataclasses, and the data-driven entity factory.

## Files

| File | Purpose |
|---|---|
| `base.py` | Abstract `Entity` base class (hp, position, damage, heal) |
| `stats.py` | `Stats` dataclass (STR, MAG, LCK, DEF, RES, DEX) + `StatusFlags` |
| `traits.py` | `Traits` dataclass (curiosity, aggression, fearfulness, sociability) |
| `status.py` | Status effect flag indices (POISON, BURN, STUNNED, etc.) |
| `factory.py` | Entity factory — spawns NPC/Player from `data/entities.json` |

## Factory Pattern

`factory.py` reads entity definitions from JSON and constructs `NPC` objects:

```python
from Mechanics.entities.factory import create_player, create_all_npcs

player = create_player()        # Player entity from entities.json
npcs   = create_all_npcs()      # All NPC-type entities
sprite = get_sprite_path("npc_01")  # Sprite path lookup
```

To add a new entity: edit `data/entities.json`, no code changes needed.
