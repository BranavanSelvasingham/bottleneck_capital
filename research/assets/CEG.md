---
ticker: CEG
name: Constellation Energy
sleeve: power_bottleneck
last_updated: 2026-06-20
source_classification: sa_adjacent_thesis_proxy
instrument_role: common_equity
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: false
evidence_quality: SA_FILING_AND_LOCAL_BASELINE
thesis_expressed: Constellation is a high-quality power scarcity proxy, but it is not latest-current SA exposure and should stay watch-only absent promotion or a priced entry.
anti_thesis: Power scarcity may already be recognized, and utility/regulatory risk can limit upside.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: Datacenter/power thesis weakens or SA/current evidence does not support promotion.
next_trigger: Next scheduled market/filing scan, SA filing change, company filing/IR update, financing or customer-contract news, guidance change, or a detected valuation dip.
one_line_rationale: "Hold/watch only: Constellation is a high-quality power scarcity proxy, but it is not latest-current SA exposure and should stay watch-only absent promotion or a priced entry."
asset_role: Adjacent nuclear/generation power proxy.
default_holding_period: multi_year
current_decision: HOLD
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: MEDIUM
last_primary_source_check: 2026-06-20
thesis_health_score: 58
confidence_score: 42
valuation_attractiveness_score: 28
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
# CEG - Constellation Energy

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

Constellation is a high-quality power scarcity proxy, but it is not latest-current SA exposure and should stay watch-only absent promotion or a priced entry.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Regulation, valuation, contract repricing, and non-SA source status. |
| Main upside driver today | Nuclear fleet scarcity, datacenter PPAs, and rising reliable-power value. |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `power_bottleneck`

Why this asset belongs here: Adjacent nuclear/generation power proxy.

What this asset is actually a bet on:

1. Nuclear fleet scarcity, datacenter PPAs, and rising reliable-power value.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- Power scarcity may already be recognized, and utility/regulatory risk can limit upside.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH  
Confidence: 42  
Time horizon: multi-year  
Importance: HIGH

Claim: Constellation is a high-quality power scarcity proxy, but it is not latest-current SA exposure and should stay watch-only absent promotion or a priced entry.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_3/CEG.md; wave execution memo.
- Sleeve thesis: `power_bottleneck`.

Evidence against:
- Power scarcity may already be recognized, and utility/regulatory risk can limit upside.
- Regulation, valuation, contract repricing, and non-SA source status.

What would break it:
- Datacenter/power thesis weakens or SA/current evidence does not support promotion.

Decision impact:
HOLD. Do not add capital until a scheduled scan or fresh primary-source event clears thesis,
valuation, and sizing.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL  
Claim: generation fleet value, PPA economics, and relative power scarcity. Current baseline does not approve a buy.

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
| Thesis purity | 4 | Adjacent nuclear/generation power proxy. |
| Durability | 4 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 4 | Main risk: Regulation, valuation, contract repricing, and non-SA source status. |
| Management / execution | 4 | Execution still matters. |
| Strategic scarcity | 4 | Upside: Nuclear fleet scarcity, datacenter PPAs, and rising reliable-power value. |
| Contract quality | 3 | Needs source-event verification. |
| Customer quality | 3 | Needs source-event verification. |
| Pricing power | 3 | Valuation frame: generation fleet value, PPA economics, and relative power scarcity. |
| Downside survivability | 3 | Invalidation: Datacenter/power thesis weakens or SA/current evidence does not support promotion. |
| Hedgeability | 3 | Long-only hedge is sizing/no action. |

Long-term owner score: 35 / 50

## 5. Valuation and Entry Discipline

Valuation frame: generation fleet value, PPA economics, and relative power scarcity

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker CEG` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- Datacenter/power thesis weakens or SA/current evidence does not support promotion.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Regulation, valuation, contract repricing, and non-SA source status.
- Power scarcity may already be recognized, and utility/regulatory risk can limit upside.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

## 10. Latest Signals

- Wave: 3
- Source classification: `sa_adjacent_thesis_proxy`
- Instrument role: `common_equity`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_3/CEG.md`
- `reports/initialization/2026-06-20-wave-3-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
