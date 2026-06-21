# SPCX Agent Task Packet

Ticker: `SPCX`  
Name: SpaceX / SPCX ticker signal  
Wave: 3  
Owner agent: `asset_analyst.SPCX`  
Sleeve agent: `sleeve_analyst.space_infra`  
Sleeve: `space_infra`  
Source classification: `sa_adjacent_thesis_proxy`  
Instrument role: `local_position_adjacent_proxy`  
Trade policy: `long_only_after_research`  
Priority: `medium`  
Initialization score: 28  

## Job

Underwrite as long-only candidate before any BUY or ADD_ON_DIP.

## Read

- `AGENTS.md`
- `configs/sa_universe.yaml`
- `configs/agent_roster.yaml`
- `configs/automation_routing.yaml`
- `research/theses/space_infra.md`
- `research/assets/SPCX.md`
- `research/decisions/SPCX.md`

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

- `research/assets/SPCX.md`
- `research/decisions/SPCX.md`
- ticker-specific memo under `research/memos/`

Do not edit other ticker files.
