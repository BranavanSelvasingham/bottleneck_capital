# Crowded AI Beta and Hedge Signals

Sleeve: `crowded_ai_beta_hedge`

## Baseline Thesis

SA's reported put exposure is a signal about crowded AI downside, valuation risk, or portfolio hedge pressure, not an instruction for this long-only system to short or buy puts.

## Current Tickers

- `AMD`
- `AVGO`
- `NVDA`
- `SMH`

## Initialization Questions

- Which long holdings are most exposed to crowded AI beta?
- What is the put signal warning us not to overpay for?
- How should position sizing substitute for puts in a long-only mandate?

## Decision Discipline

- BUY requires thesis, valuation, hedge or sizing response, and invalidation.
- ADD_ON_DIP requires no thesis damage and improved valuation.
- SELL requires a named thesis break or unacceptable risk.
- Reported puts are signal-only unless the user changes the mandate.
