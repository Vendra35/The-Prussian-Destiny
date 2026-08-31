# The Bohemian Estates Crisis — design

A disaster for whoever rules Bohemia. Written 2026-08-31.

**It exists as content, not as a lever.** Nothing in it mentions Prussia, the
Ascension, or Silesia, and it carries no `is_ai` gate — the same rules apply to
a player and to the AI. If it happens to give Prussia its opening, that is
because the Ascension's target gate is a strength ratio and Bohemia got weaker.
Emergent, not scripted. **Do not couple it to the situation later**, however
tempting: four vanilla disasters do read `situation:` state, so it would be
attested — but a crisis that fires because someone else is stuck is a handicap
wearing a costume, and a Bohemia player would feel it immediately.

## Why Bohemia, and why these dates

The Ascension's own failsafe dates bound each timeline
(`the_prussian_ascension.txt:254,259`): frontloaded hands Silesia over after
1632, strict after 1745. So the situation is live roughly 1522-1637 and
~1640-1750. Each window contains one real Bohemian catastrophe:

| Timeline | Ascension window (measured) | Disaster gate | Anchor |
|---|---|---|---|
| Frontloaded | 1522.3.9 - ~1637 | 1522-1640 | **The Bohemian Revolt, 1618-1620.** The estates threw the royal governors out of a window in Prague on 23 May 1618, deposed their king and elected Frederick V. Ferdinand broke them at the White Mountain on 8 November 1620, and the Verneuerte Landesordnung of 1627 ended Bohemian self-government. |
| Strict historical | 1648.1.1 - ~1750 | 1648-1755 | **The invasion of 1741-42.** A Franco-Bavarian army took Prague and Charles Albert was crowned King of Bohemia in December 1741, while Maria Theresa fought for her inheritance. |

The second one is worth stating plainly: in strict mode this disaster is not a
convenience for Prussia, it **is the historical reason Silesia was takeable**.
Austria lost the province because it was being dismembered from two directions
at once. The mod is not inventing an opening; it is supplying the one that
actually happened.

## The trigger: three ways in, and why not one

`ruler_religion` is not a trigger (checked against `triggers.log`), so the
religious framing of 1618 cannot be tested directly.

The first draft used `legitimacy < 50` **alone**, and that was a mistake worth
recording: legitimacy sits near the top for a stable monarchy, so a single gate
on it risks content that is written, shipped and never once seen. **No vanilla
disaster gates on one number.** Measured:

| Disaster | Gate |
|---|---|
| `succession_crisis` | `legitimacy < 50` **and** `stability < 10`, but only when there is no heir / a regent / a bad heir — otherwise `stability < 0` |
| `peasants_war` | `stability < 0` + `estate_satisfaction < 0.5` + `war_exhaustion > 0` |
| `court_and_country` | `estate_power >= 0.25` **or** `societal_value < -50` |
| `aspiration_for_liberty` | `stability < 20` + literacy + a parliament clause |

So there are three paths now, any one of which opens it:

1. **`estate_satisfaction:nobles_estate < 0.5`** — the one this disaster is
   actually about. It is the ESTATES against the crown, and the first gate
   never once asked what the estates thought.
2. `legitimacy < 50` — the crown's right to rule is questioned.
3. `stability < 0` — the realm is ungovernable.

All three stay fair. A Bohemia that keeps its nobles content, its crown secure
and its realm stable never sees this at all — the player's own play decides it,
which is the difference between content and a handicap.

```
can_start = {
	owns = location:prague          # by land, not by tag: BOH, HAB, whoever
	has_ruler = yes
	legitimacy < 50                 # 0-100 scale; vanilla uses <50, <40, <25
	in_civil_war = no               # vanilla's own guards,
	has_any_active_disaster = no    # turmoil_in_brandenburg.txt:11-12
	<timeline date window>
}
fire_only_once = yes
```

`Verified` — `location:prague` exists in `bohemia_area/prague_province`
(`definitions.txt:678`; note it is `prague`, **not** `praha`).
`legitimacy`, `in_civil_war`, `has_any_active_disaster` are all country scope.
`monthly_spawn_chance_unique = 1` is `main_menu/common/script_values/default_values.txt:1212`.

## The shape

Vanilla's own Brandenburg disaster is the pattern to copy
(`turmoil_in_brandenburg.txt`, end trigger at `disaster_triggers.txt:707-716`):
two counter variables, moved by the player's choices, and the disaster ends
when either crosses its threshold.

| Piece | Content |
|---|---|
| `modifier` | control, legitimacy and manpower penalties while it runs — the weakening |
| `on_start` | opening event to the owner (which one depends on the timeline), news to the German neighbours |
| choices | **concession** raises `PD_boh_concessions`, **repression** lowers `PD_boh_repression` |
| `can_end` | either counter past its threshold, or the crown is lost |
| `on_end` | resolution event, variables cleaned up |

Two counters rather than one so that both answers are real: buying the estates
off ends it with the crown weakened but the realm intact; crushing them ends it
with the realm cowed and the treasury spent. Neither is the "correct" answer.

## Fairness rules this must keep

1. `can_start` never names PRU, the Ascension, or Silesia.
2. No `is_ai` gate anywhere in the disaster or its events.
3. The Ascension is never told the disaster is running.
4. Every event offers the player a real choice, and handling it well ends it
   early. The AI takes whichever branch its `ai_chance` favours, and those
   weights should NOT be N-against-zero the way the situation's are — this is
   content, and the AI should vary.

## Build order

1. `in_game/common/disasters/PD_bohemian_estates_crisis.txt` + its end trigger
2. Events — opening (×2, one per timeline), the choice events, resolution
3. Localisation
4. `in_game/gui/panels/disaster/PD_bohemian_estates_crisis_disaster.gui`
   (37 of 37 vanilla disasters ship a panel; `<key>_disaster.gui` is an
   accepted name)
5. Illustration, `gfx/interface/illustrations/disaster/`
6. Harness: raise the relevant `min_count`s in the same change


## Correction, 2026-08-31 — the first windows were unusable

The first draft gated this at **1600-1645** and **1725-1775**, chosen from the
real calendar. Both are roughly **78 years after their situation can even
start** (`PD_events.txt:1007,1016` set the floors at 1522.3.9 and 1648.1.1),
and sit against the auto-conquest failsafe that ends the era at 1632 and 1745.
The crisis could only ever have arrived once the story it was meant to open was
finished — and in strict mode the Ascension may well have ended first.

The error was anchoring on the almanac. **PD's calendar is already shifted**: it
tells the 1740-1866 Prussian story between 1522 and 1637. Content written for it
has to follow the mod's chronology, not the real one.

So the gate is now each mode's actual window, and `legitimacy < 50` does the
real deciding. The opening event is chosen **by date** (before 1650 the estates
rise, after it a rival is crowned) rather than by game rule, so the text suits
whatever century it fires in even if a campaign runs long or short. Neither
event names a year, only a month, which is what makes that possible.

**The general lesson, worth carrying to 1066:** when a mod moves its own
timeline, every dated thing written for it must be checked against the *mod's*
window, not history's. A date that is historically perfect and mechanically
dead looks exactly like a date that works, and nothing errors.


## Art: both files are named after the KEY, not the file

Measured 2026-08-31, and this mod got it wrong first time:

| File | Key inside it | Panel and icon |
|---|---|---|
| `savonarola.txt` | `savonarola_disaster` | `savonarola_disaster.gui` / `.dds` |
| `ambrosian_republic.txt` | `ambrosian_republic_disaster` | `ambrosian_republic_disaster.gui` / `.dds` |
| `reform_society.txt` | `reform_society` | `reform_society.gui` / `.dds` |

The disaster `.txt` has **no** `icon` field — only `image`, which is the wide
illustration. The icon is found by convention from the key, with `_default.dds`
as the fallback.

This shipped as `PD_bohemian_estates_crisis_disaster.gui` for the key
`PD_bohemian_estates_crisis`. **The panel would never have loaded** — no error,
no missing texture, just the default panel where the authored one should be.
The icon was missing outright and would have fallen back to `_default.dds`.
`verify_pd.py` check 10 now catches both, proven against that exact bug.

Two art slots, two formats, both measured across every vanilla file:

| Slot | Path | Format |
|---|---|---|
| Illustration (`image =`) | `in_game/gfx/interface/illustrations/disaster/<key>.dds` | 1080x440, 11 mips, DXT1, 317512 bytes (22 of 32; 9 are DX10, 1 DXT5) |
| Icon (by convention) | `main_menu/gfx/interface/icons/disasters/<key>.dds` | 128x128, 8 mips, DXT5, 22000 bytes (40 of 40) |

The icon format is identical to this project's situation icons, so the same
conversion works for both. Note the illustration is an **opaque banner** — do
not ask for a magenta key when commissioning one, which is a habit worth
breaking from the icon workflow; magenta belongs only where transparency does.
