Python 3.10+

Run quick validation + balance smoke test:
    python build.py

Run a larger sim:
    python sim/simulate.py --enemy bandit --runs 2000

Where to tweak:
- data/*.json  ← items/abilities/enemies you and AI can edit freely
- gameplay/stats.py  ← clamp vs wrap behavior; status flags
- gameplay/combat.py ← damage formula, crits, DOTs
- gameplay/qfixed.py ← fixed-point utilities for movement/timing later
