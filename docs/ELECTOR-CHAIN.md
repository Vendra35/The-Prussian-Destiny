# The elector chain — five rulers, and why they now ask first

Read out of `in_game/events/DHE/PD_brandenburg_DHE_events.txt` on 2026-09-12,
when a player wrote in: *"Annoying to lose my personal unions and carefully
bred family tree every x years."* Written down so the next person does not have
to re-derive why that happened or re-decide the shape of the fix.

## The chain

Eleven DHEs live in the file (`pd_brandenburg_dhe.1`–`.11`). The first six are
AI-only flavour (`is_ai = yes` in their triggers). The last five are the
**historical succession chain**: each fires once, for `PRU` or `NGC`, at peace,
inside its ruler's real window.

| Event | Ruler seated | Window (`from`–`to`) | Stats adm/dip/mil |
|---|---|---|---|
| `.7` | Joachim (I Nestor), 22 | 1499–1535 | 55/60/45 |
| `.8` | Joachim (II Hektor), 33 | 1535–1571 | 50/65/55 |
| `.9` | Johann Sigismund, 30 | 1608–1619 | 55/60/55 |
| `.10` | Friedrich Wilhelm, 20 | 1640–1688 | 75/65/80 |
| `.11` | Friedrich (I), 44 | 1701–1900 | 60/70/50 |

Every one of them builds the man the same way: `create_character` with
`dynasty = dynasty:hohenzollern_dynasty`, `create_in_limbo = yes` and
`save_scope_as = pd_prussian_ruler`, then `set_new_ruler`.

## Why the player lost unions and heirs — the mechanism, not a guess

The complaint named two losses and the script docs explain both in one line:

- `set_new_ruler` — "Makes the target_character the new ruler"
  (`effects.log:10245-10248`, country scope, character target).
- `set_new_ruler_no_update` — "Makes the target_character the new ruler,
  **without updating any unions** or fiefdom-like titles the character has"
  (`effects.log:10250-10251`).

So the plain form *does* update unions. A personal union in EU5 is a shared
ruler: `force_union` says "the country which forces the union **keeps the
ruler**" (`effects.log:3421`) and `num_unions` counts "unions **ruled by the
scoped dynasty**" (`triggers.log:9059`). Swap the ruler for a fresh character
and the union is re-evaluated around a man who rules nothing else.

The family tree goes for a simpler reason: the new ruler is created from
nothing. He carries the Hohenzollern name but is nobody's son, so the heirs the
player spent decades arranging are no longer the ruler's line.

**Why not just switch to `set_new_ruler_no_update`?** It would keep the unions
but still discard the bred heir and still replace the ruler without asking.
The complaint was about consent as much as about unions, and the one-line docs
entry is the only thing known about the `_no_update` variant — untested here.

## The shape now (2026-09-12)

AI is forced to history; a human is offered it. Same shape in all five events.

```
immediate = {
    hidden_effect = {
        create_character = { ... create_in_limbo = yes  save_scope_as = pd_prussian_ruler }
        if = {
            limit = { is_ai = yes }
            set_new_ruler = scope:pd_prussian_ruler      # AI path, unchanged
        }
    }
}
option = {   # a — accept the historical elector
    ai_chance = { factor = 100 }
    if = {
        limit = { is_ai = no }
        set_new_ruler = scope:pd_prussian_ruler
    }
    add_prestige = prestige_severe_bonus                  # 15
}
option = {   # b — keep our own house
    ai_chance = { factor = 0 }
    add_prestige = prestige_weak_bonus                    # 5
    add_legitimacy = legitimacy_weak_bonus                # 5
    hidden_effect = { kill_character_silently = scope:pd_prussian_ruler }
}
```

Three decisions inside that, each with its precedent:

- **The AI is gated in `immediate`, not by `ai_chance` alone.** The AI's
  ruler is seated before the card opens, exactly as before; the `ai_chance`
  pair (100 / 0) is belt on top of braces. `hidden_effect { if { limit {
  is_ai = yes } } }` is vanilla's own shape at
  `events/disaster/sinicization_disaster.txt:669-671`.
- **The human's option is not hidden behind `trigger = { is_ai = no }`.**
  Option b is visible to everyone and weighted to zero for the AI, the way
  every other human-only choice in this mod is (`PD_events.txt:614-616`).
  The creation stays in `immediate` and the seating moves into the option —
  vanilla does precisely this for Jiří z Poděbrad at
  `DHE/flavor_BOH.txt:44-68` (`create_in_limbo`, `save_scope_as`, then
  `set_new_ruler = scope:...` inside option a).
- **Declining removes the limbo character.** A `create_in_limbo` man that
  nobody seats is an orphan; vanilla's refusing arms run
  `hidden_effect = { kill_character_silently = scope:x }`
  (`events/character/artist_events.txt:744-748`,
  `effects.log:3559`). Without it every declined elector would be a
  leftover character in the save.

The decline reward is deliberately small. Accepting still pays three times
the prestige and brings a ruler with scripted stats; declining buys
continuity and nothing else. A human who declines `.7` is still asked at `.8`,
`.9`, `.10` and `.11` — the events are independent.

## The census, counted by tool

`option_statements.py` (1066 Test Mod) against the written file, 2026-09-12.
Identical for `.7`, `.8`, `.9`, `.10`, `.11`:

```
== pd_brandenburg_dhe.N.a ==
   1  set_new_ruler = scope:pd_prussian_ruler          <- is_ai = no
   2  add_prestige = prestige_severe_bonus             <- (no guard)
== pd_brandenburg_dhe.N.b ==
   1  add_prestige = prestige_weak_bonus               <- (no guard)
   2  add_legitimacy = legitimacy_weak_bonus           <- (no guard)
   3  kill_character_silently = scope:pd_prussian_ruler <- hidden_effect
```

Before the change each `.a` printed exactly one effect, `add_prestige`, and
the seating lived in `immediate` with no guard at all.

## Loc

Ten new keys: `pd_brandenburg_dhe.N.b` and `pd_brandenburg_dhe.N.b.entry` for
N in 7–11. The `.b.entry` rows exist because the event browser renders its
option list with no event bound (CLAUDE.md, "A `dynamic_historical_event`
needs `<id>.entry` AND `<id>.<option>.entry`"); `verify_pd.py` check 13 now
scans 29 keys instead of 24.

The `.desc` texts still announce the new elector as a fact ("Joachim takes the
reins"). They were left alone on purpose — the change was scoped to the two
keys per event — but they read slightly ahead of a card that is now a
question. Soften them if anyone minds.

## What to test in game

Static checks cannot see any of this run. The first campaign that reaches
1499 as a human Prussia should confirm, in this order:

1. The card opens with two options and the ruler is **unchanged** while it is
   open (the old version had already swapped him).
2. Option a seats Joachim; any personal union behaves as it did under the old
   version (it is expected to break — that is the historical price).
3. Option b keeps the ruler, the heir and the unions; the character list does
   not gain a stray Joachim.
4. An AI Prussia still gets Joachim on the same date with no card shown to
   anyone.
