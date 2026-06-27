# AVGO Agent Task Packet

Ticker: `AVGO`
Name: Broadcom
Wave: 2
Owner agent: `asset_analyst.AVGO`
Sleeve agent: `sleeve_analyst.crowded_ai_beta_hedge`
Sleeve: `crowded_ai_beta_hedge`
Source classification: `sa_reported_current_13f`
Instrument role: `reported_put_signal`
Trade policy: `signal_only_no_puts_or_shorts`
Priority: `high`
Initialization score: 62
Requested runtime: best available model, prefer GPT-5.5 or newer when selectable,
reasoning effort extra-high.

## Job

Keep signal-only unless a separate long-only thesis emerges.

## Read

- `AGENTS.md`
- `configs/sa_universe.yaml`
- `configs/agent_roster.yaml`
- `configs/automation_routing.yaml`
- `research/theses/crowded_ai_beta_hedge.md`
- `research/assets/AVGO.md`
- `research/decisions/AVGO.md`

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

- `research/assets/AVGO.md`
- `research/decisions/AVGO.md`
- ticker-specific memo under `research/memos/`

Do not edit other ticker files.
