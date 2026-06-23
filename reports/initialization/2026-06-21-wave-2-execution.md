# Wave 2 Execution Memo - Baseline Applied

Date: 2026-06-21

Scope: remaining strict public 13F names. The earlier triage questions have been resolved into the all-wave baseline decision files.

Current posture: HOLD/watch for every ticker. No BUY_NOW, ADD_ON_DIP, TRIM, or SELL action is authorized before the next scheduled market/filing process or a material event.

| Ticker | Agent id | Decision | Baseline rationale | Next trigger |
|---|---|---|---|---|
| SNDK | `asset_analyst.SNDK` | HOLD | SanDisk may express NAND/storage scarcity after separation, but the memory cycle and balance sheet need discipline. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| AMD | `asset_analyst.AMD` | HOLD | AMD is a second-source AI accelerator candidate, but SA put exposure says the long case must clear high valuation and execution hurdles. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| INTC | `asset_analyst.INTC` | HOLD | Intel is a possible strategic foundry bottleneck, but execution, capital intensity, and put exposure keep the stock on hold. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| APLD | `asset_analyst.APLD` | HOLD | Applied Digital may monetize power and sites into AI/HPC datacenter capacity, but the underwriting hinges on contract quality and financing. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| BTDR | `asset_analyst.BTDR` | HOLD | Bitdeer offers power and infrastructure optionality, but the thesis is mixed across mining, ASICs, and possible HPC capacity. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| CORZ | `asset_analyst.CORZ` | HOLD | Core Scientific is one of the cleaner miner-to-HPC conversion candidates because contracted hosting can separate value from Bitcoin beta. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| AVGO | `asset_analyst.AVGO` | HOLD | Broadcom is tracked as SA reported put exposure, not as a long candidate under the current mandate. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| GLW | `asset_analyst.GLW` | HOLD | Corning may benefit from datacenter optical/fiber demand, but the put signal and non-AI end markets keep it watch-only. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| BITF | `asset_analyst.BITF` | HOLD | Bitfarms is a power/site option that could benefit from AI conversion, but current evidence is not strong enough for new capital. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| BW | `asset_analyst.BW` | HOLD | Babcock & Wilcox may fit the power bottleneck sleeve, but leverage and backlog quality make it a watch-only position until evidence improves. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| CLSK | `asset_analyst.CLSK` | HOLD | CleanSpark may own useful power/site optionality, but current posture is watch-only until AI datacenter economics become primary-source visible. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| HIVE | `asset_analyst.HIVE` | HOLD | HIVE has a plausible HPC pivot, but the equity remains too tied to mining until GPU/HPC revenue and contracts are clearer. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| PSIX | `asset_analyst.PSIX` | HOLD | Power Solutions International may supply engines/gensets into power scarcity, but the proof point is durable datacenter/customer backlog. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| PUMP | `asset_analyst.PUMP` | HOLD | ProPetro requires caution because the AI power link is less direct than other sleeve names and may be oilfield-services exposure. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| RIOT | `asset_analyst.RIOT` | HOLD | Riot has power and site optionality, but the current long-only case is not clean enough without stronger AI conversion evidence. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| SEI | `asset_analyst.SEI` | HOLD | Solaris Energy Infrastructure could fit AI power scarcity if contracted distributed power demand scales beyond legacy end markets. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| SHAZ | `asset_analyst.SHAZ` | HOLD | SharonAI is tracked because it appears in current public SA exposure, but liquidity, governance, and asset verification keep it hold-only. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| TE | `asset_analyst.TE` | HOLD | T1 Energy is tracked as a current SA holding, but business-model and financing clarity are not strong enough for new capital. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| WYFI | `asset_analyst.WYFI` | HOLD | WhiteFiber is tracked because it appears in current public SA exposure, but public evidence, liquidity, and financing quality need caution. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| INFY | `asset_analyst.INFY` | HOLD | Infosys is tracked as SA reported put exposure and should inform AI services disruption risk, not long-only action. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |

## Controls

- Long-only mandate remains active.
- Reported puts remain signal-only, not trade instructions.
- A future SA full exit forces exit/thesis-correction review.
- A material SA reduction forces high-priority thesis-weight review.
- No technical indicators are used.

## Output Files

- Ticker packets: `research/agent_packets/wave_2/`
- Asset files: `research/assets/{TICKER}.md`
- Decision files: `research/decisions/{TICKER}.md`
- Baseline summary: `reports/initialization/2026-06-21-all-wave-baseline.md`
