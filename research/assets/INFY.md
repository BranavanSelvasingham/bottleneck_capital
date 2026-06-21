---
ticker: INFY
name: Infosys
sleeve: ai_services_put_signal
last_updated: 2026-06-20
source_classification: sa_reported_current_13f
instrument_role: reported_put_signal
trade_policy: signal_only_no_puts_or_shorts
thesis_damage: false
unresolved_material_event: false
evidence_quality: SA_FILING_AND_LOCAL_BASELINE
thesis_expressed: Infosys is tracked as SA reported put exposure and should inform AI services disruption risk, not long-only action.
anti_thesis: A defensive services business does not matter if the signal is AI disruption risk.
hedge_or_sizing: No puts or shorts; use as risk signal only and do not allocate capital.
invalidation_trigger: Separate long-only thesis documented with valuation, sizing, and invalidation.
next_trigger: Next scheduled market/filing scan, SA filing change, company filing/IR update, financing or customer-contract news, guidance change, or a detected valuation dip.
one_line_rationale: Signal-only SA exposure; no long-only trade is authorized.
asset_role: Signal-only IT-services disruption risk map.
default_holding_period: multi_year
current_decision: HOLD
dip_decision: NOT_ARMED
sell_decision: NOT_TRIGGERED
research_priority: MEDIUM
last_primary_source_check: 2026-06-20
thesis_health_score: 35
confidence_score: 32
valuation_attractiveness_score: 18
urgency_score: 60
max_position_weight_pct: 0
current_position_weight_pct: 0
approved_entry_zone: No new capital until scheduled scan validates valuation.
do_not_buy_zone: Any price without thesis, valuation, sizing, and invalidation.
sell_trigger_status: false
hedge_required: true
main_hedge: No puts or shorts; use as risk signal only and do not allocate capital.
open_questions_count: 0
broken_thesis: ""
---
# INFY - Infosys

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

Infosys is tracked as SA reported put exposure and should inform AI services disruption risk, not long-only action.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | NO / SIGNAL ONLY |
| Buy today? | NO |
| Add on dip? | NO |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | AI cannibalization, pricing pressure, and demand slowdown. |
| Main upside driver today | Read-through to enterprise AI services margin pressure and labor substitution. |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `ai_services_put_signal`

Why this asset belongs here: Signal-only IT-services disruption risk map.

What this asset is actually a bet on:

1. Read-through to enterprise AI services margin pressure and labor substitution.
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- A defensive services business does not matter if the signal is AI disruption risk.
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: SIGNAL_ONLY  
Confidence: 32  
Time horizon: multi-year  
Importance: HIGH

Claim: Infosys is tracked as SA reported put exposure and should inform AI services disruption risk, not long-only action.

Evidence for:
- Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18; configs/watchlist.yaml; configs/sa_universe.yaml; research/agent_packets/wave_2/INFY.md; wave execution memo.
- Sleeve thesis: `ai_services_put_signal`.

Evidence against:
- A defensive services business does not matter if the signal is AI disruption risk.
- AI cannibalization, pricing pressure, and demand slowdown.

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
| Thesis purity | 2 | Signal-only IT-services disruption risk map. |
| Durability | 2 | Requires scheduled evidence refresh. |
| Balance sheet resilience | 2 | Main risk: AI cannibalization, pricing pressure, and demand slowdown. |
| Management / execution | 2 | Execution still matters. |
| Strategic scarcity | 2 | Upside: Read-through to enterprise AI services margin pressure and labor substitution. |
| Contract quality | 2 | Needs source-event verification. |
| Customer quality | 2 | Needs source-event verification. |
| Pricing power | 2 | Valuation frame: signal-only risk map, not an entry valuation. |
| Downside survivability | 2 | Invalidation: Separate long-only thesis documented with valuation, sizing, and invalidation. |
| Hedgeability | 2 | Long-only hedge is sizing/no action. |

Long-term owner score: 20 / 50

## 5. Valuation and Entry Discipline

Valuation frame: signal-only risk map, not an entry valuation

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run `bcap dip-investigate --ticker INFY` |
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

- AI cannibalization, pricing pressure, and demand slowdown.
- A defensive services business does not matter if the signal is AI disruption risk.
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
- `research/agent_packets/wave_2/INFY.md`
- `reports/initialization/2026-06-20-wave-2-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
