# Bottleneck Capital Weekly Sleeve Review

Date: 2026-06-30
Sleeve: `power_bottleneck`
Schedule source: Tuesday weekly sleeve rotation

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: VST, CEG.
- RESEARCH_REQUIRED: BW, BE, PSIX, PUMP, SEI, TE, TLNE.
- Adjacent equipment carry-over: VRT and WTS remain RESEARCH_REQUIRED, but are not promoted inside the primary power-bottleneck sleeve.
- TRIM / SELL WATCH: none.
- SELL: none.

No power-bottleneck capital action is authorized before primary-source review resolves
the active dip-signal backlog, stale filing ingest, and asset/decision-file state
differences. This review uses local source files only; it does not use technical
indicators.

## Sleeve Thesis

The power bottleneck thesis is that AI datacenter demand makes fast, reliable,
contracted power a scarce input. The cleanest candidates should either own scarce
generation, enable rapidly deployable onsite power, or sell equipment/services with
direct evidence of durable datacenter demand. The gating question is whether each
ticker has a verified AI power bottleneck link rather than generic utility, industrial,
energy-services, or policy-cycle exposure.

## Sleeve State

| Ticker | Working Decision | Urgency | Source Class | Review Finding |
|---|---|---:|---|---|
| BE | RESEARCH_REQUIRED | HIGH | sa_reported_current_13f | Direct onsite-power candidate, but fuel-cell economics, financing/product risk, and datacenter backlog conversion remain unresolved. |
| BW | RESEARCH_REQUIRED | MEDIUM | sa_reported_current_13f | Possible power-services fit, but leverage, liquidity, and backlog quality keep it research-first. |
| PSIX | RESEARCH_REQUIRED | MEDIUM | sa_reported_current_13f | Genset/engine exposure could benefit from power scarcity, but durable datacenter/customer backlog is not yet proven. |
| PUMP | RESEARCH_REQUIRED | MEDIUM | sa_reported_current_13f | AI power link is less direct; oilfield-services cyclicality may dominate. |
| SEI | RESEARCH_REQUIRED | MEDIUM | sa_reported_current_13f | Distributed power thesis needs proof that contracted demand is scaling beyond legacy end markets. |
| TE | RESEARCH_REQUIRED | MEDIUM | sa_reported_current_13f | Current SA-tracked name, but business model, financing, capacity value, and customer demand remain unclear. |
| VST | HOLD | MEDIUM | sa_adjacent_historical_or_thesis_proxy | Strong power-scarcity proxy, but not latest-current SA exposure and not an automatic long-only buy. |
| CEG | HOLD / WATCH_TOP | MEDIUM | sa_adjacent_thesis_proxy | Highest-quality nuclear scarcity proxy in the sleeve, but still needs priced-entry and valuation work before any add. |
| TLNE | RESEARCH_REQUIRED | MEDIUM | sa_adjacent_historical_or_thesis_proxy | Power-scarcity proxy, but not latest-current SA exposure; contract/regulatory risk and promotion evidence remain unresolved. |

## Adjacent Equipment Carry-Over

VRT and WTS are `ai_power_equipment`, not primary `power_bottleneck`, but their unresolved
events are relevant to the same datacenter-infrastructure bottleneck. VRT remains
RESEARCH_REQUIRED because datacenter power/thermal backlog and valuation risk have not
been cleared. WTS remains RESEARCH_REQUIRED after the 2026-06-29 close-board addition;
the datacenter water/thermal read-through is still too indirect for capital.

## Decision Discipline

No `BUY_NOW` candidate exists because none of the primary power-bottleneck names
currently satisfies all required buy conditions: strong thesis health, acceptable
valuation, clean sleeve expression, portfolio sizing allowance, understood anti-thesis,
explicit sizing response, and invalidation trigger.

No `ADD_ON_DIP` candidate is approved. Several power names have active dip signals, but
a price dislocation is only a research trigger. It does not become an add until the dip
cause is bounded, no thesis damage is found, valuation work improves materially, and a
starter-size cap is specified.

No sell is triggered. A sell or thesis-correction review becomes mandatory if public SA
filings show a full exit, a material SA reduction weakens the thesis weight, or
company filings/IR/customer evidence breaks the named power-bottleneck thesis.

## Priority Review Queue

1. BE: verify datacenter backlog conversion, customer quality, financing/product risk,
   warranty exposure, and gross-margin path.
2. CEG: complete valuation work for the WATCH_TOP case; promote only if a bounded
   pullback plus at least 50% plausible upside can be underwritten.
3. TLNE and VST: compare contracted datacenter power economics, regulatory risk, and
   margin of safety versus CEG before any promotion.
4. PSIX, SEI, BW, PUMP, and TE: verify whether each business has direct, durable AI
   power-bottleneck exposure or mostly cyclical/industrial exposure.
5. VRT and WTS: keep adjacent equipment events visible, but do not treat them as
   primary sleeve actions without separate evidence and valuation review.

## Source Reconciliation

The stricter working state is the action board plus `research/decisions/*.md`: BW, BE,
PSIX, PUMP, SEI, TE, TLNE, VRT, and WTS are RESEARCH_REQUIRED, while VST and CEG remain
HOLD/watch. Several `research/assets/*.md` files still show older HOLD frontmatter for
power names. Do not hand-edit old signal rows; after primary research, resolve reviewed
signal events with `bcap signal resolve` and update both asset and decision files only
if the decision itself changes.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- Market ingest is current through the 2026-06-29 close-board refresh:
  2026-06-29T16:22:52-04:00 via `market_yahoo`.
- Active signal backlog remains material for power names, including unresolved dip
  triggers for BE, BW, PSIX, PUMP, SEI, TE, TLNE, VRT, and WTS.
- Filing-window recovery remains required before any primary-source-dependent promotion
  because SEC/fallback live filing coverage is stale in local state.

## Tuesday Operating Plan

- At 07:15, run the scheduled pre-market thesis scan and refresh market data if live
  sources are available.
- If filing recovery is still unconfigured, avoid repeating the known SEC gap and keep
  the filing_data_gap visible on the action board.
- Keep BE, BW, PSIX, PUMP, SEI, TE, TLNE, VRT, and WTS at RESEARCH_REQUIRED until
  primary-source review clears the active material events and reconciles asset/decision
  file state.
