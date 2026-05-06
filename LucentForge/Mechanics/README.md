# Mechanics

Core game systems for LucentForge. Each subfolder is one isolated concern (SOLID: Single Responsibility).

| Folder | Responsibility |
|---|---|
| `entities/` | Base Entity class, Stats, Traits, StatusFlags |
| `needs/` | NeedType enum, NeedsSystem loop (`update_needs`, `apply_health_drain`, `apply_regen`), NeedSource |
| `biochem/` | Chemical registry, Drive system, Brain (decision layer) |
| `combat/` | Damage formula, Fighter, turn-based combat engine |
| `items/` | Item dataclass and loader |
| `world/` | TileMap (CSV + procedural), BFS pathfinder |
| `ai/` | NPC entity (hp, stats, cycles/stamina), NPCController (state machine), PlayerController (keyboard + source interaction) |
| `renderer/` | EntitySprite (world-map stat bars), HealthBar, CombatScene, HUD |

## Key design ruleg
`ai/controller.py` depends on abstractions from `needs/`, `biochem/`, and `world/` — never on renderer details.
The biochem layer sits between raw needs and the decision layer. Personality traits only modify biochem weights, not game rules.
