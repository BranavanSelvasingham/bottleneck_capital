# Recommendation Calibration

## Purpose

Make the September 2026 retrospective change future behavior, not merely the wording of
the next report. The objective is better long-term, risk-aware allocation, not a higher
short-term win rate or automatic aggressiveness. The sample is small and correlated;
long-horizon valuation forecasts have not matured. No reliable alpha or doubling-every-year
ability has been established.

This protocol governs conversational recommendations and Portfolio PM reviews. It does
not authorize trades, change position limits, bypass strict-live, or rewrite decisions.
The journal records what was advised; it is not a second decision writer.

## Before Recommending

1. Read the latest memo, decision, handoff and live evidence as required by the review skill.
2. Run `./bcap recommendation review`; inspect both the latest call and older unscored calls.
3. Identify what changed since the last recommendation. Separate new business evidence,
   revised valuation assumptions, changed user constraints, and correction of an old error.
4. Reconfirm capacity from local data. Distinguish direct-equity concentration from total
   household assets and TFSA contribution room from cash available to invest. Unknown is
   not zero and is not permission to invent an exact concentration percentage.
5. Resolve the marginal allocation choice below, then append a recommendation packet before
   answering. No exact holdings or transaction fills belong in the packet.

## Decision Changes

### Entry And Waiting

- Separate a sound business, an attractive price, and a favorable near-term entry. Assess
  confidence in each independently using LOW/MODERATE/HIGH, with supporting evidence.
- For an intact, adequately researched thesis at acceptable valuation and within capacity,
  explicitly compare a small starter before a catalyst with waiting. Size against loss
  tolerance, event gap risk and correlation, not desire to maximize an optimistic outcome.
- A starter is an option to evaluate, not a mandatory purchase. Do not impose a universal
  tranche percentage or weaken existing BUY_NOW/ADD_ON_DIP eligibility gates.
- Every wait needs a reason, a review deadline, and a missed-entry response. An entry zone
  derived from valuation is not a prediction that the market will visit it tomorrow.
- Model the no-dip/upside-gap path as seriously as the selloff. Do not require both a
  reassuring announcement and the pre-announcement discount without acknowledging that
  those conditions may be mutually unlikely.
- Re-underwrite after material results, contracts, financing, or supply changes. Change
  limits when the evidence changes expected per-share value, not simply to follow a rally.
- For unlocks, distinguish eligible shares, likely sellers, available liquidity, short
  positioning, and observed absorption. Do not use total eligible supply as actual selling.
  If strong absorption contradicts the forecast, update the next forecast explicitly.

### Holding And Rotating

- An intact multi-year thesis can survive a drawdown. A short-term red mark does not by
  itself invalidate it, and a later rally does not prove the valuation model correct.
- Compare the source holding, destination and cash over the same investment horizon using
  normalized earnings/cash flow, bull-case opportunity, dilution, downside and correlation.
  Compare at least two named alternatives before declaring the best next dollar.
- A full exit needs thesis damage, unacceptable risk, lost thesis relevance, or an unusually
  strong documented opportunity-cost case. High multiples alone are insufficient.
- If the rationale is concentration rather than thesis failure, say so. Evaluate retaining
  a core or making a partial rotation; do not present risk reduction as a forecast of loss.
- Identify the rotation counterparty in the journal so later scoring cannot celebrate the
  destination while ignoring the larger gain in the stock recommended for sale.
- User pushback can reveal missing evidence or different constraints. It must not silently
  increase intrinsic value, erase a risk, or change a price target just to agree.

### Forecasts

- Use plausible scenarios, a stated horizon, assumptions and failure triggers. Avoid narrow
  next-day targets when the evidence cannot support them. Include the possibility of no dip.
- Probabilities, if supplied in narrative, must be called subjective unless independently
  calibrated. Define the measurable event and deadline before outcomes are known.
- Do not turn qualitative confidence scores into statistical probabilities or post hoc
  assign overlapping scenarios to whatever happened. Unscoreable forecasts stay unscored.

## Journal Workflow

The existing review skills already read AGENTS.md, which requires this protocol. No new
scheduler or duplicate research thread is needed. The CLI deliberately does not auto-log
machine-generated HOLDs as independent advice or fetch/guess a performance history.

```bash
./bcap recommendation review
./bcap recommendation record --input reports/local_recommendations/next_call.json
./bcap recommendation outcome --input reports/local_recommendations/outcome.json
```

Use `research/templates/recommendation.json` as the packet shape. Replace example symbols,
dates and assumptions. Inputs and the JSONL journal are gitignored. Free text still requires
a privacy check: field validation cannot detect every accidental disclosure inside prose.

The recorder stamps the actual recording time and accepts no caller-supplied backdated
timestamp. Revisions append a new ID, name the superseded ID, and specify `change_kind` and
`change_reason`. Reconstructed historical audits remain separate from prospective calls.
The review date expires the advice, not an actual broker order; no broker action is taken.

Freeze `reference_start_at` when recording each call: use the first regular-session open
after the recommendation, verified against the exchange calendar. All reference outcomes
start there, including unfilled limits and waits, so a later favorable start cannot be chosen.
The recorder requires a prospective start within seven days but does not verify that it is
the exchange's next open. Check that upstream; this is a reference baseline, not a fill.
Older records without a frozen reference start remain visible but unscorable by this
workflow. Preserve them; do not backfill a prospective claim after the fact.

The system checks packet completeness and temporal/arithmetic consistency. It cannot
determine whether a cited source is true, a thesis is sound, or a price condition actually
traded without a research review. Recording BUY_NOW is not passing strict-live.

## Outcome Evidence

Record each matured 5/21/63/252-session observation and explicit event deadline. Earlier
interim marks remain visible; never select only the most favorable endpoint. Do not count
reaffirmations or correlated calls as independent trials.

An outcome input contains:

- `recommendation_id`, `window` (5_sessions, 21_sessions, 63_sessions, 252_sessions, EVENT,
  or INTERIM), timezone-aware `start_at` and `end_at`.
- `session_dates`: the provider's actual sorted, unique trading dates spanning that
  interval. The CLI checks boundaries/counts/weekends, not an exchange holiday calendar.
- Common `currency` (USD/CAD), `price_basis` (UNADJUSTED_PRICE/TOTAL_RETURN_INDEX), and
  `prices`: objects with `ticker`, positive `start`, positive `end`, and a dated `source`.
  Include the recommendation, its frozen benchmark and any rotation counterparty. Each
  pair must use the same interval and basis; convert currencies consistently upstream.
  `start_at` must equal the call's frozen `reference_start_at`; fixed-session windows end
  at the close of the Nth session including that start session.
- `entry_observation`: UNVERIFIED, PRICE_TOUCHED, NOT_TOUCHED, or NO_ORDER. A price-touch
  claim additionally requires `entry_evidence` with `observed_at`, `price` and `source`.
  The quote must meet the limit after recording and before the review/expiry deadline.
- `notes`: data quality, actual observation dates, corporate actions and limitations.

Every computed result is labeled REFERENCE_PRICE_NOT_EXECUTION. The input does not contain
user fills, weights or quantities. PRICE_TOUCHED does not prove an executable fill or
qualitative clearance. NO_ORDER/unfilled results measure foregone opportunity, not profit.
Actual household P&L requires a separately reconciled private cash-flow record.

The recorder rejects pre-recommendation prices, missing comparison series, invalid window
counts, unsupported private-data fields, and silently replaced outcomes. Corrections must
link `supersedes` and provide `correction_reason`. It computes stock-versus-benchmark and
source-versus-destination differences; it does not manufacture a win rate or risk-adjusted
alpha. Corporate actions and adjusted-return conventions require upstream verification.

## User-Facing Report

Keep the final output concise. Include one primary action and:

1. What changed since the previous call, including a correction when needed.
2. Best use of the next dollar versus retaining the source holding and cash.
3. Starter/add conditions, expiry, and what to do if the dip never arrives.
4. Thesis / valuation / timing confidence, principal downside, and invalidation.
5. One relevant matured outcome or unresolved prior call, without turning every review into
   a long retrospective. Private capacity constraints should not leak into tracked files.

Do not replace these steps with a promise to be more conservative or more aggressive.
The improvement is consistent evidence, explicit opportunity cost and measurable follow-up.
