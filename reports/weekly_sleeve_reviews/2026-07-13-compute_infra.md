# Bottleneck Capital Weekly Sleeve Review

Date: 2026-07-13
Window: 07:15 pre-market thesis scan
Sleeve: `compute_infra`
Schedule source: Monday weekly sleeve rotation
Source mode: local source-of-truth files plus live market ingest

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: NBIS, SHAZ, WYFI.
- RESEARCH_REQUIRED: CRWV.
- TRIM / SELL WATCH: none.
- SELL: none.

No compute-infra capital action is authorized before the active filing-source gap,
fresh dip-signal backlog, valuation work, and primary-source review are cleared. The
long-only mandate remains unchanged. Reported puts remain signal-only and are not trade
instructions. No technical indicators are used.

## Pre-Market Process

- Current America/Toronto time at wake: 2026-07-13 07:22.
- Checked `state/run_locks`: no active scheduled-write or per-process lock remained.
- Ran `bcap ingest market`; the sandboxed attempt failed on DNS, then the approved live
  network retry succeeded and wrote 15 market events to `state/latest_market_events.jsonl`
  and `state/latest_events.jsonl`.
- Refreshed local held-position prices from live snapshots: `updated=8`, `missing=none`.
- Did not rerun SEC filing ingest manually after the action-board/sentinel path surfaced
  repeated SEC 403/backoff evidence and no approved `BCAP_SEC_*` mirror/proxy or
  `BCAP_FILING_EVENTS_URL` recovery path was configured.
- Ran `bcap sentinel run`; 18 signal events were classified.
- Ran `bcap action-board`; wrote `reports/action_boards/2026-07-13.md`.

The market provider output used July 13 dedupe keys, but the latest regular-market
observations are from the July 10 close. Treat the output as pre-open valuation and
research context, not an intraday trade signal.

## Sleeve Thesis

AI demand can create durable scarcity in contracted, power-secured compute capacity,
especially where supply can be delivered faster than hyperscaler build cycles. The
capital question is whether each ticker owns durable contracted compute capacity with
credible financing, utilization, and customer economics, rather than speculative GPU
exposure, illiquid proxy beta, or fragile financing.

## Sleeve State

| Ticker | Working Decision | Urgency | Evidence Quality | Pre-Market Finding |
|---|---|---:|---|---|
| CRWV | RESEARCH_REQUIRED | HIGH | LIVE_PRICE_DISLOCATION_REVIEWED_NO_NEW_FILING | Action board still lists CRWV as an overdue research block. The July 10 close context included a 5.6% gap-down price-dislocation trigger, but customer concentration, leverage, GPU supply commitments, utilization, and refinancing risk remain unresolved. |
| NBIS | HOLD | HIGH | SA_FILING_AND_LOCAL_BASELINE | No fresh pre-market capital action. Nebius remains a post-quarter SA evidence name, but jurisdiction, customer, utilization, and financing risk keep it hold-only. |
| WYFI | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | July 10 close context included a 5.5% gap-down price-dislocation trigger. The dip cause is bounded as broad cross-book de-risking, but durable compute assets, financing quality, liquidity, and contract economics are not verified enough for capital. |
| SHAZ | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | July 10 close context included a 9.6% gap-down price-dislocation trigger. The dip cause is bounded as broad cross-book de-risking, but asset verification, governance, liquidity, and customer economics remain below the action threshold. |

## Decision Discipline

No `BUY_NOW` candidate exists in this sleeve. None of CRWV, NBIS, WYFI, or SHAZ currently
satisfies the required buy conditions: strong thesis health, acceptable valuation, clean
sleeve expression, portfolio sizing allowance, understood anti-thesis, explicit sizing
response, and an invalidation trigger supported by current evidence.

No `ADD_ON_DIP` is approved. CRWV, WYFI, and SHAZ triggered dip-style research signals,
but bounded broad de-risking is not buy approval. NBIS remains hold-only unless primary
evidence clears customer demand, utilization, funding runway, and jurisdiction risk.

No sell is triggered. A sell or thesis-correction review becomes mandatory if public
filings show a full Situational Awareness exit, a material SA reduction weakens thesis
weight, or company filings, IR, financing, customer evidence, or guidance break the named
compute-infra thesis.

## Priority Review Queue

1. CRWV: clear the overdue research block; determine whether customer concentration,
   leverage, GPU supply commitments, utilization, or refinancing risk impair the thesis.
2. NBIS: verify customer demand, utilization, funding runway, and jurisdiction risk from
   primary sources before any promotion from HOLD.
3. WYFI: verify durable compute assets, financing quality, liquidity, and contract
   economics before treating the dip signal as actionable.
4. SHAZ: verify durable compute assets, governance, liquidity, and customer economics
   before treating the dip signal as actionable.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- The action board has an active `filing_data_gap`: SEC company tickers and browse Atom
  returned repeated 403 responses, and a different approved filing data path is required.
- Market ingest succeeded on 2026-07-13 through the Yahoo fallback; Alpaca credentials
  remain missing but this is not blocking while the fallback is successful.
- Active unresolved signal backlog remains material. Reviewed events should be resolved
  with `bcap signal resolve`; historical JSONL rows should not be hand-edited.

## Validation

`bcap validate` completed with no ERROR issues. Warnings remain material and visible:
overdue CRWV and BITF research blocks, elevated/adverse market regime, active
high-priority dip/geopolitical/filing-gap signals, and stale filing ingest.

## Next Scheduled Work

- 09:45 open dislocation scan: review opening gaps through valuation, thesis, and sizing
  discipline; do not use technical indicators.
- 10:45 sentinel check: prefer `bcap live-check`; if filing recovery remains unavailable
  or SEC 403s persist, keep the filing gap visible and avoid hammering SEC.
