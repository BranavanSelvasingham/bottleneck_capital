# WTS Agent Task Packet

Ticker: `WTS`
Name: Watts Water Technologies
Wave: 3
Owner agent: `asset_analyst.WTS`
Sleeve agent: `sleeve_analyst.ai_power_equipment`
Sleeve: `ai_power_equipment`
Source classification: `sa_adjacent_thesis_proxy`
Instrument role: `common_equity`
Trade policy: `long_only_after_research`
Priority: `low`
Initialization score: 18
Requested runtime: best available model, prefer GPT-5.5 or newer when selectable,
reasoning effort extra-high.

## Job

Underwrite as long-only candidate before any BUY or ADD_ON_DIP.

## Read

- `AGENTS.md`
- `configs/sa_universe.yaml`
- `configs/agent_roster.yaml`
- `configs/automation_routing.yaml`
- `research/theses/ai_power_equipment.md`
- `research/assets/WTS.md`
- `research/decisions/WTS.md`

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

- `research/assets/WTS.md`
- `research/decisions/WTS.md`
- ticker-specific memo under `research/memos/`

Do not edit other ticker files.
