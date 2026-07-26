---
ticker: ASML
name: ASML Holding
sleeve: semicap_equipment
last_updated: 2026-07-25
source_classification: sa_reported_current_13f
instrument_role: common_equity_with_put_signal
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: false
evidence_quality: RESOLVER_MEMO_PM_REVIEW
thesis_expressed: ASML is the cleanest tooling scarcity asset in leading-edge chips, but the SA put signal makes valuation and China/export-control risk central.
anti_thesis: Semicap cycle, export controls, or customer capex digestion can overpower monopoly quality for long periods.
hedge_or_sizing: No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit invalidation.
invalidation_trigger: Sustained leading-edge order/backlog deterioration or export controls that impair the core EUV growth runway.
next_trigger: Reassess on export-control changes, customer capex, or a valuation reset.
one_line_rationale: "HOLD / NO ADD: Q2 guidance, backlog, and EUV demand remain strong; valuation, export controls, customer capex, and SA crowding prevent a fresh add."
asset_role: Lithography and leading-edge semicap bottleneck.
default_holding_period: multi_year
current_decision: HOLD
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: HIGH
last_primary_source_check: 2026-07-24
thesis_health_score: 70
confidence_score: 82.0
valuation_attractiveness_score: 30
urgency_score: 95
max_position_weight_pct: 0
current_position_weight_pct: 0
approved_entry_zone: No new capital until scheduled scan validates valuation.
do_not_buy_zone: Any price without thesis, valuation, sizing, and invalidation.
sell_trigger_status: false
hedge_required: true
main_hedge: No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit invalidation.
open_questions_count: 0
broken_thesis: ""
action_tier: HOLD
---
# ASML - ASML Holding

## 0. Current Decision

### Simple decision

Current action: RESEARCH_REQUIRED

### One-line decision

RESEARCH_REQUIRED: the July 15 pre-market scan flagged an unresolved ASML price dislocation; cause, valuation, order/backlog durability, export-control risk, and customer capex must be refreshed before capital.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Unresolved July 15 price dislocation, order/backlog risk, export controls, capex digestion, and put-signal crowding risk. |
| Main upside driver today | EUV demand, advanced packaging/foundry intensity, and scarcity economics. |
| Next review trigger | Resolve July 15 pre-market ASML dislocation |

## 1. Role in Bottleneck Capital

Sleeve: `semicap_equipment`

Why this asset belongs here: Lithography and leading-edge semicap bottleneck.

What this asset is actually a bet on:

1. EUV demand, advanced packaging/foundry intensity, and scarcity economics.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- Semicap cycle, export controls, or customer capex digestion can overpower monopoly quality for long periods.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH
Confidence: 55
Time horizon: multi-year
Importance: HIGH

Claim: ASML is the cleanest tooling scarcity asset in leading-edge chips, but the SA put signal makes valuation and China/export-control risk central.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_1/ASML.md; wave execution memo.
- Sleeve thesis: `semicap_equipment`.

Evidence against:
- Semicap cycle, export controls, or customer capex digestion can overpower monopoly quality for long periods.
- Order weakness, geopolitics, capex cycle drawdown, or put-signal crowding risk.

What would break it:
- Sustained leading-edge order/backlog deterioration or export controls that impair the core EUV growth runway.

Decision impact:
RESEARCH_REQUIRED. Do not add capital until the July 15 pre-market dislocation is explained
with primary-source evidence, valuation, and sizing.

Hedge implication:
No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit invalidation.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: relative semicap quality plus order/backlog durability. Current baseline does not approve a buy.

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
| Thesis purity | 5 | Lithography and leading-edge semicap bottleneck. |
| Durability | 5 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 4 | Main risk: Order weakness, geopolitics, capex cycle drawdown, or put-signal crowding risk. |
| Management / execution | 4 | Execution still matters. |
| Strategic scarcity | 4 | Upside: EUV demand, advanced packaging/foundry intensity, and scarcity economics. |
| Contract quality | 4 | Needs source-event verification. |
| Customer quality | 4 | Needs source-event verification. |
| Pricing power | 4 | Valuation frame: relative semicap quality plus order/backlog durability. |
| Downside survivability | 4 | Invalidation: Sustained leading-edge order/backlog deterioration or export controls that impair the core EUV growth runway. |
| Hedgeability | 4 | Long-only hedge is sizing/no action. |

Long-term owner score: 42 / 50

## 5. Valuation and Entry Discipline

Valuation frame: relative semicap quality plus order/backlog durability

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker ASML` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- Sustained leading-edge order/backlog deterioration or export controls that impair the core EUV growth runway.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Order weakness, geopolitics, capex cycle drawdown, or put-signal crowding risk.
- Semicap cycle, export controls, or customer capex digestion can overpower monopoly quality for long periods.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit invalidation.

## 10. Latest Signals

- 2026-07-15 pre-market scan: unresolved ASML price dislocation, event `e58e3585da498a19a4ffe5c1`; check cause, order/backlog durability, EUV demand, export-control risk, customer capex digestion, valuation, and SA put-signal context before capital.
- Wave: 1
- Source classification: `sa_reported_current_13f`
- Instrument role: `common_equity_with_put_signal`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_1/ASML.md`
- `reports/initialization/2026-06-20-wave-1-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- What caused the July 15 pre-market dislocation, and does it indicate order/backlog deterioration, China/export-control impairment, customer capex digestion, or only valuation/positioning pressure?
- Is the post-dislocation valuation attractive enough to justify new capital after long-only sizing and SA put-signal risk are accounted for?

## 13. Latest Agent Notes

2026-07-15 pre-market scan moved ASML from HOLD to RESEARCH_REQUIRED. Current action is
research before acting, with no BUY_NOW, ADD_ON_DIP, TRIM, or SELL action authorized.
