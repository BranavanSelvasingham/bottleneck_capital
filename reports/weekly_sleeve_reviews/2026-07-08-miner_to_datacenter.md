# Bottleneck Capital Weekly Sleeve Review

Date: 2026-07-08
Window: 07:15 pre-market thesis scan
Sleeve: `miner_to_datacenter`
Schedule source: Wednesday weekly sleeve rotation
Source mode: local source-of-truth files plus live market ingest

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: none under the current sleeve decision files.
- RESEARCH_REQUIRED: APLD, BITF, BTDR, CLSK, CORZ, HIVE, IREN, RIOT.
- TRIM / SELL WATCH: none.
- SELL: none.

No miner-to-datacenter capital action is authorized before the active signal backlog,
the new pre-market signal set, filing-source recovery, valuation work, and
primary-source review are cleared. The long-only mandate remains unchanged. Reported
puts are signal-only and are not trade instructions. No technical indicators are used.

## Pre-Market Process

- Checked for active run locks and conflicting Bottleneck processes: none found.
- Confirmed no `BCAP_SEC_*`, `BCAP_FILING_*`, `APCA_*`, or `SEC_*` recovery variables
  are configured.
- Ran `bcap ingest market` with live network access; Yahoo fallback succeeded and wrote
  29 market events to `state/latest_market_events.jsonl` and `state/latest_events.jsonl`.
- Did not run SEC filing ingest because no approved SEC mirror/proxy or filing vendor
  feed is configured and prior runs show repeated SEC 403/backoff failures.
- Refreshed local position prices from snapshots: `updated=6`, `missing=`.
- Ran `bcap sentinel run`; 29 signal events were appended.
- Ran `bcap action-board`; wrote `reports/action_boards/2026-07-08.md`.

The new market events are pre-market context from the latest available regular-market
provider snapshot, not buy signals. They are research triggers to be evaluated through
thesis health, valuation, margin of safety, drawdown opportunity, risk, and sizing.

## Sleeve Thesis

Some miners own scarce power, land, interconnection, and electrical infrastructure that
may be repurposed into higher-value AI/HPC datacenter capacity. The capital question is
whether each ticker can move from Bitcoin beta into durable contracted compute
infrastructure with financeable customer contracts, credible delivery timelines, and
valuation support.

## Sleeve State

| Ticker | Working Decision | Urgency | Evidence Quality | Pre-Market Finding |
|---|---|---:|---|---|
| APLD | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE_PLUS_07_08_DIP | New dip trigger appended. Applied Digital may monetize power and sites into AI/HPC datacenter capacity, but contract quality, customer economics, financing, delivery risk, and valuation remain unresolved. |
| BITF | RESEARCH_REQUIRED | HIGH | LIVE_MARKET_GAP_AND_SEC_BROWSE_ATOM_PLUS_07_08_DIP | New dip trigger appended. BITF/KEEL mapping remains unresolved; do not treat this as buyable until the successor symbol, asset base, SA mapping, and miner-to-datacenter thesis fit are corrected. |
| BTDR | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE_PLUS_07_08_DIP | New dip trigger appended. Bitdeer has power and infrastructure optionality, but the thesis is still mixed across mining, ASICs, and possible HPC capacity; contract economics and valuation need primary-source review. |
| CLSK | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE_PLUS_07_08_DIP | New dip trigger appended. CleanSpark may own useful power/site optionality, but current posture is watch-only until AI datacenter economics become primary-source visible and less mining-beta driven. |
| CORZ | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE_PLUS_07_08_DIP | New dip trigger appended. Core Scientific is one of the cleaner miner-to-HPC conversion candidates, but contract terms, capacity delivery, customer concentration, financing, leverage, and valuation remain unresolved. |
| HIVE | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE_PLUS_07_08_DIP | New dip trigger appended. HIVE has a plausible HPC pivot, but GPU/HPC revenue, contracts, financing, and margin durability are not yet clear enough versus mining beta. |
| IREN | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE_PLUS_07_08_DIP | New dip trigger appended. IREN is a high-priority power/site conversion candidate, but new capital needs verified AI/HPC economics, customer contracts, financing terms, and dilution control. |
| RIOT | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE_PLUS_07_08_DIP | New dip trigger appended. Riot has power and site optionality, but the long-only case is not clean enough until datacenter conversion, contracted demand, and valuation are primary-source supported. |

## Decision Discipline

No `BUY_NOW` candidate exists. None of the sleeve names currently satisfies the required
buy conditions: strong thesis health, acceptable valuation, clean sleeve expression,
portfolio sizing allowance, understood anti-thesis, explicit sizing response, and an
invalidation trigger supported by current evidence.

No `ADD_ON_DIP` is approved. The action board bounds several dips as broad cross-book
de-risking, but bounded cause is not buy approval. Each candidate still requires
primary-source review, valuation work, and explicit sizing before any capital action.

No sell is triggered. A sell or thesis-correction review becomes mandatory if public
filings show a full Situational Awareness exit, a material SA reduction weakens thesis
weight, company filings or IR evidence break the named conversion thesis, financing
dilutes away site value, customer contracts fail to materialize, or BITF/KEEL mapping
resolves against the intended exposure.

## Priority Review Queue

1. BITF: resolve BITF/KEEL symbol, corporate-action, source mapping, and SA exposure
   before any capital action.
2. IREN, CORZ, APLD, and BTDR: verify contracted AI/HPC customer economics, power/site
   capacity, capex and financing, delivery timelines, and valuation.
3. CLSK, HIVE, and RIOT: separate mining beta from real datacenter conversion revenue,
   contracts, and margin contribution.
4. Across the sleeve: complete valuation, local sizing, and invalidation review before
   lifting any `cap 0%` action-board constraint.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- No approved SEC mirror/proxy or filing vendor feed is configured, so filing recovery
  remains required before filing-window confidence can be restored.
- Alpaca credentials are absent; market ingestion is using Yahoo fallback.
- Active unresolved signal backlog remains material and blocks all miner-to-datacenter
  capital actions.

## Next Scheduled Work

- 09:45 open dislocation scan: use current market context through valuation, thesis, and
  sizing discipline; do not use technical indicators.
- 10:45 sentinel check: prefer `bcap live-check` only if filing recovery is configured;
  otherwise continue market-only recovery and keep the filing gap visible.
- Research review should use `bcap signal resolve` for reviewed events rather than
  hand-editing historical JSONL rows.
