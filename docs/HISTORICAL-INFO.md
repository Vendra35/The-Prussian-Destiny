# The historical_info layer — and which century each phase belongs to

Written 2026-08-31, when every PD event got a `historical_info` box.

## Why the layer exists

`historical_info` is an **event field**, documented at
`in_game/events/readme.txt:33` — "the extra text of the event describing the
historical background". Vanilla uses it 1,656 times across 100 DHE files. It
renders as a separate box inside the event window.

This mod needed it more than most. **PD tells the 1740–1866 Prussian story
between 1522 and 1640**, and until now nothing in the game told the player
that. A Zollverein offer arriving in 1560 simply looked wrong. The box is
where the real date goes, so the event body can stay in the mod's compressed
calendar and the player still knows what is being borrowed.

Mongol Resurgence reached the same conclusion from the opposite direction —
its historical_info boxes were describing the 13th century in a 16th-century
scenario, and the fix was to move the out-of-period material *into* the boxes,
"which is where it belongs anyway" (`MR Debug-and-Test-Results.md:1869`).

## THE THING TO GET RIGHT: only two of the three phases are shifted

This was got wrong on the first pass and caught by the author before it
shipped. Measured against `brandenburg_rise.txt` and `tools/check_dates.py`:

| Phase | Mod window | Real period it tells | Shifted? |
|---|---|---|---|
| **1 — the Ambition** (`pd_brandenburg.1,2,10,100-117`) | 1450–1500 / 1450–1525 | The Baltic struggle: Grunwald 1410, the Prussian Confederation 1440, the Thirteen Years' War 1454–66, Thorn 1466, the secularisation of 1525 | **NO — it sits in its own real period** |
| **2 — the Ascension** (`pd_brandenburg.200-221, 299`) | 1522–1640 / 1648–1755 | Silesia 1740–63, the Zollverein 1834, the Austro-Prussian War 1866 | **yes, by ~200 years** |
| **3 — Blood and Iron** (`pd_brandenburg.300-311`) | 1638+ / 1751+ | Luxembourg 1867, the Ems Dispatch and the Franco-Prussian War 1870, the Empire 1871 | **yes** |

So a phase-1 box must talk about the fifteenth century. Writing Frederick II
and Mollwitz into "The Drums of War" is a period error even though it is a
perfectly good Prussian anecdote — the event is about Brandenburg and the
Teutonic Order in the 1450s, and the Order's real destroyer was Poland.

**Nine phase-1 boxes were drafted with 1740s material and rewritten before
they were applied.** The general rule: read what the event's own situation
file says the event is FOR before deciding which century the box belongs to.

## Both halves, every time

The loc key alone does nothing. MR shipped 31 keys against 25 declarations and
six boxes it had paid to write never rendered
(`MR Debug-and-Test-Results.md:1846`). `verify_pd.py` check 15 is two-directional
and proven against both failures.

## historical_option

`historical_option = yes` marks the historically accurate choice
(`events/readme.txt:87`). It is independent of `historical_info` — MR verified
in game that the box renders with no `historical_option` anywhere, and vanilla
has 398 such events.

It is only meaningful where there is a real choice, so it went on **11 events**,
not all 73. Every one is `.a` except `pd_bohemia.10`, where the historical
answer is `.b`: Ferdinand broke the estates at the White Mountain in 1620 and
abolished their constitution in 1627, and Maria Theresa punished the nobles who
had knelt to a rival in 1741. Both crowns answered with soldiers.

## Coverage

71 of 73 events. The two without boxes are `pd_brandenburg.998` and `.999`,
hidden mechanical events with no title, no description and nothing to say.
