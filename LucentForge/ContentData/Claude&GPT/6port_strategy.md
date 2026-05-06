# Port Strategy

## Prototype Goals

Must prove:
- Drive-based behavior works
- NPCs act without scripting
- Basic interaction loops function

---

## What Carries Over

- System architecture
- Behavioral models
- Design philosophy

---

## What Gets Rebuilt

- Rendering
- Performance systems
- Memory storage backend
- World persistence systems

---

## UE5 Considerations

- Likely need C++ for performance
- Blueprint for rapid iteration
- Possible ECS-style system needed

---

## Prototype Completion Criteria

Prototype is complete when:
- NPCs behave autonomously
- Systems show emergent behavior
- No reliance on scripted fallback logic

---

## Final Rule

Do not port early.

Prove the system first.