---
ticker: LITE
name: Lumentum
sleeve: ai_networking_optical
last_updated: 2026-07-25
source_classification: sa_adjacent_historical_or_thesis_proxy
instrument_role: common_equity
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: true
evidence_quality: RESOLVER_MEMO_PM_REVIEW
thesis_expressed: Lumentum can benefit if AI optical components tighten, but it is not current SA exposure and should remain a watchlist proxy.
anti_thesis: Telecom cyclicality may dominate any datacenter optical upside.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: AI/datacom demand fails to offset telecom cyclicality.
next_trigger: Refresh the next primary catalyst, valuation, financing where relevant, and live filing coverage before changing capital.
one_line_rationale: "RESEARCH_REQUIRED / NO ADD: the LITE memo bounds the prior move, but current valuation, catalyst, financing, or live-source evidence remains insufficient for capital."
asset_role: Adjacent optical/networking proxy.
default_holding_period: multi_year
current_decision: RESEARCH_REQUIRED
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: MEDIUM
last_primary_source_check: 2026-07-17
thesis_health_score: 42
confidence_score: 60.0
valuation_attractiveness_score: 24
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
action_tier: RESEARCH_REQUIRED
---
# LITE - Lumentum

## 0. Current Decision

### Simple decision

Current action: RESEARCH_REQUIRED

### One-line decision

RESEARCH_REQUIRED: the July 13 open scan flagged an unresolved LITE price dislocation; cause, valuation, datacom demand, telecom cyclicality, and customer concentration must be refreshed before capital.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Telecom weakness, customer concentration, and non-SA status. |
| Main upside driver today | AI transceiver/optical demand and datacom mix improvement. |
| Next review trigger | Resolve July 13 open dislocation |

## 1. Role in Bottleneck Capital

Sleeve: `ai_networking_optical`

Why this asset belongs here: Adjacent optical/networking proxy.

What this asset is actually a bet on:

1. AI transceiver/optical demand and datacom mix improvement.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- Telecom cyclicality may dominate any datacenter optical upside.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH
Confidence: 34
Time horizon: multi-year
Importance: HIGH

Claim: Lumentum can benefit if AI optical components tighten, but it is not current SA exposure and should remain a watchlist proxy.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_3/LITE.md; wave execution memo.
- Sleeve thesis: `ai_networking_optical`.

Evidence against:
- Telecom cyclicality may dominate any datacenter optical upside.
- Telecom weakness, customer concentration, and non-SA status.

What would break it:
- AI/datacom demand fails to offset telecom cyclicality.

Decision impact:
RESEARCH_REQUIRED. Do not add capital until the July 13 open dislocation cause is bounded
and primary evidence clears thesis, valuation, datacom demand, telecom cyclicality,
customer concentration, and sizing.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: datacom recovery and optical component scenario value. Current baseline does not approve a buy.

### Thesis C - Catalyst thesis

Status: EVENT-DRIVEN
Claim: New SEC filing, IR update, financing, customer contract, guidance change, SA filing
change, or resolution of the July 13 open dislocation can reopen the decision.

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
| Thesis purity | 3 | Adjacent optical/networking proxy. |
| Durability | 3 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 3 | Main risk: Telecom weakness, customer concentration, and non-SA status. |
| Management / execution | 3 | Execution still matters. |
| Strategic scarcity | 3 | Upside: AI transceiver/optical demand and datacom mix improvement. |
| Contract quality | 2 | Needs source-event verification. |
| Customer quality | 2 | Needs source-event verification. |
| Pricing power | 2 | Valuation frame: datacom recovery and optical component scenario value. |
| Downside survivability | 2 | Invalidation: AI/datacom demand fails to offset telecom cyclicality. |
| Hedgeability | 2 | Long-only hedge is sizing/no action. |

Long-term owner score: 25 / 50

## 5. Valuation and Entry Discipline

Valuation frame: datacom recovery and optical component scenario value

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker LITE` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- AI/datacom demand fails to offset telecom cyclicality.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Telecom weakness, customer concentration, and non-SA status.
- Telecom cyclicality may dominate any datacenter optical upside.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

## 10. Latest Signals

- Wave: 3
- Source classification: `sa_adjacent_historical_or_thesis_proxy`
- Instrument role: `common_equity`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_3/LITE.md`
- `reports/initialization/2026-06-20-wave-3-execution.md`

Evidence quality: live open dislocation unresolved. No capital action is authorized until
primary evidence and valuation resolve the July 13 price-dislocation trigger.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

2026-07-13 open dislocation scan moved the working decision to RESEARCH_REQUIRED after LITE
triggered an unresolved price-dislocation event. No BUY_NOW, ADD_ON_DIP, TRIM, or SELL
action is authorized.
