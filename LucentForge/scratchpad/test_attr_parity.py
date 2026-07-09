# Phase 4.1 parity gate: derived Stats (from attributes) must equal the
# pre-change authored Stats for every entity. Run: py scratchpad/test_attr_parity.py
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Mechanics.entities.attributes import Attributes  # noqa: E402

ENTITIES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "Mechanics", "data", "entities.json")

# Pre-4.1 authored combat stats (STR, MAG, LCK, DEF, RES, DEX) — the parity target.
EXPECTED = {
    "player":    (10, 6, 5, 5, 0, 8),
    "npc_01":    (12, 0, 5, 4, 0, 6),
    "npc_02":    (8, 14, 5, 3, 3, 9),
    "npc_03":    (14, 0, 4, 6, 0, 5),
    "npc_04":    (6, 12, 6, 3, 4, 10),
    "goblin_01": (8, 0, 3, 2, 0, 6),
    "goblin_02": (10, 0, 5, 3, 0, 8),
    "dragon_01": (22, 18, 8, 12, 8, 6),
}


def derive(data):
    attrs = Attributes.from_dict(data["attributes"])
    s = attrs.to_stats(resist=data.get("resist", 0))
    return (s.STR, s.MAG, s.LCK, s.DEF, s.RES, s.DEX)


def main():
    with open(ENTITIES, encoding="utf-8") as f:
        entities = json.load(f)

    failures = 0
    for e in entities:
        eid = e["id"]
        got = derive(e)
        want = EXPECTED[eid]
        ok = got == want
        flag = "OK " if ok else "FAIL"
        print(f"[{flag}] {eid:10s} derived={got} expected={want}")
        if not ok:
            failures += 1

    print("-" * 50)
    if failures:
        print(f"PARITY FAILED: {failures} entity/entities diverged.")
        sys.exit(1)
    print("PARITY OK: all entities reproduce pre-4.1 combat stats.")


if __name__ == "__main__":
    main()
