# Phase 3B - Architecture Diagrams & Visual Reference

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        NPC Character                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    NeedManager                            │  │
│  │  (One instance per NPC, persists for lifetime)          │  │
│  │                                                           │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │ needs_: vector<NPCNeed>                            │ │  │
│  │  │  ┌──────────────┐                                  │ │  │
│  │  │  │ Hunger       │ CurrentValue: 0.8, Threshold: 0.3│ │  │
│  │  │  ├──────────────┤ ⚠️ URGENT (0.8 > 0.3)           │ │  │
│  │  │  │ Thirst       │ CurrentValue: 0.5, Threshold: 0.3│ │  │
│  │  │  ├──────────────┤ ⚠️ URGENT (0.5 > 0.3)           │ │  │
│  │  │  │ Rest         │ CurrentValue: 0.9, Threshold: 0.3│ │  │
│  │  │  ├──────────────┤ ✅ OK (0.9 > 0.3)                │ │  │
│  │  │  │ Social       │ CurrentValue: 0.2, Threshold: 0.3│ │  │
│  │  │  ├──────────────┤ ⚠️ URGENT (0.2 ≤ 0.3)           │ │  │
│  │  │  │ Energy       │ CurrentValue: 1.0, Threshold: 0.3│ │  │
│  │  │  └──────────────┘ ✅ OK (1.0 > 0.3)                │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  initialize()       → Create needs with defaults        │  │
│  │  Update(delta)      → Apply time-based decay           │  │
│  │  GetUrgentNeeds()   → Return indices of urgent needs    │  │
│  │  SatisfyNeed()      → Reset need to 1.0                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  void Tick(float delta) {                                         │
│    needs_.Update(delta);      // Every frame decay update        │
│    auto urgent = needs_.GetUrgentNeeds();  // Check urgency      │
│    if (!urgent.empty()) {                                         │
│      HandleNeedSatisfaction(urgent[0]);    // Act on urgent      │
│    }                                                               │
│  }                                                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Decay Over Time - Visualization

```
CurrentValue
    1.0 ├─────────────────────────────────────
        │  ✅ Satisfied
    0.8 │    ╲
        │     ╲  Decay happening (delta time)
    0.6 │      ╲
        │       ╲
    0.4 │    ╲   ╲  Threshold = 0.3
        │     ╲   └───⚠️ URGENT
    0.3 │      ├─────────────────────────
        │      │  Urgency threshold
    0.2 │      │  (needs satisfaction)
        │  ⚠️ │  CRITICAL
    0.0 └──────┼────────────────────────── Time →
        0    2    4    6    8    10 seconds
        
DecayRatePerSecond: 0.1 per second
Time to reach urgency (1.0 → 0.3): 7 seconds
Time to reach critical (1.0 → 0.0): 10 seconds
```

## Update Cycle - Frame by Frame

```
┌─────────────────────────────────────────────────────────────────┐
│ Frame 1 (t=0.0s)                                                │
├─────────────────────────────────────────────────────────────────┤
│ • NeedManager.Initialize() called                               │
│ • All needs: CurrentValue = 1.0                                 │
│ • No needs urgent yet                                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Update(1.0)
┌─────────────────────────────────────────────────────────────────┐
│ Frame 2 (t=1.0s)                                                │
├─────────────────────────────────────────────────────────────────┤
│ • 1 second elapsed                                              │
│ • Formula: CV = max(0, 1.0 - (0.1 * 1.0)) = 0.9               │
│ • All needs: CurrentValue = 0.9                                 │
│ • Still no urgency (0.9 > 0.3)                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Update(2.0)
┌─────────────────────────────────────────────────────────────────┐
│ Frame 3 (t=3.0s)                                                │
├─────────────────────────────────────────────────────────────────┤
│ • 2 more seconds elapsed (total: 3s)                            │
│ • Formula: CV = max(0, 0.9 - (0.1 * 2.0)) = 0.7               │
│ • All needs: CurrentValue = 0.7                                 │
│ • Still OK (0.7 > 0.3)                                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Update(4.0)
┌─────────────────────────────────────────────────────────────────┐
│ Frame 4 (t=7.0s)                                                │
├─────────────────────────────────────────────────────────────────┤
│ • 4 more seconds elapsed (total: 7s)                            │
│ • Formula: CV = max(0, 0.7 - (0.1 * 4.0)) = 0.3               │
│ • All needs: CurrentValue = 0.3                                 │
│ • ⚠️ NOW URGENT! (0.3 ≤ 0.3)                                   │
│ • GetUrgentNeeds() returns [0, 1, 2, 3, 4]                     │
│ • SatisfyNeed(0) called → Hunger reset to 1.0                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Update(1.0)
┌─────────────────────────────────────────────────────────────────┐
│ Frame 5 (t=8.0s)                                                │
├─────────────────────────────────────────────────────────────────┤
│ • 1 more second elapsed                                         │
│ • Hunger: CV = max(0, 1.0 - (0.1 * 1.0)) = 0.9 ✅ Satisfied  │
│ • Thirst: CV = max(0, 0.3 - (0.1 * 1.0)) = 0.2 ⚠️ Urgent     │
│ • Rest: CV = max(0, 0.3 - (0.1 * 1.0)) = 0.2 ⚠️ Urgent       │
│ • Social: CV = max(0, 0.3 - (0.1 * 1.0)) = 0.2 ⚠️ Urgent     │
│ • Energy: CV = max(0, 0.3 - (0.1 * 1.0)) = 0.2 ⚠️ Urgent     │
│ • GetMostUrgentNeed() returns 1 (Thirst is lowest)             │
│ • Route Thirst satisfaction to AI controller                    │
└─────────────────────────────────────────────────────────────────┘
```

## State Machine - NPC Need Cycle

```
                    ┌──────────────────┐
                    │   INITIALIZE     │
                    │  (One-time setup)│
                    └────────┬─────────┘
                             │
                             ↓
        ┌────────────────────────────────────────┐
        │         ALL NEEDS SATISFIED            │
        │      (CurrentValue = 1.0)              │
        │  NextFrame: Decay starts automatically │
        └────┬─────────────────────────┬─────────┘
             │                         │
             │                         ↓
             │          ┌──────────────────────────┐
             │          │  NEEDS DECAYING          │
             │          │  (Time-based subtraction)│
             │          │  Update() called/frame   │
             │          └──────────┬───────────────┘
             │                     │
             │                     │ (After ~7 seconds)
             │                     ↓
             │          ┌──────────────────────────┐
             │          │   NEEDS BECOME URGENT    │
             │          │  (CV ≤ Threshold)       │
             │          │  GetUrgentNeeds() finds! │
             │          └──────────┬───────────────┘
             │                     │
             │    ╔════════════════╩════════════════╗
             │    ║   AI Controller Routes Need     ║
             │    ║   Executes Satisfaction Action ║
             │    ║   (Move to food, drink, rest)  ║
             │    ╚════════════════╬════════════════╝
             │                     │
             │                     ↓
             │          ┌──────────────────────────┐
             │          │    ACTION COMPLETES      │
             │          │  SatisfyNeed() called    │
             │          │  (CV reset to 1.0)      │
             │          └──────────┬───────────────┘
             │                     │
             └─────────────────────┘
                    (Cycle repeats)
```

## Need Priority Sorting

```
Initial State (random order):
┌─────────────────────────────┐
│ Hunger:  0.5                │
│ Thirst:  0.1  ← LOWEST      │
│ Rest:    0.8                │
│ Social:  0.3                │
│ Energy:  0.4                │
└─────────────────────────────┘
              ↓
        GetMostUrgentNeed()
              ↓
┌─────────────────────────────┐
│ Thirst:  0.1  ← PRIORITY #1 │
└─────────────────────────────┘

GetUrgentNeeds() (threshold: 0.3):
┌─────────────────────────────┐
│ Thirst:  0.1  ← URGENT      │
│ Social:  0.3  ← URGENT      │
│ Hunger:  0.5  ← OK          │
│ Energy:  0.4  ← OK          │
│ Rest:    0.8  ← OK          │
└─────────────────────────────┘
              ↓
        [1, 3]  (indices)
```

## Class Hierarchy - Future Extension (Phase 4)

```
┌──────────────────────────────────┐
│     NeedManager (Phase 3B)        │
│  ✅ Time-based decay              │
│  ✅ Threshold detection           │
│  ✅ Instance persistence          │
└────────────┬─────────────────────┘
             │
             │ extends
             ↓
┌──────────────────────────────────────────┐
│   PersonalityNeedSystem (Phase 4)        │
│  ✅ Personality-based modifiers          │
│  ✅ Decay rate multipliers               │
│  ✅ Threshold adjustments                │
└────────────┬─────────────────────────────┘
             │
             │ feeds
             ↓
┌──────────────────────────────────────────┐
│      AI Controller System                 │
│  • Decision tree integration              │
│  • Need satisfaction routing              │
│  • Action execution                       │
└──────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────┐
│  NeedManager operation called        │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   NOT INITIALIZED  INITIALIZED
        │             │
        ↓             ↓
   EXCEPTION    ┌─────────────────┐
   "Not init"   │ Check parameters│
                └────────┬────────┘
                         │
                    ┌────┴────┐
                    │          │
                 VALID    INVALID
                    │          │
                    ↓          ↓
              SUCCESS    EXCEPTION
                         (invalid_arg
                          out_of_range
                          runtime_error)
```

## Memory Layout

```
NeedManager Instance (~120 bytes)
┌─────────────────────────────────────────────────────┐
│ needs_: vector<NPCNeed>                             │
│  ├─ pointer to heap: 8 bytes                        │
│  ├─ size: 8 bytes                                   │
│  └─ capacity: 8 bytes                               │
│                                                     │
│ Element 0: NPCNeed (24 bytes)                       │
│  ├─ NeedType: 1 byte (enum value 0-4)             │
│  ├─ CurrentValue: 8 bytes (double)                 │
│  ├─ Threshold: 8 bytes (double)                    │
│  └─ DecayRatePerSecond: 8 bytes (double)          │
│                                                     │
│ Elements 1-4: NPCNeed × 4 (96 bytes)               │
│  (Same layout as Element 0)                        │
│                                                     │
│ initialized_: 1 byte (bool)                        │
│ [padding]: 7 bytes                                 │
└─────────────────────────────────────────────────────┘
Total: ~120 bytes per manager
```

## Decay Formula Visualization

```
Decay Calculation per Update:
                                           
new_value = max(0.0, old_value - (decay_rate * delta_time))
                    │                     │              │
                    └─ Lower bound        │              │
                                          │              │
                       Decay amount ──────┘              │
                                                         │
                          Time since last update ────────┘

Example with decay_rate = 0.1:
┌─────────────────┬──────────────┬──────────────┬──────────┐
│ Time (seconds)  │ Decay Amount │ Old Value    │ New Value│
├─────────────────┼──────────────┼──────────────┼──────────┤
│ 1.0             │ 0.1 × 1.0    │ 1.0          │ 0.9      │
├─────────────────┼──────────────┼──────────────┼──────────┤
│ 2.0             │ 0.1 × 2.0    │ 0.9          │ 0.7      │
├─────────────────┼──────────────┼──────────────┼──────────┤
│ 0.5             │ 0.1 × 0.5    │ 0.7          │ 0.65     │
├─────────────────┼──────────────┼──────────────┼──────────┤
│ 1.0 (to 0.0)    │ 0.1 × 1.0    │ 0.05         │ 0.0 ✅   │
│                 │              │              │ clamped  │
└─────────────────┴──────────────┴──────────────┴──────────┘
```

## Test Coverage Map

```
NeedSystem Tests (48 total)
│
├─ Struct Tests (6)
│  ├─ NPCNeed initialization
│  ├─ IsUrgent() logic
│  └─ ... 4 more
│
├─ Initialization Tests (4)
│  ├─ Default init (all 5 types)
│  ├─ Custom init
│  └─ Error cases
│
├─ Decay Tests (10) ⭐ CRITICAL
│  ├─ Basic decay formula
│  ├─ Multi-step decay
│  ├─ Clamping behavior
│  └─ ... 7 more
│
├─ Threshold Tests (6) ⭐ CRITICAL  
│  ├─ Urgent detection
│  ├─ Priority sorting
│  └─ ... 4 more
│
├─ Accessor Tests (5)
├─ Satisfaction Tests (4)
├─ Persistence Tests (3) ⭐ CRITICAL
├─ Integration Tests (2)
└─ Enum Tests (1)

⭐ = Most important for Blueprint compatibility
```

---

**Visual Reference Complete**  
For implementation details, see PHASE_3B_IMPLEMENTATION_GUIDE.md

