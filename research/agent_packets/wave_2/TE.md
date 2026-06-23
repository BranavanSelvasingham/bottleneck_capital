# TE Agent Task Packet

Ticker: `TE`
Name: T1 Energy
Wave: 2
Owner agent: `asset_analyst.TE`
Sleeve agent: `sleeve_analyst.power_bottleneck`
Sleeve: `power_bottleneck`
Source classification: `sa_reported_current_13f`
Instrument role: `common_equity`
Trade policy: `long_only_after_research`
Priority: `medium`
Initialization score: 58
Requested runtime: best available model, prefer GPT-5.5 or newer when selectable,
reasoning effort extra-high.

## Job

Underwrite as long-only candidate before any BUY or ADD_ON_DIP.

## Read

- `AGENTS.md`
- `configs/sa_universe.yaml`
- `configs/agent_roster.yaml`
- `configs/automation_routing.yaml`
- `research/theses/power_bottleneck.md`
- `research/assets/TE.md`
- `research/decisions/TE.md`

## Required Questions

1. What exact bottleneck or SA signal does this ticker express?
2. Is this current public SA exposure, post-quarter evidence, or only adjacent?
3. If put exposure exists, what risk is the put signal warning about?
4. Is this a clean long-only candidate under the user's mandate?
5. What would make it BUY_NOW, ADD_ON_DIP, HOLD, TRIM, SELL, or RESEARCH_REQUIRED?
6. What primary sources must be checked before changing the decision?
7. What hedge or sizing response replaces puts/shorts?
8. What named thesis break would force exit review?

## Write Scope

- `research/assets/TE.md`
- `research/decisions/TE.md`
- ticker-specific memo under `research/memos/`

Do not edit other ticker files.
