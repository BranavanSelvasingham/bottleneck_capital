---
ticker: TE
name: T1 Energy
sleeve: power_bottleneck
last_updated: 2026-06-21
source_classification: sa_reported_current_13f
instrument_role: common_equity
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: false
evidence_quality: SA_FILING_AND_LOCAL_BASELINE
thesis_expressed: T1 Energy is tracked as a current SA holding, but business-model and financing clarity are not strong enough for new capital.
anti_thesis: It may be policy/manufacturing cyclicality rather than an AI power bottleneck.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: Business model, capacity funding, or customer demand fails to support power-bottleneck role.
next_trigger: Next scheduled market/filing scan, SA filing change, company filing/IR update, financing or customer-contract news, guidance change, or a detected valuation dip.
one_line_rationale: "Hold/watch only: T1 Energy is tracked as a current SA holding, but business-model and financing clarity are not strong enough for new capital."
asset_role: Power supply/manufacturing thesis candidate.
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
# TE - T1 Energy

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

T1 Energy is tracked as a current SA holding, but business-model and financing clarity are not strong enough for new capital.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Funding, customer demand, policy risk, and thesis purity. |
| Main upside driver today | Manufacturing capacity, offtake/customer demand, and policy-supported power supply. |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `power_bottleneck`

Why this asset belongs here: Power supply/manufacturing thesis candidate.

What this asset is actually a bet on:

1. Manufacturing capacity, offtake/customer demand, and policy-supported power supply.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- It may be policy/manufacturing cyclicality rather than an AI power bottleneck.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH
Confidence: 30
Time horizon: multi-year
Importance: HIGH

Claim: T1 Energy is tracked as a current SA holding, but business-model and financing clarity are not strong enough for new capital.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_2/TE.md; wave execution memo.
- Sleeve thesis: `power_bottleneck`.

Evidence against:
- It may be policy/manufacturing cyclicality rather than an AI power bottleneck.
- Funding, customer demand, policy risk, and thesis purity.

What would break it:
- Business model, capacity funding, or customer demand fails to support power-bottleneck role.

Decision impact:
HOLD. Do not add capital until a scheduled scan or fresh primary-source event clears thesis,
valuation, and sizing.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: capacity value, offtake quality, and funding-adjusted scenario value. Current baseline does not approve a buy.

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
| Thesis purity | 2 | Power supply/manufacturing thesis candidate. |
| Durability | 2 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 2 | Main risk: Funding, customer demand, policy risk, and thesis purity. |
| Management / execution | 2 | Execution still matters. |
| Strategic scarcity | 2 | Upside: Manufacturing capacity, offtake/customer demand, and policy-supported power supply. |
| Contract quality | 2 | Needs source-event verification. |
| Customer quality | 2 | Needs source-event verification. |
| Pricing power | 2 | Valuation frame: capacity value, offtake quality, and funding-adjusted scenario value. |
| Downside survivability | 1 | Invalidation: Business model, capacity funding, or customer demand fails to support power-bottleneck role. |
| Hedgeability | 1 | Long-only hedge is sizing/no action. |

Long-term owner score: 18 / 50

## 5. Valuation and Entry Discipline

Valuation frame: capacity value, offtake quality, and funding-adjusted scenario value

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker TE` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- Business model, capacity funding, or customer demand fails to support power-bottleneck role.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Funding, customer demand, policy risk, and thesis purity.
- It may be policy/manufacturing cyclicality rather than an AI power bottleneck.
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
- `research/agent_packets/wave_2/TE.md`
- `reports/initialization/2026-06-20-wave-2-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
