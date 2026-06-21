---
ticker: CRWV
name: CoreWeave
sleeve: compute_infra
last_updated: 2026-06-20
source_classification: sa_reported_current_13f
instrument_role: common_equity_and_call_signal
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: false
evidence_quality: SA_FILING_AND_LOCAL_BASELINE
thesis_expressed: CoreWeave is a direct compute scarcity expression, but customer concentration, leverage, and GPU supply commitments make valuation discipline mandatory.
anti_thesis: It may be a highly financed GPU-capacity trade rather than durable infrastructure value.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: Large customer demand weakens, refinancing risk rises, or contracted utilization breaks.
next_trigger: Next scheduled market/filing scan, SA filing change, company filing/IR update, financing or customer-contract news, guidance change, or a detected valuation dip.
one_line_rationale: "Hold/watch only: CoreWeave is a direct compute scarcity expression, but customer concentration, leverage, and GPU supply commitments make valuation discipline mandatory."
asset_role: Scarce contracted AI cloud compute.
default_holding_period: multi_year
current_decision: HOLD
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: HIGH
last_primary_source_check: 2026-06-20
thesis_health_score: 55
confidence_score: 43
valuation_attractiveness_score: 30
urgency_score: 90
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
# CRWV - CoreWeave

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

CoreWeave is a direct compute scarcity expression, but customer concentration, leverage, and GPU supply commitments make valuation discipline mandatory.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Customer concentration, debt/refinancing, GPU supply, and utilization durability. |
| Main upside driver today | Contracted AI demand, power-secured capacity, and faster deployment than hyperscalers. |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `compute_infra`

Why this asset belongs here: Scarce contracted AI cloud compute.

What this asset is actually a bet on:

1. Contracted AI demand, power-secured capacity, and faster deployment than hyperscalers.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- It may be a highly financed GPU-capacity trade rather than durable infrastructure value.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH  
Confidence: 43  
Time horizon: multi-year  
Importance: HIGH

Claim: CoreWeave is a direct compute scarcity expression, but customer concentration, leverage, and GPU supply commitments make valuation discipline mandatory.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_1/CRWV.md; wave execution memo.
- Sleeve thesis: `compute_infra`.

Evidence against:
- It may be a highly financed GPU-capacity trade rather than durable infrastructure value.
- Customer concentration, debt/refinancing, GPU supply, and utilization durability.

What would break it:
- Large customer demand weakens, refinancing risk rises, or contracted utilization breaks.

Decision impact:
HOLD. Do not add capital until a scheduled scan or fresh primary-source event clears thesis,
valuation, and sizing.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL  
Claim: contracted revenue, capacity economics, and leverage-adjusted scenario value. Current baseline does not approve a buy.

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
| Thesis purity | 4 | Scarce contracted AI cloud compute. |
| Durability | 3 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 3 | Main risk: Customer concentration, debt/refinancing, GPU supply, and utilization durability. |
| Management / execution | 3 | Execution still matters. |
| Strategic scarcity | 3 | Upside: Contracted AI demand, power-secured capacity, and faster deployment than hyperscalers. |
| Contract quality | 3 | Needs source-event verification. |
| Customer quality | 3 | Needs source-event verification. |
| Pricing power | 3 | Valuation frame: contracted revenue, capacity economics, and leverage-adjusted scenario value. |
| Downside survivability | 3 | Invalidation: Large customer demand weakens, refinancing risk rises, or contracted utilization breaks. |
| Hedgeability | 3 | Long-only hedge is sizing/no action. |

Long-term owner score: 31 / 50

## 5. Valuation and Entry Discipline

Valuation frame: contracted revenue, capacity economics, and leverage-adjusted scenario value

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker CRWV` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- Large customer demand weakens, refinancing risk rises, or contracted utilization breaks.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Customer concentration, debt/refinancing, GPU supply, and utilization durability.
- It may be a highly financed GPU-capacity trade rather than durable infrastructure value.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

## 10. Latest Signals

- Wave: 1
- Source classification: `sa_reported_current_13f`
- Instrument role: `common_equity_and_call_signal`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_1/CRWV.md`
- `reports/initialization/2026-06-20-wave-1-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
