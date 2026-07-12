# Bottleneck Capital Weekly Sleeve Review

Date: 2026-07-07
Window: 07:15 pre-market thesis scan
Sleeve: `power_bottleneck`
Schedule source: Tuesday weekly sleeve rotation
Source mode: local source-of-truth files plus live market ingest

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: VST only under the current decision files.
- RESEARCH_REQUIRED: BW, BE, PSIX, PUMP, SEI, TE, CEG, TLNE.
- TRIM / SELL WATCH: none.
- SELL: none.

No power-bottleneck capital action is authorized before the active signal backlog,
the new BW pre-market signal, filing-source recovery, valuation work, and
primary-source review are cleared. The long-only mandate remains unchanged. Reported
puts are signal-only and are not trade instructions. No technical indicators are used.

## Pre-Market Process

- Checked for active run locks and conflicting Bottleneck processes: none found.
- Confirmed no `BCAP_SEC_*`, `BCAP_FILING_*`, or `APCA_*` recovery variables are
  configured.
- Ran `bcap ingest market` with live network access; Yahoo fallback succeeded and wrote
  1 market event to `state/latest_market_events.jsonl` and `state/latest_events.jsonl`.
- Did not run SEC filing ingest because no approved SEC mirror/proxy or filing vendor
  feed is configured and prior runs show repeated SEC 403/backoff failures.
- Refreshed local position prices from snapshots: `updated=0`.
- Ran `bcap sentinel run`; 1 signal event was appended.
- Ran `bcap action-board`; wrote `reports/action_boards/2026-07-07.md`.

The new market event is `BW` with dedupe key
`market:BW:2026-07-07:price_dislocation`, observed at
2026-07-06T16:00:02-04:00. Treat it as pre-market context from the latest available
regular-market provider snapshot and a research trigger, not a buy signal.

## Sleeve Thesis

AI infrastructure demand can make power availability, onsite generation, reliable
capacity, interconnection, and contracted power delivery the binding constraint. The
capital question is whether each ticker owns a durable, financeable power-bottleneck
asset with customer evidence and valuation support, rather than generic industrial,
utility, or energy-services beta.

## Sleeve State

| Ticker | Working Decision | Urgency | Evidence Quality | Pre-Market Finding |
|---|---|---:|---|---|
| BE | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE | Local position exists, but the action board still blocks adds. Bloom remains the cleanest direct onsite-power candidate, yet backlog conversion, product reliability, financing needs, customer concentration, margins, and valuation are unresolved. |
| BW | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | New BW price-dislocation signal appended. Leverage, liquidity, backlog quality, and whether this is an AI power solution versus a levered industrial turnaround remain unresolved. |
| PSIX | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Still needs primary-source proof that engine/genset backlog is durable datacenter or AI-load demand, not small industrial cyclicality. |
| PUMP | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | AI power link remains indirect. Treat as oilfield-services cyclicality until primary sources prove a durable power-bottleneck role. |
| SEI | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Dip cause is bounded as broad de-risking, but contracted distributed-power demand, margins, and fleet expansion economics need review. |
| TE | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Tracked as current SA exposure, but business-model clarity, capacity funding, customer demand, and valuation are not enough for new capital. |
| VST | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Strong adjacent power-scarcity proxy, but not latest-current public SA exposure and not an automatic buy without valuation margin of safety. |
| CEG | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Highest-quality watch-top proxy in the sleeve, but promotion requires valuation work, no regulatory/thesis damage, and a defined starter-size cap. |
| TLNE | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Generation/power-scarcity proxy remains watch-only pending valuation and contract/regulatory evidence. |

## Decision Discipline

No `BUY_NOW` candidate exists. None of the sleeve names currently satisfies the required
buy conditions: strong thesis health, acceptable valuation, clean sleeve expression,
portfolio sizing allowance, understood anti-thesis, explicit sizing response, and an
invalidation trigger supported by current evidence.

No `ADD_ON_DIP` is approved. Several dips are bounded as broad cross-book de-risking,
and BW has a fresh dip trigger, but bounded cause is not buy approval. Each candidate
still requires primary-source review, valuation work, and explicit sizing before any
capital action.

No sell is triggered. A sell or thesis-correction review becomes mandatory if public
filings show a full Situational Awareness exit, a material SA reduction weakens thesis
weight, or company filings, IR, financing, customer evidence, or guidance break the
named power-bottleneck thesis.

## Priority Review Queue

1. BW: review the new price-dislocation signal against liquidity, leverage, backlog
   quality, and credible AI power-bottleneck exposure.
2. BE: verify datacenter backlog conversion, product reliability, financing needs,
   customer concentration, margins, and valuation before any add.
3. CEG: run valuation and regulatory/contract review to determine whether WATCH_TOP can
   become an ADD_ON_DIP candidate with a defined starter-size cap.
4. PSIX and SEI: verify customer backlog, contracted power demand, margin quality, and
   scalability from primary sources.
5. TE, PUMP, and TLNE: keep watch-only until business-model, contract, regulatory, and
   valuation evidence clears.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- No approved SEC mirror/proxy or filing vendor feed is configured, so filing recovery
  remains required before filing-window confidence can be restored.
- Alpaca credentials are absent; market ingestion is using Yahoo fallback.
- Active unresolved signal backlog remains material and blocks all power-bottleneck
  capital actions.

## Next Scheduled Work

- 09:45 open dislocation scan: use current market context through valuation, thesis, and
  sizing discipline; do not use technical indicators.
- 10:45 sentinel check: prefer `bcap live-check` only if filing recovery is configured;
  otherwise continue market-only recovery and keep the filing gap visible.
- Research review should use `bcap signal resolve` for reviewed events rather than
  hand-editing historical JSONL rows.
