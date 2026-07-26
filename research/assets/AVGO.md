---
ticker: AVGO
name: Broadcom
sleeve: crowded_ai_beta_hedge
last_updated: 2026-07-25
source_classification: sa_reported_current_13f
instrument_role: common_equity_long_with_reported_put_risk_signal
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: false
evidence_quality: RESOLVER_MEMO_PM_REVIEW
thesis_expressed: Broadcom is a direct custom-AI-silicon and networking bottleneck, with the multi-generation OpenAI accelerator platform adding a marquee deployment to an already accelerating AI semiconductor business.
anti_thesis: Valuation, hyperscaler/customer concentration, custom-silicon competition, VMware execution, debt, or slower AI deployment can compress the premium multiple despite strong revenue growth.
hedge_or_sizing: Do not add near $400. Add only at $370-$375 or lower with no thesis damage, subject to an 8% policy cap applied from the local ledger.
invalidation_trigger: AI semiconductor growth falls below 25% for two quarters, the OpenAI multi-generation deployment is materially delayed or reduced, major custom-accelerator customers are lost, networking share deteriorates, or leverage/VMware execution worsens materially.
next_trigger: Reassess after Q3 AI revenue, custom-silicon deployment evidence, and valuation refresh.
one_line_rationale: "HOLD / NO ADD: Broadcom custom-silicon and OpenAI thesis remains intact, but deployment economics and valuation require the existing entry discipline."
asset_role: Custom AI silicon, networking, connectivity, and infrastructure software bottleneck.
default_holding_period: multi_year
current_decision: HOLD
dip_decision: NOT_ARMED
sell_decision: NOT_TRIGGERED
research_priority: HIGH
last_primary_source_check: 2026-07-21
thesis_health_score: 90
confidence_score: 85.0
valuation_attractiveness_score: 45
urgency_score: 90
max_position_weight_pct: 8
current_position_weight_pct: 0
approved_entry_zone: ADD_ON_DIP at $370-$375 or lower with no thesis damage; do not add at the July 10 close near $400.
do_not_buy_zone: Above $400, after a customer/program loss, after an AI semiconductor guidance cut, or when the local capacity gate reaches the 8% policy cap.
sell_trigger_status: false
hedge_required: true
main_hedge: No puts or shorts; use price discipline and an 8% position cap, while treating SA put exposure as a crowding-risk signal.
open_questions_count: 0
broken_thesis: ""
action_tier: HOLD
---
# AVGO - Broadcom

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

Broadcom is tracked as SA reported put exposure, not as a long candidate under the current mandate.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | NO / SIGNAL ONLY |
| Buy today? | NO |
| Add on dip? | NO |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Crowded AI expectations, integration risk, and valuation sensitivity. |
| Main upside driver today | Risk read-through for AI networking, custom silicon, VMware leverage, and semis. |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `crowded_ai_beta_hedge`

Why this asset belongs here: Signal-only AI networking/custom-silicon risk map.

What this asset is actually a bet on:

1. Risk read-through for AI networking, custom silicon, VMware leverage, and semis.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- A strong AI networking/custom-silicon business does not make a trade if the signal is only downside/crowding risk.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: SIGNAL_ONLY
Confidence: 35
Time horizon: multi-year
Importance: HIGH

Claim: Broadcom is tracked as SA reported put exposure, not as a long candidate under the current mandate.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_2/AVGO.md; wave execution memo.
- Sleeve thesis: `crowded_ai_beta_hedge`.

Evidence against:
- A strong AI networking/custom-silicon business does not make a trade if the signal is only downside/crowding risk.
- Crowded AI expectations, integration risk, and valuation sensitivity.

What would break it:
- Separate long-only thesis documented with valuation, sizing, and invalidation.

Decision impact:
HOLD. Do not add capital until a scheduled scan or fresh primary-source event clears thesis,
valuation, and sizing.

Hedge implication:
No puts or shorts; use as risk signal only and do not allocate capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: signal-only risk map, not an entry valuation. Current baseline does not approve a buy.

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
| Thesis purity | 3 | Signal-only AI networking/custom-silicon risk map. |
| Durability | 3 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 3 | Main risk: Crowded AI expectations, integration risk, and valuation sensitivity. |
| Management / execution | 3 | Execution still matters. |
| Strategic scarcity | 3 | Upside: Risk read-through for AI networking, custom silicon, VMware leverage, and semis. |
| Contract quality | 2 | Needs source-event verification. |
| Customer quality | 2 | Needs source-event verification. |
| Pricing power | 2 | Valuation frame: signal-only risk map, not an entry valuation. |
| Downside survivability | 2 | Invalidation: Separate long-only thesis documented with valuation, sizing, and invalidation. |
| Hedgeability | 2 | Long-only hedge is sizing/no action. |

Long-term owner score: 25 / 50

## 5. Valuation and Entry Discipline

Valuation frame: signal-only risk map, not an entry valuation

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker AVGO` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: NO

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- Separate long-only thesis documented with valuation, sizing, and invalidation.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Crowded AI expectations, integration risk, and valuation sensitivity.
- A strong AI networking/custom-silicon business does not make a trade if the signal is only downside/crowding risk.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use as risk signal only and do not allocate capital.

## 10. Latest Signals

- Wave: 2
- Source classification: `sa_reported_current_13f`
- Instrument role: `reported_put_signal`
- Trade policy: `signal_only_no_puts_or_shorts`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_2/AVGO.md`
- `reports/initialization/2026-06-20-wave-2-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
