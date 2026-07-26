---
ticker: BE
name: Bloom Energy
sleeve: power_bottleneck
last_updated: 2026-07-25
source_classification: sa_reported_current_13f
instrument_role: common_equity_and_call_signal
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: true
evidence_quality: RESOLVER_MEMO_PM_REVIEW
thesis_expressed: Bloom may be a direct answer to grid-constrained AI campuses if customers value rapid onsite power deployment.
anti_thesis: Fuel-cell economics, warranty risk, financing needs, or loose energy-transition exposure may swamp datacenter upside.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: Datacenter backlog fails to convert or financing/product risk impairs delivery economics.
next_trigger: Refresh the next primary catalyst, valuation, financing where relevant, and live filing coverage before changing capital.
one_line_rationale: "RESEARCH_REQUIRED / NO ADD: the BE memo bounds the prior move, but current valuation, catalyst, financing, or live-source evidence remains insufficient for capital."
asset_role: Onsite power solution for AI datacenter scarcity.
default_holding_period: multi_year
current_decision: RESEARCH_REQUIRED
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: HIGH
last_primary_source_check: 2026-07-24
thesis_health_score: 55
confidence_score: 60.0
valuation_attractiveness_score: 32
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
# BE - Bloom Energy

## 0. Current Decision

### Simple decision

Current action: RESEARCH_REQUIRED

### One-line decision

RESEARCH_REQUIRED: the July 15 10:45 sentinel flagged an unresolved BE price dislocation; cause, valuation, customer conversion, product reliability, warranty risk, financing needs, margins, and onsite-power demand must be refreshed before capital.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, RESEARCH BLOCKED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Contract quality, product reliability, cash needs, customer concentration, and margins. |
| Main upside driver today | Datacenter customer wins, backlog conversion, margin improvement, and financing access. |
| Next review trigger | Resolve July 15 10:45 sentinel dislocation |

## 1. Role in Bottleneck Capital

Sleeve: `power_bottleneck`

Why this asset belongs here: Onsite power solution for AI datacenter scarcity.

What this asset is actually a bet on:

1. Datacenter customer wins, backlog conversion, margin improvement, and financing access.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- Fuel-cell economics, warranty risk, financing needs, or loose energy-transition exposure may swamp datacenter upside.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH
Confidence: 45
Time horizon: multi-year
Importance: HIGH

Claim: Bloom may be a direct answer to grid-constrained AI campuses if customers value rapid onsite power deployment.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_1/BE.md; wave execution memo.
- Sleeve thesis: `power_bottleneck`.

Evidence against:
- Fuel-cell economics, warranty risk, financing needs, or loose energy-transition exposure may swamp datacenter upside.
- Contract quality, product reliability, cash needs, customer concentration, and margins.

What would break it:
- Datacenter backlog fails to convert or financing/product risk impairs delivery economics.

Decision impact:
RESEARCH_REQUIRED. Do not add capital until the July 15 10:45 sentinel dislocation is resolved
with primary-source review of customer conversion, product reliability, warranty risk,
financing needs, margins, onsite-power demand, and valuation.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: backlog quality, gross-margin path, and funded growth scenario value. Current baseline does not approve a buy.

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
| Thesis purity | 3 | Onsite power solution for AI datacenter scarcity. |
| Durability | 3 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 3 | Main risk: Contract quality, product reliability, cash needs, customer concentration, and margins. |
| Management / execution | 3 | Execution still matters. |
| Strategic scarcity | 3 | Upside: Datacenter customer wins, backlog conversion, margin improvement, and financing access. |
| Contract quality | 3 | Needs source-event verification. |
| Customer quality | 3 | Needs source-event verification. |
| Pricing power | 3 | Valuation frame: backlog quality, gross-margin path, and funded growth scenario value. |
| Downside survivability | 3 | Invalidation: Datacenter backlog fails to convert or financing/product risk impairs delivery economics. |
| Hedgeability | 3 | Long-only hedge is sizing/no action. |

Long-term owner score: 30 / 50

## 5. Valuation and Entry Discipline

Valuation frame: backlog quality, gross-margin path, and funded growth scenario value

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker BE` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- Datacenter backlog fails to convert or financing/product risk impairs delivery economics.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Contract quality, product reliability, cash needs, customer concentration, and margins.
- Fuel-cell economics, warranty risk, financing needs, or loose energy-transition exposure may swamp datacenter upside.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

## 10. Latest Signals

- July 15, 2026 10:45 sentinel: event `610a5c7d15b537730394f822` flagged BE price dislocation: intraday -6.3%. Treat as RESEARCH_REQUIRED until cause and valuation are resolved.
- Wave: 1
- Source classification: `sa_reported_current_13f`
- Instrument role: `common_equity_and_call_signal`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_1/BE.md`
- `reports/initialization/2026-06-20-wave-1-execution.md`

Evidence quality: live intraday dislocation unresolved, plus SA filing and local baseline. No new capital is authorized before the July 15 sentinel event is resolved.

## 12. Open Questions

- Resolve the July 15 10:45 BE dislocation with primary company/filing/IR evidence, customer conversion, product reliability, warranty risk, financing needs, margins, onsite-power demand, and valuation.

## 13. Latest Agent Notes

July 15 10:45 sentinel moved current action to RESEARCH_REQUIRED. No BUY_NOW, ADD_ON_DIP,
TRIM, or SELL action is authorized until the dislocation is resolved.
