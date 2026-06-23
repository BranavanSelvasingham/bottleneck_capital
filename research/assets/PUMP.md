---
ticker: PUMP
name: ProPetro Holding
sleeve: power_bottleneck
last_updated: 2026-06-21
source_classification: sa_reported_current_13f
instrument_role: common_equity
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: false
evidence_quality: SA_FILING_AND_LOCAL_BASELINE
thesis_expressed: ProPetro requires caution because the AI power link is less direct than other sleeve names and may be oilfield-services exposure.
anti_thesis: Oilfield services cyclicality may dominate any power-equipment read-through.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: No primary-source evidence ties the business to durable AI power bottlenecks.
next_trigger: Next scheduled market/filing scan, SA filing change, company filing/IR update, financing or customer-contract news, guidance change, or a detected valuation dip.
one_line_rationale: "Hold/watch only: ProPetro requires caution because the AI power link is less direct than other sleeve names and may be oilfield-services exposure."
asset_role: Power-bottleneck purity test.
default_holding_period: multi_year
current_decision: HOLD
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: MEDIUM
last_primary_source_check: 2026-06-21
thesis_health_score: 35
confidence_score: 30
valuation_attractiveness_score: 20
urgency_score: 60
max_position_weight_pct: 0
current_position_weight_pct: 0
approved_entry_zone: No new capital until scheduled scan validates valuation.
do_not_buy_zone: Any price without thesis, valuation, sizing, and invalidation.
sell_trigger_status: false
hedge_required: true
main_hedge: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
open_questions_count: 0
broken_thesis: ""
---
# PUMP - ProPetro Holding

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

ProPetro requires caution because the AI power link is less direct than other sleeve names and may be oilfield-services exposure.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Thesis purity, oilfield cycle, customer concentration, and capex. |
| Main upside driver today | Electric fleet or distributed power capabilities that translate into broader power demand. |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `power_bottleneck`

Why this asset belongs here: Power-bottleneck purity test.

What this asset is actually a bet on:

1. Electric fleet or distributed power capabilities that translate into broader power demand.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- Oilfield services cyclicality may dominate any power-equipment read-through.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH
Confidence: 30
Time horizon: multi-year
Importance: HIGH

Claim: ProPetro requires caution because the AI power link is less direct than other sleeve names and may be oilfield-services exposure.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_2/PUMP.md; wave execution memo.
- Sleeve thesis: `power_bottleneck`.

Evidence against:
- Oilfield services cyclicality may dominate any power-equipment read-through.
- Thesis purity, oilfield cycle, customer concentration, and capex.

What would break it:
- No primary-source evidence ties the business to durable AI power bottlenecks.

Decision impact:
HOLD. Do not add capital until a scheduled scan or fresh primary-source event clears thesis,
valuation, and sizing.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: normalized oilfield-services earnings plus any verified power-equipment option. Current baseline does not approve a buy.

### Thesis C - Catalyst thesis

Status: EVENT-DRIVEN
Claim: New SEC filing, IR update, financing, customer contract, guidance change, SA filing
change, or detected dip can reopen the decision.

## 3. Market-Implied View vs Variant View

What the market seems to believe:
- AI infrastructure scarcity matters, but quality, timing, and valuation vary by ticker.
- Crowded AI beta and financing risk can overwhelm a correct high-level theme.

Our variant view:
- The SA signal is useful for prioritization, not a trade instruction.
- HOLD is the right baseline until valuation and primary-source evidence justify a stronger action.

Why we may be wrong:
- The company may already be a cleaner bottleneck expression than the baseline allows.
- The risk signal may be stale or purely hedge-related.

Is the variant view big enough to matter?
UNCLEAR until a scheduled scan updates primary evidence and valuation.

## 4. Long-Term Ownership Quality

| Dimension | Score | Notes |
|---|---:|---|
| Thesis purity | 2 | Power-bottleneck purity test. |
| Durability | 2 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 2 | Main risk: Thesis purity, oilfield cycle, customer concentration, and capex. |
| Management / execution | 2 | Execution still matters. |
| Strategic scarcity | 2 | Upside: Electric fleet or distributed power capabilities that translate into broader power demand. |
| Contract quality | 2 | Needs source-event verification. |
| Customer quality | 2 | Needs source-event verification. |
| Pricing power | 2 | Valuation frame: normalized oilfield-services earnings plus any verified power-equipment option. |
| Downside survivability | 1 | Invalidation: No primary-source evidence ties the business to durable AI power bottlenecks. |
| Hedgeability | 1 | Long-only hedge is sizing/no action. |

Long-term owner score: 18 / 50

## 5. Valuation and Entry Discipline

Valuation frame: normalized oilfield-services earnings plus any verified power-equipment option

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker PUMP` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- No primary-source evidence ties the business to durable AI power bottlenecks.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Thesis purity, oilfield cycle, customer concentration, and capex.
- Oilfield services cyclicality may dominate any power-equipment read-through.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

## 10. Latest Signals

- Wave: 2
- Source classification: `sa_reported_current_13f`
- Instrument role: `common_equity`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_2/PUMP.md`
- `reports/initialization/2026-06-20-wave-2-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
