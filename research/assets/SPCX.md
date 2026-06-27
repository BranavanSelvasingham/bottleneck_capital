---
ticker: SPCX
name: SpaceX / SPCX ticker signal
sleeve: space_infra
last_updated: 2026-06-22
source_classification: sa_adjacent_thesis_proxy
instrument_role: local_position_adjacent_proxy
trade_policy: long_only_after_research
thesis_damage: false
unresolved_material_event: false
evidence_quality: LIVE_SEC_8K_AND_PRICE_DISLOCATION_REVIEWED
thesis_expressed: SPCX is tracked as Space Exploration Technologies Corp. live public equity exposure and a user-held adjacent proxy for launch, satellite, connectivity, defense infrastructure, and AI-infrastructure scarcity.
anti_thesis: The June 22 senior unsecured notes filing and price dislocation highlight debt, bridge-loan refinancing, valuation, and post-IPO volatility risk.
hedge_or_sizing: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
invalidation_trigger: Senior-note terms, bridge-loan refinancing, customer demand, or liquidity risk show the post-IPO equity is overlevered or no longer a clean space/AI infrastructure expression.
next_trigger: Review June 22 senior-note pricing/use of proceeds, bridge-loan repayment, post-IPO valuation, and local cost basis before any add/sell decision.
one_line_rationale: "RESEARCH_REQUIRED: SPCX June 22 8-K launched senior unsecured notes to repay bridge-loan borrowings while the stock fell sharply; no buy or sell until financing terms, valuation, and local cost basis are reviewed."
asset_role: Space infrastructure adjacent proxy and local-position tracker.
default_holding_period: multi_year
current_decision: RESEARCH_REQUIRED
dip_decision: RESEARCH_FIRST
sell_decision: NOT_TRIGGERED
research_priority: MEDIUM
last_primary_source_check: 2026-06-21
thesis_health_score: 42
confidence_score: 28
valuation_attractiveness_score: 18
urgency_score: 60
max_position_weight_pct: 0
current_position_weight_pct: 0
approved_entry_zone: No new capital until scheduled scan validates valuation.
do_not_buy_zone: Any price without thesis, valuation, sizing, and invalidation.
sell_trigger_status: false
hedge_required: true
main_hedge: No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.
open_questions_count: 3
broken_thesis: ""
---
# SPCX - SpaceX / SPCX ticker signal

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

SPCX is tracked as a user-held adjacent proxy for SpaceX-style launch, satellite, connectivity, and defense infrastructure scarcity, not as current public SA exposure.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | POSSIBLE, NOT APPROVED |
| Buy today? | NO |
| Add on dip? | RESEARCH_FIRST |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | Private-market access, listing uncertainty, liquidity, valuation, custody, and headline risk. |
| Main upside driver today | Reusable launch, satellite communications, defense demand, and space logistics scarcity. |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `space_infra`

Why this asset belongs here: Space infrastructure adjacent proxy and local-position tracker.

What this asset is actually a bet on:

1. Reusable launch, satellite communications, defense demand, and space logistics scarcity.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- The ticker/listing path, liquidity, valuation, and actual instrument exposure may be unclear or non-actionable.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE WATCH
Confidence: 28
Time horizon: multi-year
Importance: HIGH

Claim: SPCX is tracked as a user-held adjacent proxy for SpaceX-style launch, satellite, connectivity, and defense infrastructure scarcity, not as current public SA exposure.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_3/SPCX.md; wave execution memo.
- Sleeve thesis: `space_infra`.

Evidence against:
- The ticker/listing path, liquidity, valuation, and actual instrument exposure may be unclear or non-actionable.
- Private-market access, listing uncertainty, liquidity, valuation, custody, and headline risk.

What would break it:
- SPCX does not represent investable SpaceX/space-infra exposure or listing/liquidity risk becomes unacceptable.

Decision impact:
HOLD. Do not add capital until a scheduled scan or fresh primary-source event clears thesis,
valuation, and sizing.

Hedge implication:
No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: private-market infrastructure scarcity and listing/liquidity-adjusted scenario value. Current baseline does not approve a buy.

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
| Thesis purity | 3 | Space infrastructure adjacent proxy and local-position tracker. |
| Durability | 3 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 3 | Main risk: Private-market access, listing uncertainty, liquidity, valuation, custody, and headline risk. |
| Management / execution | 3 | Execution still matters. |
| Strategic scarcity | 2 | Upside: Reusable launch, satellite communications, defense demand, and space logistics scarcity. |
| Contract quality | 2 | Needs source-event verification. |
| Customer quality | 2 | Needs source-event verification. |
| Pricing power | 2 | Valuation frame: private-market infrastructure scarcity and listing/liquidity-adjusted scenario value. |
| Downside survivability | 2 | Invalidation: SPCX does not represent investable SpaceX/space-infra exposure or listing/liquidity risk becomes unacceptable. |
| Hedgeability | 2 | Long-only hedge is sizing/no action. |

Long-term owner score: 24 / 50

## 5. Valuation and Entry Discipline

Valuation frame: private-market infrastructure scarcity and listing/liquidity-adjusted scenario value

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker SPCX` |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: RESEARCH_FIRST

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- SPCX does not represent investable SpaceX/space-infra exposure or listing/liquidity risk becomes unacceptable.
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- Private-market access, listing uncertainty, liquidity, valuation, custody, and headline risk.
- The ticker/listing path, liquidity, valuation, and actual instrument exposure may be unclear or non-actionable.
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

No puts or shorts; use no-action discipline until valuation and thesis evidence justify capital.

## 10. Latest Signals

- Wave: 3
- Source classification: `sa_adjacent_thesis_proxy`
- Instrument role: `local_position_adjacent_proxy`
- Trade policy: `long_only_after_research`

## 11. Source Register

- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_3/SPCX.md`
- `reports/initialization/2026-06-20-wave-3-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
