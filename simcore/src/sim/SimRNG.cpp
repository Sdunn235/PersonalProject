#include "simcore/sim/SimRNG.h"
#include <algorithm>
#include <stdexcept>

namespace simcore {

SimRNG::SimRNG(uint32_t seed)
    : m_state(seed == 0u ? 1u : seed) // avoid zero state
{}

uint32_t SimRNG::next_u32() {
    // LCG parameters from Numerical Recipes. Matches iso_rpg_lab/rng.py RNG32.
    m_state = (1664525u * m_state + 1013904223u) & 0xFFFFFFFFu;
    return m_state;
}

float SimRNG::next_float() {
    return static_cast<float>(next_u32()) / 4294967296.0f; // / 2^32
}

int32_t SimRNG::range_int(int32_t lo, int32_t hi) {
    if (lo > hi) { int32_t t = lo; lo = hi; hi = t; }
    float r = next_float();
    return lo + static_cast<int32_t>(r * static_cast<float>(hi - lo + 1));
}

bool SimRNG::chance(float percent) {
    // Matches iso_rpg_lab: range_int(0, 9999) < int(percent * 100)
    return range_int(0, 9999) < static_cast<int32_t>(percent * 100.0f);
}

} // namespace simcore

