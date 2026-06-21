---
ticker:
name:
sleeve:
asset_role:
default_holding_period: multi_year
current_decision: RESEARCH_REQUIRED
dip_decision: NOT_ARMED
sell_decision: NOT_TRIGGERED
research_priority: MEDIUM
last_updated:
last_primary_source_check:
thesis_health_score:
confidence_score:
valuation_attractiveness_score:
urgency_score:
max_position_weight_pct:
current_position_weight_pct:
approved_entry_zone:
do_not_buy_zone:
sell_trigger_status: false
hedge_required:
main_hedge:
open_questions_count:
thesis_damage: false
unresolved_material_event: false
broken_thesis:
invalidation_trigger:
---

# {TICKER} - {Company Name}

## 0. Current Decision

### Simple decision

Current action: BUY_NOW / ADD_ON_DIP / HOLD / TRIM / SELL / RESEARCH_REQUIRED

### One-line decision

Write one sentence that says exactly what to do and why.

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | YES / NO / UNCLEAR |
| Buy today? | YES / NO / ONLY_ON_DIP |
| Add on dip? | YES / NO / RESEARCH_FIRST |
| Sell / exit? | YES / NO / ONLY_IF_TRIGGERED |
| Hedge required? | YES / NO |
| Main risk today |  |
| Main upside driver today |  |
| Next review trigger |  |

### Action rules

BUY_NOW if:
- Thesis health is strong.
- Valuation is attractive or acceptable.
- Hedge or sizing response and invalidation trigger are explicit.

ADD_ON_DIP if:
- Price fell faster than the thesis deteriorated.
- No primary-source evidence shows core thesis damage.
- Valuation improved and portfolio risk allows adding.

HOLD if:
- Thesis remains intact.
- Valuation or uncertainty does not justify new capital.
- Sell triggers are not active.

TRIM if:
- Valuation outruns thesis.
- Position risk rises while thesis remains intact.
- Hedge or sizing discipline requires lower exposure.

SELL if:
- A named thesis breaks.
- Risk becomes unacceptable.
- The asset no longer expresses the intended sleeve thesis.

RESEARCH_REQUIRED if:
- Price, filing, news, financing, or contract movement is material but unresolved.
- Primary-source evidence is stale.
- The action cannot be justified from current research.

---

## 1. Role in Bottleneck Capital

### Sleeve

Compute scarcity / power bottleneck / miner-to-datacenter / memory-storage-networking / crowded-AI hedge / other.

### Why this asset belongs here

Explain why this company is a clean or imperfect expression of the sleeve thesis.

### What this asset is actually a bet on

This position expresses the following theses:

1.
2.
3.

### What this asset is not a bet on

Clarify hidden assumptions you do not want.

---

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: ACTIVE / FRAGILE / BROKEN / UNPROVEN  
Confidence: 0-100  
Time horizon:  
Importance: CRITICAL / HIGH / MEDIUM / LOW

Claim:

Why it matters:

Evidence for:
-
-

Evidence against:
-
-

What would strengthen it:
-

What would weaken it:
-

What would break it:
-

Decision impact:
BUY / ADD / HOLD / TRIM / SELL

Hedge implication:

### Thesis B - Secondary thesis

Use the same structure.

### Thesis C - Valuation thesis

Use the same structure.

### Thesis D - Catalyst thesis

Use the same structure.

### Thesis E - Balance sheet / financing thesis

Use the same structure.

---

## 3. Market-Implied View vs Variant View

### What the market seems to believe

-
-

### Our variant view

-
-

### Why the market may be wrong

-
-

### Why we may be wrong

-
-

### Is the variant view big enough to matter?

YES / NO / UNCLEAR

Explanation:

---

## 4. Long-Term Ownership Quality

Score each 0-5.

| Dimension | Score | Notes |
|---|---:|---|
| Thesis purity |  |  |
| Durability |  |  |
| Balance sheet resilience |  |  |
| Management / execution |  |  |
| Strategic scarcity |  |  |
| Contract quality |  |  |
| Customer quality |  |  |
| Pricing power |  |  |
| Downside survivability |  |  |
| Hedgeability |  |  |

### Long-term owner score

Total: __ / 50

Interpretation:
- 40-50: Core long-term candidate
- 30-39: Good but needs valuation discipline
- 20-29: Tactical or speculative
- Under 20: Avoid unless special situation

---

## 5. Valuation and Entry Discipline

This section exists because the strategy is long-term, but discounts and dips matter.

### Valuation frame

Use the best available framework:

- DCF
- revenue multiple
- EBITDA multiple
- asset value
- power capacity value
- contracted backlog value
- sum-of-the-parts
- replacement cost
- relative value
- scenario value

### Fair value ranges

| Case | Assumptions | Value / Range | Probability |
|---|---|---:|---:|
| Bear |  |  |  |
| Base |  |  |  |
| Bull |  |  |  |

### Required margin of safety

Required discount to base case: __%

### Entry zones

| Zone | Meaning | Action |
|---|---|---|
| Deep discount | Thesis intact, price very attractive | BUY_NOW / ADD |
| Fair entry | Acceptable long-term entry | BUY / SMALL_ADD |
| Full price | Good company, weak entry | HOLD |
| Overextended | Risk/reward poor | TRIM / WAIT |
| Danger zone | Price implies unrealistic assumptions | TRIM / SELL |

### Current valuation judgment

Cheap / fair / expensive / unknowable.

### Valuation-based decision

BUY / ADD_ON_DIP / HOLD / TRIM / SELL.

---

## 6. Dip Protocol

This is the fast-reaction section.

### Is this asset dip-buy eligible?

YES / NO / ONLY_AFTER_RESEARCH

### Dip-buy thesis

We buy dips only when the price falls faster than the thesis deteriorates.

### Approved dip causes

Buyable dip causes:
- Broad-market selloff
- Sector-wide AI-beta selloff
- Temporary sentiment shock
- Non-thesis-related liquidity move
- Overreaction to known risk
- Short-term disappointment that does not impair long-term thesis

Non-buyable dip causes:
- Customer loss
- Financing stress
- Dilution worse than expected
- Contract quality deterioration
- Guidance cut tied to core thesis
- Evidence that demand is weaker than believed
- Management credibility damage
- Regulatory or legal issue that impairs long-term value

### Dip trigger checklist

If price falls sharply, answer:

1. What caused the move?
2. Is the cause thesis-related?
3. Did primary evidence change?
4. Did valuation become attractive?
5. Is the balance sheet still safe?
6. Has the hedge book changed?
7. Does portfolio sizing allow adding?
8. Is there a better asset expressing the same thesis?

### Dip action

- BUY_DIP_NOW
- ADD_SMALL
- WAIT_FOR_RESEARCH
- DO_NOT_BUY
- SELL_BECAUSE_THESIS_BROKE

### Dip memo template

Date:  
Move:  
Cause:  
Thesis damage? YES / NO / UNCLEAR  
Evidence checked:  
Decision:  
Reason:  
Review window:

---

## 7. Sell / Exit Protocol

We are long-term holders, so sell signals should be rare and serious.

### Sell immediately if

- Core thesis broken
- Fraud / governance impairment
- Liquidity or solvency risk becomes unacceptable
- Asset no longer expresses the intended thesis
- Better risk-adjusted alternative exists and opportunity cost is high
- Position exceeds risk budget and hedge is insufficient

### Trim if

- Valuation outruns thesis
- Portfolio concentration becomes too high
- Risk rises but thesis remains intact
- Hedge becomes too expensive
- Upcoming binary event is not worth full exposure

### Hold through volatility if

- Thesis intact
- Drawdown caused by broad market or sector
- Evidence remains favorable
- Position size is appropriate
- Hedge map still works

### Current sell trigger status

NOT_TRIGGERED / WATCH / TRIGGERED

---

## 8. Failure Modes

Classify wrongness.

| Failure Mode | Description | Probability | Damage | Detection Signal | Response |
|---|---|---:|---:|---|---|
| Thesis wrong |  |  |  |  |  |
| Timing wrong |  |  |  |  |  |
| Valuation wrong |  |  |  |  |  |
| Sizing wrong |  |  |  |  |  |
| Portfolio wrong |  |  |  |  |  |
| Hedge wrong |  |  |  |  |  |
| Evidence wrong |  |  |  |  |  |
| Regime wrong |  |  |  |  |  |
| Liquidity wrong |  |  |  |  |  |
| Behavioral wrong |  |  |  |  |  |

---

## 9. Hedge Map

### Main risk we need to hedge

...

### Preferred hedge

...

### Why this hedge matches the failure mode

...

### Hedge alternatives

| Hedge | Risk addressed | Cost | Basis risk | Upside sacrificed | Stress reliability | Verdict |
|---|---|---:|---:|---:|---:|---|
| Position sizing |  |  |  |  |  |  |
| Sector hedge |  |  |  |  |  |  |
| Pair trade |  |  |  |  |  |  |
| Index hedge |  |  |  |  |  |  |
| Options hedge |  |  |  |  |  |  |
| Cash |  |  |  |  |  |  |

### Current hedge decision

UNHEDGED / HEDGED / PARTIALLY_HEDGED / HEDGE_REQUIRED / SIZE_REDUCTION_BETTER_THAN_HEDGE

---

## 10. Latest Signals

### Signal ledger

| Date | Signal | Source | Materiality | Thesis Impact | Decision Impact |
|---|---|---|---:|---|---|
|  |  |  |  |  |  |

### What changed since last update?

...

### What is noise?

...

### What needs immediate follow-up?

...

---

## 11. Source Register

Primary sources:
- SEC filings:
- Company IR:
- Earnings calls:
- Investor presentations:
- Press releases:

Secondary sources:
-

Low-confidence / do-not-overweight sources:
- Social media
- Unverified rumor
- Unsourced analyst commentary
- Recycled market narrative

---

## 12. Open Questions

| Priority | Question | Why it matters | Owner | Status |
|---|---|---|---|---|
| HIGH |  |  |  | OPEN |
| MEDIUM |  |  |  | OPEN |
| LOW |  |  |  | OPEN |

---

## 13. Latest Agent Notes

### YYYY-MM-DD - agent_name

Summary:

Decision change:

Thesis changes:

Hedge changes:

New open questions:

Next action:

