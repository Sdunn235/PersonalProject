# settings.py — Global tuning constants for LucentForge prototype

# --- Display ---
TILE_SIZE   = 32
COLS        = 18
ROWS        = 18

# Level dimensions (the playable area — unchanged)
LEVEL_W     = COLS * TILE_SIZE   # 576
LEVEL_H     = ROWS * TILE_SIZE   # 576

# Window dimensions (full application window with UI border)
WINDOW_W    = 1024
WINDOW_H    = 768

# Level position within the window (centered)
LEVEL_X     = (WINDOW_W - LEVEL_W) // 2   # 224
LEVEL_Y     = (WINDOW_H - LEVEL_H) // 2   # 96

# Backward-compat aliases (game logic uses these for world-space bounds)
SCREEN_W    = LEVEL_W
SCREEN_H    = LEVEL_H

FPS         = 60

# --- Simulation time scale ---
# 1 sim-day = SIM_DAY_SECONDS real seconds (default 120 = 2 min per day)
# Increase to slow down (e.g. 300 = 5 min/day), decrease to speed up
SIM_DAY_SECONDS = 300

# =============================================================================
# NEEDS SYSTEM — 3-Zone Design (Fine / Warning / Critical)
# Based on: RimWorld, Project Zomboid, real human biology
#
# Perfect day guarantee:
#   NPC responds at WARNING threshold -> eats 3x, drinks 5x, sleeps 8hr
#   No need ever reaches 0 on a perfect day
#
# Health drain only starts at exactly 0 (not at Critical)
# =============================================================================

# --- Zone thresholds (per need) ---
HUNGER_WARNING   = 60.0   # NPC starts seeking food here
HUNGER_CRITICAL  = 30.0   # NPC abandons all tasks here

THIRST_WARNING   = 50.0   # NPC starts seeking water here
THIRST_CRITICAL  = 25.0   # NPC abandons all tasks here

SLEEP_WARNING    = 40.0   # NPC starts seeking bed here
SLEEP_CRITICAL   = 20.0   # NPC abandons all tasks here

# --- Decay rates (per real second) ---
# Formula: (100 - WARNING) / (SIM_DAY_SECONDS * waking_fraction / meals_per_day)
# waking_fraction = 16/24 = 0.667 (awake 16hr, asleep 8hr)
# Hunger 3x/day:  40 / (SIM_DAY * 0.222) = 180 / SIM_DAY
# Thirst 5x/day:  50 / (SIM_DAY * 0.133) = 375 / SIM_DAY
# Sleep  1x/day:  60 / (SIM_DAY * 0.667) =  90 / SIM_DAY
HUNGER_DECAY_RATE = 180.0 / SIM_DAY_SECONDS   # per real second
THIRST_DECAY_RATE = 375.0 / SIM_DAY_SECONDS   # per real second (5x more urgent)
SLEEP_DECAY_RATE  =  90.0 / SIM_DAY_SECONDS   # per real second (awake only)

# Convert to per-tick (divide by FPS when used in tick-based code)
HUNGER_DECAY_PER_TICK = HUNGER_DECAY_RATE / FPS
THIRST_DECAY_PER_TICK = THIRST_DECAY_RATE / FPS
SLEEP_DECAY_PER_TICK  = SLEEP_DECAY_RATE  / FPS

# --- Need fill rates (per real second at source) ---
HUNGER_FILL_RATE  = 80.0 / (FPS * 8)    # ~8 sec to eat a full meal
THIRST_FILL_RATE  = 80.0 / (FPS * 3)    # ~3 sec to drink
SLEEP_FILL_RATE   = 80.0 / (FPS * 30)   # ~30 sec to sleep (scaled from 8hr)

# --- Health drain at zero (per real second) ---
# Biology: dehydration kills 5x faster than starvation
# Thirst at 0: dies in ~2 sim-days | Hunger: ~10 sim-days | Sleep: ~5 sim-days
HUNGER_HP_DRAIN = 10.0 / SIM_DAY_SECONDS   # per real second
THIRST_HP_DRAIN = 50.0 / SIM_DAY_SECONDS   # per real second
SLEEP_HP_DRAIN  = 20.0 / SIM_DAY_SECONDS   # per real second

# --- NPC movement ---
NPC_SPEED    = 90    # pixels per second
LOG_INTERVAL = 60    # print to console every N ticks

# --- Colors ---
BG_COLOR        = (30, 30, 30)
TILE_FLOOR      = (65, 65, 65)
TILE_WALL       = (35, 35, 35)
FOOD_COLOR      = (180, 110, 50)
WATER_COLOR     = (50, 120, 200)
SLEEP_COLOR     = (80, 55, 140)
RIVER_COLOR     = (30, 90, 180)
BRIDGE_COLOR    = (140, 100, 55)
GOBLIN_CAMP_COLOR = (120, 50, 50)

# --- Region ground colors (Heartbeat-2 procedural map) ---
REGION_COLORS = {
    "forest":         (55,  85,  45),    # medium forest green (lighter for tree contrast)
    "town_outskirts": (140, 128, 100),   # warm tan
    "town_center":    (160, 145, 115),   # lighter warm tan
    "homes":          (130, 110,  85),   # earthy brown
    "farm":           (95,  120,  60),   # lighter green (tilled land)
    "storage":        (150, 135, 105),   # similar to town center
    "goblin_camp":    (75,   50,  40),   # dark reddish-brown
    "river":          (30,   90, 180),   # blue (same as RIVER_COLOR)
    "bridge":         (140, 100,  55),   # brown wood (same as BRIDGE_COLOR)
    "unknown":        (65,   65,  65),   # fallback gray
}
TREE_COLOR      = (15,  30,  12)     # very dark green obstacle (high contrast vs forest)
ROCK_COLOR      = (90,  85,  80)     # gray-brown rock

NPC_COLOR       = (220, 190, 80)
PLAYER_COLOR    = (100, 160, 255)

# --- Asset paths ---
SPRITE_PLAYER     = "assets/images/human_shadow_warrior.png"
SPRITE_ALDER      = "assets/images/goblin_archer.png"
SPRITE_SECOND_NPC = "assets/images/human_mystic.png"
TEXT_COLOR      = (240, 240, 240)
URGENT_COLOR    = (220, 60, 60)
HUD_BG          = (20, 20, 20, 180)

# Zone bar colors
COLOR_FINE      = (68,  206,  27)   # green
COLOR_WARNING   = (242, 161,  52)   # orange
COLOR_CRITICAL  = (229,  31,  31)   # red

# =============================================================================
# WORLD SIMULATION — Heartbeat-1 (World Orchestration Layer)
# Bible ref: lucentforge_sim_core_schema_v_1.md §13
# =============================================================================

# --- Simulation Clock ---
SIM_TICK_RATE      = 1.0    # sim ticks per real second (1 = real-time pacing)
TICKS_PER_DAY      = SIM_DAY_SECONDS * SIM_TICK_RATE
DAY_PHASE_RATIO    = 0.667  # fraction of day that is daytime (16hr/24hr)

# --- Resource State (legacy — replaced by source-based economy in H5) ---
FOOD_INITIAL       = 100.0  # legacy: starting food supply
FOOD_PRODUCTION    = 0.5    # legacy: food produced per sim tick
FOOD_CONSUMPTION   = 0.3    # legacy: food consumed per sim tick per NPC

# --- Goblin Threat ---
THREAT_INITIAL     = 10.0   # starting threat level
THREAT_GROWTH_RATE = 0.02   # threat increase per sim tick (legacy, kept as fallback)
THREAT_PASSIVE_MAX = 20.0   # below this: goblins are passive (lowered in H5 for faster escalation)
THREAT_RAIDING_MAX = 60.0   # below this: goblins raid; above: attempt crossing
THREAT_MAX         = 100.0  # hard cap

# --- Goblin Behavior (Heartbeat-4) ---
GOBLIN_HUNGER_THREAT_WEIGHT = 0.12   # threat growth per tick scaled by avg goblin hunger (H5: faster escalation)
GOBLIN_THREAT_NATURAL_DECAY = 0.005  # slight threat decay when goblins are fed
GOBLIN_RAID_DURATION        = 30.0   # seconds a goblin blocks a source before retreating
GOBLIN_PATROL_PAUSE         = 3.0    # seconds between patrol waypoints
GOBLIN_FEAR_RADIUS          = 3      # tiles — NPCs within this range of a goblin feel fear
GOBLIN_FEAR_AMOUNT          = 0.15   # fear chemical injected per proximity tick
FORAGE_SATISFACTION         = 40.0   # weak food — less satisfying than FOOD (80) or FARM (60)
FORAGE_INTERACTION_TIME     = 15.0   # slow — 15s vs 8s for FOOD

# --- Town Evaluation ---
TOWN_FOOD_STRAIN   = 30.0   # food_total below this → STRAINED
TOWN_FOOD_COLLAPSE = 10.0   # food_total below this → COLLAPSING
TOWN_THREAT_STRAIN = 50.0   # threat above this contributes to strain
TOWN_MIN_POP       = 2      # fewer living NPCs than this → COLLAPSING

# =============================================================================
# HEARTBEAT-3 — NPC Decision Loop (Interpret / Remember / Drift)
# =============================================================================

# --- NPC Memory ---
MEMORY_EMA_ALPHA       = 0.3     # exponential moving average weight for new observations

# --- Source Selection Weights (rebalanced in H5 for stock factor) ---
SOURCE_DIST_WEIGHT     = 0.4     # weight for distance in source selection
SOURCE_MEMORY_WEIGHT   = 0.3     # weight for memory preference in source selection
SOURCE_STOCK_WEIGHT    = 0.2     # weight for source stock availability (H5)
SOURCE_NOVELTY_WEIGHT  = 0.1     # weight for novelty (curiosity-driven exploration)

# --- Trait Drift ---
TRAIT_DRIFT_AMOUNT     = 0.005   # per outcome event
TRAIT_DECAY_RATE       = 0.001   # per tick toward neutral (0.5)
TRAIT_MIN              = 0.05    # minimum trait value (prevents degenerate behavior)
TRAIT_MAX              = 0.95    # maximum trait value

# --- Interpretation ---
MAX_MAP_DISTANCE       = (LEVEL_W ** 2 + LEVEL_H ** 2) ** 0.5  # map diagonal

# =============================================================================
# HEARTBEAT-5 — Resource Economy (Finite Sources, Depletion, Regeneration)
# =============================================================================

# --- Source Stock Capacities & Regen Rates ---
# Stock = number of "units" a source holds. One full meal costs satisfaction_amount units.
# Regen = units restored per sim tick (1 tick = 1 real second).
# Per-day regen = regen_rate * TICKS_PER_DAY (300 ticks/day at default settings).

# Demand estimate: 4 human NPCs × 3 meals × 80 units = 960/day from civilized sources
# Goal: FARM sustains town alone (~1000/day), FOOD is supplementary, FORAGE fails fast
FOOD_STOCK_CAPACITY    = 300.0   # forest food max stock
FOOD_STOCK_REGEN       = 1.5     # units/tick (~450/day — natural regrowth, decent)
FARM_STOCK_CAPACITY    = 500.0   # farm max stock (largest, most reliable)
FARM_STOCK_REGEN       = 3.5     # units/tick (~1050/day — sustains 4 humans alone)
FORAGE_STOCK_CAPACITY  = 60.0    # goblin forage max (tiny, depletes in hours)
FORAGE_STOCK_REGEN     = 0.08    # units/tick (~24/day — can't sustain 2 goblins)

# --- Source Stock Bar Rendering ---
SOURCE_BAR_WIDTH       = 28
SOURCE_BAR_HEIGHT      = 4
SOURCE_BAR_OFFSET_Y    = -8      # pixels above source center tile

# --- Economy Logging ---
ECON_LOG_INTERVAL      = 30      # source stock summary every N sim ticks
