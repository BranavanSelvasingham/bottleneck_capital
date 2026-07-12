# Bottleneck Capital Weekly Sleeve Review

Date: 2026-07-06
Window: 07:15 pre-market thesis scan
Sleeve: `compute_infra`
Schedule source: Monday weekly sleeve rotation
Source mode: local source-of-truth files plus live market ingest

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: none as the stricter working state for this sleeve.
- RESEARCH_REQUIRED: CRWV, NBIS, SHAZ, WYFI.
- TRIM / SELL WATCH: none.
- SELL: none.

No compute-infra capital action is authorized before the active dip-signal backlog,
filing-source gap, valuation work, and primary-source review are cleared. The long-only
mandate remains unchanged. Reported puts remain signal-only and are not trade
instructions. No technical indicators are used.

## Pre-Market Process

- Checked for active run locks and conflicting Bottleneck processes: none found.
- Ran `bcap ingest market` after sandbox DNS failure; live network retry succeeded and
  wrote 20 market events to `state/latest_market_events.jsonl` and
  `state/latest_events.jsonl`.
- Did not run SEC filing ingest because no `BCAP_SEC_*` or `BCAP_FILING_*` recovery
  variables are configured and prior runs show repeated SEC 403/backoff failures.
- Refreshed local position prices from snapshots: `updated=0`.
- Ran `bcap sentinel run`; 20 signal events were appended.
- Ran `bcap action-board`; wrote `reports/action_boards/2026-07-06.md`.

The live market fetch still reflects the last regular close available in the provider
feed (`observed_at` 2026-07-02) while using July 6 dedupe keys. Treat the output as
pre-open context and a research trigger, not a new Monday intraday trade signal.

## Sleeve Thesis

AI demand can create durable scarcity in contracted, power-secured compute capacity,
especially where supply can be delivered faster than hyperscaler build cycles. The
capital question is whether each ticker owns durable contracted compute capacity with
credible financing, utilization, and customer economics, rather than speculative GPU
exposure or illiquid proxy beta.

## Sleeve State

| Ticker | Working Decision | Urgency | Evidence Quality | Pre-Market Finding |
|---|---|---:|---|---|
| CRWV | RESEARCH_REQUIRED | HIGH | LIVE_PRICE_DISLOCATION_REVIEWED_NO_NEW_FILING | Action board still flags a company-specific event review. Customer concentration, leverage, GPU supply commitments, utilization, and refinancing risk remain unresolved. |
| NBIS | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE | Action board bounds the dip cause as broad cross-book de-risking, but customer demand, utilization, funding runway, and jurisdiction risk still need primary-source proof. |
| WYFI | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Current public SA exposure remains tracked, but durable compute assets, financing quality, liquidity, and contract economics are not verified enough for capital. |
| SHAZ | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Current public SA exposure remains tracked, but asset verification, governance, liquidity, and customer economics remain below the action threshold. |

## Decision Discipline

No `BUY_NOW` candidate exists. None of the sleeve names currently satisfies the required
buy conditions: strong thesis health, acceptable valuation, clean sleeve expression,
portfolio sizing allowance, understood anti-thesis, explicit sizing response, and an
invalidation trigger supported by current evidence.

No `ADD_ON_DIP` is approved. NBIS, WYFI, and SHAZ are broad de-risking dip candidates only
if valuation and source evidence clear; CRWV remains a primary event review. Bounded cause
is not buy approval.

No sell is triggered. A sell or thesis-correction review becomes mandatory if public
filings show a full Situational Awareness exit, a material SA reduction weakens thesis
weight, or company filings, IR, financing, customer evidence, or guidance break the named
compute-infra thesis.

## Priority Review Queue

1. CRWV: determine whether the company-specific event impairs customer concentration,
   leverage, GPU supply commitments, utilization, or refinancing risk.
2. NBIS: verify customer demand, utilization, funding runway, and jurisdiction risk from
   primary sources.
3. WYFI: verify durable compute assets, financing quality, liquidity, and contract
   economics before treating any dip as actionable.
4. SHAZ: verify durable compute assets, governance, liquidity, and customer economics
   before any capital action.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- No approved SEC mirror/proxy or filing vendor feed is configured, so filing recovery
  remains required before filing-window confidence can be restored.
- Market ingest succeeded on 2026-07-06, but the underlying latest regular-market
  observations in the provider output remain from 2026-07-02 after the July 3 observed
  U.S. market holiday.
- Active unresolved signal backlog remains material and blocks all compute-infra capital
  actions.

## Next Scheduled Work

- 09:45 open dislocation scan: use current market context through valuation, thesis, and
  sizing discipline; do not use technical indicators.
- 10:45 sentinel check: prefer `bcap live-check` only if filing recovery is configured;
  otherwise continue market-only recovery and keep the filing gap visible.
- Research review should use `bcap signal resolve` for reviewed events rather than
  hand-editing historical JSONL rows.
