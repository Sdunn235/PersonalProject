# Autonomy policy

How much Claude (with Caelum as Director) may do on LucentForge without Shawn. Shawn is the owner and
the only one who can change this policy. Adopted 2026-11-19 (Shawn chose the "hybrid" line), modeled on
the Smug Cat Games (enviz-crew) organization governance, where agents work up to the PR and the owner
approves.

**The deal:** tests carry the trust, so Shawn's time goes to decisions, not quality checks. Anything
Shawn used to check at the window gets a test first ([testing](testing.md)).

## What Claude may do alone

- Write tests and code for work Shawn has asked for or that the [BACKLOG](../BACKLOG.md) marks `ready`.
- **Commit and push to `master`** when all three hold: the change began with a test that failed for the
  right reason; `scratchpad/run_all_tests.py` is green locally (the pre-push hook enforces it); and CI's
  `verify` job is green on the pushed commit. If CI goes red after a push, fixing it is the next job.
- Fix bugs that tests find, inside the same rules (example: the C0079 queueing fix found by the soak suite).
- Keep the record current: CHANGELOG, BACKLOG, `context/session_state.md`, READMEs, the
  [verification log](verification.md), Studio department logs, Caelum session logs and memory.
- Add **dated code-reality notes** where the bible and the code disagree (bible README "Authority order").
- Run Studio departments, write design notes and drafts, open branches and PRs.

## What stops at a PR for Shawn

These can be drafted, tested and proposed, but only Shawn merges them. They cannot authorize themselves.

- **Doctrine:** adding, removing or rewriting bible §-rules or canon (world, cosmology, story, lore).
  Code-reality notes are not doctrine changes; deciding *which side changes* is.
- **Policy and enforcement:** this file, [testing](testing.md), `CLAUDE.md`, Studio charters and agent
  definitions, the CI workflow, git hooks, and any change that relaxes, skips or deletes an existing check.
- **Shawn's material:** deleting or rewriting his art, maps, the Gobby source, saves, or anything he
  authored by hand. `ReferenceFilesAndCode/` is never modified.
- **New outside things:** new repositories, services, paid tools, recurring costs, publishing anywhere
  outside this repo, or changing repository visibility/settings.

## Never

Force-push, rewrite published history, bypass hooks (`--no-verify`), weaken or delete a test to get a
green gate, or claim a check ran that didn't. Green CI, a Studio QC verdict or a passing test is
evidence, not owner approval, for anything in the PR list.

## Autonomous runs ("build it all" mode)

Only when Shawn asks, with a scope (e.g. "Arc B") and, if he wants, a budget. Claude then works the
scope's BACKLOG items in order, test-first, and after each item: commit + push (gate and CI green),
a verification-log entry, and BACKLOG/CHANGELOG updates. It stops and reports when it reaches a PR-list
decision, fails twice to turn the same red test green, exhausts the scope, or hits the budget. A run
never expands its own scope.

## States are separate

**Implemented** (on a branch) → **merged** (on `master`) → **verified** (gate + CI green, logged in
[verification](verification.md)) → **reviewed** (Shawn looked, optional). The CHANGELOG lists merged and
verified work. A Shawn live check is now an optional *feel* review, not a gate. If it finds something,
the first fix is a test that would have caught it.
