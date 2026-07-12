# Bottleneck Capital Weekend Thesis Rebuild

Date: 2026-07-04
Sleeve: `crowded_ai_beta_hedge`
Schedule source: Saturday weekend thesis rebuild
Source mode: local source-of-truth files only

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: NVDA.
- RESEARCH_REQUIRED: AMD, AVGO, SMH.
- TRIM / SELL WATCH: none.
- SELL: none.

No capital action is authorized from this rebuild. The sleeve remains a risk-control and
valuation-discipline sleeve under the long-only mandate. Reported puts are treated as
signal-only evidence of crowded AI beta, not as instructions to short or buy puts.

## Rebuilt Sleeve Thesis

The crowded AI beta hedge sleeve exists to prevent the portfolio from overpaying for the
most consensus AI winners. The core signal is not that these assets must be avoided; it
is that downside/crowding pressure should raise the entry hurdle, lower initial sizing,
and force explicit invalidation before any long-only capital is added.

The sleeve should therefore separate three roles:

1. Clean long-only bottleneck exposure with crowding risk: NVDA and AMD.
2. Signal-only downside/crowding map: AVGO and SMH under the current files.
3. Portfolio synthesis input: use this sleeve to compare AI beta risk against cleaner
   bottleneck expressions in power, memory, networking, semicap, and compute.

## Current Sleeve State

| Ticker | Working Decision | Role | Finding |
|---|---|---|---|
| AMD | RESEARCH_REQUIRED | common equity with put signal | Second-source accelerator upside exists, but execution, datacenter traction, margins, valuation, and active dip signals remain unresolved. |
| AVGO | RESEARCH_REQUIRED | reported put signal | Strong AI/custom silicon business, but current local policy treats it as signal-only until a separate long-only thesis, valuation, sizing, and invalidation are documented. |
| NVDA | HOLD | common equity with put signal | Highest-quality AI accelerator bottleneck, but valuation/crowding risk keeps it at hold/watch rather than buy-now. |
| SMH | RESEARCH_REQUIRED | common equity with put signal | Useful market-wide semiconductor beta signal, but too broad to express the best single-name Bottleneck Capital theses right now. |

## Portfolio Synthesis

The sleeve argues for patience rather than broad AI-beta accumulation. If capital is added
on Monday or later, it should go first to names where a specific bottleneck mechanism,
primary-source evidence, valuation, sizing, and invalidation are clearer than broad
semiconductor beta exposure.

NVDA remains the quality benchmark. AMD can only graduate if accelerator traction and
margin evidence improve enough to compensate for execution risk. AVGO and SMH should not
receive capital without a new long-only thesis package; they remain useful as crowding
and valuation-warning inputs.

## Decision Discipline

No `BUY_NOW` candidate satisfies all required buy conditions. NVDA has the cleanest thesis
quality, but the current files do not clear valuation and crowding risk enough to authorize
a new tranche. AMD has potential upside but remains research-first. AVGO and SMH are
signal-only under the current mandate.

No `ADD_ON_DIP` candidate is approved. The active dip signals for AMD, AVGO, and SMH are
research triggers only. A dip cannot become an add until cause is bounded, no thesis damage
is found, valuation work materially improves, and sizing/invalidation are explicit.

No sell is triggered. A sell or thesis-correction review becomes mandatory if public SA
filings show a full exit, a material SA reduction weakens thesis weight, or company filings,
IR, customer evidence, margins, export controls, or platform demand break the named thesis.

## Priority Review Queue

1. NVDA: update valuation and sizing discipline versus datacenter earnings durability,
   export controls, customer concentration, and accelerator competition.
2. AMD: verify AI accelerator roadmap traction, datacenter customer evidence, margin path,
   and whether the thesis is strong enough to offset NVIDIA ecosystem strength.
3. AVGO: decide whether it remains signal-only or deserves a separate long-only custom
   silicon/networking thesis with valuation, sizing, and invalidation.
4. SMH: keep as a broad beta/crowding signal; do not promote without a separate ETF-level
   long-only thesis.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was 2026-06-22T14:32:37-04:00.
- Market ingest is stale as of this Saturday rebuild because Friday, 2026-07-03 was an
  observed U.S. market holiday and no weekend market refresh was attempted.
- Active signal backlog remains material, including AMD, AVGO, and SMH dip signals.
- Filing-window recovery remains required before any primary-source-dependent promotion.

## Monday Operating Plan

- Keep AMD, AVGO, and SMH at RESEARCH_REQUIRED and NVDA at HOLD unless primary-source
  research clears the active material events.
- Do not resolve old signal rows by hand. After research review, use `bcap signal resolve`
  with a concrete reason.
- Use long-only sizing and higher valuation hurdles as the substitute for puts or shorts.
- Resume market-day scans only after the next valid market-day window; do not treat the
  holiday/weekend stale market warning as a trade signal.
