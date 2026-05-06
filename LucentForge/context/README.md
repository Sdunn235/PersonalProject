# Context — For Future AI Agents and Sessions

This folder is the handoff point between sessions. Read `session_state.md` first.

## What this project is
LucentForge — a medieval fantasy RPG simulation targeting Unreal Engine 5.
Near-term prototype: PyGame RPG with NPC needs/biochem simulation visible on screen.

## Master design doc
`C:\Users\Shawn\Documents\Workspace\Caelum\Caelum_Framework_Shawn_2026-03-12_Workflow_Expansion\projects\lucent_forge_master.md`

## How to run
```
cd "C:\Users\Shawn\Documents\Workspace\Personal Project\LucentForge"
pip install -r requirements.txt
python main.py
```

## Last session
Session 7 — 2026-03-17: Combat UI polish + stamina/regen system. All 5 issues from Session 6 resolved.

## Key architectural decisions
- **Language**: Python 3.10+ / PyGame for prototype. C++ / UE5 for final product.
- **AI model**: Creatures-inspired biochem (chemical drives → need urgency) not scripted state machines
- **Dialog**: Deferred — focus on needs + movement + combat first
- **SOLID**: Every file in `Mechanics/` has one job. Controller depends on abstractions.
