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

**That rule governs the TRIGGER and the framing. It does not govern the
CONSEQUENCES, and reading it as though it did is how the first version came
out toothless — see the correction at the end of this file.** A disaster is
allowed to wreck the country it lands on. Vanilla's do. What it may not do is
know why anyone wants it wrecked.

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

## The trigger: two ways in, and why not one

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

Breadth was the first answer, and it went too wide: paths on `legitimacy < 50`
and `stability < 0` were added, then dropped again once the historical event
below made the crisis certain. Neither had anything to do with the estates, so
a country whose stability had merely dipped would have got "the estates against
the crown" with no estates in it.

**Two ways in, both about the estates:**

1. `PD_boh_estates_aggrieved` — the flag set by `pd_bohemia_dhe.1`. This is the
   one that always holds; see the guarantee section below.
2. **`estate_satisfaction:nobles_estate < 0.5`** — the natural early route, for
   a Bohemia whose nobility is already discontented before the grievance is
   ever formally presented.

Both stay fair. Nothing here is gated on `is_ai`, and the choices that resolve
the crisis live in the disaster, where a player has real agency.

```
can_start = {
	owns = location:prague          # by land, not by tag: BOH, HAB, whoever
	has_ruler = yes
	OR = {
		has_variable = PD_boh_estates_aggrieved       # the guarantee
		AND = {                                       # the natural early route
			country_has_estate = estate_type:nobles_estate
			estate_satisfaction:nobles_estate < 0.5
		}
	}
	in_civil_war = no               # vanilla's own guards,
	has_any_active_disaster = no    # turmoil_in_brandenburg.txt:11-12
	PD_bohemian_era_window = yes    # shared with pd_bohemia_dhe.1
}
fire_only_once = yes
```

`Verified` — `location:prague` exists in `bohemia_area/prague_province`
(`definitions.txt:678`; note it is `prague`, **not** `praha`).
`estate_satisfaction`, `country_has_estate`, `in_civil_war` and `has_any_active_disaster` are all country scope.
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
4. `in_game/gui/panels/disaster/<KEY>.gui` — **named after the disaster KEY.**
   This line originally said `<key>_disaster.gui` was an accepted name and that
   was wrong: vanilla's four `_disaster` files are the ones whose KEY ends in
   `_disaster`. Get it wrong and the panel is never loaded, silently. The mod
   shipped exactly that bug; `verify_pd.py` check 10 catches it now.
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

So the gate is now each mode's actual window, factored into
`PD_bohemian_era_window` and shared with the event that guarantees the crisis. The opening event is chosen **by date** (before 1650 the estates
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


## Guaranteeing it: Bohemia's own historical event

Three natural paths still may all stay shut in a given campaign, which would
leave this written, shipped and never once seen. `pd_bohemia_dhe.1` closes that
gap without rigging anything:

```
dynamic_historical_event = {
    tag = BOH
    tag = HAB          # `tag` is required - 3198 vanilla uses, none without
    from = 1522.1.1
    to   = 1755.1.1
    monthly_chance = 100        # the first month it can
}
trigger = { owns = location:prague  ...  PD_bohemian_era_window = yes }
option  = { add_estate_satisfaction = {
                type = estate_type:nobles_estate
                value = estate_satisfaction_radical_penalty } }   # -0.5
```

**The guarantee is the variable, not the satisfaction hit.** The first version
had the event drop noble satisfaction by `-0.5` and relied on that crossing the
disaster's `< 0.5` threshold. From a full 1.0 that lands on exactly 0.5, and
`< 0.5` is strictly less than — so the "guaranteed" path failed precisely in the
commonest case, a content nobility. The scale is confirmed 0-1 by the defines
(`REBEL_FORT_LOYALTY_ESTATE_SATISFACTION_SCALE = 30 # ... multiplied by
satisfaction 0-1`).

Building a guarantee out of arithmetic against a threshold was the mistake, not
the number — any later tuning of either value would have broken it again, and
silently. So the event now *says* the grievance happened: it sets
`PD_boh_estates_aggrieved`, and the disaster accepts that as a fourth path,
listed first because it is the one that always holds. The satisfaction hit
stays as flavour at `-0.2` and can be retuned freely.

If another disaster is already running in Bohemia the flag simply waits, and
this one starts when that one ends.

**It carries no `is_ai` gate and never names Prussia.** The alternative
considered was Prussia sending an event to an AI Bohemia to force the
conditions; that is the "handicap wearing a costume" this document warns about
in its first paragraph, and it would leave a player Bohemia never seeing the
content at all. A player holding Bohemia gets the crisis too, which is what a
disaster is for - vanilla forces `turmoil_in_brandenburg` on the player the
same way, and the choices that resolve it live in the disaster where the player
has real agency.

The era window lives in `PD_bohemian_era_window` and is called by both the
disaster and this event, so the two cannot drift. Note that factoring it out
silently narrowed `tools/check_dates.py` - the dates left the file the tool knew
about - until its block map was taught the new name. **A refactor can quietly
shrink a checker's coverage**, which is worth a look every time one moves.


## Correction, 2026-08-31 (second pass) — the consequences moved nothing

The disaster shipped, fired, and did not do the job it exists for. Worth
recording in full, because the mistake was not in any line of script.

### What the Ascension's gate actually reads

Measured, not inferred (`triggers.log:3577`), and this is the sentence the
whole design hangs on:

> `defensive_alliance_strength` — "Strength of a defensive alliance, **including
> the nation** with all countries giving defensive support and those that can be
> called in for defensive wars"

So the gate has exactly two terms: **Bohemia's own army, and its allies'
armies.** Tier 2 adds `relative_military_strength`, which is the army again.
Nothing else is in there.

### What the first version did to those terms

| Modifier | Reaches the gate? |
|---|---|
| `global_max_control = -0.1` | no |
| `global_monthly_control = -0.0005` | no |
| `monthly_legitimacy = -0.03` | no |
| `global_manpower_modifier = -0.2` | indirectly, slowly — the pool, not the army in the field |
| `nobles_estate_levy_size = -0.25` | partly, the only one |

And the diet's own choices — `add_legitimacy`, `add_gold`, `add_prestige` —
reach **none** of it. The alliance term, which is the dominant one and the
actual reason a strong Bohemia deadlocks the situation, was never touched by
anything at all.

The crisis ran, the panel filled in, the counters moved, the log was clean, and
Bohemia was exactly as unattackable at the end as at the start.

### The lesson

**A disaster's fairness lives in its trigger. Its usefulness lives in its
consequences. Auditing only the first is how you ship a fair disaster that does
nothing.** The static harness cannot catch this class: every tag was real,
every scope correct, every brace balanced. Only asking "which number that
somebody reads does this move?" catches it — so ask that of any content written
to open a door.

### What it does now

**1. The alliances go first, in `on_start`.** The only thing that can reach the
dominant term. Pattern from `generic_actions/general_religion.txt:195-205`:

```
save_scope_as = PD_boh_crown
every_related_country = {
    type = alliance
    remove_relation = { type = relation_type:alliance
                        first = this  second = scope:PD_boh_crown }
}
```

It is also the history rather than a convenience: in 1618 the Protestant Union
declined to fight for the king the estates had just elected, and in 1741 half
the Bohemian nobility swore to the rival claimant. Nobody stays bound to a
crown that may not be a crown next year. It names no one, and every neighbour
gains the same opening — a player holding Bohemia pays exactly the same price.

It is also the **durable** half: an alliance broken does not come back when the
crisis ends. That matters, because the crisis itself is short — four diets at
24 months is eight years, and Prussia's war cooldown is 60 months in
historical, so barely one war window fits inside it.

**2. The modifier block is english_civil_war's.** Measured across all 32
vanilla disasters: the tool of the trade is **rebels** — `monthly_rebel_growth`
in 9 of them — and a flat "-20% army" sticker appears in none. Rebels tie down
and destroy the army, and the army is what the gate weighs.
`pop_join_rebel_threshold = 0.05`, `monthly_rebel_growth = 0.01`,
`monthly_war_exhaustion = 0.15` and `global_manpower_modifier = -0.33` are
`english_civil_war.txt:47-50` exactly.

### The two branches are priced by DURATION, not by size

The first attempt at fixing the diet charged concession one legitimacy hit
against a bill of gold, manpower and war exhaustion for repression. Nobody
would ever have repressed. **A choice only one side of which is payable is not
a choice**, and the 50/50 `ai_chance` would have been decorative.

| | Concede | Repress |
|---|---|---|
| Now | -10 legitimacy, nobles satisfied | -500 gold, 3 months' manpower, +2 war exhaustion, -2 prestige, nobles angered |
| **Later** | **one permanent stack of `PD_boh_confirmed_privileges`, four by the end** | nothing — all of it recovers |
| Resolution | +20 legitimacy | +30 legitimacy, +20 prestige |

So conceding is a cheap present and an expensive future; repressing is the
reverse. `PD_boh_confirmed_privileges` lives in
`main_menu/common/static_modifiers/PD_modifiers.txt` and carries
`global_crown_estate_power`, `nobles_estate_levy_size` and
`global_levy_size_modifier`, small per stack and permanent — `years = -1` with
`mode = add_and_extend`, vanilla's stacking form at `black_death.txt:915-917`.

**And the key inside it is `modifier =`, not `name =`.** `effects.log`'s usage
string for `add_country_modifier` says `name = name`; vanilla writes `modifier`
**1653** times and `name` **zero**. This mod's own peace treaties already wrote
`modifier`. The wrong key applies nothing and reports nothing — the same silent
family as everything else in this file, and it was written into this very
change before being caught. `verify_pd.py` check 12 catches it now.

Either branch still leaves Bohemia weaker than it was, which is the point: the
opening does not depend on which one the AI picks.

### A trap caught before it shipped

`add_war_exhaustion = war_exhaustion_mild_bonus` would have **reduced** war
exhaustion. The `_bonus` values are negative and the `_penalty` values positive
(`war_exhaustion_mild_bonus = -2`, `war_exhaustion_mild_penalty = 2`), and the
same inversion exists for `estate_satisfaction_*`. Nothing about the wrong one
looks wrong.

### The check that came with it

`verify_pd.py` check 11, "modifier tags": every tag written in the mod's
`static_modifiers` definitions and in each disaster's `modifier = { }` block
must appear in `modifiers.log`. **A tag the engine does not know is applied to
nothing, and reported by nothing** — it sits in the country's modifier list
looking correct and does zero.

It is scanned narrowly on purpose, in the two places where every line is a
modifier tag by construction; the same regex anywhere else would collect
ordinary script keys and cry wolf. Proven against a known positive: planting
`global_manpwer_modifier` in the disaster and `nobles_estate_levvy_size` in the
static modifiers made it fail on both, and only those two.

**It does not catch the bug above, and cannot.** That one was a design error
made entirely out of valid tags. This file is what catches that one.


## First live test, 2026-08-31 — what the game found

Loaded into a 1531 frontloaded save (player Italy, Bohemia holding Prague and
most of Silesia, allied to Hungary and Poland). **The crisis started, and every
new modifier was live on the tooltip** — manpower -33%, monthly rebel growth
+1%, pop join rebels +5%, war exhaustion +0.15, nobles levy -25%. The grievance
path worked: `can_start` showed both "the estates have laid their grievances
before the crown and been refused" and the nobles-satisfaction clause ticked.
`monthly_spawn_chance_unique` rendered as "100.00% chance to appear each
month", confirming the 0-1 scale.

Three faults, all in things nothing static had been looking at.

### 1. 24,378 error lines — every `var:` read was unguarded

```
Failed to fetch variable for 'PD_boh_concessions' due to not being set
Event target link 'var' returned an unset scope
Invalid left side during comparison 'var'
    Script location: common/scripted_triggers/PD_scripted_triggers.txt:640
    common/disasters/PD_bohemian_estates_crisis.txt:64      <- can_end
```

16,254 lines from `can_end` and 8,124 from `on_monthly`, three per evaluation,
across six rotated logs.

**A disaster's `can_end`, `on_monthly` and `on_end` are walked to draw the
disaster's TOOLTIP**, with no country bound and therefore no variables. This is
the same family as the peace-treaty `scope:winner` throws in the decoder: an
effect written for one context, rendered in another.

Vanilla guards every one of its reads — `turmoil_in_brandenburg_end_trigger`
wraps each counter as `AND = { has_variable = X  var:X >= N }`
(`disaster_triggers.txt:707-716`). **This file's comment said the shape was
copied from that trigger. The shape was. The guard was not.** Copying a
vanilla pattern means copying the parts that look like paranoia, because in
this engine they are the parts that were paid for.

Fixed by putting `has_variable = X` beside all five reads. `verify_pd.py`
check 14 now scans the disasters and every scripted trigger they call.

### 2. The event browser printed a raw key

The historical-event list showed the literal text `pd_bohemia_dhe.1.entry`.
**A `dynamic_historical_event` needs `<id>.entry`, and so does every option**
(`<id>.<option>.entry`) — the browser renders that list with no event bound, so
it cannot use `.title` or `.a`, which may carry scope references. Vanilla's
`flavor_ach` alone carries 40 `.entry` keys against 19 `.title`.

The Brandenburg DHEs already had their event-level `.entry` keys and were
missing all eleven **option** ones, so this was not new — it had simply never
been looked at. `verify_pd.py` check 13 covers both levels now.

### 3. The panel does not open

Clicking the disaster icon does nothing. Ruled out, in this order:

| Suspect | Measured |
|---|---|
| filename vs KEY | correct — check 10 |
| BOM on a `.gui` | none (`23 20 54`) |
| unbalanced braces | 49 / 49 |
| GUI errors in the log | **zero**, across all six rotations |
| wrong block names | all four exist in `disasters_common.gui` |
| structure | the 11 `blockoverride` names are **identical** to vanilla's `reform_society.gui` |

So the panel file itself is not obviously wrong, and the standing hypothesis is
fault 1: the END_REQUIREMENTS card calls `GetEndConditions`, which evaluates
the `can_end` that was throwing. **That is a hypothesis, not a finding.** If
the panel still will not open with the flood gone, the next measurement is a
control: open a VANILLA disaster's panel the same way and see whether that
works, which separates "our panel is broken" from "that click is not what
opens it".
