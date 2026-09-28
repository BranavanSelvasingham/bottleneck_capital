---
name: calibrate-investment-recommendations
description: Apply and evaluate Bottleneck Capital investment lessons across current-state reviews, broad outlooks, multibagger searches, and recommendation retrospectives. Reconcile earlier calls, apply versioned lessons, preregister changes against the previous approach, and distinguish process corrections from unproven return improvements. Use as a supporting step for those investment workflows, not as a substitute for live research or as permission to trade.
---

# Calibrate Investment Recommendations

## Load Shared Memory

Find the Bottleneck Capital root from the current project. Read its `AGENTS.md`,
`research/theses/recommendation_calibration.md`, and `research/learning/lessons.yaml`.
Run `./bcap recommendation review`. Do not use chat recollection as the source of an
old call, create a separate journal in a temporary worktree, or invent missing outcomes.
If the canonical local journal is unavailable, disclose the gap and locate the authorized
primary checkout before writing. Do not copy private data to a new checkout.

This is a supporting workflow. Continue the invoking skill's live research, valuation,
portfolio-capacity, and strict-live checks. It does not authorize orders, scheduler changes,
tracked investment-decision updates, or automatic policy promotion.

## Apply Before Choosing

Read each relevant lesson's scope, counterexamples, evidence and status, not just its title.
PROVISIONAL means a hypothesis to evaluate, not demonstrated alpha. SUPPORTED is limited
to the tested scope; RETIRED is historical context, not an active rule.

Record relevant `lesson_applications` in the recommendation packet: lesson ID, version,
APPLIED / NOT_APPLICABLE / COUNTEREVIDENCE, and the concrete effect on this call.
An unchanged decision is a valid effect; do not manufacture a change to satisfy the log.
Separate business conviction, valuation and timing, and explain a revision to the prior call.
Lessons cannot override thesis damage, capacity limits or missing entry clearance.

When testing a changed approach, freeze a `lesson_test` in that packet before the result:
lesson ID/version, old and new approaches, common evaluation window, success and failure
criteria, and a cohort key grouping correlated calls. Use executable conditional rules and
the same information, horizon, currency and hypothetical risk budget. Specify both paths
when a limit is not reached. Keep real quantities, weights and fills out of this record.
If the old approach cannot be reconstructed prospectively, mark the comparison untestable;
do not manufacture an old policy after seeing the result.

Append the packet with `./bcap recommendation record --input ...` before the final answer.
Store inputs only under `reports/local_recommendations/`. A failed record must be disclosed.

## Evaluate In Existing Reviews

Check matured windows before issuing the next call. Obtain sourced matching-date data and
append outcomes with `./bcap recommendation outcome --input ...`. Where a frozen lesson
test exists, include `lesson_assessment`: old/new approach results, sources, conclusion,
and a reason tied to the original criterion. Immature, missing-data, or ambiguous tests
stay INCONCLUSIVE. A price touch is not a fill; stock appreciation alone does not score a
staged-entry policy or prove multi-year intrinsic value.

For a lesson review, read all relevant application/test records, including unfavorable,
superseded and unscored calls. Use the latest explicit correction of an outcome. Group
reaffirmations, the same catalyst and common factor exposures; do not call them independent
trials. Compare opportunity cost, downside, implementation costs and process quality, not
only terminal return. Freeze any new test before collecting its evaluation sample.

Follow the protocol's lesson lifecycle. Routine reviews append private observations and
flag proposed rule changes; only an authorized lesson-maintenance/audit task edits the
public register through a scoped PR. Increment the version, preserve Git history, include
counterevidence and a privacy-safe evaluation note, and narrow or retire unsupported rules.
No automatic promotion, win-rate threshold, or new scheduler is implied.

## Keep The Report Short

Add one line to the invoking skill's existing report, not another full report:

`Lesson applied: L001 v1; compared a starter with waiting; the entry remains gated.`

Use the actual effect, or state that no relevant lesson changed the decision. When evidence
contradicts a lesson, say so. Mention one relevant matured comparison when available.
No claim that the process improved returns until prospective evidence supports it.
