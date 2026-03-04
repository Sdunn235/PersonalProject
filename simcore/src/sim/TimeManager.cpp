#include "simcore/sim/TimeManager.h"
#include <cassert>

namespace simcore {

TimeManager::TimeManager(const Config& cfg)
    : m_cfg(cfg)
{
    assert(cfg.sim_step_seconds > 0.0f);
    assert(cfg.steps_per_day    > 0);
    assert(cfg.days_per_season  > 0);
    assert(cfg.seasons_per_year > 0);
    assert(cfg.years_per_gen    > 0);
}

int TimeManager::advance(float delta_real_seconds) {
    m_accumulator += delta_real_seconds;
    int steps_fired = 0;

    while (m_accumulator >= m_cfg.sim_step_seconds) {
        m_accumulator -= m_cfg.sim_step_seconds;
        tick_one_step();
        ++steps_fired;
    }

    return steps_fired;
}

void TimeManager::tick_one_step() {
    ++m_total_steps;

    // Step → Day
    if (m_total_steps % static_cast<uint64_t>(m_cfg.steps_per_day) == 0) {
        ++m_world_day;

        // Day → Season
        uint32_t days_per_season = static_cast<uint32_t>(m_cfg.days_per_season);
        if (m_world_day % days_per_season == 0) {
            m_season = (m_season + 1) % static_cast<uint32_t>(m_cfg.seasons_per_year);

            // Season rollover → Year
            if (m_season == 0) {
                ++m_year;

                // Year → Generation
                if (m_year % static_cast<uint32_t>(m_cfg.years_per_gen) == 0) {
                    ++m_generation;
                }
            }
        }
    }
}

} // namespace simcore

