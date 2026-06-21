---
ticker: SNDK
name: SanDisk
sleeve: memory_storage_networking
last_updated: 2026-06-20
source_classification: sa_reported_current_13f
instrument_role: common_equity_and_call_signal
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: false
evidence_quality: SA_FILING_AND_LOCAL_BASELINE
thesis_expressed: SanDisk may express NAND/storage scarcity after separation, but the memory cycle and balance sheet need discipline.
anti_thesis: The case may be cyclical NAND beta rather than durable AI storage scarcity.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: NAND/storage recovery fails or balance sheet risk overwhelms AI storage upside.
next_trigger: Next scheduled market/filing scan, SA filing change, company filing/IR update, financing or customer-contract news, guidance change, or a detected valuation dip.
one_line_rationale: "Hold/watch only: SanDisk may express NAND/storage scarcity after separation, but the memory cycle and balance sheet need discipline."
asset_role: AI storage/NAND scarcity candidate.
default_holding_period: multi_year
current_decision: HOLD
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: HIGH
last_primary_source_check: 2026-06-20
thesis_health_score: 48
confidence_score: 38
valuation_attractiveness_score: 27
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
# SNDK - SanDisk

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

SanDisk may express NAND/storage scarcity after separation, but the memory cycle and balance sheet need discipline.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Memory cyclicality, leverage/separation issues, and pricing power uncertainty. |
| Main upside driver today | NAND recovery, AI storage demand, and separation-driven operating focus. |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `memory_storage_networking`

Why this asset belongs here: AI storage/NAND scarcity candidate.

What this asset is actually a bet on:

1. NAND recovery, AI storage demand, and separation-driven operating focus.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- The case may be cyclical NAND beta rather than durable AI storage scarcity.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH  
Confidence: 38  
Time horizon: multi-year  
Importance: HIGH

Claim: SanDisk may express NAND/storage scarcity after separation, but the memory cycle and balance sheet need discipline.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_2/SNDK.md; wave execution memo.
- Sleeve thesis: `memory_storage_networking`.

Evidence against:
- The case may be cyclical NAND beta rather than durable AI storage scarcity.
- Memory cyclicality, leverage/separation issues, and pricing power uncertainty.

What would break it:
- NAND/storage recovery fails or balance sheet risk overwhelms AI storage upside.

Decision impact:
HOLD. Do not add capital until a scheduled scan or fresh primary-source event clears thesis,
valuation, and sizing.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL  
Claim: cycle-normalized NAND earnings and AI storage scenario value. Current baseline does not approve a buy.

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
| Thesis purity | 3 | AI storage/NAND scarcity candidate. |
| Durability | 3 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 3 | Main risk: Memory cyclicality, leverage/separation issues, and pricing power uncertainty. |
| Management / execution | 3 | Execution still matters. |
| Strategic scarcity | 3 | Upside: NAND recovery, AI storage demand, and separation-driven operating focus. |
| Contract quality | 3 | Needs source-event verification. |
| Customer quality | 3 | Needs source-event verification. |
| Pricing power | 2 | Valuation frame: cycle-normalized NAND earnings and AI storage scenario value. |
| Downside survivability | 2 | Invalidation: NAND/storage recovery fails or balance sheet risk overwhelms AI storage upside. |
| Hedgeability | 2 | Long-only hedge is sizing/no action. |

Long-term owner score: 27 / 50

## 5. Valuation and Entry Discipline

Valuation frame: cycle-normalized NAND earnings and AI storage scenario value

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker SNDK` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- NAND/storage recovery fails or balance sheet risk overwhelms AI storage upside.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Memory cyclicality, leverage/separation issues, and pricing power uncertainty.
- The case may be cyclical NAND beta rather than durable AI storage scarcity.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

## 10. Latest Signals

- Wave: 2
- Source classification: `sa_reported_current_13f`
- Instrument role: `common_equity_and_call_signal`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_2/SNDK.md`
- `reports/initialization/2026-06-20-wave-2-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
