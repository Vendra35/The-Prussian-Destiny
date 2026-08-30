# CLAUDE.md — The Prussian Destiny

## What this is
An EU5 mod that carries Brandenburg to the German Empire through three linked
situations: `the_prussian_ambition` (Brandenburg against the Teutonic Order),
`the_prussian_ascension` (Silesia, then the western march, then the great
ultimatum) and `the_blood_and_iron` (the Franco-Prussian tension clock and the
Ems Dispatch). Game rules choose the timeline (frontloaded / strict historical)
and whether the AI gets conquest safety nets.

## Run this after every change

```
python tools/verify_pd.py
```

Six checks. **Every check prints how many items it scanned, and a check that
scans zero FAILS** — a silent zero is the exact failure this mod keeps
producing. It locates vanilla by probing a known FILE; if it reports the tree
missing, add your path to `VANILLA_CANDIDATES` rather than ignoring the
degraded run.

What it flags today is real and queued, not noise: two `.gui` files still carry
a BOM, and two situations still name `c:TAG` inside map-mode blocks.

## The mistakes this mod actually makes

**Silent failure is the default.** A missing loc key prints its own name. A
missing texture draws nothing. A dead tag reference throws into debug.log
forever. None of it stops the game, so nothing tells you but a check.

**Never name `c:TAG` inside `map_color`, `secondary_map_color` or `tooltip`.**
Those run for every location on every redraw, so one tag that has left the map
is thousands of log lines a minute — the loudest version of the quietest bug.
- identity → `owner ?= { tag = PRU }`. `tag =` compares a literal name and
  never resolves a scope, so a dead tag is simply false.
- relations → `PD_bi_owner_is_subject_of = { TAG = PRU }` or
  `PD_bi_owner_allied_to = { TAG = PRU }` in `common/scripted_triggers/`. They
  check `country_exists` first and carry an explicit `trigger_else`.

**`?=` guards the LEFT side of a comparison.** It does nothing about a missing
scope on the right, and nothing at all for a `target = ` field. `owner ?= c:PRU`
still throws once PRU is off the map.

**Peace treaty events belong inside `hidden_effect`.** A treaty tooltip is
drawn while the deal is only being previewed, so `scope:winner` is unbound and
the auto-generated line renders as "Country gets the Event '...'". Let the
treaty's `custom_tooltip` do the talking.

**Peace treaties need a BARE loc key** — `PD_x: "Name"`, not only `_entry` /
`_entry_short` / `_desc` / `_tt`. The engine derives the display name from the
treaty key itself; without it every place that asks prints the raw key.

**`#Y` needs a space after it.** `#YGerman` is read as a tag named `YGerman`,
logged once per render, and the word is eaten off the screen.

## Files

- `.txt` and `.yml`: UTF-8 **with BOM**. `.gui`: **no BOM** — vanilla ships 483
  `.gui` files and only 49 have one.
- Localisation values sit on ONE physical line. `\n` stays two characters; a
  real newline splits the entry and the game drops it.
- **Match a file's existing line endings.** Line endings are not a convention
  to enforce (1198 of 1200 sampled vanilla `in_game/common` .txt files are
  LF-only), but a file carrying BOTH means something edited it carelessly — a
  regex line-replacement that eats a `\r` leaves exactly one bare LF and
  nothing complains.
- Write edit scripts to a FILE and run them; piping Python through a shell
  heredoc has silently corrupted the source more than once here.
- English for new code and comments. Existing comments are largely Turkish and
  some files carry cp1254 mojibake (`Aþama`, `Deðiþkenleri`) — leave those
  alone unless you are rewriting the file anyway.

## Situation panels

Rebuilt vanilla-style. `in_game/gui/panels/situation/the_blood_and_iron.gui` is
the reference implementation. The card stack:

description (short, in-world) · historical context · live state read from the
situation's own variables · End Requirements · what the player can do, with a
section per seat and one on what the AI actually decides.

Two rules that are easy to get wrong:
- The situation `_desc` key is read by the **engine**, in places far narrower
  than the panel. Keep it narrative; mechanics go on cards, where they can be
  live instead of a paragraph that ages.
- A panel cannot branch on which tag exists. Have the situation write the
  answer into a variable and read it back with `GetVariable('x').GetCountry`.

## This mod's own notes — read them before re-deriving anything

`docs/` holds what has already been read out of the script, so that a later
session does not pay for it twice:

- `ASCENSION-NOTES.md` — the three-step state machine, what actually advances
  each step, and a digest of all 21 phase-2 events with their `ai_chance`
  weights.
- `AMBITION-NOTES.md` — the score formula (army strength + monthly trade and tax
  + a fifth of prestige, recomputed monthly, nothing else), the fact that a tie
  counts as Brandenburg's, both cooldown paces, and a digest of the 18 phase-1
  events.
- `ASCENSION-WIP.md` — the checklist that panel rebuild ran on, kept as the
  worked example of how to slice this kind of job so it survives being
  interrupted.

The headline finding, true across all three situations: nearly every branching
event is weighted N against **zero**, so the AI takes the first option every
time and the alternative exists only for human players. The sole exception is
`pd_brandenburg.108`, weighted 1000 to 1. Do not restate that from memory —
if it matters again, re-count, because the weights can change.

The three situations are also an event-driven **chain**: each opens when the
previous one resolves. The dates inside them are floors and time limits, not a
schedule.

## Where the shared knowledge lives

The sibling project carries the EU5 reference this mod relies on:

`../1066 Test Mod/docs/`
- `EU5-ERROR-DECODER.md` — **grep this before investigating any log line.**
  Several signatures are recorded as vanilla-side, accept-it. More than one
  session has re-derived an entry that was already there.
- `EU5-MODDING-GUIDE.md`, `SITUATION-CRAFT.md` — general and panel craft.
- `EU5-Vanilla-Script-Docs/` — the authority. `triggers.log`, `effects.log`,
  `event_targets.log`, `modifiers.log`, `data_types/`. Grepping vanilla shows
  what someone happened to write; these show what is **legal**.

No field, effect or trigger enters a file without either an entry in the script
docs or a vanilla `file:line` using it in the same position and scope.
