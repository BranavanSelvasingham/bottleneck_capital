# Bottleneck Capital Weekly Sleeve Review

Date: 2026-07-15
Window: 07:15 pre-market thesis scan
Sleeve: `miner_to_datacenter`
Schedule source: Wednesday weekly sleeve rotation
Source mode: local source-of-truth files plus live market ingest

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: APLD, BTDR, CLSK, CORZ, HIVE, IREN, RIOT.
- RESEARCH_REQUIRED: BITF.
- TRIM / SELL WATCH: none.
- SELL: none.

No miner-to-datacenter capital action is authorized by this wake. The sleeve still has
power/site optionality, but the investable question is whether each miner can convert
Bitcoin-mining infrastructure into durable contracted AI/HPC datacenter economics without
diluting away site value. The current source-of-truth decisions keep most names on HOLD
and keep BITF/KEEL blocked by mapping and thesis-fit uncertainty. Active high-priority
price-dislocation signals remain visible for APLD, BTDR, BITF, CLSK, HIVE, IREN, and
RIOT, but they are not buy signals. The long-only mandate remains unchanged; reported
puts are signal-only and are not trade instructions. No technical indicators are used.

## Pre-Market Process

- Current America/Toronto time at wake: 2026-07-15 07:25.
- Checked for lock files and active Bottleneck scheduled processes: no active conflict
  found.
- The worktree was already dirty from prior scheduled outputs, but no same-file active
  writer was detected, so the due process continued with scoped writes.
- Confirmed no `BCAP_SEC_*` or `BCAP_FILING_*` recovery source is configured.
- Ran `bcap ingest market` with approved live network access; Yahoo fallback succeeded
  and wrote 3 market events to `state/latest_market_events.jsonl` and
  `state/latest_events.jsonl`.
- Did not run SEC filing ingest because the active SEC 403/backoff filing gap remains
  unresolved and no approved SEC mirror/proxy or `BCAP_FILING_EVENTS_URL` feed is
  configured.
- Refreshed local held-position prices from market snapshots: `updated=7`, `missing=`.
- Ran `bcap sentinel run`; 3 signal events were appended.
- Ran `bcap action-board`; wrote `reports/action_boards/2026-07-15.md`.
- Fresh July 15 pre-market signals were ASML, WYFI, and NBIS. ASML was moved from HOLD
  to RESEARCH_REQUIRED because the new unresolved material price dislocation needs
  primary-source review before capital. WYFI and NBIS were already RESEARCH_REQUIRED.

## Sleeve Thesis

Some miners own scarce power, land, interconnection, and electrical infrastructure that
may be repurposed into higher-value AI/HPC datacenter capacity. The capital question is
whether each ticker can move from Bitcoin beta into durable contracted compute
infrastructure with financeable customer contracts, credible delivery timelines, and
valuation support.

## Sleeve State

| Ticker | Working Decision | Urgency | Evidence Quality | Pre-Market Finding |
|---|---|---:|---|---|
| APLD | HOLD | HIGH | SA_FILING_AND_LOCAL_BASELINE | Active high-priority dip signals remain visible. Applied Digital may monetize power and sites into AI/HPC datacenter capacity, but contract quality, customer economics, financing, delivery risk, and valuation still need primary-source support before any add. |
| BTDR | HOLD | HIGH | SA_FILING_AND_LOCAL_BASELINE | Active high-priority dip signals remain visible. Bitdeer has power and infrastructure optionality, but the thesis is mixed across mining, ASICs, and possible HPC capacity; contract economics and valuation still need review. |
| BITF | RESEARCH_REQUIRED | HIGH | LIVE_MARKET_GAP_AND_SEC_BROWSE_ATOM | BITF live-market coverage maps to KEEL / Keel Infrastructure in `configs/live_sources.yaml`; thesis fit, successor symbol, SA mapping, and asset base remain unresolved. No capital action. |
| CLSK | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Active high-priority dip signal remains visible. CleanSpark may own useful power/site optionality, but AI datacenter economics are not yet primary-source visible enough versus mining beta. |
| CORZ | HOLD | HIGH | SA_FILING_AND_LOCAL_BASELINE | One of the cleaner miner-to-HPC conversion candidates, but contract terms, capacity delivery, customer concentration, financing, leverage, and valuation still need a stronger source refresh before promotion. |
| HIVE | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Active high-priority dip signal remains visible. HIVE has a plausible HPC pivot, but GPU/HPC revenue, contracts, financing, and margin durability are not yet clear enough versus mining beta. |
| IREN | HOLD | HIGH | SA_FILING_AND_LOCAL_BASELINE | Active high-priority dip signal remains visible. IREN is a high-priority power/site conversion candidate, but new capital needs verified AI/HPC economics, customer contracts, financing terms, and dilution control. |
| RIOT | HOLD | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Active high-priority dip signals remain visible. Riot has power and site optionality, but the long-only case is not clean enough until datacenter conversion, contracted demand, and valuation are primary-source supported. |

## Decision Discipline

No `BUY_NOW` candidate exists. None of the sleeve names currently satisfies the required
buy conditions: strong thesis health, acceptable valuation, clean sleeve expression,
portfolio sizing allowance, understood anti-thesis, explicit sizing response, and an
invalidation trigger supported by current evidence.

No `ADD_ON_DIP` is approved. The action board bounds several miner dips as broad
cross-book de-risking, but bounded cause is not buy approval. Each candidate still
requires primary-source review, valuation work, and explicit sizing before any capital
action.

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
   converting any bounded dip into ADD_ON_DIP.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- The action board has an active `filing_data_gap`; direct SEC and SEC browse Atom access
  previously returned repeated 403 responses, and a different approved filing data path is
  required.
- No `BCAP_SEC_*`, `BCAP_FILING_*`, or `APCA_*` recovery credentials were visible in the
  current environment.
- Market ingest is live and fresh as of 2026-07-15T07:26:01-04:00, with Yahoo fallback
  and no missing tickers.
- Active unresolved signal backlog remains material and should be resolved with
  `bcap signal resolve` only after research review; historical JSONL rows should not be
  hand-edited.

## Next Scheduled Work

- 09:45 open dislocation scan: use current market context through valuation, thesis, and
  sizing discipline; do not use technical indicators.
- 10:45 sentinel check: prefer `bcap live-check` only if filing recovery is configured;
  otherwise continue market-only recovery and keep the filing gap visible.
- Research review should prioritize BITF/KEEL mapping and the APLD, BTDR, IREN, and CORZ
  conversion-economics checks before any sleeve promotion.
