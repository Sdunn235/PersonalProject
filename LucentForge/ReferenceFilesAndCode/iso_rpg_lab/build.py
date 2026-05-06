import json, os, sys, subprocess

def load(path):
    with open(path,"r",encoding="utf-8") as f: return json.load(f)

def validate_ids(things, kind):
    ids = [t["id"] for t in things]
    dup = len(ids) != len(set(ids))
    if dup:
        seen=set(); dups=[]
        for i in ids:
            if i in seen: dups.append(i)
            seen.add(i)
        raise SystemExit(f"[ERROR] duplicate {kind} ids: {dups}")

def main():
    root = os.path.dirname(__file__)
    data = os.path.join(root,"data")
    items = load(os.path.join(data,"items.json"))
    abilities = load(os.path.join(data,"abilities.json"))
    enemies = load(os.path.join(data,"enemies.json"))
    validate_ids(items,"item")
    validate_ids(abilities,"ability")
    validate_ids(enemies,"enemy")
    print("[OK] Data validated.")
    # Run a tiny balance smoke test
    print("[RUN] 500 duels vs slime_green ...")
    subprocess.run([sys.executable, "-m", "sim.simulate", "--runs", "500", "--enemy", "slime_green"], check=True)

if __name__ == "__main__":
    main()
