# Bottleneck Capital Weekly Sleeve Review

Date: 2026-07-09
Window: 07:15 pre-market thesis scan
Sleeves: `memory_storage_networking`, `semicap_equipment`, `ai_networking_optical`
Schedule source: Thursday weekly sleeve rotation plus semicap/networking adjunct review
Source mode: local source-of-truth files plus live market ingest

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: none under the current sleeve decision files.
- RESEARCH_REQUIRED: MU, SNDK, TSM, ASML, INTC, ONTO, GLW, LITE, MRVL.
- TRIM / SELL WATCH: none.
- SELL: none.

No memory, storage, semicap, or AI networking capital action is authorized before the
active signal backlog, today's pre-market signals, filing-source recovery, valuation
work, and primary-source review are cleared. The long-only mandate remains unchanged.
Reported puts are signal-only and are not trade instructions. No technical indicators
are used.

## Pre-Market Process

- Checked for active run locks and conflicting Bottleneck processes: none found.
- Confirmed no `BCAP_SEC_*`, `BCAP_FILING_*`, `APCA_*`, or `SEC_*` recovery variables
  are configured.
- Ran `bcap ingest market` with live network access; Yahoo fallback succeeded and wrote
  3 market events to `state/latest_market_events.jsonl` and `state/latest_events.jsonl`.
- Did not run SEC filing ingest because no approved SEC mirror/proxy or filing vendor
  feed is configured and prior runs show repeated SEC 403/backoff failures.
- Refreshed local position prices from snapshots: `updated=0`, `missing=`.
- Ran `bcap sentinel run`; 3 signal events were appended.
- Ran `bcap action-board`; wrote `reports/action_boards/2026-07-09.md`.

The new pre-market signal set was BE, GLW, and SHAZ. Only GLW directly overlaps this
Thursday review. These events are research triggers, not buy signals, and must be
evaluated through thesis health, valuation, margin of safety, drawdown opportunity,
risk, and sizing.

## Sleeve Theses

Memory, storage, and foundry: AI infrastructure bottlenecks extend beyond GPUs into
HBM, NAND/storage, advanced packaging, foundry capacity, and high-performance
networking.

Semicap equipment: critical tooling, lithography, process control, and foundry
enablement can become durable bottleneck assets when AI chip demand stresses
leading-edge capacity.

AI networking and optical: AI scale-out can create scarcity in optical interconnect,
switching, and networking components needed to move data inside and between clusters.

## Sleeve State

| Ticker | Sleeve | Working Decision | Urgency | Evidence Quality | Pre-Market Finding |
|---|---|---|---:|---|---|
| MU | memory_storage_networking | RESEARCH_REQUIRED | HIGH | MARKET_NEWS_AND_LOCAL_BASELINE_NEEDS_PRIMARY_SOURCE | No new July 9 market event, but prior material MU/Anthropic memory-storage signal and memory-cycle valuation work remain unresolved. |
| SNDK | memory_storage_networking | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE | No new July 9 market event. SanDisk remains watch-only until NAND/storage recovery, separation economics, balance sheet risk, and valuation are underwritten. |
| TSM | memory_storage_networking | RESEARCH_REQUIRED | HIGH | PRIMARY_FILINGS_AND_SA_13F | No new July 9 market event. TSM has the strongest underlying bottleneck case, but current decision and action board still require research before adding capital. |
| ASML | semicap_equipment | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE | No new July 9 market event. ASML remains the cleanest tooling scarcity asset, but valuation, China/export-control risk, and SA put-signal interpretation remain gating items. |
| INTC | semicap_equipment | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE | No new July 9 market event. Intel's strategic foundry option remains blocked by execution, capital intensity, process-roadmap, and put-signal uncertainty. |
| ONTO | semicap_equipment | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | No new July 9 market event. Onto remains a plausible advanced-packaging/process-control proxy, but cyclicality versus unique AI bottleneck status is unresolved. |
| GLW | ai_networking_optical | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE_PLUS_07_09_DIP | New GLW dip trigger appended. Corning's datacenter optical/fiber upside remains too diluted by non-AI end markets and put-signal ambiguity for new capital. |
| LITE | ai_networking_optical | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | No new July 9 market event. Lumentum remains an adjacent proxy until AI/datacom demand clearly offsets telecom cyclicality and valuation clears. |
| MRVL | ai_networking_optical | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | No new July 9 market event. Marvell remains a plausible AI networking/custom-silicon beneficiary, but contract cadence, margins, valuation, and adjacent-proxy status require review. |

## Decision Discipline

No `BUY_NOW` candidate exists. TSM has the highest-quality evidence set and the strongest
upstream bottleneck thesis, but the current decision file and action board still mark it
`RESEARCH_REQUIRED`; this blocks new capital until the unresolved signal backlog,
valuation, geopolitical/customer-concentration, and filing-source issues are resolved.

No `ADD_ON_DIP` is approved. GLW's new July 9 dip trigger is bounded as a research event,
not an entry. A dip can only become actionable after the cause is bounded, thesis damage
is ruled out, valuation improves materially, the asset is dip-buy eligible, and sizing is
explicit.

No sell is triggered. A sell or thesis-correction review becomes mandatory if a future
public filing shows a full Situational Awareness exit, a material SA reduction weakens
thesis weight, primary filings break the named bottleneck thesis, valuation/risk becomes
unacceptable, or the asset no longer expresses the intended sleeve.

## Priority Review Queue

1. GLW: review the new July 9 dip event against AI optical/fiber earnings contribution,
   non-AI segment dilution, SA put-signal context, and valuation.
2. TSM: reconcile the strong primary-source case with the current `RESEARCH_REQUIRED`
   decision, action-board constraint, SA exposure, valuation band, and geopolitical risk.
3. MU and SNDK: verify memory/storage demand, customer economics, cycle-normalized
   valuation, balance sheet risk, and whether AI demand is structural rather than
   cyclical beta.
4. ASML, INTC, and ONTO: separate monopoly-like tooling/foundry bottleneck quality from
   semicap cycle risk, export controls, capex digestion, and execution risk.
5. LITE and MRVL: confirm whether AI networking/optical demand is a durable bottleneck or
   an adjacent cyclical recovery before approving any capital.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- No approved SEC mirror/proxy or filing vendor feed is configured, so filing recovery
  remains required before filing-window confidence can be restored.
- Alpaca credentials are absent; market ingestion is using Yahoo fallback.
- Active unresolved signal backlog remains material and blocks all reviewed sleeve
  capital actions.

## Next Scheduled Work

- 09:45 open dislocation scan: use current market context through valuation, thesis, and
  sizing discipline; do not use technical indicators.
- 10:45 sentinel check: prefer `bcap live-check` only if filing recovery is configured;
  otherwise continue market-only recovery and keep the filing gap visible.
- Research review should use `bcap signal resolve` for reviewed events rather than
  hand-editing historical JSONL rows.
