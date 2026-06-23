---
ticker: MU
name: Micron
sleeve: memory_storage_networking
last_updated: 2026-06-22
source_classification: sa_reported_current_13f
instrument_role: common_equity_call_signal_and_put_signal
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: true
evidence_quality: MARKET_NEWS_AND_LOCAL_BASELINE_NEEDS_PRIMARY_SOURCE
thesis_expressed: Micron is a direct HBM/memory scarcity expression, but the memory cycle and SA put signal make entry discipline crucial.
anti_thesis: The upside may be cyclical pricing rather than durable structural scarcity.
hedge_or_sizing: No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit invalidation.
invalidation_trigger: HBM leadership or memory pricing breaks while valuation remains elevated.
next_trigger: Resolve the June 22 Anthropic partnership economics and June 24 earnings setup before any new capital.
one_line_rationale: "RESEARCH_REQUIRED: Micron's reported Anthropic memory/storage partnership and 5-6% move reopen the HBM scarcity thesis, but contract economics, June 24 earnings, valuation, and sizing are unresolved."
asset_role: HBM and AI memory bottleneck.
default_holding_period: multi_year
current_decision: RESEARCH_REQUIRED
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: HIGH
last_primary_source_check: 2026-06-21
thesis_health_score: 60
confidence_score: 48
valuation_attractiveness_score: 34
urgency_score: 90
max_position_weight_pct: 0
current_position_weight_pct: 0
approved_entry_zone: No new capital until scheduled scan validates valuation.
do_not_buy_zone: Any price without thesis, valuation, sizing, and invalidation.
sell_trigger_status: false
hedge_required: true
main_hedge: No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit invalidation.
open_questions_count: 0
broken_thesis: ""
---
# MU - Micron

## 0. Current Decision

### Simple decision

Current action: RESEARCH_REQUIRED

### One-line decision

Micron is a direct HBM/memory scarcity expression, but today's reported Anthropic partnership and share move require research before any capital change.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Chasing an unresolved customer/AI demand signal into a crowded memory-cycle move before June 24 earnings. |
| Main upside driver today | HBM demand, DRAM/NAND recovery, supply discipline, and AI server content growth. |
| Next review trigger | Partnership terms, primary-source confirmation, and June 24 earnings |

## 1. Role in Bottleneck Capital

Sleeve: `memory_storage_networking`

Why this asset belongs here: HBM and AI memory bottleneck.

What this asset is actually a bet on:

1. HBM demand, DRAM/NAND recovery, supply discipline, and AI server content growth.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- The upside may be cyclical pricing rather than durable structural scarcity.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: RESEARCH_REQUIRED
Confidence: 48
Time horizon: multi-year
Importance: HIGH

Claim: Micron is a direct HBM/memory scarcity expression, but the memory cycle and SA put signal make entry discipline crucial.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_1/MU.md; wave execution memo.
- Sleeve thesis: `memory_storage_networking`.
- June 22, 2026 market reports describe an Anthropic partnership spanning HBM, DRAM, and SSDs, with MU up roughly 5-6% ahead of June 24 earnings.

Evidence against:
- The upside may be cyclical pricing rather than durable structural scarcity.
- Memory cycle reversal, oversupply, capex response, and customer concentration.
- Reported deal economics, duration, margin impact, and valuation support are not yet underwritten.

What would break it:
- HBM leadership or memory pricing breaks while valuation remains elevated.

Decision impact:
RESEARCH_REQUIRED. Do not add capital until the partnership economics, June 24 earnings setup,
valuation, and sizing are reviewed.

Hedge implication:
No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit invalidation.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: cycle-normalized earnings plus HBM scarcity scenario value. The June 22 move may improve the structural demand case, but current evidence does not approve a buy.

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
| Thesis purity | 4 | HBM and AI memory bottleneck. |
| Durability | 4 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 4 | Main risk: Memory cycle reversal, oversupply, capex response, and customer concentration. |
| Management / execution | 4 | Execution still matters. |
| Strategic scarcity | 3 | Upside: HBM demand, DRAM/NAND recovery, supply discipline, and AI server content growth. |
| Contract quality | 3 | Needs source-event verification. |
| Customer quality | 3 | Needs source-event verification. |
| Pricing power | 3 | Valuation frame: cycle-normalized earnings plus HBM scarcity scenario value. |
| Downside survivability | 3 | Invalidation: HBM leadership or memory pricing breaks while valuation remains elevated. |
| Hedgeability | 3 | Long-only hedge is sizing/no action. |

Long-term owner score: 34 / 50

## 5. Valuation and Entry Discipline

Valuation frame: cycle-normalized earnings plus HBM scarcity scenario value

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker MU` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- HBM leadership or memory pricing breaks while valuation remains elevated.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Memory cycle reversal, oversupply, capex response, and customer concentration.
- The upside may be cyclical pricing rather than durable structural scarcity.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit invalidation.

## 10. Latest Signals

- June 22, 2026: Market reports describe a Micron-Anthropic AI memory/storage partnership and a 5-6% MU share move ahead of June 24 earnings. Treat as unresolved material event until economics and valuation are underwritten.
- Wave: 1
- Source classification: `sa_reported_current_13f`
- Instrument role: `common_equity_call_signal_and_put_signal`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_1/MU.md`
- `reports/initialization/2026-06-20-wave-1-execution.md`

Evidence quality: market-news update plus SA filing and local baseline. No unscheduled market
action is authorized until primary-source terms, earnings, valuation, and sizing are reviewed.

## 12. Open Questions

- What are the Anthropic partnership term, volume, margin, prepayment, and duration economics?
- Does June 24 earnings confirm structural HBM/DRAM scarcity or only peak-cycle pricing?
- Is valuation still acceptable after the reported 5-6% move and large year-to-date run?

## 13. Latest Agent Notes

June 22 material news moved current action to RESEARCH_REQUIRED, with no BUY_NOW, ADD_ON_DIP,
TRIM, or SELL action authorized.
