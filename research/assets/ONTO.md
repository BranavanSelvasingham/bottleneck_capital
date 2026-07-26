---
ticker: ONTO
name: Onto Innovation
sleeve: semicap_equipment
last_updated: 2026-07-25
source_classification: sa_adjacent_historical_or_thesis_proxy
instrument_role: common_equity
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: true
evidence_quality: RESOLVER_MEMO_PM_REVIEW
thesis_expressed: Onto is a plausible advanced packaging/process-control bottleneck proxy, but not current SA exposure.
anti_thesis: The company may be a cyclical semicap beneficiary rather than a unique AI bottleneck.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: Advanced packaging/process-control demand fails to create differentiated growth.
next_trigger: Refresh the next primary catalyst, valuation, financing where relevant, and live filing coverage before changing capital.
one_line_rationale: "RESEARCH_REQUIRED / NO ADD: the ONTO memo bounds the prior move, but current valuation, catalyst, financing, or live-source evidence remains insufficient for capital."
asset_role: Adjacent process-control and advanced-packaging proxy.
default_holding_period: multi_year
current_decision: RESEARCH_REQUIRED
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: HIGH
last_primary_source_check: 2026-07-23
thesis_health_score: 46
confidence_score: 60.0
valuation_attractiveness_score: 26
urgency_score: 90
max_position_weight_pct: 0
current_position_weight_pct: 0
approved_entry_zone: No new capital until scheduled scan validates valuation.
do_not_buy_zone: Any price without thesis, valuation, sizing, and invalidation.
sell_trigger_status: false
hedge_required: true
main_hedge: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
open_questions_count: 1
broken_thesis: ""
action_tier: RESEARCH_REQUIRED
---
# ONTO - Onto Innovation

## 0. Current Decision

### Simple decision

Current action: RESEARCH_REQUIRED

### One-line decision

RESEARCH_REQUIRED: the July 15 10:45 sentinel flagged an unresolved ONTO price dislocation; cause, valuation, advanced-packaging/process-control demand, customer exposure, margins, and thesis-proxy fit must be refreshed before capital.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, RESEARCH BLOCKED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Capex cycle, customer concentration, and non-SA status. |
| Main upside driver today | Advanced packaging, HBM/process control, and semicap recovery. |
| Next review trigger | Resolve July 15 10:45 sentinel dislocation |

## 1. Role in Bottleneck Capital

Sleeve: `semicap_equipment`

Why this asset belongs here: Adjacent process-control and advanced-packaging proxy.

What this asset is actually a bet on:

1. Advanced packaging, HBM/process control, and semicap recovery.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- The company may be a cyclical semicap beneficiary rather than a unique AI bottleneck.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH
Confidence: 36
Time horizon: multi-year
Importance: HIGH

Claim: Onto is a plausible advanced packaging/process-control bottleneck proxy, but not current SA exposure.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_3/ONTO.md; wave execution memo.
- Sleeve thesis: `semicap_equipment`.

Evidence against:
- The company may be a cyclical semicap beneficiary rather than a unique AI bottleneck.
- Capex cycle, customer concentration, and non-SA status.

What would break it:
- Advanced packaging/process-control demand fails to create differentiated growth.

Decision impact:
RESEARCH_REQUIRED. Do not add capital until the July 15 10:45 sentinel dislocation is resolved
with primary-source review of advanced-packaging/process-control demand, customer exposure,
margins, valuation, and thesis-proxy fit.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: semicap cycle-normalized earnings plus advanced-packaging contribution. Current baseline does not approve a buy.

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
| Thesis purity | 3 | Adjacent process-control and advanced-packaging proxy. |
| Durability | 3 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 3 | Main risk: Capex cycle, customer concentration, and non-SA status. |
| Management / execution | 3 | Execution still matters. |
| Strategic scarcity | 3 | Upside: Advanced packaging, HBM/process control, and semicap recovery. |
| Contract quality | 3 | Needs source-event verification. |
| Customer quality | 3 | Needs source-event verification. |
| Pricing power | 3 | Valuation frame: semicap cycle-normalized earnings plus advanced-packaging contribution. |
| Downside survivability | 2 | Invalidation: Advanced packaging/process-control demand fails to create differentiated growth. |
| Hedgeability | 2 | Long-only hedge is sizing/no action. |

Long-term owner score: 28 / 50

## 5. Valuation and Entry Discipline

Valuation frame: semicap cycle-normalized earnings plus advanced-packaging contribution

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker ONTO` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- Advanced packaging/process-control demand fails to create differentiated growth.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Capex cycle, customer concentration, and non-SA status.
- The company may be a cyclical semicap beneficiary rather than a unique AI bottleneck.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

## 10. Latest Signals

- July 15, 2026 10:45 sentinel: event `366f22a93d1dc94ee605ffd3` flagged ONTO price dislocation: intraday -5.9%. Treat as RESEARCH_REQUIRED until cause and valuation are resolved.
- Wave: 3
- Source classification: `sa_adjacent_historical_or_thesis_proxy`
- Instrument role: `common_equity`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_3/ONTO.md`
- `reports/initialization/2026-06-20-wave-3-execution.md`

Evidence quality: live intraday dislocation unresolved, plus SA filing and local baseline. No new capital is authorized before the July 15 sentinel event is resolved.

## 12. Open Questions

- Resolve the July 15 10:45 ONTO dislocation with primary company/filing/IR evidence, advanced-packaging/process-control demand, customer exposure, margins, valuation, and thesis-proxy fit.

## 13. Latest Agent Notes

July 15 10:45 sentinel moved current action to RESEARCH_REQUIRED. No BUY_NOW, ADD_ON_DIP,
TRIM, or SELL action is authorized until the dislocation is resolved.
