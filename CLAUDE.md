# CLAUDE.md — The Prussian Destiny

## What this is
An EU5 mod that carries Brandenburg to the German Empire through three linked
situations: `the_prussian_ambition` (Brandenburg against the Teutonic Order),
`the_prussian_ascension` (Silesia, then the western march, then the great
ultimatum) and `the_blood_and_iron` (the Franco-Prussian tension clock and the
Ems Dispatch). Game rules choose the timeline (frontloaded / strict historical)
and whether the AI gets conquest safety nets.

It also ships one **disaster**, `PD_bohemian_estates_crisis` — the crown
of Bohemia against its estates. Read `docs/BOHEMIA-DISASTER.md` before
touching it: it is deliberately NOT coupled to the situations, and the
reasoning for that is the part worth keeping.

## Run this after every change

```
python tools/verify_pd.py
```

Ten checks. **Every check prints how many items it scanned, and a check that
scans zero FAILS** — a silent zero is the exact failure this mod keeps
producing. It locates vanilla by probing a known FILE; if it reports the tree
missing, add your path to `VANILLA_CANDIDATES` rather than ignoring the
degraded run.

It is green as of 2026-08-30. When it goes red, the finding is real until
proven otherwise — but prove it: three of these checks were themselves wrong
before the mod was.

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

**A disaster's panel and icon are found by its KEY, not by its filename.**
`savonarola.txt` holds the key `savonarola_disaster` and ships
`savonarola_disaster.gui` / `.dds`. Name either file anything else and the
panel is simply never loaded — no error, no missing texture, just the
default panel where yours should be. This mod shipped exactly that bug for
an afternoon. `verify_pd.py` check 10 catches it now.

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

Four rules that are easy to get wrong:
- The situation `_desc` key is read by the **engine**, in places far narrower
  than the panel. Keep it narrative; mechanics go on cards, where they can be
  live instead of a paragraph that ages.
- A panel cannot branch on which tag exists. Have the situation write the
  answer into a variable and read it back with `GetVariable('x').GetCountry`.
- **A variable the panel reads must be one the script writes.** A name that
  matches nothing produces no error at all — the widget draws a blank, or a
  zero that reads as a real value, and the panel confidently reports the wrong
  state. `check_panel_variables` in the harness catches it; it was added the
  day a new variable made the risk real, and it is proven against a known
  positive.
- **If the AI is allowed to act outside the step the panel advertises, the
  panel owes the player a state for it.** The Ascension's step 1 was once
  widened to let Prussia march west when Silesia was unreachable, while every
  tooltip still said Silesia. The fix was not a vaguer tooltip; it was
  `PD_phase2_diverted`, a variable whose only job is to let the panel say what
  is actually happening. See `docs/ASCENSION-NOTES.md`.

## Releasing — this repo is NOT what gets published

Steam is fed from a separate folder, so that the development files never reach
players:

```
mod/The Prussian Destiny                      <- this repo, where work happens
mod/My Mod Releases/The Prussian Destiny Release   <- what is uploaded to Steam
```

The release folder holds `in_game/`, `main_menu/` and `.metadata/` only. It must
never contain `CLAUDE.md`, `docs/`, `tools/`, `.claude/` or `.git/`.

**The failure this arrangement invites is publishing a stale copy.** The two
trees are kept in step by hand, so a release can silently ship the previous
version's content while the repo holds the new one, and nothing anywhere
complains. Before every upload:

```
python tools/check_release.py
```

It compares the two trees file by file and refuses to say "up to date" unless
they match, and separately reports any development file that leaked across.

`tools/check_dates.py` reviews every dated gate against the era it belongs
to. **This mod's calendar is shifted** — it tells the 1740-1866 story across
1450-1640 or 1520-1755 — so a historically perfect year can be mechanically
dead and look identical in a diff. That has already happened once: the
Bohemian disaster was first gated ~78 years after the situation it exists to
open. Run it after writing any `current_date`.

`tools/new_disaster.py <key> "<Name>"` scaffolds a disaster with the three
silent traps already handled: the panel named after the KEY, both art slots
and their formats, and the loc conventions. The skeleton is inert until you
remove its `always = no`, so it can land without a test debt.

`tools/art_to_dds.py` converts commissioned art to a game DDS — magenta
key, despill, decontamination, premultiplied downscale, colour bleed. Every
one of those steps is there because leaving it out produced a visible pink
rim; the reasoning is in `../1066 Test Mod/docs/EU5-MODDING-GUIDE.md`.

**Bump the version in BOTH `.metadata/metadata.json` files.** As of 2026-08-30
they both read `4.0.0` while the Steam page had been at `4.1.0` for a release —
the field had simply not been touched, so the in-game launcher and the workshop
page disagreed. It breaks nothing, but it makes "which build is this?"
unanswerable.

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
- `BOHEMIA-DISASTER.md` — the disaster's design, its fairness rules, and a
  correction worth reading before writing anything dated: the first version
  gated it on real-world years and landed ~78 years after the situation it
  was meant to open. **This mod's calendar is shifted; check dates against
  the mod's window, not history's.**

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
