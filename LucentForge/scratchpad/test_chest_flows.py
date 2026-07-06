"""test_chest_flows.py — Phase 2.7 headless smoke tests for chest/lock/trap/loot flows.

Usage: py scratchpad/test_chest_flows.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
from unittest.mock import patch

import settings
from Mechanics.items.containers import Chest, ItemStack, Inventory
from Mechanics.items.enums import TrapType
from Mechanics.services.inventory_service import InventoryService
from Mechanics.services.outcome import OutcomeResolver, OutcomeResult, Degree

# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class _Stats:
    STR = 5
    DEX = 5
    LCK = 3
    MAG = 0

class _Player:
    entity_id = "player"
    hp = 50
    max_hp = 50
    stats = _Stats()

class _Item:
    def __init__(self, id_, name, weight=1):
        self.id = id_
        self.name = name
        self.weight = weight

class _ItemRepo:
    def __init__(self, items):
        self._map = {i.id: i for i in items}
    def find_by_id(self, id_):
        return self._map.get(id_)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_inv_svc(player_id, stacks=None):
    svc = InventoryService()
    svc.register(player_id, Inventory(player_id, stacks or []))
    return svc

def _make_locked_chest(loot_stacks, lock_dc=5):
    return Chest(id="test_chest", col=0, row=0, locked=True, lock_dc=lock_dc,
                 contents=loot_stacks)

def _make_trapped_chest(loot_stacks, trap_damage=15):
    return Chest(id="test_chest", col=0, row=0, locked=False,
                 is_trapped=True, trap_type=TrapType.MECHANICAL,
                 trap_damage=trap_damage, contents=loot_stacks)

def _patch_resolver(degree: Degree, success: bool):
    """Return a resolver whose resolve() always returns the given degree."""
    result = OutcomeResult(success=success, degree=degree, score=0, margin=0, variance=0)
    class FixedResolver:
        def resolve(self, check): return result
    return FixedResolver()

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_lockpick_success():
    """SUCCESS: chest unlocks, lockpick NOT consumed."""
    from Mechanics.renderer.chest_menu import _execute
    sword = _Item("iron_sword", "Iron Sword", weight=8)
    pick  = _Item("lockpick", "Lockpick", weight=1)
    player = _Player()
    inv_svc = _make_inv_svc(player.entity_id, [ItemStack(pick, 2)])
    chest = _make_locked_chest([ItemStack(sword, 1)])
    item_repo = _ItemRepo([sword, pick])

    resolver = _patch_resolver(Degree.SUCCESS, True)
    msg, ok = _execute("pick_lock", chest, player, inv_svc, item_repo, resolver)

    assert not chest.locked, "Chest should be unlocked after SUCCESS"
    assert ok
    # lockpick is NOT consumed on success — inventory still has 2
    inv = inv_svc.get_inventory(player.entity_id)
    remaining = inv.find_stack("lockpick")
    assert remaining is not None and remaining.qty == 2, \
        f"Lockpick should not be consumed on success, got {remaining}"
    print(f"  PASS test_lockpick_success — {msg}")


def test_lockpick_failure():
    """FAILURE: chest stays locked, lockpick IS consumed."""
    from Mechanics.renderer.chest_menu import _execute
    pick   = _Item("lockpick", "Lockpick", weight=1)
    sword  = _Item("iron_sword", "Iron Sword", weight=8)
    player = _Player()
    inv_svc = _make_inv_svc(player.entity_id, [ItemStack(pick, 1)])
    chest = _make_locked_chest([ItemStack(sword, 1)])
    item_repo = _ItemRepo([sword, pick])

    resolver = _patch_resolver(Degree.FAILURE, False)
    msg, ok = _execute("pick_lock", chest, player, inv_svc, item_repo, resolver)

    assert chest.locked, "Chest should still be locked after FAILURE"
    assert not ok
    inv = inv_svc.get_inventory(player.entity_id)
    remaining = inv.find_stack("lockpick")
    assert remaining is None, "Lockpick should be consumed on FAILURE"
    print(f"  PASS test_lockpick_failure — {msg}")


def test_lockpick_critical_failure_fires_trap():
    """CRITICAL_FAILURE on trapped chest: trap fires, HP clamped to 1."""
    from Mechanics.renderer.chest_menu import _execute
    pick   = _Item("lockpick", "Lockpick", weight=1)
    sword  = _Item("iron_sword", "Iron Sword", weight=8)
    player = _Player()
    player.hp = 5
    inv_svc = _make_inv_svc(player.entity_id, [ItemStack(pick, 1)])
    chest = Chest(id="trap_chest", col=0, row=0, locked=True, lock_dc=5,
                  is_trapped=True, trap_type=TrapType.MECHANICAL, trap_damage=15,
                  contents=[ItemStack(sword, 1)])
    item_repo = _ItemRepo([sword, pick])

    resolver = _patch_resolver(Degree.CRITICAL_FAILURE, False)
    msg, ok = _execute("pick_lock", chest, player, inv_svc, item_repo, resolver)

    assert player.hp == 1, f"HP should be clamped to 1, got {player.hp}"
    assert chest.is_opened, "Chest should be opened after crit fail trap"
    assert not chest.locked
    assert not ok
    print(f"  PASS test_lockpick_critical_failure_fires_trap — {msg}")


def test_take_from_encumbrance_block():
    """take_from returns False when item would exceed carry capacity."""
    heavy = _Item("big_rock", "Big Rock", weight=999)
    player = _Player()
    player.stats.STR = 1  # capacity = CARRY_BASE + CARRY_PER_STR*1 = 22
    inv_svc = _make_inv_svc(player.entity_id, [])
    chest = Chest(id="c", col=0, row=0, contents=[ItemStack(heavy, 1)])

    ok = inv_svc.take_from(chest, player.entity_id, heavy, 1, str_stat=player.stats.STR)
    assert not ok, "take_from should return False when item is too heavy"
    assert len(chest.contents) == 1, "Chest contents should be unchanged"
    print("  PASS test_take_from_encumbrance_block")


def test_take_from_success():
    """take_from moves item from chest to inventory."""
    gem = _Item("gem", "Gem", weight=1)
    player = _Player()
    inv_svc = _make_inv_svc(player.entity_id, [])
    chest = Chest(id="c", col=0, row=0, contents=[ItemStack(gem, 3)])

    ok = inv_svc.take_from(chest, player.entity_id, gem, 2, str_stat=player.stats.STR)
    assert ok, "take_from should succeed"
    inv = inv_svc.get_inventory(player.entity_id)
    stack = inv.find_stack("gem")
    assert stack is not None and stack.qty == 2, f"Expected 2 gems in inventory, got {stack}"
    remaining = chest.contents[0].qty
    assert remaining == 1, f"Expected 1 gem left in chest, got {remaining}"
    print("  PASS test_take_from_success")


if __name__ == "__main__":
    print("=== Phase 2.7 Chest Flow Smoke Tests ===\n")
    tests = [
        test_lockpick_success,
        test_lockpick_failure,
        test_lockpick_critical_failure_fires_trap,
        test_take_from_encumbrance_block,
        test_take_from_success,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed.")
    sys.exit(0 if passed == len(tests) else 1)
