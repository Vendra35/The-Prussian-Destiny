# The Prussian Ascension — panel rebuild: DONE, awaiting an in-game test

Started and finished 2026-08-30, statically. Nothing here has been seen running. `the_blood_and_iron` is the finished reference: its panel,
its loc block and its scripted-trigger guards are the templates for everything
here. Every box is ticked and verify_pd.py reports all checks passed. What is NOT
done is an in-game test: static verification is not evidence of behaviour.

Run `python tools/verify_pd.py` at every step. It reported two failures when
this work started; as of the hygiene pass it reports **all checks passed**.

## 1. Hygiene — small, mechanical, clears the verifier

- [x] **1a. Map-mode tag guards.** `the_prussian_ascension.txt` names `c:PRU`
      three times inside blocks that run per-location per-redraw:
      `map_color:1167` (`owner ?= c:PRU`), `secondary_map_color:1187`
      (`is_subject_of = c:PRU`), `secondary_map_color:1208`
      (`NOT = { owner = c:PRU }`). Same fix as Blood and Iron: `tag = PRU` for
      identity, the parameterised scripted trigger for the relation.
      `brandenburg_rise.txt` has the same problem with `c:BRA` / `c:TEU`.
- [x] **1b. BOM.** `the_prussian_ascension.gui` and `the_prussian_ambition.gui`
      both carry one; vanilla ships 483 `.gui` files and only 49 have one.
- [x] **1c. cp1254 mojibake.** `the_prussian_ascension.txt` has 251 mangled
      characters, `the_prussian_ambition.gui` has 11. Mapping is unambiguous:
      `ý→ı Ý→İ þ→ş Þ→Ş ð→ğ Ð→Ğ`. Comments only, no gameplay effect.
      `brandenburg_rise.txt` is already clean. **`PD_peace_treaties.txt` is NOT
      in scope** — it carries a second, different mangling (`Ä±`), so it needs
      its own pass.

## 2. Read the 21 phase-2 events → `docs/ASCENSION-NOTES.md`

DONE - banked in docs/ASCENSION-NOTES.md. The headline: all five branching
events are weighted N against 0, so the AI never takes a second option.

- [x] **2a.** Events `pd_brandenburg.200`–`.217`, `.220`, `.221`, `.299`. For
      each: what fires it, what it does, its `ai_chance` weights, any
      `is_ai` gate.
- [x] **2b.** From that, the honest answer to "what does the AI actually
      decide here" — 21 `ai_chance` blocks against Blood and Iron's one.

## 3. Localisation

- [x] **3a.** Trim `the_prussian_ascension_desc` to narrative only (1743 chars
      today, with a `HISTORICAL CONTEXT` heading and a `What to Expect` block
      that the new cards will replace). The engine reads this key in cramped
      places — see `../1066 Test Mod/docs/SITUATION-CRAFT.md`.
- [x] **3b.** History card keys, written as real history.
- [x] **3c.** Step / road / target strings.
- [x] **3d.** Levers card, including a `How the AI plays this` section built
      from 2b — not from guesswork.

## 4. The panel

- [x] **4a.** Three-dot step meter on `PD_phase2_current_step` (1 = Silesia,
      2 = the western march, 3 = the great ultimatum).
- [x] **4b.** Road card, one rung per step, plus sub-lines for
      `PD_zollverein_asked` and `PD_austria_ultimatum_sent`.
- [x] **4c.** Current target row from
      `PD_phase2_conquest_target_country` (guard on `PD_phase2_conquest_target`).
- [x] **4d.** Card stack in the agreed order: description · historical context ·
      road · End Requirements · what we can do.

## State the panel can read

| Variable | Meaning |
|---|---|
| `PD_phase2_current_step` | 1 Silesia, 2 west, 3 ultimatum. Set at :122, moves at :443 and :618 |
| `PD_phase2_conquest_target` | 0 = no target picked, 1 = target held in the country var |
| `PD_phase2_conquest_target_country` | the country being aimed at |
| `PD_phase2_conquest_cooldown` | AI pacing, +1/month, gates at >12 and >60 |
| `PD_zollverein_asked` | set at :480 |
| `PD_austria_ultimatum_sent` | set at :681, cleared at :665 |

## Post-test polish (2026-08-30, from the first screenshots)

- [x] The header's right-hand icon repeated the situation icon already on the
      left of the same strip; it is now Prussia's flag.
- [x] `PD_pa_target_none` read "No target is being aimed at this month"; it now
      matches the Ambition panel's "Nothing this month".
- [x] The road card's right column showed 1 / 2 / 3, which only repeated the row
      order. It now shows Done / Current / Ahead, gated by exactly the same
      expressions as the dots so the two can never disagree. The type's value
      slot became a block around the whole widget to allow that in one override.
