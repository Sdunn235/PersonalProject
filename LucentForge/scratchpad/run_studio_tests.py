# run_studio_tests.py — the Studio is complete and self-consistent (docs/testing.md "Unit").
#
# Every department is a mini-Caelum: studio/<dept>/charter.md + memory_log.md + references/, listed in
# studio/README.md's department table with its agent, and loadable by that agent. Required departments
# are named here so adding one is test-first (QA + Art, 2026-11-19).
#
# Each department also has a direction.md: its values, craft, signature, handoffs, how its craft survives
# beyond 2D, and open questions (Shawn, 2026-11-19: "each department needs to find its values and
# direction and how to work together"). Handoffs must name every other department, and
# studio/WORKING_TOGETHER.md maps every artifact that passes between departments.
#
#   py scratchpad/run_studio_tests.py
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIO = os.path.join(ROOT, "studio")
# Agent definitions live in the Workspace repo (outside this repo); absent on CI.
AGENTS = os.path.normpath(os.path.join(ROOT, "..", "..", ".claude", "agents"))
SKILLS = os.path.normpath(os.path.join(ROOT, "..", "..", ".claude", "skills"))
DIRECTION_SECTIONS = ("Values", "Craft", "Signature", "Handoffs", "Beyond 2D", "Open questions")
# How each department is named in prose (folder -> accepted spellings, compared without spaces).
NAMES = {"systems_design": ("SystemsDesign",), "code_review_qc": ("QC", "CodeReview"),
         "engineering": ("Engineering",), "world_building": ("WorldBuilding",),
         "story_lore": ("Story/Lore", "StoryLore"), "qa": ("QA",), "art": ("Art",)}
REQUIRED = {"systems_design", "code_review_qc", "engineering", "world_building", "story_lore",
            "qa", "art"}

_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


print("=" * 64)
print("Studio tests - every department complete, listed, and loadable")
print("=" * 64)

depts = sorted(d for d in os.listdir(STUDIO) if os.path.isdir(os.path.join(STUDIO, d)))
check("all required departments exist", REQUIRED <= set(depts), f"missing {sorted(REQUIRED - set(depts))}")
for d in depts:
    base = os.path.join(STUDIO, d)
    check(f"{d}: charter.md", os.path.isfile(os.path.join(base, "charter.md")))
    check(f"{d}: memory_log.md", os.path.isfile(os.path.join(base, "memory_log.md")))
    refs = os.path.join(base, "references")
    check(f"{d}: references/ with at least one doc",
          os.path.isdir(refs) and any(f.endswith(".md") for f in os.listdir(refs)))



def section(text: str, name: str) -> str:
    m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def names_dept(text: str, d: str) -> bool:
    flat = re.sub(r"\s+", "", text)
    return any(re.search(rf"(?<![A-Za-z]){re.escape(n)}(?![a-z])", flat) for n in NAMES[d])


for d in depts:
    path = os.path.join(STUDIO, d, "direction.md")
    ok = os.path.isfile(path)
    check(f"{d}: direction.md", ok)
    if not ok:
        continue
    text = open(path, encoding="utf-8").read()
    missing = [s_ for s_ in DIRECTION_SECTIONS if not section(text, s_).strip()]
    check(f"{d}: direction has every section {DIRECTION_SECTIONS}", not missing, f"missing/empty {missing}")
    hand = section(text, "Handoffs")
    absent = [o for o in depts if o != d and o in NAMES and not names_dept(hand, o)]
    check(f"{d}: handoffs name every other department", not absent, f"not named: {absent}")

wt_path = os.path.join(STUDIO, "WORKING_TOGETHER.md")
check("studio/WORKING_TOGETHER.md exists", os.path.isfile(wt_path))
if os.path.isfile(wt_path):
    wt = open(wt_path, encoding="utf-8").read()
    check("WORKING_TOGETHER names every department", all(names_dept(wt, d) for d in depts if d in NAMES),
          str([d for d in depts if d in NAMES and not names_dept(wt, d)]))
    flow = section(wt, "Handoff map")
    rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in flow.splitlines()
            if r.strip().startswith("|") and not re.match(r"^\|\s*-", r.strip())][1:]
    check("WORKING_TOGETHER has a handoff map table", len(rows) >= 7, f"{len(rows)} rows")
    known = {n.lower() for ns in NAMES.values() for n in ns} | {"director", "shawn"}
    bad = [r for r in rows if len(r) < 3 or any(
        not all(re.sub(r"\s+", "", p).lower() in known for p in re.split(r",|\+| and ", cell) if p.strip())
        for cell in r[1:3])]
    check("every handoff's producer and consumer is a department, the Director or Shawn", not bad, str(bad[:2]))

readme = open(os.path.join(STUDIO, "README.md"), encoding="utf-8").read()
check("README points to WORKING_TOGETHER.md", "WORKING_TOGETHER.md" in readme)
table_agents = re.findall(r"^\|[^|]+\|\s*`(lucentforge-[a-z-]+)`\s*\|", readme, re.M)
check("README department table lists one agent per department folder",
      len(table_agents) == len(depts), f"{len(table_agents)} agents vs {len(depts)} folders")

if os.path.isdir(AGENTS):
    loaded = set()
    for agent in table_agents:
        path = os.path.join(AGENTS, f"{agent}.md")
        ok = os.path.isfile(path)
        check(f"agent definition exists: {agent}", ok)
        if ok:
            text = open(path, encoding="utf-8").read().replace("/", "\\")
            for d in depts:
                if f"studio\\{d}\\charter.md" in text:
                    loaded.add(d)
    check("every department's charter is loaded by some agent definition",
          loaded == set(depts), f"not loaded: {sorted(set(depts) - loaded)}")
    if os.path.isdir(SKILLS):
        for agent in table_agents:
            skill = os.path.join(SKILLS, agent, "SKILL.md")
            check(f"skill adapter exists: {agent}", os.path.isfile(skill))
else:
    print("[PASS] agent/skill checks n/a here (workspace .claude/ not present, e.g. CI)")

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Studio tests CLEAN")
