# Bottleneck Capital Instructions

Always try to validate work and results. If you cannot see or evaluate your own output, say so clearly.

Be concise without losing signal.

## Runtime Policy

Any subagent, delegated task, spawned Codex thread, or automation-created research thread
from this project should use the strongest available model and highest available reasoning
effort. Prefer GPT-5.5 or newer when selectable, with reasoning effort set to extra-high.

If the runtime cannot explicitly select model or effort, state that limitation in the
handoff and proceed with the best available equivalent.

## Operating Loop Hardening

Do not defer scheduled Bottleneck runs solely because the worktree is dirty. First check
whether another run is active or whether the due process would conflict with same-file
writes already in progress. If there is no active conflict, proceed with scoped writes,
preserve unrelated changes, and validate.
Scheduled write commands use a shared `scheduled-write` lock plus per-process locks; treat a
live lock conflict as a real same-file collision, and stale dead-PID locks as recoverable.

For scheduled sentinel collection, prefer `bcap collector-check`. It runs market ingestion,
attempts market-structure and filing ingestion subject to source availability and active SEC
backoff, refreshes local held-position prices, classifies sentinel events, and validates without
rewriting decisions or decision boards.
Use `bcap live-check` when an updated action board is also required. Use the lower-level
sequence `bcap ingest market`, `bcap ingest filings`, `bcap sentinel run`, then
`bcap action-board` only for diagnostics or recovery. Use `state/latest_events.jsonl`
or `state/latest_events.json` as the preferred sentinel input. `mock/latest_events.*` is a
fallback only and should be treated as a validation warning on market days.

Run scheduled collectors in one persistent daily monitoring task at 07:15, 09:45, 12:30,
15:30, 16:20, and 19:30 America/Toronto. Use `bcap collector-check --quiet`; a successful
check without a new signal should not create a user-visible update. Run Portfolio PM at 07:15
and 16:20 and immediately after every new resolver handoff. Surface the single overwritten
`reports/local_daily_digests/{date}.md` report instead of separate collector summaries.

Signal events are append-only. Use `bcap signal resolve --event-id ... --reason ...` after
research review; do not hand-edit old JSONL rows just to mark them resolved.
Every resolver memo must also create one structured pending PM handoff per covered ticker with
`bcap handoff add`. Resolving the source event does not complete the investment review. Keep the
handoff pending until Portfolio PM updates or reaffirms the ticker decision and records the result
with `bcap handoff apply`. Never treat a resolved signal as an applied portfolio conclusion.
Use stable `--cause-key` and `--primary-evidence-key` values when creating the handoff. Do not
write another resolver memo for the same ticker, cause, and day unless a new primary-source
filing, release, or disclosure changes the evidence key.

Use `bcap validate` after process or universe changes and `bcap validate --strict-live`
before resuming market-day automation. Use `bcap live-readiness` to write the dated resume
checklist and recovery actions. Strict-live must use live provider sources, live market
ingest status, SEC user-agent configuration, and exact local position data. Alpaca
credentials are preferred but not mandatory when the auto market provider successfully uses
the Yahoo fallback. Use `bcap action-board` whenever the user needs the latest actionable
steps outside the close-board window. Use `bcap portfolio-pm` at the pre-market and close
decision windows. It is the sole scheduled decision writer and writes both the decision board
and the gitignored local portfolio board. Collectors, macro/geopolitical watchers, and research
resolvers may append events or write bounded memos, but must not rewrite ticker decisions.
Before `bcap portfolio-pm`, run `bcap validate --pm-preflight`, review every row from
`bcap handoff list`, update or explicitly reaffirm the public ticker decision, and apply each
reviewed handoff. `--pm-preflight` is a recovery gate: it leaves live-source gaps visible but
does not let an overdue research block prevent the PM from repairing that block. New BUY_NOW or
ADD_ON_DIP decisions still require a clean `bcap validate --strict-live`; when strict-live is
blocked, PM may only reaffirm or move to HOLD, RESEARCH_REQUIRED, TRIM, or SELL.
Before clearing a market-day entry, refresh the configured cross-asset context basket and
record a structured geopolitical/macro heartbeat with `bcap regime-event`. The heartbeat
must state region, status, severity, confidence, affected channels, observed time, summary,
and primary source. A newer status for the same region supersedes an older ceasefire or
escalation state in the regime assessment. Do not treat a stale or missing heartbeat as
neutral. Compare headline escalation against oil, volatility, broad-equity, dollar, and
rates proxies; use market confirmation to scale execution risk without pretending the
company thesis itself broke.
Use `bcap resume-check` as the final unpause gate; it writes the readiness report and exits
non-zero until the automation is safe to resume.
`bcap ingest filings` uses SEC submissions when reachable and falls back to the official
SEC browse Atom feed when the submissions API is blocked. Include foreign-issuer equivalents
such as `6-K` and `20-F` in filing coverage for ADRs and non-U.S. issuers.
If direct SEC access is blocked, use an approved SEC mirror/proxy via
`BCAP_SEC_COMPANY_TICKERS_URL`, `BCAP_SEC_SUBMISSIONS_URL_TEMPLATE`, or
`BCAP_SEC_BROWSE_ATOM_URL`; alternatively use `BCAP_FILING_EVENTS_URL` for an approved live
filing vendor/proxy feed that reports `covered_tickers` and normalized events. Use
`configs/live_sources.yaml` for provider-symbol overrides after ticker changes or corporate
actions; do not edit code for simple symbol remaps.
An SEC 403 creates a bounded backoff, not a permanent filing skip. Auto mode retries after
`filings.sec_403_retry_minutes` from `configs/live_sources.yaml`; an approved configured feed
or mirror bypasses the backoff immediately.
Treat `market_data_gap` and filing coverage gaps as operationally material. Strict-live
blocks held or actionable ticker gaps; non-actionable watchlist gaps are warnings, but must
remain visible on the action board until resolved or the universe mapping is corrected.

Before treating a dislocation as a discount, assess market structure from current, dated
sources. Cover reported short interest and days-to-cover; FINRA/exchange daily short-sale
volume; borrow fee, availability, and utilization when available; options skew, open interest,
implied volatility, and dealer positioning when reliable; float, liquidity, lockups, offerings,
ATMs, converts, insider supply, index flows, and catalyst timing. Daily short-sale volume is
not net short interest and may reflect market making, hedging, or intraday-covered activity.
Fails-to-deliver and threshold-list status are investigation signals, not proof of naked
shorting. A squeeze setup requires corroboration from at least three independent channels plus
a catalyst and limited new supply. Market structure may change entry timing, tranche size, and
near-term convexity; it must never raise intrinsic value or override thesis damage. Keep missing
borrow, options, ownership, or supply data visible rather than assuming neutral conditions.

## Decision Discipline

## Position Privacy

Exact user positions are local-only and must never be committed, pushed, included in a PR,
or written into tracked research or generated reports. This includes share quantities, cost
basis, account values, current portfolio weights, account names, and transaction fills.

- Keep exact holdings only in `state/local_positions.yaml` and local reports derived from it.
- Keep `state/local_positions.yaml`, `reports/local_exposure.md`, `state/signal_events.jsonl`,
  and generated local-portfolio/action-board/sunday-prep directories gitignored and untracked.
- Public research may include company market prices, valuation ranges, entry zones, and policy
  position caps. It must not include the user's actual exposure.
- Set tracked `current_position_weight_pct` metadata to `0` or omit it. Runtime decisions must
  apply local position capacity without persisting the result.
- PR titles, bodies, commits, and review comments must not repeat local position data.

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
