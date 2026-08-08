# Bottleneck Capital

Bottleneck Capital is a long-term, thesis-led investment research system with a lightweight sentinel for fast dip and source-change detection.

The core command is:

```bash
./bcap daily-board
```

It updates `research/decisions/index.md` and writes a dated board under `reports/daily_decision_boards/`.

For the portfolio-first decision process:

```bash
./bcap portfolio-pm
```

This is the sole scheduled decision writer. It compiles ticker decisions, writes the dated
decision board, and writes a private gitignored portfolio board under
`reports/local_portfolio_boards/`. The private board applies exact local positions and cash
to factor concentration, scenario vulnerability, discount classification, remaining capacity,
and marginal-capital ranking without persisting position data in tracked research. It also
overwrites one concise daily digest under `reports/local_daily_digests/` with what changed,
the best executable action, entry conditions, invalidation, and data-quality blockers.

Resolver evidence is handed to Portfolio PM through an append-only queue:

```bash
./bcap handoff add --memo research/memos/2026-07-25-AAA-evidence.md \
  --ticker AAA --cause-status BOUNDED --thesis-status INTACT \
  --valuation-status UNREVIEWED --provisional-bias HOLD --confidence 80 \
  --cause-key market-wide-risk-off --primary-evidence-key release-2026-07-25 \
  --summary "Cause is bounded; PM must refresh valuation before changing capital."
./bcap handoff list
./bcap handoff apply --handoff-id HANDOFF_ID --decision HOLD \
  --reason "Decision reaffirmed after reviewing the linked primary-source memo."
```

Pending handoffs force `RESEARCH_REQUIRED` for capital-increasing decisions and remain visible
until PM records an application. `handoff add` refreshes Portfolio PM outputs immediately;
pass `--no-run-pm` only during controlled recovery. The stable cause and evidence keys suppress
same-ticker, same-cause, same-day repeats unless genuinely new primary evidence arrives. Use
`./bcap validate --pm-preflight` before PM recovery work;
use `./bcap validate --strict-live` before authorizing BUY_NOW or ADD_ON_DIP.

For a compact current-action surface that does not rewrite decision files:

```bash
./bcap action-board
```

It writes `reports/action_boards/YYYY-MM-DD.md` with only actionable decisions and active high-priority signal events.

For sentinel checks:

```bash
./bcap live-check
```

That single command runs market ingest, attempts filing ingest, classifies sentinel events,
writes the action board, and runs validation. It continues market signal detection even if
filing ingestion is temporarily unavailable, but reports that as a warning. If market
ingest itself fails, it still refreshes the action board from existing signal state,
prints validation context, records an error-status run ledger entry, and exits non-zero.

Scheduled collection uses:

```bash
./bcap collector-check --quiet
```

It performs ingestion, local held-price refresh, signal classification, and validation without
writing decisions or boards. It also attempts official FINRA daily short-volume ingestion.
Quiet mode emits output only for a new signal or an error. Filing mode defaults to `auto`,
which backs off for 60 minutes after an SEC 403 and then retries automatically; an approved
mirror, proxy, or authenticated filing feed bypasses the SEC backoff immediately.

The tracked schedule uses one persistent daily monitor and six material collection windows:
07:15, 09:45, 12:30, 15:30, 16:20, and 19:30 Toronto time. Portfolio PM runs at 07:15 and
16:20, plus immediately after a resolver handoff. Collector success without a new signal is
silent, so repeated checks do not create user-visible research noise.

For a direct market-structure refresh:

```bash
./bcap ingest market-structure
```

The default source is FINRA's consolidated daily short-sale volume file. This is flow data, not
net short interest. Configure `BCAP_MARKET_STRUCTURE_URL` and the optional
`BCAP_MARKET_STRUCTURE_AUTH_HEADER` for an enriched feed carrying dated short interest, borrow,
options, float, and supply-event fields. Opportunity ranking uses these inputs only to adjust
execution risk and timing; squeeze potential does not increase intrinsic value.

For lower-level diagnostics:

```bash
./bcap ingest market
./bcap ingest filings
./bcap sentinel run
./bcap action-board
```

`ingest market` defaults to `--provider auto`: it uses Alpaca when `APCA_API_KEY_ID`
and `APCA_API_SECRET_KEY` are configured, otherwise it falls back to Yahoo chart data.
If Yahoo misses a symbol, the provider attempts a Stooq daily-data fallback. Use
`--provider alpaca` or `--provider yahoo` to force one source. `ingest filings` uses SEC
submissions when reachable and falls back to the official SEC browse Atom feed when the
submissions API is blocked. It uses `--sec-user-agent`, `BCAP_SEC_USER_AGENT`, or git
`user.email` as the SEC User-Agent contact. Filing triggers include U.S. forms plus
foreign-issuer equivalents such as `6-K` and `20-F`. See `.env.example` for the environment
names expected by unattended automations. `BCAP_SEC_REQUEST_DELAY_SECONDS` controls pacing
for SEC browse Atom fallback requests; increase it if SEC returns 403/rate-limit responses.
If direct SEC access is blocked from the runtime, configure
`BCAP_SEC_COMPANY_TICKERS_URL`, `BCAP_SEC_SUBMISSIONS_URL_TEMPLATE`, or
`BCAP_SEC_BROWSE_ATOM_URL` to point at an approved SEC mirror/proxy.
Alternatively, configure `BCAP_FILING_EVENTS_URL` for an approved filing vendor/proxy feed.
The feed should return JSON with `covered_tickers` and `events`; each event should include
at least `ticker`, `filing_type` or `form`, `filing_date`, and a stable `accession` or
`dedupe_key`. `BCAP_FILING_EVENTS_AUTH_HEADER` can carry a single `Header-Name: value`
secret for that feed.

Corporate-action or provider-symbol mismatches belong in `configs/live_sources.yaml`:

```yaml
market:
  symbol_overrides:
    OLD: NEW
```

The internal ticker remains `OLD`, but market ingest queries `NEW` and writes snapshots and
signals back to `OLD`.

If market ingest cannot cover every requested ticker, it writes a high-priority
`market_data_gap` signal for each missing ticker. `validate --strict-live` treats partial
market coverage as an error for held or actionable tickers; non-actionable watchlist gaps
remain warnings but still appear on the action board.

If filing ingest fails, `live-check` writes a high-priority `filing_data_gap` signal so the
action board shows that SEC/company-filing coverage is blind.

The ingest commands write channel files under `state/latest_*_events.jsonl`, refresh
`state/latest_events.jsonl`, update `state/ingest_status.json`, and append run evidence to
`state/run_ledger.jsonl`. The sentinel reads `state/latest_events.jsonl` or
`state/latest_events.json` first, then falls back to `mock/latest_events.*`. Events are
idempotent by deterministic event id.

To resolve an event after research review:

```bash
./bcap signal list
./bcap signal resolve --event-id EVENT_ID --reason "Reviewed; no thesis damage."
```

Signal resolution is append-only in `state/signal_events.jsonl`; the decision engine ignores resolved events.

Before or after automation changes:

```bash
./bcap validate
./bcap validate --strict-live
./bcap live-readiness
./bcap resume-check
```

Validation checks ticker coverage, generated agent wiring, decision discipline, active
signals, event-input mode, live ingest freshness, and local position placeholders.
Use `--strict-live` before resuming automation; mock fallback, missing ingest status, stale
market data, stale filing data, fixture/manual ingest sources, missing Alpaca credentials
when the latest source was Alpaca, a missing SEC contact identity, or held/actionable live
coverage gaps become errors. Missing `state/local_positions.yaml`, missing held-position
current prices, missing or mismatched held-position currencies, and zero/placeholder/pending
held-position cost basis also become strict-live errors because sizing and actionability
depend on the exact local book.
`live-readiness` writes `reports/live_readiness/YYYY-MM-DD.md` with strict-live errors,
active high-priority signals, and concrete recovery actions. `resume-check` writes the same
report and exits non-zero until the readiness state is `READY`.

To enter exact broker fills without hand-editing the local YAML:

```bash
./bcap positions-set --ticker TSM --quantity 2 --average-cost 230.50 --currency USD --notes ""
./bcap positions-refresh-prices
./bcap resume-check
```

To generate the five-layer AI value-chain visualizer:

```bash
./bcap value-chain
```

It writes `reports/value_chain_visualizer.html`, mapping the tracked universe onto Jensen Huang's energy, chips, infrastructure, models, and applications stack.

For a local browser URL with a working in-page Update button:

```bash
./bcap value-chain --serve
```

Then open `http://127.0.0.1:8765/reports/value_chain_visualizer.html`.
