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
                                 # (reused for per-region affinity comfort — Phase B)

# --- Affinity comfort relocate (biochem/affinity addendum §B4, Phase B) ---
COMFORT_RELOCATE_STRESS_THRESHOLD = 0.4  # sustained stress at/above this can trigger a drift
COMFORT_RELOCATE_MARGIN           = 0.3  # best-remembered comfort must beat current by this
COMFORT_CONTENT_THRESHOLD         = 0.4  # comfort at/above this dampens the drift (settle, stay)

# --- Affinity strain → need urgency (biochem/affinity addendum §B7, Phase C) ---
AFFINITY_STRAIN_GAIN       = 0.0003  # per-tick approach toward discomfort target (~60s to ~50%)
AFFINITY_STRAIN_NEED_BOOST = 0.0002  # per unit strain added to each need chemical per tick

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

# =============================================================================
# HEARTBEAT-6 — Observation Layer (world-overview panel + per-run CSV log)
# =============================================================================

# --- Observation panel (left margin; the level starts at LEVEL_X=224) ---
OBS_PANEL_X        = 8        # left edge of the world-overview panel
OBS_PANEL_W        = 208      # width — fits the free left margin
OBS_PANEL_BG       = (18, 18, 24, 200)   # translucent dark background
OBS_HEADER_COLOR   = (200, 200, 230)
OBS_LABEL_COLOR    = (175, 175, 190)
OBS_HINT_COLOR     = (100, 100, 120)
ZONE_LABEL_DURATION = 90   # frames the room-name flash persists (~1.5 s at 60 fps)

# Town state -> panel color
TOWN_STATE_COLORS  = {
    "stable":     (68, 206, 27),    # green
    "strained":   (242, 161, 52),   # orange
    "collapsing": (229, 31, 31),    # red
}

# --- Run-log (CSV emergence record) ---
RUN_LOG_INTERVAL   = 30      # sample world + NPC state every N sim ticks
RUN_LOG_DIR        = "logs"  # per-run folders created here (gitignored)

# =============================================================================
# PHASE 1.5 — World-State Save / Load
# =============================================================================

AUTOSAVE_INTERVAL  = 1800    # sim ticks between autosaves (~5 sim-minutes at 300s/day)
SAVE_ON_QUIT       = True    # write save slot 0 on clean exit

# PHASE 1.6 — Save Slot UI
AUTOSAVE_SLOT_ID   = 0       # slot 0 is reserved for autosave and quit-save
SAVE_SLOT_COUNT    = 3       # manual save slots (IDs 1, 2, 3)

# =============================================================================
# PHASE 2.3 — Inventory carry budget (§A2)
# =============================================================================
CARRY_BASE    = 20   # base carry capacity in weight units
CARRY_PER_STR = 2    # additional capacity per point of STR

# =============================================================================
# PHASE 2.6 — §12.2 Outcome Resolver
# Bible ref: lucentforge_items_addendum_v_1.md §A5
# =============================================================================
OUTCOME_VARIANCE_MAX  = 5    # max ±variance; |det_margin| beyond this → no roll
OUTCOME_CRIT_MARGIN   = 5    # |final_margin| >= this → critical outcome
ATTR_SCALE            = 1    # each attribute point → 1 outcome score point
LOCKPICK_BASE_VALUE   = 5    # base score for lockpick checks (no skill until Stage 4)

# =============================================================================
# PHASE 2.7 — Chests, Locks, Traps, Keys (E key interaction)
# Bible ref: lucentforge_items_addendum_v_1.md §12.2
# =============================================================================
TRAP_DISARM_DC        = 5    # difficulty class for trap disarm attempts

# Phase 4.2 — passive Intuition trap perception (§M8). Deterministic danger-sense:
# TRAP_PERCEIVE_BASE + Intuition >= perceive DC reveals a nearby trap in advance.
TRAP_PERCEIVE_BASE    = 4    # base score for passive trap perception
TRAP_PERCEIVE_DC      = 10   # Intuition threshold to notice a trap (player Intuition 6 -> clears)
TRAP_PERCEIVE_RADIUS  = 3    # tiles (Manhattan) within which perception runs

# =============================================================================
# PHASE 4.5 — Bit/Byte casting economy (§M4)
# Spell costs are formula-derived from power: one tuning knob per pool, not
# per-spell hand-tuning. Heals use amount_pct * HEAL_POWER_SCALE as pseudo-power.
# =============================================================================
BIT_COST_PER_POWER   = 5     # bit-spell cost = round(power * this)
BYTE_COST_PER_POWER  = 3     # byte-spell cost = round(pseudo_power * this)
HEAL_POWER_SCALE     = 10    # heal amount_pct -> pseudo-power for cost derivation
CONVERT_RATE_BITS    = 16    # Bits consumed per Convert action (-> /8 Bytes), Phase 4.5b
