# The Prussian Ascension — what the script actually does

Read out of `in_game/common/situations/the_prussian_ascension.txt` and the
21 phase-2 events in `in_game/events/situations/PD_events.txt` on 2026-08-30.
Written down so the panel's text can be built from the code rather than from an
impression of it, and so a later session does not have to read it again.

## The three steps

`PD_phase2_current_step` is the state machine. Nothing else advances it.

| Step | Set at | Advances when |
|---|---|---|
| 1 — Silesia | `:122` (on_start) | every location in `silesia_area` is owned by PRU or a PRU subject → `:443` sets step 2 |
| 2 — the western march | `:443` | the same is true of `lower_saxony`, `upper_saxony`, `mecklenburg`, `holstein`, `westphalia`, `hesse` and `rhineland` → `:618` sets step 3 |
| 3 — the great ultimatum | `:618` | ends with the hegemony war; `PD_austria_ultimatum_sent` set `:681`, cleared `:665` |

Supporting variables: `PD_phase2_conquest_target` (0 none / 1 held),
`PD_phase2_conquest_target_country`, `PD_phase2_conquest_cooldown` (+1 a month,
gates at >12 and >60), `PD_zollverein_asked` (`:480`).

Each transition also fires news: step 1→2 sends `.208` to onlookers and `.209`
to whoever owns the western areas next on the list; step 2→3 sends `.216` to
everyone with a presence in Europe.

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
- `PD_zollverein_asked` and `PD_austria_ultimatum_sent` are the two sub-lines:
  they say whether the offer has gone out and whether the ultimatum has been
  sent.
- The conquest cooldown is AI pacing, not player-facing. Keep it out of the
  panel or put it in a tooltip.
