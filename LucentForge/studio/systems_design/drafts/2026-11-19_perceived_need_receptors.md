# Design Note — Perceived-Need Receptors as Formulas (v1 — IMPLEMENTED: Phase A C0077, B C0078, C docs)

> **Decisions (Shawn, 2026-11-19):** approach approved, phased A → B → C; strain resistance = Constitution only;
> strain perception trait = `fearfulness`; bible: classify doctrine vs factual error first (see Q5) — doctrine stands.

> Director review, 2026-11-19. Triggered by Shawn while scoping LF-042 (strain receptor): *"go over docs,
> notes, and bible. I see you doing a lot of hard number sets too."* He's right. The fatigue fix (C0072)
> shipped `FATIGUE_BASE_GAIN = 0.0015` and `FATIGUE_SLEEP_PULL = 30` as magic numbers with the reasoning in
> a comment, against Systems Design standard 1 ("formulas, not numbers"). The strain plan was about to do
> it again (decay 0.05, pull 20). This note re-grounds both in the bible before any more code.

## 1. Problem / intent

Chemicals only change behavior through a receptor (`biochem/receptor.py`) that writes a perceived pull onto
a need. The first receptor (fatigue → sleep) works, but its rates and magnitudes are hand-picked per-frame
literals. Strain (LF-042) needs a receptor too, and measuring it showed the same disease: strain settles
`fade/gain` = 0.2 below its target, the harshest ground anyone stands on is comfort −0.40, so it peaks
around 0.07. Hand-tuning another pair of numbers would "fix" it the same fragile way. Intent: make
receptor rates and pulls **derived** — from authored game-meaningful quantities (days, need bands),
attributes, and traits — so they keep working as attributes ascend and content changes.

## 2. What the docs actually say (the review)

| Source | What it requires | What the code / my work does |
|---|---|---|
| Foundation §4.1 Constitution | "fatigue tolerance, sustained effort, pain tolerance, **physical resilience**" | Fatigue uses `endurance(attrs)` ✓. Strain has **no** attribute resistance. |
| Foundation §13 "Interpret Result" | outcomes are "filtered through **traits**, stress, memory" | Pulls ignore traits entirely (flat `× 30`). |
| Foundation §2.5 | context over universal balance | A flat pull is universal by construction. |
| needs/wants §W2, §W5, charter std 2 | wants reach behavior through `Drive` `base_weight` arithmetic; Maslow suppression "falls out" of it | **False in code** — drives are display-only; decisions read need zones. §W5's recipe ("register a Drive") produces an inert want. |
| needs/wants §W7 | addiction susceptibility from `fearfulness` + `resilience` | There is no `resilience` trait (traits: curiosity, aggression, fearfulness, sociability). |
| biochem §B2 | a receptor reads a chemical with a **threshold and a gain** (Creatures) | `receptor.py` has a threshold (the dead-band) but one global literal for gain. |
| biochem §B7 | strain "−0.8 reaches ~50% after ~60 s" | Nobody experiences −0.8; worst real ground is −0.40, where decay cancels most of it. |
| `settings.py` / `needs.json` existing pattern | rates authored per **day**, converted: `decay_per_day / SIM_DAY_SECONDS / FPS` | Fatigue/strain/chemical decay are raw **per-frame** literals (0.0015, 0.0003, 0.0002 × mult). |
| Ideas doc ("needs at different tiers affect regen") | unmet needs feed back into recovery | Consistent with the receptor pausing regen ✓. |

## 3. Proposed mechanic

Keep the receptor architecture (it works and every decision path agrees). Change *how its numbers are made*:

1. **Author time, derive rate.** Each slow chemical gets two authored time constants in **in-game days**:
   a rise time (for a *reference* entity under full exposure) and a fade time. Per-frame rates are derived
   (`1 / (tau_days × SIM_DAY_SECONDS × FPS)`), exactly like need decay already is.
2. **Resistance is an attribute strategy.** Rise rate is scaled by `reference / strategy(attrs)`:
   fatigue → `endurance` (exists); strain → a new `resilience(attrs)` strategy, Constitution-led per §4.1.
3. **Pull is a fraction of the need's own band.** A need's "comfort band" is `100 − warning_threshold`
   (authored per need in `needs.json`). A receptor pull = `chemical × receptor_gain × band`. Because every
   gain is a fraction ≤ 1 and the **sum** of pulls on one need is capped below the band, "a just-satisfied
   need stays FINE" becomes structural instead of a hand-checked number. (Today: 30 = 0.5 × (100 − 40).)
4. **Personality shapes perception.** Receptor gain = base gain × a trait modulator. Strain is a felt
   threat/discomfort pressure → `fearfulness` (the "fear sensitivity" axis, already used by
   `Drive.compute_urgency`). Fatigue stays attribute-driven (no trait fits it cleanly yet — open Q).
5. **Derived invariants replace hand checks.** For every slow chemical, the plateau under the harshest
   *authored* exposure (`target − fade/gain`) is computed from content and asserted in tests — so a content
   change that makes a want inert fails a test instead of silently dying.

## 4. Formulas

```
frames_per_day        = SIM_DAY_SECONDS × FPS                       # existing
rate(tau_days)        = 1 / (tau_days × frames_per_day)              # per-frame rate from authored time

# fatigue (re-expressed — same behavior)
fatigue_gain(attrs)   = rate(FATIGUE_RISE_DAYS)  × ENDURANCE_REF   / endurance(attrs)
fatigue_fade          = rate(FATIGUE_FADE_DAYS)
# today's values ≈ FATIGUE_RISE_DAYS 0.37, FATIGUE_FADE_DAYS 1.11, ENDURANCE_REF 10 (human reference)

# strain (new)
resilience(attrs)     = constitution × RESILIENCE_CON_WEIGHT  (+ other weights if Shawn wants)
strain_gain(attrs)    = rate(STRAIN_RISE_DAYS)   × RESILIENCE_REF  / resilience(attrs)
strain_fade           = rate(STRAIN_FADE_DAYS)

# receptors
band(need)            = 100 − need.warning_threshold                 # from needs.json
pull_fatigue(sleep)   = fatigue × FATIGUE_PULL_FRACTION × band(sleep)
pull_strain(need)     = strain  × STRAIN_PULL_FRACTION  × (1 + fearfulness × STRAIN_FEAR_WEIGHT) × band(need)
perceived_pull(need)  = min(Σ pulls on need, band(need) × PULL_CAP_FRACTION)    # PULL_CAP_FRACTION < 1

# invariant (tests, computed from content — not hand numbers)
plateau(chem, entity) = target_max − fade / gain(entity)    must be ≥ VISIBLE_FLOOR for the harshest
                        authored exposure of each entity that can experience it
```

Every literal left is a **named, authored quantity in game units** (days, fractions of a band, trait
weights, reference attribute values) — no per-frame magic numbers.

## 5. Where it slots in

- `entities/derivation.py` — add `resilience` beside `endurance` (same Protocol pattern).
- `settings.py` — fatigue/strain blocks rewritten as authored days + fractions; derived per-frame values
  computed there (like `HUNGER_DECAY_PER_TICK`).
- `biochem/emitter.py` — gains come from the derivation functions (already does for fatigue).
- `biochem/chemical.py` — fatigue/strain fade read the derived rates instead of `_DECAY × mult`.
- `biochem/receptor.py` — receptors become small `(chemical, need_ids, gain_formula)` entries; one
  combine-and-cap step. Still adds instances, not architecture.
- Tests — fatigue suite keeps passing (parity re-expression); new strain integrated + kernel A/B tests;
  the plateau invariant computed from `rooms.json` × `entities.json`.

## 6. Interactions & risks

- **Phase order (parity-first):** (A) re-express fatigue as formulas with byte-near-identical values →
  suite green; (B) strain receptor + retune via authored days; (C) bible corrections. Don't mix A and B.
- Strain retune changes C0046's feel (strain will actually exist). It also starts pausing HP/SP regen for
  stressed NPCs, through the perceived zone.
- The rest of the chemical table (`_DECAY 0.0002`, pain/fear/anger mults, the 0.03/0.05 approach rates
  in `Chemicals.tick`) is the same per-frame-literal pattern. **Out of scope here** — log as a backlog
  item rather than widen this change.

## 7. Open questions (for Shawn)

1. **Approve the approach** — authored days + band fractions + attribute/trait modulation, phased A → B → C?
2. **Strain's resistance:** Constitution only, or Constitution + Intuition ("knows how to live with hostile
   ground")? Default proposal: Constitution only (§4.1 says "physical resilience").
3. **Strain's trait:** `fearfulness` (existing) as the perception modulator? Or wait for a new trait axis
   (the Foundation §8.2 list has "fear sensitivity" and "control ↔ acceptance")?
4. **Fatigue + trait:** leave fatigue attribute-only for now?
5. ~~**Bible fixes:** correct §W2/§W5/§W7 + charter?~~ **Shawn (2026-11-19): first decide whether the bible
   states a goal we're working toward — you can't change it just because the code disagrees.** Classified:
   - *Doctrine / aspiration — keep, code is behind:* §B1 "a decision that follows the strongest drive";
     `design/npc_mind_architecture.md` §4 "weighted drive urgency"; §W2 Maslow emergence by weight
     arithmetic; charter standard 2; §W7 `resilience` (a designed future trait, Foundation §8.2 axes).
   - *Factual claims about the code — false today, get dated code-reality notes only:* §B1/§B2 "already has
     the receptor half"; §W2 "the drive architecture already supports this"; §W5 "without structural
     change"; §B7 "acts sooner".
   - *Consequence:* receptors are an **interim bridge**; the doctrinal fix is LF-043 (decisions follow drive
     urgency). Phase C = code-reality notes on the factual claims only; no doctrine is rewritten.

## 8. Bible citations

Foundation §2.5, §4.1, §5, §8.2, §9, §13.2 · needs/wants §W2, §W3, §W5, §W6, §W6.1, §W7 · biochem §B1, §B2,
§B4, §B7 · stats/magic §M3 · bible README "Authority order" · Systems Design charter standards 1–2.
