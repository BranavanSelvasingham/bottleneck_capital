# Bottleneck Upside Framework

This framework separates the official decision from the opportunity queue.

The official decision answers: what action is authorized now?

The bottleneck upside map answers: if the thesis is right, how far can the equity move and what evidence promotes it?

## Action Tiers

| Tier | Meaning |
|---|---|
| BUY_NOW | Authorized first tranche now. |
| ADD_ON_DIP | Authorized only if the named dip trigger and sizing rule are satisfied. |
| WATCH_TOP | Not authorized yet, but one of the best candidates to underwrite next. |
| HOLD_CORE | Owned or approved long-term hold with intact thesis. |
| HOLD_SPECULATIVE | Owned or tracked option-like exposure; upside exists but terms or evidence are uncertain. |
| WATCH_LOW | Tracked, but not close to capital. |
| AVOID_FOR_NOW | Tracked for signal value, but current risk/reward is unattractive. |

## Upside Score

Score 0-100 using thesis-specific upside, not technical indicators.

| Range | Meaning |
|---|---|
| 80-100 | Bottleneck can plausibly create multi-bagger upside if evidence clears. |
| 60-79 | Attractive upside if valuation and thesis proof align. |
| 40-59 | Real upside, but likely not enough without a better entry. |
| 20-39 | Mostly watchlist value. |
| 0-19 | Signal-only or unclear expression. |

## Required Fields

Every serious candidate should include:

- bottleneck mechanism: scarce resource that reprices the asset
- base-case return band
- bull-case return band
- downside return band
- market-implied ceiling
- variant upside
- promotion trigger
- first tranche rule

## Promotion Discipline

Promote HOLD to ADD_ON_DIP when:

- the dip cause is identified or bounded
- no core thesis damage is found
- valuation improves materially
- base or weighted upside is large enough to matter
- position sizing and invalidation are explicit

Promote HOLD to BUY_NOW when:

- thesis health is strong
- base-case upside is attractive without relying on heroic assumptions
- valuation is acceptable
- position size fits the portfolio
- anti-thesis and invalidation are explicit

Keep HOLD when:

- upside exists but is mostly bull-case optionality
- merger, financing, customer, or governance terms are unresolved
- entry price does not compensate for downside
- the asset is useful as a signal but not clean enough for capital
