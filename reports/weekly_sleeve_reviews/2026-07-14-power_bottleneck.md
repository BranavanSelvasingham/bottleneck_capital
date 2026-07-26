# Bottleneck Capital Weekly Sleeve Review

Date: 2026-07-14
Window: 07:15 pre-market thesis scan
Sleeve: `power_bottleneck`
Schedule source: Tuesday weekly sleeve rotation
Source mode: local source-of-truth files plus live market ingest

## Executive Decision

- BUY_NOW: VST, half-starter only under the existing sizing gate.
- ADD_ON_DIP: none newly approved.
- HOLD: BE, PUMP, TE, CEG, TLNE.
- RESEARCH_REQUIRED: BW, PSIX, SEI.
- TRIM / SELL WATCH: none.
- SELL: none.

No new power-bottleneck capital action is authorized by this wake. VST remains the only
approved BUY_NOW expression, but only at the existing half-starter sizing gate. CEG
remains the higher-quality nuclear proxy but does not beat VST on current entry quality.
BW, PSIX, and SEI remain blocked by unresolved material price-dislocation reviews. The
long-only mandate remains unchanged; reported puts are signal-only and are not trade
instructions. No technical indicators are used.

## Pre-Market Process

- Current America/Toronto time at wake: 2026-07-14 07:24.
- Checked for lock files and active Bottleneck scheduled processes: no active conflict
  found.
- The worktree was already dirty from earlier scheduled outputs, but no same-file active
  writer was detected, so the due process continued with scoped writes.
- Ran `bcap ingest market`; the sandboxed attempt failed on DNS, then the approved live
  network retry succeeded and wrote 13 market events to `state/latest_market_events.jsonl`
  and `state/latest_events.jsonl`.
- Refreshed local held-position prices from live snapshots: `updated=7`, `missing=none`.
- Did not rerun filing ingest because the active SEC 403/backoff filing gap remains
  unresolved and no approved `BCAP_SEC_*` mirror/proxy or `BCAP_FILING_EVENTS_URL` vendor
  feed is configured.
- Ran `bcap sentinel run`; 13 signal events were appended.
- Ran `bcap action-board`; wrote `reports/action_boards/2026-07-14.md`.

The fresh July 14 market events are broad price-dislocation and valuation-context signals
from the latest available regular-market provider snapshots. Inside this sleeve, the new
events add another BW and PSIX research trigger. They are not buy instructions.

## Sleeve Thesis

AI infrastructure demand can make reliable power, onsite generation, grid connection,
contracted capacity, and dispatchable generation the binding constraint. The capital
question is whether each ticker owns a durable, financeable power-bottleneck asset with
credible customers, balance-sheet capacity, and valuation support, rather than generic
utility, industrial, energy-transition, or oilfield beta.

## Sleeve State

| Ticker | Working Decision | Urgency | Evidence Quality | Pre-Market Finding |
|---|---|---:|---|---|
| VST | BUY_NOW | HIGH | PRIMARY_COMPANY_IR_AND_SEC | Only approved sleeve buy. Keep the existing half-starter gate: initial sizing is capped because debt, preferred stock, integration risk, and growth-capex exclusions make a full allocation unjustified. |
| CEG | HOLD | HIGH | PRIMARY_COMPANY_IR_AND_SEC | Cleaner nuclear scarcity asset, but valuation remains less attractive than VST. Existing add-on-dip framing stays inactive until the defined entry range and thesis checks clear. |
| BE | HOLD | HIGH | SA_FILING_AND_LOCAL_BASELINE | Still a clean onsite-power candidate, but customer conversion, warranty/product risk, financing needs, margins, and valuation are not strong enough for new capital. |
| BW | RESEARCH_REQUIRED | MEDIUM | LIVE_INTRADAY_DISLOCATION_UNRESOLVED | New July 14 gap-down signal reinforces the existing block. Liquidity, leverage, backlog quality, and credible AI power-bottleneck exposure must be refreshed before capital. |
| PSIX | RESEARCH_REQUIRED | MEDIUM | LIVE_INTRADAY_DISLOCATION_UNRESOLVED | New July 14 gap-down signal reinforces the existing block. Need primary-source proof that engine/genset demand is durable datacenter or AI-load demand, not small industrial cyclicality. |
| SEI | RESEARCH_REQUIRED | MEDIUM | LIVE_INTRADAY_DISLOCATION_UNRESOLVED | Existing July 13 dislocation remains unresolved. Contracted power demand, fleet economics, margin quality, and financing risk still block capital. |
| TE | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Tracked as current SA exposure, but business-model clarity, capacity funding, customer demand, and valuation are not enough for new capital. |
| PUMP | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | AI power link remains indirect. Treat as oilfield-services cyclicality until primary sources prove durable power-bottleneck exposure. |
| TLNE | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Watch-only adjacent proxy. Needs better entry evidence, contract/regulatory review, and source support before promotion. |

## Decision Discipline

VST remains the only `BUY_NOW` candidate. It satisfies the current sleeve expression test
better than the alternatives, but sizing must stay capped and staged because leverage,
preferred stock, integration, power-price normalization, regulatory intervention, and
outage risk are still material.

No new `ADD_ON_DIP` is approved. BW and PSIX have fresh broad de-risking style
dislocation signals, and SEI remains blocked by the prior signal, but bounded price
movement is not buy approval. Each requires primary-source review, valuation work, and an
explicit sizing response before any capital action.

No sell is triggered. A sell or thesis-correction review becomes mandatory if public
filings show a full Situational Awareness exit, a material SA reduction weakens thesis
weight, or company filings, IR, financing, customer evidence, or guidance break the named
power-bottleneck thesis.

## Priority Review Queue

1. BW: clear the repeated price-dislocation block against liquidity, leverage, backlog
   quality, customer evidence, and whether the asset is an AI power solution or a levered
   industrial turnaround.
2. PSIX: verify customer backlog, datacenter demand tie, liquidity, margins, and whether
   genset demand is durable AI-load demand.
3. SEI: verify contracted distributed-power demand, fleet expansion economics, financing
   risk, and margin quality.
4. BE: refresh customer conversion, product reliability, warranty risk, financing needs,
   margins, and valuation before any promotion.
5. CEG and TLNE: maintain watch-only status until valuation, contract/regulatory risk,
   and entry gates improve.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- The action board has an active `filing_data_gap`; direct SEC and SEC browse Atom access
  previously returned repeated 403 responses, and a different approved filing data path is
  required.
- No `BCAP_SEC_*`, `BCAP_FILING_*`, or `APCA_*` recovery credentials were visible in the
  current environment.
- Active unresolved signal backlog remains material and blocks all research-required
  names. Reviewed events should be resolved with `bcap signal resolve`; historical JSONL
  rows should not be hand-edited.

## Next Scheduled Work

- 09:45 open dislocation scan: review opening gaps through valuation, thesis, and sizing
  discipline; do not use technical indicators.
- 10:45 sentinel check: prefer `bcap live-check`; if the filing source remains blocked,
  report the active filing gap and avoid repeated SEC hammering.
