# NVDA Agent Task Packet

Ticker: `NVDA`  
Name: NVIDIA  
Wave: 1  
Owner agent: `asset_analyst.NVDA`  
Sleeve agent: `sleeve_analyst.crowded_ai_beta_hedge`  
Sleeve: `crowded_ai_beta_hedge`  
Source classification: `sa_reported_current_13f`  
Instrument role: `common_equity_with_put_signal`  
Trade policy: `long_only_after_research`  
Priority: `high`  
Initialization score: 109  

## Job

Underwrite as long-only candidate before any BUY or ADD_ON_DIP.

## Read

- `AGENTS.md`
- `configs/sa_universe.yaml`
- `configs/agent_roster.yaml`
- `configs/automation_routing.yaml`
- `research/theses/crowded_ai_beta_hedge.md`
- `research/assets/NVDA.md`
- `research/decisions/NVDA.md`

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

- `research/assets/NVDA.md`
- `research/decisions/NVDA.md`
- ticker-specific memo under `research/memos/`

Do not edit other ticker files.
