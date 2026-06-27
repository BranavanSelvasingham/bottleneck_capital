# Wave 3 Execution Memo - Baseline Applied

Date: 2026-06-21

Scope: adjacent proxies. The earlier triage questions have been resolved into the all-wave baseline decision files.

Current posture: HOLD/watch for every ticker. No BUY_NOW, ADD_ON_DIP, TRIM, or SELL action is authorized before the next scheduled market/filing process or a material event.

| Ticker | Agent id | Decision | Baseline rationale | Next trigger |
|---|---|---|---|---|
| CEG | `asset_analyst.CEG` | HOLD | Constellation is a high-quality power scarcity proxy, but it is not latest-current SA exposure and should stay watch-only absent promotion or a priced entry. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| LITE | `asset_analyst.LITE` | HOLD | Lumentum can benefit if AI optical components tighten, but it is not current SA exposure and should remain a watchlist proxy. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| MRVL | `asset_analyst.MRVL` | HOLD | Marvell is a plausible AI networking and custom silicon beneficiary, but not current SA exposure in this system. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| ONTO | `asset_analyst.ONTO` | HOLD | Onto is a plausible advanced packaging/process-control bottleneck proxy, but not current SA exposure. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| SPCX | `asset_analyst.SPCX` | HOLD | SPCX is tracked as a user-held adjacent proxy for SpaceX-style launch, satellite, connectivity, and defense infrastructure scarcity, not as current public SA exposure. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| TLNE | `asset_analyst.TLNE` | HOLD | Talen is a power scarcity proxy, but it is not latest-current SA exposure and should stay watch-only pending promotion or better entry evidence. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| VRT | `asset_analyst.VRT` | HOLD | Vertiv is a clear datacenter power/thermal equipment beneficiary, but it is not latest-current SA exposure in this system. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| VST | `asset_analyst.VST` | HOLD | Vistra is a strong power scarcity proxy, but not current public SA exposure and not an automatic long-only buy. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| WTS | `asset_analyst.WTS` | HOLD | Watts is a possible datacenter water/thermal infrastructure read-through, but the AI link is not yet material enough for action. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |

## Controls

- Long-only mandate remains active.
- Reported puts remain signal-only, not trade instructions.
- A future SA full exit forces exit/thesis-correction review.
- A material SA reduction forces high-priority thesis-weight review.
- No technical indicators are used.

## Output Files

- Ticker packets: `research/agent_packets/wave_3/`
- Asset files: `research/assets/{TICKER}.md`
- Decision files: `research/decisions/{TICKER}.md`
- Baseline summary: `reports/initialization/2026-06-21-all-wave-baseline.md`
