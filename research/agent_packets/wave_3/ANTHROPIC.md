# ANTHROPIC Agent Task Packet

Ticker: `ANTHROPIC` (internal pre-IPO research ID; not a public symbol)
Name: Anthropic PBC
Wave: 3
Owner agent: `asset_analyst.ANTHROPIC`
Sleeve agent: `sleeve_analyst.frontier_ai_platform`
Sleeve: `frontier_ai_platform`
Source classification: `sa_adjacent_thesis_proxy`
Instrument role: `pre_ipo_research_issuer`
Trade policy: `research_only_until_listed`
Priority: `high`
Requested runtime: best available model, prefer GPT-5.5 or newer when selectable,
reasoning effort extra-high.

## Job

Monitor the IPO path and underwrite the public instrument before any BUY or ADD_ON_DIP.

## Read

- `AGENTS.md`
- `configs/ipo_watch.yaml`
- `configs/agent_roster.yaml`
- `configs/automation_routing.yaml`
- `research/theses/frontier_ai_platform.md`
- `research/assets/ANTHROPIC.md`
- `research/decisions/ANTHROPIC.md`

## Required Questions

1. Has a public S-1, amendment, price range, exchange, ticker, or trading date appeared?
2. What do audited revenue, gross margin after compute, operating loss, and cash flow show?
3. What is fully diluted enterprise value across the proposed price range?
4. How much of the offering is primary versus secondary, and what supply unlocks later?
5. What cloud, chip, power, financing, and minimum-purchase commitments constrain cash flow?
6. How concentrated are customers, distribution partners, and compute providers?
7. What open-weight competition, regulation, safety, governance, or litigation can break the thesis?
8. What entry, sizing, invalidation, and no-chase rules apply after listing?

## Write Scope

- `research/assets/ANTHROPIC.md`
- `research/decisions/ANTHROPIC.md`
- ticker-specific memo under `research/memos/`

Do not invent a ticker, use private-market marks as a buy signal, or make the issuer actionable
before Portfolio PM records a post-prospectus decision.
