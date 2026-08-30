# The Prussian Ascension — what the script actually does

Read out of `in_game/common/situations/the_prussian_ascension.txt` and the
21 phase-2 events in `in_game/events/situations/PD_events.txt` on 2026-08-30.
Written down so the panel's text can be built from the code rather than from an
impression of it, and so a later session does not have to read it again.

## The three steps

`PD_phase2_current_step` is the state machine. Nothing else advances it.

| Step | Set at | Advances when |
|---|---|---|
| 1 — Silesia | `:122` (on_start) | every location in `silesia_area` is owned by PRU or a PRU subject → `:490` sets step 2 |
| 2 — the western march | `:490` | the same is true of `lower_saxony`, `upper_saxony`, `mecklenburg`, `holstein`, `westphalia`, `hesse` and `rhineland` → `:674` sets step 3 |
| 3 — the great ultimatum | `:674` | ends with the hegemony war; `PD_austria_ultimatum_sent` set `:746`, cleared `:730` |

**Step 1 closes on Silesia and nothing else.** That has never changed and must
not: it is the whole spine of the situation, and the panel promises it in three
places. What changed on 2026-08-30 is how Prussia is allowed to *reach* it —
see the target gate below.

Supporting variables: `PD_phase2_conquest_target` (0 none / 1 held),
`PD_phase2_conquest_target_country`, `PD_phase2_conquest_cooldown` (+1 a month,
gates at >12 and >60), `PD_zollverein_asked` (`:536`),
`PD_phase2_step_stall` (`:823`, +1 a month, zeroed only on a step change) and
`PD_phase2_diverted` (`:835`).

Each transition also fires news: step 1→2 sends `.208` to onlookers and `.209`
to whoever owns the western areas next on the list; step 2→3 sends `.216` to
everyone with a presence in Europe.

**A new situation variable needs a save-migration guard** (`:207-242`). `on_start`
has already run in any campaign that is mid-situation, so a variable added later
simply does not exist there, while `on_monthly` goes on reading and incrementing
it every month for the rest of the game. The guard is two `has_variable` tests at
the very top of `on_monthly`, before anything looks at either one — a no-op in a
new campaign. It also clears `PD_phase2_conquest_target`, because the war block
(`:874`) fires on that flag alone. That was a one-time rescue for existing
saves; the permanent fix is the shared trigger described below. **Do this every time a live situation gains a variable.** The panel
side needs no guard as long as its "normal" branch is the `Not(EqualTo(x, 1))`
one, because an unset variable reads as zero there.

## The target gate, and why it has three tiers

The AI picks its next war in one `ordered_neighbor_country` block (`:771`).
The test itself is **not** inline: it is the scripted trigger
`PD_ascension_valid_target` (`scripted_triggers/PD_scripted_triggers.txt:491`),
called in the target's scope from two places that must never disagree — the
picker (`:793`) and the fallback that re-validates the stored target (`:860`).

**Why one copy and not two.** Selection and declaration are 12 to 60 months
apart, so the fallback has to apply exactly the test that picked the target,
or a target that gains an ally in between still gets attacked. Mongol
Resurgence found that first (`MR_mongol_resurgence.txt:534`, audited
2026-08-28) and fixed it by duplicating the gate — and its two copies then
drifted, leaving comments that said `1.1` above code that said `0.7`. One
definition, two call sites, no drift.

The trigger deliberately contains no `prev`: it is evaluated at different
nesting depths in the two call sites, and `prev` counts scope-changing hops.
The `prev`-using lines (`has_truce_with`, `is_subject_of`) stayed behind in
the situation.

Until 2026-08-30 the gate was a single hard test:

```
defensive_alliance_strength < c:PRU.offensive_alliance_strength
```

**That gate can be permanently unsatisfiable, and when it is, the situation
stops dead with no error anywhere.** A Silesia held by Bohemia with a couple of
allies fails it for the whole game, so step 1 never closes, so nothing else in
the situation ever runs. It was seen live: Prussia sat on step 1 while the
panel cheerfully reported "Step 1 — Silesia · In progress".

The first attempt at a fix widened step 1's *target areas* to include
Mecklenburg and both Saxonies. That traded the deadlock for a lie — Prussia
marched west while every tooltip in the panel said Silesia. Do not do that
again. The gate is the thing that is wrong, not the map and not the step.

What is there now:

| Tier | Opens at | Test |
|---|---|---|
| 1 — the calculation | always | the target's whole defensive network is weaker than PRU's offensive one |
| 2 — the gamble | `PD_ascension_stall_gamble` (36 buff / **120** hist) | the coalition may outweigh ours by **1.5x** (`defensive_alliance_strength < { value = c:PRU.offensive_alliance_strength multiply = 1.5 }`) **and** we still out-gun the target's own army (`relative_military_strength < 1.0`) |
| 3 — the diversion | `PD_ascension_stall_divert` (72 buff / **240** hist) | step 1's target areas widen west, **and `PD_phase2_diverted` is set so the panel says so**. Cleared again the month a Silesia-holder passes the gate, with the stall pushed back to 120 so the flag cannot flap |

Tier 2 is Frederick in December 1740: he did not attack Austria because he
out-weighed its alliance network, he attacked because he out-gunned its army
and bet the allies would be slow.

**It does not stop counting the allies** - a first version did, and would have marched on a Bohemia with Poland behind it without noticing. It raises what Prussia will
accept from that coalition, from 1:1 to 1.5:1, and still demands that Prussia
out-gun the enemy's own army. Both halves must hold.

Being conservative here is free, and that asymmetry should drive any future
tuning: tier 3 opens the west at 240 months regardless, so a tier 2 that
rarely fires cannot bring the deadlock back - while a tier 2 that fires too
eagerly can lose Prussia the campaign.

`Verified — a value block on the right of a trigger comparison`: `gold <= { value = scope:actor.monthly_income_trade_and_tax multiply = 4 }`,
`generic_actions/church_power.txt:75`; again at `coup_attempt_actions.txt:225`
and `situations/italian_wars.txt:428`. Decimal multipliers are attested at
`hundred_years_war.txt:1393` (`multiply = 0.05`).

Tier 3 is a detour, not a second way to finish step 1: expanding west makes
Prussia stronger, tier 2's test eventually flips, and Prussia turns back to
Silesia. **No tier changes what closes step 1.**

## The ordering is a second gate, and it was pointing the wrong way

`limit` decides who is *eligible*; `order_by` decides who is taken *first*.
Those are easy to conflate, and conflating them cost this situation its
objective.

The picker sorts `num_locations` with `multiply = -1`, i.e. **smallest first**.
That was chosen so a big untouchable neighbour could not stall the loop — but
it never could: an ineligible country is filtered out by `limit` before the
sort ever sees it. What smallest-first actually did was bury the objective.
Step 1 closes on Silesia alone, and Silesia's holder is normally the biggest
country on the list, so it sorted behind every homeland squatter and — once
diverted — every small western state. Silesia would have been taken last, if
ever.

So a Silesia-holder now gets `add = 100000` while on step 1, which puts it
ahead of anything size could produce. Everything else keeps smallest-first:
the gate has already discarded the unwinnable, so among what remains the easy
war before the hard one is right.

`Verified — a conditional order_by`: `in_game/common/country_interactions/hre.txt:2143-2153`
uses `value = population` with `if { multiply = 5 }` and `else_if { multiply = 2 }`;
`add` inside `if` at `generic_actions/italian_wars.txt:730`. `any_neighbor_country`
is `triggers.log:1487`, country scope, and takes its triggers directly with no
`limit =` wrapper.

**The general rule, for any railroad:** whenever a picker has both a filter and
a sort, check that the sort cannot push the win condition to the back of the
queue. A gate that says "yes" and an ordering that says "but not you first" look
identical from outside — nothing errors, the AI simply never does the thing the
situation is about.

`Verified — relative_military_strength, EU5-Vanilla-Script-Docs/triggers.log:9910`,
country scope, ratio scale where 1.0 is parity; vanilla writes `value < 0.5` and
`value < 0.3` at `in_game/common/country_interactions/lend_unit_to_ally.txt:157`
and `:178`. The sibling `relative_defensive_alliance_strength`
(`triggers.log:9904`) exists too but is used exactly once in vanilla and its
denominator is not documented, so it was left alone.

There is also a **fourth** escape that predates all of this and is easy to miss:
`:245` onward, gated on the `PD_the_prussian_ascension_auto_conquest_yes` game
rule, simply hands PRU every AI-owned location in Silesia and the western areas
after 1632 (frontloaded) or 1745 (strict). Note `owner = { is_ai = yes }` — it
never takes a player's land, and neither may anything added here.


**The thresholds scale with the war-pacing rule, and must keep doing so.** The
war cooldown is 12 months under `BRA_buff_enabled` and 60 without it, so a flat
threshold means two different things:

| Mode | cooldown | 120 months is |
|---|---|---|
| Historical / Vanilla | 60 | 2 missed war windows |
| Terminator (`BRA_buff_enabled`) | 12 | **10** missed war windows |

Terminator is the mode labelled "fast aggressive expansion" and it was the more
patient of the two. Both numbers now live in `PD_ascension_stall_gamble` and
`PD_ascension_stall_divert` (`PD_scripted_triggers.txt`) rather than inline, so
there is one place to change them. `has_game_rule` is scope-none
(`triggers.log:4830`), so those triggers work from a country scope and from the
situation scope alike.

## The 21 events

Sixteen carry a single option and exist to tell somebody what happened:
`.200` The Silesian Question · `.201` The Sleeping Giant Awakens ·
`.202` The Shadow of Prussia · `.204` The Birth of the North German
Confederation · `.205` Master of the North (`form_country`) · `.206` The Eagle
Repelled · `.207` Halted in our Tracks · `.208` The Fall of Silesia ·
`.209` The Zollverein's Shadow · `.212` The Zollverein is Rejected ·
`.213` The Northern Menace · `.216` The Gathering Storm · `.217` The Brothers'
War · `.220` The Upstart Crushed · `.221` The Ambition Shattered ·
`.299` The Prussian Ascension.

Five offer a choice:

| Event | Title | `ai_chance` weights |
|---|---|---|
| `.203` | Blood and Iron | **50 / 0** — declares war |
| `.210` | The Zollverein Proposal | **1000 / 0** — accepts |
| `.211` | A Northern State Joins the Zollverein! | **100 / 0** |
| `.214` | The Northern Insolence | **100 / 0** |
| `.215` | The Emperor's Ultimatum | **100 / 0** — declares war |

## The finding worth putting on the panel

**Every branching event in this situation is weighted N against 0.** The AI
takes the first option every single time, in all five. The second option is not
hidden from it — there is not one `trigger = { is_ai = no }` gate anywhere in
the phase-2 range — it is simply weighted to zero and therefore never chosen.

So the AI's path through the Ascension is deterministic: it takes Silesia, it
offers the Zollverein and accepts every answer that keeps it moving, it presses
the insolence, and it answers the Emperor's ultimatum with war. The choices in
those five events exist for a human sitting in one of those seats.

That is the honest "How the AI plays this" section, and it is close to what
Blood and Iron turned out to be — one weighted branch, always taken the same
way — only five times over instead of once.

## For the panel

- The road card wants the three steps above, with their real advance
  conditions, not a paraphrase.
- The target row wants `PD_phase2_conquest_target_country`, guarded on
  `PD_phase2_conquest_target = 1`.
- The step-1 rung has **three** states, not two: done, in progress, and
  diverted (`PD_phase2_diverted = 1`). The third exists so that the panel can
  never again promise Silesia while the armies march somewhere else. If a
  future change lets the AI act outside the step it advertises, that change
  owes the panel a state — not a quieter tooltip.
- `PD_zollverein_asked` and `PD_austria_ultimatum_sent` are the two sub-lines:
  they say whether the offer has gone out and whether the ultimatum has been
  sent.
- The conquest cooldown is AI pacing, not player-facing. Keep it out of the
  panel or put it in a tooltip.
