---
ticker: BITF
name: Bitfarms
sleeve: miner_to_datacenter
last_updated: 2026-07-25
source_classification: sa_reported_current_13f
instrument_role: common_equity
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: true
evidence_quality: RESOLVER_MEMO_PM_REVIEW
thesis_expressed: BITF was tracked as a Bitfarms power/site option; live checks now verify the successor market symbol as KEEL / Keel Infrastructure Corp., with Bitfarms Ltd as a former name dated 2026-03-31.
anti_thesis: Keel may no longer express the intended miner-to-datacenter thesis, making SA-mirroring conclusions unreliable until the rebrand, asset base, and current strategic focus are reviewed.
hedge_or_sizing: No puts or shorts; maintain zero/add-none sizing and do not treat BITF/KEEL as buyable until SA mapping and thesis fit are corrected.
invalidation_trigger: Confirmed Keel no longer expresses the intended miner-to-datacenter exposure, or SA/public filing mapping no longer supports tracking this name as current SA exposure.
next_trigger: Refresh the next primary catalyst, valuation, financing where relevant, and live filing coverage before changing capital.
one_line_rationale: "RESEARCH_REQUIRED / NO ADD: the BITF memo bounds the prior move, but current valuation, catalyst, financing, or live-source evidence remains insufficient for capital."
asset_role: Miner-to-datacenter optionality.
default_holding_period: multi_year
current_decision: RESEARCH_REQUIRED
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: HIGH
last_primary_source_check: 2026-07-20
thesis_health_score: 20
confidence_score: 60.0
valuation_attractiveness_score: 0
urgency_score: 90
max_position_weight_pct: 0
current_position_weight_pct: 0
approved_entry_zone: No new capital until scheduled scan validates valuation.
do_not_buy_zone: Any price without thesis, valuation, sizing, and invalidation.
sell_trigger_status: false
hedge_required: true
main_hedge: No puts or shorts; maintain zero/add-none sizing until SA mapping and thesis fit are verified.
open_questions_count: 3
broken_thesis: ""
action_tier: RESEARCH_REQUIRED
---
# BITF - Bitfarms

## 0. Current Decision

### Simple decision

Current action: RESEARCH_REQUIRED

### One-line decision

BITF was tracked as a Bitfarms power/site option; live checks now verify the successor market symbol as KEEL / Keel Infrastructure Corp., with Bitfarms Ltd as a former name dated 2026-03-31.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | UNRESOLVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Keel may no longer be the intended miner-to-datacenter exposure. |
| Main upside driver today | None actionable until Keel's post-rebrand assets, strategy, and SA mapping are reviewed. |
| Next review trigger | Research KEEL thesis fit and SA mapping |

## 1. Role in Bottleneck Capital

Sleeve: `miner_to_datacenter`

Why this asset belongs here: Miner-to-datacenter optionality.

What this asset is actually a bet on:

1. Confirming whether KEEL remains the right live-market expression of the old BITF/Bitfarms SA exposure.
2. Confirming whether Keel's post-rebrand asset base still fits the miner-to-datacenter sleeve.
3. Long-only discipline preventing action until SA mapping and thesis fit are verified.

What this asset is not a bet on:

- Keel may not represent the intended miner-to-datacenter exposure after the rebrand.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: RESEARCH_REQUIRED
Confidence: 20
Time horizon: multi-year
Importance: HIGH

Claim: BITF was tracked as a Bitfarms power/site option; live checks now verify the successor market symbol as KEEL / Keel Infrastructure Corp., with Bitfarms Ltd as a former name dated 2026-03-31.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_2/BITF.md; wave execution memo.
- Live market probe, 2026-06-22, returned active Yahoo chart data for `KEEL` and `KEEL.TO`; `BITF` returned 404.
- SEC browse Atom query for BITF, 2026-06-22, returned CIK 0001812477, conformed name Keel Infrastructure Corp., and Bitfarms Ltd as a former name dated 2026-03-31.
- `configs/live_sources.yaml` now maps internal ticker `BITF` to market provider symbol `KEEL`.
- Sleeve thesis: `miner_to_datacenter`.

Evidence against:
- Keel may no longer express the intended miner-to-datacenter exposure.
- Price, valuation, and SA-mirroring conclusions are unreliable until the post-rebrand thesis is reviewed.

What would break it:
- Confirmed Keel no longer expresses the intended miner-to-datacenter exposure, or SA/public filing mapping no longer supports tracking this name as current SA exposure.

Decision impact:
RESEARCH_REQUIRED. Do not add capital until SA mapping, thesis fit, valuation, and sizing
are corrected.

Hedge implication:
No puts or shorts; maintain zero/add-none sizing until the thesis mapping issue is resolved.

### Thesis B - Valuation thesis

Status: NOT ACTIONABLE
Claim: valuation is not usable until Keel's post-rebrand thesis mapping is verified.

### Thesis C - Catalyst thesis

Status: IDENTITY-DRIVEN
Claim: KEEL thesis review is required before normal filing, IR, financing,
customer-contract, guidance, or dip signals can be interpreted as buyable.

## 3. Market-Implied View vs Variant View

What the market seems to believe:
- The public company has rebranded to Keel and the market now prices the successor symbol.
- A higher share price and strategic shift may reflect new expectations for HPC/AI infrastructure.

Our variant view:
- The SA signal is useful for prioritization, not a trade instruction.
- The ticker identity must be corrected before this name can be used as a live market signal.

Why we may be wrong:
- The SEC/Yahoo mismatch may reflect a provider lag or corporate action that still preserves some economic continuity.
- The intended exposure may trade under a different ticker or venue.

Is the variant view big enough to matter?
NO. The variant view is not actionable until current instrument identity is verified.

## 4. Long-Term Ownership Quality

| Dimension | Score | Notes |
|---|---:|---|
| Thesis purity | 1 | Ticker identity mismatch makes thesis expression unresolved. |
| Durability | 3 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 2 | Main risk: Bitcoin price beta, dilution, conversion capex, and weak customer evidence. |
| Management / execution | 2 | Execution still matters. |
| Strategic scarcity | 2 | Upside: Power portfolio monetization, AI/HPC conversion, or strategic site value. |
| Contract quality | 2 | Needs source-event verification. |
| Customer quality | 2 | Needs source-event verification. |
| Pricing power | 2 | Valuation frame: power-site value versus mining NAV and funding dilution. |
| Downside survivability | 2 | Invalidation: No credible AI/HPC path emerges and economics remain dominated by mining exposure. |
| Hedgeability | 2 | Long-only hedge is sizing/no action. |

Long-term owner score: 22 / 50

## 5. Valuation and Entry Discipline

Valuation frame: not actionable until ticker identity is verified.

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Disabled until ticker identity is corrected | Reconcile BITF corporate action/current symbol first |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST, but not actionable while ticker identity is unresolved.

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- Confirmed current instrument is no longer the intended Bitfarms / miner-to-datacenter exposure.
- SA/public filing mapping no longer supports tracking this name as current SA exposure.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Ticker identity or corporate-action mismatch.
- Treating a stale SA/public-filing name as current live exposure.
- Interpreting missing or wrong-symbol quotes as a valuation signal.

## 9. Hedge Map

No puts or shorts; maintain zero/add-none sizing until ticker identity, SA mapping, and thesis
fit are verified.

## 10. Latest Signals

- Wave: 2
- Source classification: `sa_reported_current_13f`, pending reconciliation with current
  corporate action and trading symbol.
- Instrument role: `common_equity`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_2/BITF.md`
- `reports/initialization/2026-06-20-wave-2-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- What is the current trading symbol and venue for the intended Bitfarms exposure?
- Does the latest SA/public-filing mapping still refer to this instrument after the corporate action?
- Should configs/watchlist.yaml and configs/sa_universe.yaml be updated to a successor ticker or removed from live-action coverage?

## 13. Latest Agent Notes

2026-06-22 live hardening scan found BITF no longer resolves through the live market data
fallback and SEC browse maps the identifier to Keel Infrastructure Corp. with Bitfarms Ltd
as a former name. Current action changed to RESEARCH_REQUIRED; no BUY_NOW, ADD_ON_DIP,
TRIM, or SELL action is authorized until the corporate-action mapping is reconciled.
