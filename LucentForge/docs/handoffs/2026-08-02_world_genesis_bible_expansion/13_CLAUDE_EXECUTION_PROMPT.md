# Claude Execution Prompt

You are working locally in Shawn Dunn's `Sdunn235/PersonalProject` repository.

Implement the **documentation integration** described in this handoff.

## First responsibility

Audit the live repository before editing.

Read:

1. `LucentForge/docs/bible/README.md`
2. `lucentforge_simulation_foundation_v_1.md`
3. `lucentforge_rooms_panels_addendum_v1.md`
4. terminology, Grace, affinity, runtime, and other documents relevant to world/map authority
5. current map assets under `LucentForge/assets/maps/world_map`
6. current context/session state

## Required behavior

- Preserve the Bible as canonical authority.
- Do not create a separate competing Planet Bible.
- Reconcile the proposed planetary map layer with the existing one-scale Panel doctrine.
- Add only documents that reduce uncertainty.
- Use the existing Bible's filename, authority, section-ID, and out-of-scope conventions.
- Update the Bible README index when new Bible documents are added.
- Put Genesis implementation architecture outside the Bible.
- Preserve source PSDs, exported layers, notes, and original CSVs.
- Correct copied registries rather than altering historical source files.
- Do not implement generators during this task.
- Do not classify uncertain plate boundaries as canon.
- Create a draft PR; do not merge.

## Suggested branch

```text
docs/world-genesis-bible-expansion
```

## Expected deliverables

- 4 proposed Bible documents, adapted to the live repository;
- Genesis architecture documentation;
- map standards documentation;
- plate and layer registries;
- asset README/navigation;
- updated Bible index;
- completion report.

## Review gates

Before commit:

- check all relative links;
- compare terminology with current Bible;
- verify no duplicate authority;
- verify no unrelated code changes;
- verify original source assets are unchanged;
- run `git diff --check`;
- review the full diff.

Return the report format in `14_COMPLETION_REPORT.md`.
