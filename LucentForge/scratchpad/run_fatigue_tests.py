# run_fatigue_tests.py - Rest/Fatigue want acceptance suite (needs/wants SW6).
#
# Covers the Implementation Acceptance list from the LOCKED design note
# (2026-08-04_rest_fatigue_want.md, Director Decisions 2026-08-09):
#   1. Parity: fatigue=0 -> Chemicals.tick byte-identical to pre-change.
#   2. Fatigue accrues in an exerting locus and decays at rest (emitter + natural decay).
#   3. The tiredness special-case: fatigue nonzero WHILE SLEEPING still nets tiredness DOWN
#      (the sleep-decay branch dominates the boost - QC's major note).
#   4. Rides the generic chemicals save blob - no migration (round-trip via real SaveManager).
#   5. endurance() polymorphic strategy: hardy NPC tires slower (formula, not coefficient).
#
# Runnable as a subprocess (exits 1 on any failure).
#   py scratchpad/run_fatigue_tests.py
import os
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import settings  # noqa: E402
from Mechanics.biochem.chemical import Chemicals  # noqa: E402
from Mechanics.biochem.emitter import ExertionEmitter, EXERTING_STATES  # noqa: E402
from Mechanics.entities.attributes import Attributes  # noqa: E402
from Mechanics.entities.derivation import endurance, fatigue_gain  # noqa: E402

_fails: list[str] = []


def check(label: str, cond: bool) -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        _fails.append(label)


# A minimal need stub matching what Chemicals.tick reads (chemical, need_id, is_urgent,
# current_value). The sleep need is the one that matters for the special-case test.
class _MockNeed:
    def __init__(self, nid, chem, val, urgent):
        self.need_id = nid
        self.chemical = chem
        self.current_value = val
        self._urgent = urgent

    @property
    def is_urgent(self):
        return self._urgent


print("=" * 64)
print("Rest/Fatigue want acceptance - needs/wants SW6")
print("=" * 64)

# ---------------------------------------------------------------------------
# (1) PARITY - fatigue=0 -> Chemicals.tick is byte-identical to pre-change.
# We tick two identical chemical stores over a full needs list; one has fatigue
# left at 0 (default). The result must equal a store where the fatigue block
# cannot fire. Since fatigue defaults to 0 and the boost is gated on
# fatigue > FATIGUE_ACTIVE_FLOOR, a default store proves the no-op.
# ---------------------------------------------------------------------------
needs = [
    _MockNeed("hunger", "hunger_chem", 80, False),
    _MockNeed("thirst", "thirst_chem", 80, False),
    _MockNeed("sleep",  "tiredness",   80, False),
]
ch_parity = Chemicals()
ch_parity.set("hunger_chem", 0.20)
ch_parity.set("thirst_chem", 0.20)
ch_parity.set("tiredness",   0.20)
before_tired = ch_parity.get("tiredness")
ch_parity.tick(needs)   # fatigue == 0 -> fatigue boost is a no-op
# With sleep NOT urgent, the sleep-decay branch subtracts _DECAY*5 from tiredness;
# the fatigue boost must add NOTHING, so tiredness ends strictly below its pre-tick
# value by exactly the sleep-decay amount (no fatigue contribution).
expected_tired = max(0.0, before_tired - Chemicals._DECAY * 5)
check("(1) parity: fatigue=0 -> tiredness follows pure sleep-decay branch (no boost)",
      abs(ch_parity.get("tiredness") - expected_tired) < 1e-12)
check("(1) parity: fatigue stays 0 across a tick with no emitter input",
      ch_parity.get("fatigue") == 0.0)

# ---------------------------------------------------------------------------
# (2) ACCRUAL + REST - fatigue rises in an exerting locus, falls at rest.
# ---------------------------------------------------------------------------
attrs = Attributes()   # default: constitution 5, physique 10
em = ExertionEmitter()

ch_exert = Chemicals()
for _ in range(2000):
    em.emit(ch_exert, attrs, "MOVING", at_bed=False)
peak = ch_exert.get("fatigue")
check("(2) fatigue accrues in an exerting locus (MOVING, 2000 ticks)", peak > 0.05)

# Rest at a bed: emitter pulls toward 0 AND natural decay applies via tick().
# Drive tick with sleep urgent=False so no interference beyond decay.
rest_needs = [_MockNeed("sleep", "tiredness", 90, False)]
for _ in range(2000):
    em.emit(ch_exert, attrs, "SATISFYING", at_bed=True)
    ch_exert.tick(rest_needs)
check("(2) fatigue decays at rest (bed locus + natural decay, 2000 ticks)",
      ch_exert.get("fatigue") < peak * 0.5)

# Neutral loci (IDLE, SATISFYING non-bed) do NOT actively push - only natural decay.
ch_neutral = Chemicals()
ch_neutral.set("fatigue", 0.5)
f0 = ch_neutral.get("fatigue")
em.emit(ch_neutral, attrs, "IDLE", at_bed=False)
check("(2) IDLE is neutral: emitter does not actively change fatigue",
      ch_neutral.get("fatigue") == f0)
em.emit(ch_neutral, attrs, "SATISFYING", at_bed=False)
check("(2) SATISFYING at a non-bed source is neutral (no active push)",
      ch_neutral.get("fatigue") == f0)

# EXERTING_STATES membership is exactly the Director-locked set.
check("(2) EXERTING_STATES == {MOVING, RAIDING, RELOCATING, PATROLLING}",
      EXERTING_STATES == frozenset({"MOVING", "RAIDING", "RELOCATING", "PATROLLING"}))

# ---------------------------------------------------------------------------
# (3) THE tiredness SPECIAL-CASE (QC major note) - a SLEEPING NPC with nonzero
# fatigue must still net tiredness DOWNWARD. Sleep is "not urgent" while filling
# (above warning), so the sleep-decay branch (_DECAY*5) fires; the fatigue boost
# runs after and adds back, but conservatively tuned to lose to the decay.
# ---------------------------------------------------------------------------
sleep_needs = [_MockNeed("sleep", "tiredness", 90, False)]  # not urgent -> decay branch
ch_sleep = Chemicals()
ch_sleep.set("tiredness", 0.30)
ch_sleep.set("fatigue", 1.0)   # worst case: maximal fatigue while sleeping
t_before = ch_sleep.get("tiredness")
ch_sleep.tick(sleep_needs)
t_after = ch_sleep.get("tiredness")
check("(3) SPECIAL-CASE: sleeping + fatigue=1.0 -> tiredness still nets DOWN",
      t_after < t_before)
# Also verify multi-tick monotonic downward trend while sleeping with high fatigue.
mono_down = True
prev = ch_sleep.get("tiredness")
for _ in range(50):
    ch_sleep.set("fatigue", 1.0)      # hold fatigue pinned high (worst case)
    ch_sleep.tick(sleep_needs)
    cur = ch_sleep.get("tiredness")
    if cur > prev + 1e-12:
        mono_down = False
    prev = cur
check("(3) SPECIAL-CASE: 50 sleeping ticks at fatigue=1.0 keep tiredness monotone-down",
      mono_down)

# Sanity on the tuning invariant itself: max boost (fatigue=1) + max strain boost
# must be strictly below the sleep-decay magnitude.
max_boost = (1.0 * settings.FATIGUE_TIREDNESS_BOOST_FRACTION * Chemicals._SLEEP_DECAY
             + 1.0 * settings.AFFINITY_STRAIN_NEED_BOOST)
check("(3) tuning invariant: max(fatigue+strain boost) < sleep-decay (_SLEEP_DECAY)",
      max_boost < Chemicals._SLEEP_DECAY)

# Contrast: while AWAKE (sleep urgent), the boost DOES elevate tiredness (the point
# of the want). Urgent sleep uses the approach branch, not hard-decay.
ch_awake = Chemicals()
ch_awake.set("tiredness", 0.20)
awake_needs = [_MockNeed("sleep", "tiredness", 30, True)]  # urgent -> approach branch
ch_awake.tick(awake_needs)
base_tired = ch_awake.get("tiredness")
ch_awake2 = Chemicals()
ch_awake2.set("tiredness", 0.20)
ch_awake2.set("fatigue", 0.8)
ch_awake2.tick(awake_needs)
check("(3) contrast: while awake, fatigue boosts perceived tiredness upward",
      ch_awake2.get("tiredness") > base_tired)

# ---------------------------------------------------------------------------
# (4) SAVE BLOB - fatigue rides the generic chemicals blob; no migration.
# Uses the REAL SaveManager.snapshot()/restore() + apply_save pipeline.
# ---------------------------------------------------------------------------
print("-" * 64)
try:
    from Mechanics.bootstrap import (create_game_context, create_npc_controller,
                                     create_world_sim, apply_save)
    from Mechanics.entities.factory import create_all_npcs, create_player
    from Mechanics.needs.need import make_default_needs
    from Mechanics.world.tile_map import TileMap

    tmp_db = os.path.join(tempfile.gettempdir(), "lf_fatigue_persist.db")
    if os.path.exists(tmp_db):
        try:
            os.remove(tmp_db)
        except OSError:
            pass
    ctx = create_game_context(db_path=tmp_db)
    tmap = TileMap()
    tmap.load_real_map()
    sources = tmap.get_need_sources()
    world = create_world_sim(sources)
    npcs = create_all_npcs(ctx)
    villager = next(n for n in npcs if n.name == "Alder")
    ctrl = create_npc_controller(villager, ctx, sources, tmap, world)
    player = create_player(ctx)
    player_needs = make_default_needs()

    ctrl.brain.chemicals.set("fatigue", 0.42)
    pre = ctrl.brain.chemicals.get("fatigue")

    ctx.save_manager.snapshot(world, sources, [ctrl], player, player_needs, set(), {})
    ctrl.brain.chemicals.set("fatigue", 0.0)   # wipe live value
    save_data = ctx.save_manager.restore()
    apply_save(save_data, world, sources, [ctrl], player, player_needs, set(), {})

    post = ctrl.brain.chemicals.get("fatigue")
    check("(4) fatigue survives snapshot/restore round-trip (generic chemicals blob)",
          abs(post - pre) < 1e-9 and post > 0.41)
    if hasattr(ctx, "close"):
        ctx.close()
except Exception as ex:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    check(f"(4) fatigue save round-trip (exception: {ex})", False)

# ---------------------------------------------------------------------------
# (5) ENDURANCE polymorphic strategy - hardy NPC tires slower (formula, not number).
# ---------------------------------------------------------------------------
print("-" * 64)
frail = Attributes(constitution=1, physique=1)
hardy = Attributes(constitution=20, physique=20)
check("(5) endurance is Constitution-led (CON weight > PHY weight)",
      settings.ENDURANCE_CON_WEIGHT > settings.ENDURANCE_PHY_WEIGHT)
check("(5) endurance(hardy) > endurance(frail); both >= ENDURANCE_MIN",
      endurance(hardy) > endurance(frail) >= settings.ENDURANCE_MIN)

em2 = ExertionEmitter()
ch_frail = Chemicals()
ch_hardy = Chemicals()
for _ in range(500):
    em2.emit(ch_frail, frail, "MOVING", at_bed=False)
    em2.emit(ch_hardy, hardy, "MOVING", at_bed=False)
check("(5) frail NPC accrues fatigue FASTER than hardy over identical exertion",
      ch_frail.get("fatigue") > ch_hardy.get("fatigue"))

# effective_gain is recomputed from live attrs each tick (never spawn-frozen):
# bumping constitution mid-run must slow accrual on the very next tick.
ch_live = Chemicals()
live_attrs = Attributes(constitution=2, physique=2)
em2.emit(ch_live, live_attrs, "MOVING", at_bed=False)
step_low = ch_live.get("fatigue")
live_attrs.constitution = 50   # ascension-style bump
before = ch_live.get("fatigue")
em2.emit(ch_live, live_attrs, "MOVING", at_bed=False)
step_high = ch_live.get("fatigue") - before
check("(5) effective_gain recomputes from LIVE attrs (higher CON -> smaller step)",
      step_high < step_low)

# ---------------------------------------------------------------------------
# (6) INTEGRATED ACCRUAL - the check the 2026-08-09 suite was missing (live gate
# failed 2026-11-17: fatigue stayed 0 for every NPC). Real authored entities, the
# full emitter + Chemicals.tick path together (natural decay included), exerting
# for one in-game day of frames. Each half passing alone proves nothing: the gain
# must beat the leak for the HARDIEST authored entity.
# ---------------------------------------------------------------------------
print("-" * 64)
try:
    from Mechanics.bootstrap import create_game_context as _cgc
    from Mechanics.entities.factory import create_all_npcs as _can
    from Mechanics.needs.need import make_default_needs as _mdn

    tmp_db6 = os.path.join(tempfile.gettempdir(), "lf_fatigue_integrated.db")
    if os.path.exists(tmp_db6):
        try:
            os.remove(tmp_db6)
        except OSError:
            pass
    ctx6 = _cgc(db_path=tmp_db6)
    roster = _can(ctx6)
    decay = settings.FATIGUE_FADE_PER_FRAME
    frames_per_day = int(settings.SIM_DAY_SECONDS * settings.FPS)  # controller runs per frame
    em6 = ExertionEmitter()
    for npc6 in roster:
        gain0 = fatigue_gain(npc6.attributes)
        check(f"(6) {npc6.name}: exertion gain beats natural decay "
              f"({gain0:.6f} > {decay:.6f}, endurance {endurance(npc6.attributes):.0f})",
              gain0 > decay)
        ch6 = Chemicals()
        needs6 = _mdn()                       # needs stay FINE: isolates fatigue itself
        for _ in range(frames_per_day):
            em6.emit(ch6, npc6.attributes, "PATROLLING", at_bed=False)
            ch6.tick(needs6)
        check(f"(6) {npc6.name}: one day of exertion reaches visible fatigue "
              f"(got {ch6.get('fatigue'):.3f}, need > 0.1)",
              ch6.get("fatigue") > 0.1)
    if hasattr(ctx6, "close"):
        ctx6.close()
except Exception as ex:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    check(f"(6) integrated accrual (exception: {ex})", False)

# ---------------------------------------------------------------------------
# (7) PERCEIVED-NEED RECEPTOR - fatigue lowers the sleep need's PERCEIVED value, which is
# what every zone-based decision reads. Parity: no fatigue -> pull 0 -> zone unchanged.
# ---------------------------------------------------------------------------
print("-" * 64)
from Mechanics.biochem.receptor import apply_perceived_pulls, comfort_band, fatigue_sleep_pull  # noqa: E402
from Mechanics.needs.need import NeedZone, make_default_needs  # noqa: E402
from Mechanics.needs.needs_system import get_priority_need  # noqa: E402

ch7 = Chemicals()
needs7 = make_default_needs()
sleep7 = next(n for n in needs7 if n.need_id == "sleep")
sleep7.current_value = sleep7.warning_threshold + 10.0          # just above WARNING -> FINE
apply_perceived_pulls(needs7, ch7)
check("(7) parity: fatigue 0 -> pull 0, sleep zone FINE, nothing prioritized",
      sleep7.perceived_pull == 0.0 and sleep7.zone == NeedZone.FINE
      and get_priority_need(needs7) is None)
ch7.set("fatigue", 0.5)
apply_perceived_pulls(needs7, ch7)
check("(7) fatigue 0.5 -> sleep pull = 0.5 x FATIGUE_PULL_FRACTION x sleep band",
      abs(sleep7.perceived_pull
          - 0.5 * settings.FATIGUE_PULL_FRACTION * comfort_band(sleep7)) < 1e-9)
check("(7) band is authored per need: sleep band = full - warning threshold",
      comfort_band(sleep7) == 100.0 - sleep7.warning_threshold)
check("(7) fatigued NPC perceives sleep as WARNING and prioritizes it (actual value unchanged)",
      sleep7.zone == NeedZone.WARNING and get_priority_need(needs7) is sleep7
      and sleep7.current_value == sleep7.warning_threshold + 10.0)
check("(7) pull targets ONLY sleep (other needs keep pull 0)",
      all(n.perceived_pull == 0.0 for n in needs7 if n.need_id != "sleep"))
sleep7.current_value = 100.0
ch7.set("fatigue", 1.0)
apply_perceived_pulls(needs7, ch7)
check("(7) no bed loop: just-slept NPC at max fatigue still perceives sleep FINE",
      sleep7.zone == NeedZone.FINE)
ch7.set("fatigue", settings.FATIGUE_ACTIVE_FLOOR)
check("(7) dead-band: fatigue at the floor -> no pull", fatigue_sleep_pull(ch7, sleep7) == 0.0)

# ---------------------------------------------------------------------------
# (8) FULL LOOP (live-gate check 4, headless) - the real SimulationKernel, same seed, one
# in-game day, run twice: with the receptor and with FATIGUE_PULL_FRACTION = 0 (decisions then
# ignore fatigue = the pre-receptor baseline). Hard-exerting goblins must bed down SOONER.
# ---------------------------------------------------------------------------
print("-" * 64)
try:
    import contextlib
    import io
    import random
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))     # PlayerController reads key state
    from Mechanics.bootstrap import create_game_context as _cgc8
    from Mechanics.world.tile_map import TileMap as _TM8
    from Mechanics.runtime.kernel import SimulationKernel

    def _first_sleep_frames(pull: float, frames: int) -> dict:
        saved_pull = settings.FATIGUE_PULL_FRACTION
        settings.FATIGUE_PULL_FRACTION = pull
        try:
            random.seed(1234)
            db8 = os.path.join(tempfile.mkdtemp(), "lf_fatigue_loop.db")
            ctx8 = _cgc8(db_path=db8)
            tm8 = _TM8()
            with contextlib.redirect_stdout(io.StringIO()):
                tm8.load_real_map()
                kern = SimulationKernel.new_session(ctx8, tm8, tm8.get_need_sources())
                first: dict = {}
                dt8, now8 = 1.0 / settings.FPS, 0.0
                for frame in range(frames):
                    now8 += dt8
                    kern.step(dt8, now8)
                    for ent, ctl in kern.session.npc_list:
                        asleep = (ctl.state == "SATISFYING" and ctl.target_source is not None
                                  and ctl.target_source.need_id == "sleep")
                        if asleep and ent.name not in first:
                            first[ent.name] = frame
            ctx8.db.close()
            return first
        finally:
            settings.FATIGUE_PULL_FRACTION = saved_pull

    day = int(settings.SIM_DAY_SECONDS * settings.FPS)
    with_pull = _first_sleep_frames(settings.FATIGUE_PULL_FRACTION, day)
    no_pull = _first_sleep_frames(0.0, day)
    for gob in ("Gruk", "Skrix"):          # patrol/raid nonstop -> the exertion test cases
        a8, b8 = with_pull.get(gob), no_pull.get(gob)
        check(f"(8) {gob} beds down sooner with fatigue (frame {a8} vs {b8} without)",
              a8 is not None and b8 is not None and a8 < b8)
except Exception as ex:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    check(f"(8) full-loop sleep timing (exception: {ex})", False)

# ---------------------------------------------------------------------------
# (9) AUTHORED TARGETS HOLD - the per-frame rates are SOLVED from authored game-term targets
# (reference human: plateau FATIGUE_REF_PLATEAU, reaches 0.5 in FATIGUE_REF_HALF_DAYS). Simulate
# the reference through the real emitter + Chemicals.tick and confirm the derivation delivers them.
# Also derive each authored entity's plateau from its attributes (content-computed invariant).
# ---------------------------------------------------------------------------
print("-" * 64)


class _RefAttrs:   # endurance exactly ENDURANCE_REFERENCE (Constitution only, Physique 0)
    constitution = settings.ENDURANCE_REFERENCE / settings.ENDURANCE_CON_WEIGHT
    physique = 0


check("(9) reference stand-in has reference endurance",
      abs(endurance(_RefAttrs) - settings.ENDURANCE_REFERENCE) < 1e-9)
ch9, needs9, em9 = Chemicals(), make_default_needs(), ExertionEmitter()
half_frame = None
for frame9 in range(int(3 * settings.FRAMES_PER_DAY)):
    em9.emit(ch9, _RefAttrs, "PATROLLING", at_bed=False)
    ch9.tick(needs9)
    if half_frame is None and ch9.get("fatigue") >= 0.5:
        half_frame = frame9 + 1
half_days = (half_frame or 0) / settings.FRAMES_PER_DAY
check(f"(9) reference human reaches 0.5 in ~FATIGUE_REF_HALF_DAYS ({half_days:.3f} vs "
      f"{settings.FATIGUE_REF_HALF_DAYS})",
      half_frame is not None and abs(half_days - settings.FATIGUE_REF_HALF_DAYS) < 0.02)
check(f"(9) reference human levels off at ~FATIGUE_REF_PLATEAU ({ch9.get('fatigue'):.3f} vs "
      f"{settings.FATIGUE_REF_PLATEAU:.3f})",
      abs(ch9.get("fatigue") - settings.FATIGUE_REF_PLATEAU) < 0.02)
try:
    for npc9 in roster:      # from (6): the real authored roster
        plateau9 = 1.0 - settings.FATIGUE_FADE_PER_FRAME / fatigue_gain(npc9.attributes)
        check(f"(9) {npc9.name}: derived plateau {plateau9:.2f} is visible (> 0.1)", plateau9 > 0.1)
except NameError:
    check("(9) roster unavailable (section 6 failed)", False)

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Fatigue acceptance CLEAN - all SW6 checks pass")
