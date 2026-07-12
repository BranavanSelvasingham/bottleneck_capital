# Bottleneck Capital Weekly Sleeve Review

Date: 2026-06-29
Sleeve: `compute_infra`
Schedule source: Monday weekly sleeve rotation

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: none as the stricter working state.
- RESEARCH_REQUIRED: CRWV, NBIS, SHAZ, WYFI.
- TRIM / SELL WATCH: none.
- SELL: none.

No compute-infra capital action is authorized before Monday market/filing scans and
primary-source review clear the unresolved signal backlog. This review uses local source
files only; it does not use technical indicators.

## Sleeve Thesis

AI model demand can create durable scarcity in contracted, power-secured compute
capacity, especially where supply can be delivered faster than hyperscaler build cycles.
For this sleeve, the gating question is whether each ticker owns durable contracted
compute capacity or is merely levered/speculative GPU exposure.

## Sleeve State

| Ticker | Working Decision | Urgency | Evidence Quality | Review Finding |
|---|---|---:|---|---|
| CRWV | RESEARCH_REQUIRED | HIGH | LIVE_PRICE_DISLOCATION_REVIEWED_NO_NEW_FILING | Direct compute scarcity expression, but company-specific event review, customer concentration, leverage, GPU supply commitments, and utilization economics remain unresolved. |
| NBIS | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE | Post-quarter SA clue and AI cloud candidate, but jurisdiction, funding, customer proof, and utilization evidence remain gating risks. |
| SHAZ | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Current public SA exposure, but liquidity, governance, asset verification, and customer economics remain below the capital-action threshold. |
| WYFI | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Current public SA exposure and bounded broad de-risking dip cause, but public evidence, liquidity, financing quality, and contract economics remain unresolved. |

## Decision Discipline

No `BUY_NOW` candidate exists because none of the four names currently satisfies all
required buy conditions: strong thesis health, acceptable valuation, clean sleeve
expression, portfolio sizing allowance, understood anti-thesis, explicit sizing response,
and invalidation trigger.

No `ADD_ON_DIP` candidate is approved. Friday's dip review bounds the WYFI, SHAZ, and
NBIS dislocations as broad cross-book de-risking and flags CRWV as a company-specific
event review, but bounded cause is not buy approval. Each name still needs primary-source
review, valuation work, and sizing discipline before any add.

No sell is triggered. A sell or thesis-correction review would become mandatory if public
filings show a full SA exit, a material SA reduction weakens thesis weight, or company
filings/IR/financing/customer evidence breaks the named compute-infra thesis.

## Priority Review Queue

1. CRWV: resolve whether the company-specific event affects customer concentration,
   leverage, GPU supply commitments, utilization, or refinancing risk.
2. NBIS: verify customer demand, utilization, funding runway, and jurisdiction risk from
   primary sources.
3. WYFI: verify durable compute assets, financing quality, liquidity, and contract
   economics before treating the dip as actionable.
4. SHAZ: verify durable compute assets, governance, liquidity, and customer economics
   before any capital action.

## Source Reconciliation

The stricter working state is the action board plus `research/decisions/*.md`, where all
four compute-infra names are `RESEARCH_REQUIRED`. Some asset files still show older
`HOLD` text for NBIS, SHAZ, and WYFI. Do not hand-edit old signal rows; after primary
research, resolve reviewed signal events with `bcap signal resolve` and update both
asset and decision files only if the decision itself changes.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- Market ingest remains stale from Friday close: last successful market ingest was
  2026-06-26T16:22:23-04:00.
- Active signal backlog remains material, including unresolved compute-infra dip triggers
  for CRWV, NBIS, SHAZ, and WYFI.
- No SEC recovery variables or approved filing vendor/proxy feed are visible in local
  state; filing-window recovery remains required.

## Monday Operating Plan

- At 07:15, run the scheduled pre-market thesis scan and refresh market data if live
  sources are available.
- Avoid `bcap live-check` if filing recovery is still unconfigured and would repeat the
  known SEC gap; use the market-only recovery path and report the filing gap.
- Keep all compute-infra names at `RESEARCH_REQUIRED` until primary-source review clears
  the active material events and reconciles asset/decision-file state.
