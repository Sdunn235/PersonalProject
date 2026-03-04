#pragma once
#include <cstdint>

namespace simcore {

/**
 * TimeManager — Engine-agnostic simulation clock.
 *
 * Separates simulation time from Unreal frame time.
 * SimStep is the atomic simulation unit (default 1.0s sim-time).
 * Multiple SimSteps may accumulate before processing.
 *
 * Time layers:
 *   FrameTime   — Engine (NOT owned here)
 *   SimStep     — 0.5–5 real seconds per tick (configurable)
 *   WorldDay    — N SimSteps = 1 WorldDay
 *   Season      — N WorldDays
 *   Year        — 4 Seasons
 *   Generation  — N Years
 */
class TimeManager {
public:
    struct Config {
        float sim_step_seconds  = 1.0f;   // real seconds per SimStep
        int   steps_per_day     = 240;    // 240 × 1s steps = 4-minute world day
        int   days_per_season   = 30;
        int   seasons_per_year  = 4;
        int   years_per_gen     = 20;
    };

    explicit TimeManager(const Config& cfg = Config{});

    // ── Advance ──────────────────────────────────────────────────────────────

    /// Call every real-time tick with elapsed wall seconds.
    /// Returns how many full SimSteps occurred this tick.
    int advance(float delta_real_seconds);

    // ── Accessors ────────────────────────────────────────────────────────────

    uint64_t total_steps()   const { return m_total_steps; }
    uint32_t world_day()     const { return m_world_day; }
    uint32_t season()        const { return m_season; }   // 0–3
    uint32_t year()          const { return m_year; }
    uint32_t generation()    const { return m_generation; }
    float    step_seconds()  const { return m_cfg.sim_step_seconds; }

    /// Accumulated real-time seconds not yet consumed into a full step.
    float    accumulator()   const { return m_accumulator; }

    const Config& config() const { return m_cfg; }

private:
    Config   m_cfg;
    float    m_accumulator  = 0.0f;
    uint64_t m_total_steps  = 0;
    uint32_t m_world_day    = 0;
    uint32_t m_season       = 0;
    uint32_t m_year         = 0;
    uint32_t m_generation   = 0;

    void tick_one_step();
};

} // namespace simcore

