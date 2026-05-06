# LucentForge — Project Instructions

## What This Is

Medieval fantasy RPG prototype in PyGame. Core goal: emergent NPC autonomy driven by needs/personality/AI, inspired by Creatures (1996). Simulation and philosophical experiment about agency.

## Build & Run

- `pip install -r requirements.txt`
- `python main.py`

## Current State

Always read `context/session_state.md` first — it is the source of truth.

## Project Master

Full design context: `../../Caelum/Caelum_Framework_Shawn_2026-03-12_Workflow_Expansion/projects/lucent_forge_master.md`

## Architecture Rules

- NEVER flatten Mechanics/ — subfolder structure is intentional (ai/, biochem/, combat/, data/, entities/, items/, needs/, renderer/, world/)
- Keep needs/, biochem/, ai/ as separate systems
- Data-driven: JSON for game data
- SOLID principles, modular ecology

## ReferenceFilesAndCode/

READ ONLY — never modify, rename, or delete files inside it.
DO read, reference, deconstruct, and copy patterns from it. This is source material that informs Mechanics/ and other systems.

## Sprite & Map Conventions

- Sprite sheets: 3 cols × 4 rows (down/left/right/up, 3 frames each)
- Tiles: 32×32px, grid: 18×18 (576×576 screen)
- CSV obstacle maps: 18×18, direct 1:1 mapping

## Key Directories

| Directory | Purpose |
|-----------|---------|
| Mechanics/ | Core game systems |
| assets/ | Images and maps |
| context/ | Session state and project context |
| data/ | Game data files |
| design/ | Canonical design vision docs — architecture, philosophy, port strategy |
| ReferenceFilesAndCode/ | READ ONLY source material — read and reference freely, never modify |

## Philosophy

Emergent NPC autonomy. Modular ecology, not isolated mechanics. Every system is a building block toward the Unreal Engine 5 port.
