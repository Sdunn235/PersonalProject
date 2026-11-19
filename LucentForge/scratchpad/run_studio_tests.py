# run_studio_tests.py — the Studio is complete and self-consistent (docs/testing.md "Unit").
#
# Every department is a mini-Caelum: studio/<dept>/charter.md + memory_log.md + references/, listed in
# studio/README.md's department table with its agent, and loadable by that agent. Required departments
# are named here so adding one is test-first (QA + Art, 2026-11-19).
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

readme = open(os.path.join(STUDIO, "README.md"), encoding="utf-8").read()
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
