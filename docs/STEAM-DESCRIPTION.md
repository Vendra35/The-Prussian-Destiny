# The Steam page — what goes where, and the text itself

The workshop page lived only on Steam until 2026-08-31, which meant a release
could not tell you what the previous one had said. 4.1.0's notes had to be
pasted back in by hand from the live page to write 4.3.0's. This file is so
that does not happen again.

## Two fields, two formats. They are not interchangeable.

| Field | Format | What it holds |
|---|---|---|
| **Description** (Edit title & description) | **BBCode** — `[h1]`, `[h2]`, `[list]`, `[*]`, `[b]`, `[i]` | The page body. Its top is the "What's New" section, which is REPLACED every release. |
| **Change Notes** (posted with the upload) | **plain text**, `*-` bullets, no markup | The full changelog for that one version. Accumulates forever; nothing is ever removed. |

Pasting BBCode into the change notes field prints the tags literally. Pasting
plain text into the description loses every heading.

## The rule for "What's New", which exists because of 4.1→4.3

Three releases landed within about 24 hours, and the description's What's New
is overwritten each time, so the first two would have vanished from the front
page before anyone read them. Most visitors never open the change-notes tab.

So the section **demotes** rather than replaces:

- the **current** release gets full bullets
- the **previous two** get one line each under `📌 Also recent:`
- anything older falls off — it is in the change notes

Next release, 4.3.0's bullets become one line, it goes to the top of *Also
recent*, and 4.1.0 falls off. The section never grows.

## At release time, produce BOTH

Do not hand over one and leave the other. A release needs:

1. the **change notes** for the new version, plain `*-` format
2. the **whole description block** in BBCode, with What's New rewritten and
   Also recent demoted
3. this file updated with both, so the next release can read them

---

# Current description block — 4.3.0

```
[h1]The Prussian Destiny 4.3.0:[/h1]

[h2]🔧 What's New in 4.3.0:[/h2]
[list]
[*] [b]Added:[/b] [b]The Bohemian Estates Crisis[/b] — the mod's first disaster, and it can happen to you. Whoever holds Prague eventually falls out with their own estates over who is actually entitled to govern. The realm's alliances lapse the same month, rebels grow, and a third of the manpower goes unavailable. Every two years the estates convene and you answer: [b]confirm their privileges[/b] — cheap today, and permanent, deepening up to Four Charters Confirmed and marked until the end of the game — or [b]answer them with the army[/b], which costs gold, men and patience and leaves nothing behind. Four of one answer ends it; the two are never added together. Both endings pay you for surviving, and losing Prague ends it and pays nothing. No part of it is gated on the AI, so a human Bohemia faces exactly the same crisis on exactly the same terms.
[*] [b]Added:[/b] A [b]history box[/b] under every event in the mod — all 71 of them — and a marker on the 11 choices history actually made. This mod tells the 1740–1866 story between 1522 and 1640, and until now nothing in the game said so. The event now speaks in the compressed calendar while the box underneath tells you what really happened and when: the Zollverein is 1834, Blood and Iron is a speech to a hostile budget committee on 30 September 1862, and the Empire was proclaimed at Versailles on 18 January 1871 because the first Hohenzollern had crowned himself exactly a hundred and seventy years earlier.
[*] [b]Fixed:[/b] The historical events list showed raw keys instead of event names, on all twelve of the mod's historical events.
[*] [b]Fixed:[/b] Three characters that had died to a codepage and were being shown to players — "K?nigsberg" in Brandenburg's opening event, "Deutschland ?ber alles" in a Franco-Prussian War option, and a mangled dash in the hegemony war goal.
[*] [b]Changed:[/b] Brandenburg's opening option no longer echoes a slogan it has no business echoing, and is no longer four and a half centuries early. It now reads "Für die Mark und das Haus Hohenzollern!"
[/list]

[h2]📌 Also recent:[/h2]
[list]
[*] [b]4.2.0[/b] — All three situation panels rebuilt to read live from the mod's own variables, each situation given its own icon, and a map-mode tag bug fixed that had been flooding the error log.
[*] [b]4.1.0[/b] — Two ways Stage 1 could deadlock forever, both closed: a third power annexing the Teutonic Order, and the PRU tag already existing as someone else's vassal. Plus the Hohenzollern line given its real rulers at their real dates.
[/list]

[i]"Prussia is not a state with an army, but an army with a state."[/i]
--------- [img]https://i.imgur.com/5EFfZ8A.gif[/img] ---------
[hr][/hr]

[h2]👑 THE THREE STAGES OF DESTINY[/h2]
[list]
[*] [b]Stage 1: The Foundation[/b] — Begins after the Turmoil in Brandenburg. Not a simple conquest phaplomatic and military struggle between Brandenburg and the Teutonic Order. The victor subjugates theloser into a Fiefdom, mirroring the authentic historical power shift. Includes a failsafe if the AI stalls.
[*] [b]Stage 2: The Ascension[/b] — Post-Reformation. Prussia strikes wealthy Silesia and Saxony. Introduces custom [b]Zollverein Diplomacy[/b] to peacefully vassalize the North German minors, culminating in the [b]North German Confederation[/b].
[*] [b]Stage 3: Blood & Iron[/b] — The finale. Navigate the Franco-Prussian War and achieve the unification of the [b]German Empire[/b].
[/list]
Whoever holds Prague also gets a story of their own: [b]The Bohemian Estates Crisis[/b], the crown against its own diet, with no AI-only gates and real consequences either way.

[hr][/hr]
[h2]⏳ Pacing — read this before you panic[/h2]
Nothing fires on day one. Stage 1 ignites around the [b]1370s[/b], right after vanilla's 'Turmoil in Brandenburg' resolves — if the early game seems quiet, the diplomatic board is just being set.

And no, Prussia will [b]not[/b] eat the HRE by 1500. Expansion is hard-capped by script: after securingts time on economy and drill, and the real growth only begins after the Reformation. A calculated rise,not map painting.

[hr][/hr]
[h2]⚙️ Game Rules[/h2]
The mod is built to make [b]AI Prussia a formidable end-game boss[/b], and is fully playable as Prussia yourself. Everything is toggleable in the Game Rules menu:
[list]
[*] [b]Prussian Military Buffs[/b] — [b]Historical & Balanced[/b] (default) for a fair, realistic campaign. [b]Terminator[/b] turns the AI into an apocalyptic threat. (Not recommended 💀)
[*] [b]Timeline[/b] — [b]Dynamic & Frontloaded[/b] accelerates the Prussian content into the mid-game. [b]Strict Historical[/b] locks every milestone to its authentic date for a long-burn campaign.
[*] [b]Auto-Consolidation[/b] — failsafes that force historical borders (1499 for Stage 1, 1632 for Staestiny cannot be denied.
[*] [b]Blood and Iron Mechanics[/b] — toggle Stage 3's events and diplomatic tension.
[/list]

[hr][/hr]
[h2]📦 Recommended Mods[/h2]
Play with my [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3678585677]Vanilla+ Historical Immersion & Essential QoL[/url] collection for the intended experience.
[list]
[*] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3675113573]Brandenburg Country Pack[/url] — [b]mandatory[/b], so the AI survives the early disaster and lets this mod take the wheel.
[*] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3668193813]National Destinies - Formables Content[/url] — highly recommended for its bureaucracies and concepts.
[/list]

[hr][/hr]
[h2]🤝 Compatibility & Credits[/h2]
[list]
[*] Uses the vanilla EU5 Situation system. Modifies the vanilla alliance file via [b]TRY:REPLACE[/b], so other mods touching it will not crash the game.
[*] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3599962922]North German Federation[/url] — credits for the NGC foundation.
[*] [b]🇨🇳 中文翻译:[/b] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3599706198]Chinese localization[/url], by 牛奶大魔王.
[*] [b]Known issues:[/b] none right now — tell me if something breaks.
[/list]

[h2]My Other Mods[/h2]
[list]
[*] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3721031562]REAI: Rational Empire AI[/url]
[*] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3723654962]REAI: Army & Manpower Overhaul (AAMO)[/url]
[*] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3774990167]Mongol Resurgence[/url]
[/list]

[hr][/hr]
[b]What I am working on next:[/b] a full total conversion that moves the start date to [b]1066[/b] — the whole map rebuilt for the eleventh century, with its own countries, rulers, borders and events. A large project and a long build; no date announced. I will post here when it is ready.

[hr][/hr]
[i]"The era of fractured princes is over. The age of Berlin has begun. Are you ready to face the Destiny?"[/i]

---

# Change notes

## 4.3.0 — 2026-08-31

```
🔧 UPDATE 4.3.0:

*- Added: The Bohemian Estates Crisis — the mod's first disaster, and it can
happen to you. Whoever holds Prague eventually faces their own estates: the
crown and the Landtag fall out over who is actually entitled to govern, and
neither can rule without the other. It is not scripted around Prussia, carries
no AI-only gate, and a human Bohemia gets exactly the same crisis on exactly
the same terms.

It opens with the Defenestration of Prague or, in a later campaign, with a
rival crowned in the capital while the nobility decides which king to obey.
The realm's alliances lapse the same month — nobody stays bound to a crown
that may not be a crown next year — rebels grow, and a third of the manpower
goes unavailable. Every two years the estates convene again and you answer:

  · Confirm their privileges. Cheap today, and permanent. Every charter
    signed replaces the last with a deeper one — up to Four Charters
    Confirmed — and it is marked until the end of the game. Ending the
    crisis does not lift it. Nothing does.
  · Answer them with the army. Expensive today — gold, standing manpower,
    war exhaustion, prestige, and a nobility that remembers — and none of
    it permanent. What is spent can be earned back.

Four of one answer ends it; the two counters are never added together. Both
endings hand out a fifty-year standing bonus, because surviving a disaster
should be visible. Losing Prague ends it too, and gives nothing.

The AI is weighted evenly between the two answers and is deliberately given
no historical option here, so an AI Bohemia will show you both roads across
different campaigns.

One consequence worth knowing: a Bohemia in the middle of this is a Bohemia
without allies and without an army, which is very often the opening Prussia
needed for Silesia. That is emergent, not scripted — the Ascension is never
told the crisis is running. It is also what actually happened. Austria lost
Silesia in 1740 because it was being pulled apart from two directions at once.

*- Added: Historical context on every event in the mod. All 71 now carry a
history box under their description, and 11 mark the choice history actually
made. This matters more here than in most mods, because The Prussian Destiny
tells the 1740–1866 story between 1522 and 1640 and nothing in the game ever
said so. Now the event speaks in the mod's compressed calendar and the box
underneath tells you what really happened and when — that the Zollverein is
1834, that Blood and Iron is a speech to a hostile budget committee on 30
September 1862, that the Empire was proclaimed at Versailles on 18 January
1871 and the date was chosen because the first Hohenzollern had crowned
himself King in Prussia exactly a hundred and seventy years earlier.

The history is real history, checked against each event's own date window.
Stage 1 is the only part of this mod that sits in its own century — the
Baltic struggle of Grunwald, the Prussian Confederation and the Second Peace
of Thorn — and its boxes say so rather than borrowing Frederick II.

*- Fixed: Three characters had died somewhere in this mod's history and the
game was printing the damage. The Hohenzollern opening event read
"K?nigsberg", a Franco-Prussian War option read "Deutschland ?ber alles", and
the hegemony war goal had a question mark where a dash belonged.

*- Fixed: Every historical event in the mod was missing the localisation key
the event browser uses, so the historical events list showed raw keys like
"pd_bohemia_dhe.1.entry" instead of the event's name. This affected all twelve
of them, at both the event and the option level.

*- Changed: Brandenburg's opening event had an option line reading "Ein Volk,
ein Reich, ein Schicksal!" — the construction of a slogan that has no business
in this mod, and four and a half centuries early for a quarrel between an
electorate and a crusading order. It now reads "Für die Mark und das Haus
Hohenzollern!"

*- Note for translators: this update adds 136 new localisation keys and
changes 7 existing ones. No keys were removed, so existing translation submods
will not break — the new disaster and the history boxes will simply appear in
English until translated.
```

## 4.2.0 — 2026-08-30

```
🔧 UPDATE 4.2.0:

*- Reworked: All three situation panels have been rebuilt from the ground up.
Each one now shows what is actually happening inside its situation, read live
from the mod's own variables instead of described in a paragraph:

- The Prussian Ambition opens with a balance bar between Brandenburg and the
Teutonic Order, and a Standings card naming which side is currently allowed to
act. The score behind it is no longer a mystery — hovering it now states the
exact formula (army strength, monthly trade and tax income, and one fifth of
prestige, recomputed every month), and that a tie counts as Brandenburg's.

- The Prussian Ascension opens with a three-step meter — Silesia, the Western
March, the Great Ultimatum — and a road card showing which step is done, which
is current, and what closes each one. It also shows whether the Zollverein has
been offered, whether the ultimatum has gone to the Emperor, and which country
is currently being worked against.

- Blood and Iron opens with a tension bar carrying the four crisis thresholds at
25, 50, 75 and 100, each explaining what it fires. Two lists at the foot of the
panel show who would actually march on each side, taken from the game's own
will-join calculation.

*- Added: Every panel now carries a Historical Context card and a "What We Can
Do" card. The history is real history — Tannenberg and the 1525 secularisation
for Stage 1, Silesia 1740 and the Zollverein for Stage 2, the Ems Dispatch for
Stage 3. "What We Can Do" has a section for each seat you might be sitting in,
plus a section on what the AI actually decides, written by counting the event
weights rather than describing them.

*- Added: Each situation now has its own icon. All three previously shared one
image — the Kingdom of Prussia arms, which was also anachronistic on Stage 1,
a quarrel between an electorate and a crusading order in the 1400s.

*- Fixed: A tag reference bug in all three situations' map-mode blocks. Those
blocks run for every location on every redraw, so once Prussia became the North
German Confederation the game's error log filled at thousands of lines a minute.
Harmless to your save, but it slowed logging and buried real errors.

*- Fixed: The Empire's proclamation tooltip was missing a word. A formatting tag
without a space after it was swallowing the word behind it, so the End
Requirements read "ready to proclaim the Empire" instead of "the German Empire".

*- Fixed: All five peace treaties were missing the localisation key the game
uses for a treaty's name, so anything asking for one printed the raw key
(PD_blood_and_iron_proclaim_germany) instead of "Proclaim the German Empire".

*- Note for translators: this update adds 69 new localisation keys and changes
6 existing ones. No keys were removed, so existing translation submods will not
break — the new panel text will simply appear in English until translated.
```

## 4.1.0 — 2026-08-29

Recovered from the live Steam page 2026-08-31; this version's work predates the
repository's current history.

```
🔧 UPDATE 4.1.0:

*- Fixed a critical bug in the Prussian Ambition situation (Stage 1) where the
situation could get permanently stuck if the Teutonic Order was fully annexed by
a third-party country (e.g. Poland) before Brandenburg won the historical
struggle. Previously, both the situation's end conditions and its automatic
territory-transfer logic assumed the Teutonic Order would still exist when the
situation resolved, so if a third country wiped them out first, Brandenburg
could never receive the core Prussian provinces (Danzig, Lower Prussia,
Pomerania), the situation would never end, and Stage 2 (and eventual Prussia
formation) could become permanently blocked.

- This update adds a proper fallback: if the Teutonic Order is destroyed by
anyone other than Brandenburg, the mod now automatically transfers the AI-held
core Prussian territories to Brandenburg (once the usual game-rule and date
requirements are met) and correctly ends the situation afterward, allowing the
storyline to progress into Stage 2 as intended.

*- Fixed a critical bug in the Prussian Ambition situation (Stage 1) where
Brandenburg or the Teutonic Order could become permanently unable to form
Prussia if the PRU tag already existed as a vassal of an unrelated third-party
country (e.g. Poland) before either side won the historical struggle.
Previously, the formation events only checked whether the Teutonic Order still
existed and was Brandenburg's vassal (or vice versa) — they had no awareness
that Prussia itself could already be on the map under someone else's control,
so form_country would silently do nothing once that tag was taken.

- This update adds a proper fallback: if PRU already exists and is a subject of
any country — walking the full overlord chain to correctly handle multi-layered
vassalage (e.g. a vassal of a vassal) — its true top overlord now automatically
annexes it before the formation logic runs, clearing the tag so Brandenburg (or
the Teutonic Order, in the mirrored historical branch) can properly form Prussia
afterward. The fix is applied symmetrically to both sides of the historical
struggle, so it resolves correctly regardless of which country ultimately
prevails.

*- Added: A chain of historical succession events. When Prussia (or its later
North German Confederation form) is controlled by the AI or the player, a series
of one-time events now installs the actual historical Hohenzollern rulers —
Joachim I, Joachim II, Johann Sigismund, Friedrich Wilhelm "The Great Elector,"
and Friedrich I — at the calendar years they historically held power, rather
than leaving the throne to a randomly generated heir. Each event only fires
within its ruler's real historical window, so the correct figure appears
regardless of how early or late your playthrough reaches that stage.
```
