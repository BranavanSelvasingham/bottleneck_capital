# Bottleneck Capital Weekend Thesis Rebuild

Date: 2026-07-11
Window: Saturday thesis rebuild
Sleeve: `compute_infra`
Schedule source: weekend thesis rebuild rotation
Source mode: local source-of-truth files and latest persisted state; no weekend live ingest run

## Executive Decision

- BUY_NOW: none.
- ADD_ON_DIP: none approved.
- HOLD: none as the stricter working state for this sleeve.
- RESEARCH_REQUIRED: CRWV, NBIS, SHAZ, WYFI.
- TRIM / SELL WATCH: none.
- SELL: none.

No compute-infra capital action is authorized. The sleeve still needs primary-source
customer, utilization, financing, valuation, and filing evidence before any name can move
from research-gated to buyable. The long-only mandate remains unchanged. Reported puts
remain signal-only and are not trade instructions. No technical indicators are used.

## Process Check

- Checked for active run locks and conflicting Bottleneck processes before writing:
  none found.
- Selected `compute_infra` because the latest Sunday prep and Monday sleeve review kept
  CRWV, NBIS, SHAZ, and WYFI in the highest-priority research queue.
- Wrote this report only; asset pages, decision pages, and the append-only decision
  ledger were not changed because no decision changed.

## Rebuilt Sleeve Thesis

AI model demand can create durable scarcity in contracted, power-secured compute
capacity, especially where capacity can be delivered faster than hyperscaler build
cycles. The investable thesis is not "own any AI cloud beta." It is "own durable,
contracted, financed, and power-secured compute capacity at a valuation that compensates
for customer concentration, leverage, utilization, and liquidity risk."

The sleeve should therefore split candidates into three evidence tiers:

1. Direct compute scarcity expression: CRWV. It has the cleanest thematic fit, but
   customer concentration, leverage, GPU supply commitments, utilization durability, and
   refinancing risk make valuation discipline mandatory.
2. AI cloud infrastructure clue: NBIS. It may express the same bottleneck through AI
   cloud capacity, but jurisdiction, customer demand, utilization, and funding runway
   need primary-source proof.
3. Small current SA compute-infra exposures: WYFI and SHAZ. These are useful signals, but
   both require a much higher evidence threshold because liquidity, governance, financing,
   and asset verification are not yet strong enough for capital.

## Current Sleeve State

| Ticker | Working Decision | Urgency | Evidence Quality | Rebuild Finding |
|---|---|---:|---|---|
| CRWV | RESEARCH_REQUIRED | HIGH | LIVE_PRICE_DISLOCATION_REVIEWED_NO_NEW_FILING | Cleanest compute-scarcity expression, but company-specific event review, customer concentration, leverage, GPU supply, utilization, and refinancing risk remain unresolved. |
| NBIS | RESEARCH_REQUIRED | HIGH | SA_FILING_AND_LOCAL_BASELINE | Post-quarter SA evidence and AI cloud candidate, but customer demand, utilization, funding runway, and jurisdiction risk still need primary-source confirmation. |
| WYFI | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Current public SA exposure, but durable compute assets, financing quality, liquidity, and contract economics are not verified enough for capital. |
| SHAZ | RESEARCH_REQUIRED | MEDIUM | SA_FILING_AND_LOCAL_BASELINE | Current public SA exposure, but asset verification, governance, liquidity, and customer economics remain below the action threshold. |

## Portfolio Synthesis

Compute infrastructure is one of the cleanest Bottleneck Capital sleeves because it maps
directly to AI capacity scarcity. It is also one of the easiest sleeves to overpay for:
the strongest revenue story can still fail as an investment if financing cost, customer
concentration, power access, utilization, or refinancing risk overwhelms the scarcity
premium.

For now, the sleeve should remain a research queue rather than a capital queue. CRWV and
NBIS deserve the fastest review because they are more direct capacity expressions and are
already high urgency. WYFI and SHAZ should stay tracked as public SA signals, but their
liquidity and evidence-quality discounts should keep max add at zero until primary
evidence improves.

## Decision Discipline

No `BUY_NOW` candidate exists. None of the sleeve names currently satisfies the required
buy conditions: strong thesis health, acceptable valuation, clean sleeve expression,
portfolio sizing allowance, understood anti-thesis, explicit sizing response, and an
invalidation trigger supported by current evidence.

No `ADD_ON_DIP` is approved. The latest action board bounded several dip causes as broad
cross-book de-risking, but bounded cause is not buy approval. A dip buy still requires no
core thesis damage, improved valuation, source evidence, and portfolio sizing capacity.

No sell is triggered. A sell or thesis-correction review becomes mandatory if public
filings show a full Situational Awareness exit, a material SA reduction weakens thesis
weight, or company filings, IR, financing, customer evidence, or guidance break the named
compute-infra thesis.

## Priority Review Queue

1. CRWV: determine whether customer concentration, leverage, GPU supply commitments,
   utilization durability, or refinancing risk impair the direct compute-scarcity thesis.
2. NBIS: verify customer demand, utilization, funding runway, and jurisdiction risk from
   primary sources.
3. WYFI: verify durable compute assets, financing quality, liquidity, and contract
   economics before treating any dip as actionable.
4. SHAZ: verify durable compute assets, governance, liquidity, customer economics, and
   financing discipline before any capital action.
5. Sleeve-level: build a valuation and sizing framework that distinguishes contracted
   compute capacity from speculative AI infrastructure beta.

## Data Gaps

- Filing ingest remains stale: last successful filing ingest was
  2026-06-22T14:32:37-04:00.
- No approved SEC mirror/proxy or filing vendor feed is configured in the persisted source
  state, so filing recovery remains required before filing-window confidence can be
  restored.
- Market ingest state is fresh as of 2026-07-11T06:47:12-04:00 through the Yahoo fallback,
  with Alpaca credentials still missing. This rebuild does not treat weekend market state
  as a trade signal.
- The latest action board still shows a material unresolved signal backlog, including all
  four compute-infra names, so max add remains zero for the sleeve.

## Monday Operating Plan

- Use the next Monday pre-market thesis scan to update CRWV and NBIS first.
- Keep WYFI and SHAZ as SA-signal research names until source evidence verifies durable
  assets, financing quality, customer contracts, and liquidity.
- Use `bcap signal resolve` only after documented research review; do not hand-edit old
  JSONL rows.
- Do not promote any compute-infra name out of `RESEARCH_REQUIRED` without explicit
  thesis, anti-thesis, sizing response, invalidation trigger, confidence, evidence
  quality, and valuation support.
