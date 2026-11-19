# run_soak_tests.py — "nothing odd" as invariants over a long seeded run (docs/testing.md "Soak").
#
# Replaces Shawn's open-ended live check ("no NPC bouncing between sources, nobody stuck, nothing
# odd"). Runs the real SimulationKernel for SOAK_DAYS in-game days from the shared seed and checks
# invariants every frame. Each limit states its rationale; none is a tuned magic number.
#
#   py scratchpad/run_soak_tests.py
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness.headless import new_kernel, quiet  # noqa: E402

import settings  # noqa: E402
from Mechanics.biochem.receptor import comfort_band  # noqa: E402

SOAK_DAYS = 3                                       # long enough for every daily rhythm to repeat
FRAMES_PER_MINUTE = settings.FPS * 60               # one real minute of frames
# Thrash limit: at most one behavioral state change per second, averaged over any real minute —
# faster than that, a viewer can't follow what the NPC is doing (and the event feed floods).
MAX_TRANSITIONS_PER_MINUTE = 60
# Frozen-MOVING limit: an NPC in MOVING must actually move; one real second without moving is
# already visibly stuck (NPC_SPEED covers a tile in well under a second).
MAX_STATIONARY_MOVING_FRAMES = settings.FPS
# Rhythm: over SOAK_DAYS each NPC must have satisfied each need at least once per day.
MIN_SATISFACTIONS = SOAK_DAYS

_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


print("=" * 64)
print(f"Soak tests - {SOAK_DAYS} in-game days, seeded, invariants every frame")
print("=" * 64)

ctx, kernel = new_kernel()
frames = int(SOAK_DAYS * settings.FRAMES_PER_DAY)
dt, now = 1.0 / settings.FPS, 0.0
names = [e.name for e, _ in kernel.session.npc_list]
bad_chem, bad_need, bad_pull = [], [], []
stationary = collections.Counter()
worst_stationary = collections.Counter()
last_pos: dict = {}
prev_state: dict = {}
transitions = collections.defaultdict(collections.Counter)    # name -> minute -> count
satisfied = collections.defaultdict(collections.Counter)      # name -> need_id -> count

with quiet():
    for f in range(frames):
        now += dt
        kernel.step(dt, now)
        for ent, ctl in kernel.session.npc_list:
            n = ent.name
            for key, val in ctl.brain.chemicals.as_dict().items():
                if math.isnan(val) or not 0.0 <= val <= 1.0:
                    bad_chem.append((f, n, key, val))
            for need in ctl.needs:
                if not 0.0 <= need.current_value <= 100.0:
                    bad_need.append((f, n, need.need_id, need.current_value))
                if need.perceived_pull > settings.PULL_CAP_FRACTION * comfort_band(need) + 1e-9:
                    bad_pull.append((f, n, need.need_id, need.perceived_pull))
            pos = (ent.x, ent.y)
            if ctl.state == "MOVING" and last_pos.get(n) == pos:
                stationary[n] += 1
                worst_stationary[n] = max(worst_stationary[n], stationary[n])
            else:
                stationary[n] = 0
            last_pos[n] = pos
            state = (ctl.state, ctl.target_source.need_id if ctl.target_source else None)
            if prev_state.get(n) != state:
                transitions[n][f // FRAMES_PER_MINUTE] += 1
                if state[0] == "SATISFYING":
                    satisfied[n][state[1]] += 1
            prev_state[n] = state

check("chemicals stay finite and within [0, 1] every frame", not bad_chem, str(bad_chem[:3]))
check("need values stay within [0, 100] every frame", not bad_need, str(bad_need[:3]))
check("perceived pulls never exceed PULL_CAP_FRACTION x band", not bad_pull, str(bad_pull[:3]))
check("nobody dies of neglect in a quiet world", not kernel.session.defeated_npcs,
      str(kernel.session.defeated_npcs))
for n in names:
    worst_minute = max(transitions[n].values()) if transitions[n] else 0
    check(f"{n}: no thrashing (worst minute {worst_minute} state changes, limit "
          f"{MAX_TRANSITIONS_PER_MINUTE})", worst_minute <= MAX_TRANSITIONS_PER_MINUTE)
    check(f"{n}: never frozen while MOVING (worst {worst_stationary[n]} frames, limit "
          f"{MAX_STATIONARY_MOVING_FRAMES})", worst_stationary[n] <= MAX_STATIONARY_MOVING_FRAMES)
    for need_id in ("hunger", "thirst", "sleep"):
        check(f"{n}: satisfies {need_id} at least once a day ({satisfied[n][need_id]} in "
              f"{SOAK_DAYS} days)", satisfied[n][need_id] >= MIN_SATISFACTIONS)

# Determinism: the same seed must replay the same world (autonomy relies on reproducible runs).
# Each run seeds, builds and steps before the next starts — they share the global RNG.
def snapshot(k):
    return [(e.name, round(e.x, 6), round(e.y, 6), c.state,
             tuple(round(v, 9) for v in c.brain.chemicals.as_dict().values()))
            for e, c in k.session.npc_list]


def seeded_run(day_fraction: float = 0.25):
    _, k = new_kernel()
    t = 0.0
    with quiet():
        for _ in range(int(day_fraction * settings.FRAMES_PER_DAY)):
            t += dt
            k.step(dt, t)
    return snapshot(k)


check("same seed replays the same world (positions, states, chemistry)",
      seeded_run() == seeded_run())

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Soak tests CLEAN")
