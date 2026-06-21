# Bottleneck Capital Instructions

Always try to validate work and results. If you cannot see or evaluate your own output, say so clearly.

Be concise without losing signal.

## Decision Discipline

This repo is a long-term, thesis-led investment research system.

Every asset must have a current decision:

- BUY_NOW
- ADD_ON_DIP
- HOLD
- TRIM
- SELL
- RESEARCH_REQUIRED

Do not produce generic research without a decision.

A BUY_NOW requires:

1. Thesis health is strong.
2. Valuation is attractive or acceptable.
3. The asset is a clean expression of the sleeve thesis.
4. Portfolio sizing allows the position.
5. Anti-thesis is understood.
6. Hedge or sizing response is specified.
7. Invalidation trigger is explicit.

An ADD_ON_DIP requires:

1. Dip cause is identified or bounded.
2. No core thesis damage is found.
3. Valuation improved materially.
4. The asset is dip-buy eligible.
5. The dip protocol is satisfied.

A SELL requires:

1. A named thesis has broken; or
2. Risk has become unacceptable; or
3. The asset no longer expresses the intended thesis; or
4. Opportunity cost is extreme versus better sleeve candidates.

HOLD is valid and should be common.

RESEARCH_REQUIRED is mandatory when price, news, or filing movement is material but unresolved.

Never use technical indicators as the reason for a decision. Price only matters through valuation, margin of safety, drawdown opportunity, risk, and position sizing.

## Situational Awareness Mirroring

Keep the research universe as close as practical to Leopold Aschenbrenner / Situational Awareness LP's public portfolio.

Use three source classifications:

- `sa_reported_current_13f` for names in the latest public 13F information table.
- `sa_post_quarter_13g` for later public ownership clues.
- `sa_adjacent_historical_or_thesis_proxy` or `sa_adjacent_thesis_proxy` for names that fit the worldview but are not latest-current public 13F holdings.

Do not treat reported puts as instructions to short or buy puts. The user is long-only for now. Keep put exposure as `trade_policy: signal_only_no_puts_or_shorts`, and use it as evidence about crowded-AI downside, relative risk, or hedge pressure.

Do not label adjacent proxies as current Situational Awareness holdings.

If a future public filing indicates Situational Awareness fully exited a tracked name, do not auto-sell, but immediately mark the ticker `RESEARCH_REQUIRED` and investigate whether our thesis should be corrected, downgraded, or exited. A full SA exit is a material concern signal.

If a future public filing indicates a material SA position reduction, treat it as a high-priority thesis-weight review, especially when the name was classified as `sa_reported_current_13f`.

Every changed decision must update:

- `research/assets/{TICKER}.md`
- `research/decisions/{TICKER}.md`
- `state/decision_ledger.jsonl`

Every decision must include:

- thesis expressed
- anti-thesis
- hedge or sizing response
- invalidation trigger
- confidence
- evidence quality
