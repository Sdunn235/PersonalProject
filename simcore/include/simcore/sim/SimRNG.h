#pragma once
#include <cstdint>

namespace simcore {

/**
 * SimRNG — Deterministic 32-bit LCG random number generator.
 *
 * Ported from iso_rpg_lab/gameplay/rng.py (RNG32).
 * SimCore owns its own RNG to guarantee determinism across sessions,
 * server authority, and replay debugging.
 *
 * NOT suitable for cryptography.
 */
class SimRNG {
public:
    explicit SimRNG(uint32_t seed = 123456789u);

    /// Advance state and return raw uint32.
    uint32_t next_u32();

    /// Return a float in [0, 1).
    float next_float();

    /// Return integer in [lo, hi] inclusive.
    int32_t range_int(int32_t lo, int32_t hi);

    /// Return true with the given percentage probability (0–100).
    bool chance(float percent);

    /// Current seed/state (for serialization).
    uint32_t state() const { return m_state; }

    /// Restore state (for deserialization / replay).
    void set_state(uint32_t s) { m_state = s; }

private:
    uint32_t m_state;
};

} // namespace simcore

