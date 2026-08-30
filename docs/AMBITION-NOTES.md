# The Prussian Ambition — notes and checklist

Read out of `in_game/common/situations/brandenburg_rise.txt` and the 18
phase-1 events on 2026-08-30. `the_blood_and_iron` and
`the_prussian_ascension` are the finished references for the panel shape.

Run `python tools/verify_pd.py` at every step. All boxes are ticked and it
reports all checks passed. What is NOT done is an in-game test - static
verification is not evidence of behaviour.

## Checklist

- [x] Hygiene — map-mode `c:BRA` / `c:TEU` guards, `.gui` BOM, cp1254 comments.
      All three were done in the Ascension pass.
- [x] Loc — trim `the_prussian_ambition_desc`, history card, standings strings,
      levers card with a `How the AI plays this` section built from below.
- [x] Panel — balance bar in the header, Standings card, history card, levers.

## The score, which is the whole situation

Recomputed **every month** for both sides (`brandenburg_rise.txt:186-239`):

```
score = military_strength
      + monthly_income_trade_and_tax
      + prestige * 0.2
```

Nothing else feeds it. The situation then compares `PD_bra_score` against
`PD_teu_score` and lets whichever side is ahead act — `:262` gives Brandenburg
the knockout when `PD_bra_score >= PD_teu_score`, `:336` gives the Teutonic
Order its own when `PD_teu_score > PD_bra_score`. A tie favours Brandenburg.

Both sides also carry a target and a cooldown: `PD_conquest_target` /
`PD_conquest_target_country` / `PD_conquest_cooldown` (gates at >12 and >240)
for Brandenburg, and `PD_teu_conquest_*` (gates at >48 and >480) for the Order.
The Order is paced four times slower.

## How the situation ends

`prussian_ambition_end_trigger`, each branch with its own tooltip:

- Brandenburg wins — the Order is its subject, **or** the Order holds nothing in
  `prussia_area` / `brandenburg_area` / `pomerania_area` while Brandenburg owns
  Koenigsberg or Gdansk.
- The Order is destroyed by somebody else, and the timeline date has passed.
- The Order wins — its own knockout branch.
- The time limit runs out.

## The 18 events

Fourteen are single-option news. Four branch:

| Event | Title | Weights |
|---|---|---|
| `.103` | The Drums of War | 50 / 0 |
| `.108` | Diplomatic Maneuvers | **1000 / 1** (three options) |
| `.109` | An Envoy from Berlin | 50 / 0 |
| `.117` | The Crusade Resumes | 50 / 0 |

`.113` and `.115` carry an `ai_chance` on a single option, which changes
nothing.

## What is worth saying about the AI

Three of the four branches are weighted against **zero**, so the AI takes the
first option every time — the same pattern as the other two situations.

`.108` is the exception and the only place in the whole mod where the AI can
do two different things. Its immediate block searches the target's enemies and
rivals for the strongest one in Europe that holds no land in Brandenburg,
Pomerania or Prussia (`ordered_country`, `order_by = expected_army_size`,
`max = 1`) and saves it as the rival. Then:

- **a** — "Send an envoy to their rival. We strike together!" — weight **1000**,
  only offered when such a rival was found.
- **b** — "We need no help. Prussian steel is enough." — weight **1**.
- **c** — "So be it. We march alone." — the fallback when no rival exists.

So roughly once in a thousand the AI refuses the alliance it just went looking
for. Worth stating precisely rather than as "always": it is the one genuine
coin-flip in the mod, even if it is a very unfair coin.
