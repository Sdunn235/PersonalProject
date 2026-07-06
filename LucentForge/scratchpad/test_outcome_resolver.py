"""Smoke tests for §12.2 outcome resolver (Phase 2.6)."""
import random
import sys
sys.path.insert(0, ".")

import settings
from Mechanics.services.outcome import (
    Degree, OutcomeCheck, OutcomeResult, OutcomeResolver,
)

SEED = 42
N    = 10_000

# ---------------------------------------------------------------------------
# 1. Overwhelming advantage → 100% success, variance always 0
# ---------------------------------------------------------------------------
# det_margin = 20 - 5 = 15 > VARIANCE_MAX(5) → variance locked at 0
r1      = OutcomeResolver(rng=random.Random(SEED).randint)
check1  = OutcomeCheck(base_value=20, difficulty=5)
results1 = [r1.resolve(check1) for _ in range(N)]
assert all(res.success   for res in results1), "Overwhelming advantage must always succeed"
assert all(res.variance == 0 for res in results1), "Variance must be 0 when margin > VARIANCE_MAX"

# ---------------------------------------------------------------------------
# 2. Overwhelming disadvantage → 0% success, variance always 0
# ---------------------------------------------------------------------------
# det_margin = 5 - 20 = -15 < -VARIANCE_MAX(5)
r2      = OutcomeResolver(rng=random.Random(SEED).randint)
check2  = OutcomeCheck(base_value=5, difficulty=20)
results2 = [r2.resolve(check2) for _ in range(N)]
assert not any(res.success for res in results2), "Overwhelming disadvantage must always fail"
assert all(res.variance == 0 for res in results2), "Variance must be 0 when margin < -VARIANCE_MAX"

# ---------------------------------------------------------------------------
# 3. Perfect neutral (det = diff) → ~54.5% success (6/11 integer range)
# ---------------------------------------------------------------------------
r3      = OutcomeResolver(rng=random.Random(SEED).randint)
check3  = OutcomeCheck(base_value=10, difficulty=10)
results3 = [r3.resolve(check3) for _ in range(N)]
rate    = sum(1 for res in results3 if res.success) / N
assert 0.50 <= rate <= 0.60, f"Expected ~54.5% success at neutral, got {rate:.2%}"

# ---------------------------------------------------------------------------
# 4. Band edges — deterministic rng (variance=0 mock)
# ---------------------------------------------------------------------------
zero_rng = lambda lo, hi: 0   # noqa: E731
r4 = OutcomeResolver(rng=zero_rng)

V = settings.OUTCOME_VARIANCE_MAX   # 5  — det_margin must exceed this for no-roll
C = settings.OUTCOME_CRIT_MARGIN    # 5  — margin threshold for critical outcomes

# Critical success: margin == C (at boundary)
assert r4.resolve(OutcomeCheck(base_value=10 + C, difficulty=10)).degree == Degree.CRITICAL_SUCCESS
# Success: margin == 0
assert r4.resolve(OutcomeCheck(base_value=10,     difficulty=10)).degree == Degree.SUCCESS
# Failure: margin == -1
assert r4.resolve(OutcomeCheck(base_value=10 - 1, difficulty=10)).degree == Degree.FAILURE
# Critical failure: margin == -C (at boundary)
assert r4.resolve(OutcomeCheck(base_value=10 - C, difficulty=10)).degree == Degree.CRITICAL_FAILURE

# ---------------------------------------------------------------------------
# 5. Variance bounds — det_margin exactly at ±VARIANCE_MAX stays in uncertain zone
# ---------------------------------------------------------------------------
r5 = OutcomeResolver(rng=random.Random(SEED).randint)
# det_margin = V → |V| > V is False → variance applies → outcome can vary
check5 = OutcomeCheck(base_value=10 + V, difficulty=10)
results5 = [r5.resolve(check5) for _ in range(N)]
assert any(res.variance != 0 for res in results5), "det_margin == VARIANCE_MAX should still roll"

print("All outcome resolver tests passed.")
