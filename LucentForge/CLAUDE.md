# LucentForge — Project Instructions

## What This Is

Medieval fantasy RPG prototype in PyGame. Core goal: emergent NPC autonomy driven by needs/personality/AI, inspired by Creatures (1996). Simulation and philosophical experiment about agency.

## Build & Run

- `pip install -r requirements.txt` (requires `pygame-ce` — NOT vanilla `pygame`; vanilla fails to build on Python 3.14)
- `py main.py` (Windows PowerShell — `python` and `python3` do not resolve on this machine)

## Current State

Always read `context/session_state.md` first — it is the source of truth for working state.

- `CHANGELOG.md` — what shipped, arc by arc (C#### commit IDs). Add to it when an arc or feature lands.
- `BACKLOG.md` — every open item as `LF-###` with a source link. Delete an item when it ships (and log it in the CHANGELOG); give new ideas the next free ID.
- Headless gate before any commit that touches runtime: `py scratchpad/run_all_tests.py` (all green).

## Test-first and autonomy

- **Work test-first:** acceptance example → a test that fails for the right reason → code → full gate.
  Anything you'd check by eye gets a test instead. How: [docs/testing.md](docs/testing.md).
- **What you may do alone vs. what stops at a PR for Shawn:** [docs/autonomy.md](docs/autonomy.md).
  In short: code within approved scope merges to `master` on a green gate + CI; doctrine, policy,
  enforcement and Shawn's own material go through a PR.
- Record results in [docs/verification.md](docs/verification.md) (dated, never rewritten).

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
| Mechanics/ | Core game systems (game data JSON lives in `Mechanics/data/`) |
| assets/ | Images and maps |
| context/ | Session state and project context |
| docs/bible/ | **Design authority** — §-numbered doctrine; requirements cite these sections |
| docs/genesis/, docs/maps/ | World-generator design (docs only) and map layer standards |
| design/ | Early (March 2026) vision docs — philosophy and port strategy; the bible supersedes them where they differ |
| studio/ | AI department agents (Systems Design, QC, Engineering, World Building, Story/Lore) — see `studio/README.md` |
| scratchpad/ | Headless test suites + `run_all_tests.py` master runner |
| ReferenceFilesAndCode/ | READ ONLY source material — read and reference freely, never modify |

## Philosophy

Emergent NPC autonomy. Modular ecology, not isolated mechanics. Every system is a building block toward the Unreal Engine 5 port.
