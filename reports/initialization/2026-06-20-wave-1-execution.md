# Wave 1 Execution Memo - Baseline Applied

Date: 2026-06-20

Scope: core / highest-signal names. The earlier triage questions have been resolved into the all-wave baseline decision files.

Current posture: HOLD/watch for every ticker. No BUY_NOW, ADD_ON_DIP, TRIM, or SELL action is authorized before the next scheduled market/filing process or a material event.

| Ticker | Agent id | Decision | Baseline rationale | Next trigger |
|---|---|---|---|---|
| MU | `asset_analyst.MU` | HOLD | Micron is a direct HBM/memory scarcity expression, but the memory cycle and SA put signal make entry discipline crucial. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| TSM | `asset_analyst.TSM` | HOLD | TSMC is a core foundry/advanced packaging scarcity asset, but geopolitics, customer concentration, and SA put exposure require sizing discipline. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| BE | `asset_analyst.BE` | HOLD | Bloom may be a direct answer to grid-constrained AI campuses if customers value rapid onsite power deployment. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| CRWV | `asset_analyst.CRWV` | HOLD | CoreWeave is a direct compute scarcity expression, but customer concentration, leverage, and GPU supply commitments make valuation discipline mandatory. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| ASML | `asset_analyst.ASML` | HOLD | ASML is the cleanest tooling scarcity asset in leading-edge chips, but the SA put signal makes valuation and China/export-control risk central. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| NVDA | `asset_analyst.NVDA` | HOLD | NVIDIA remains the highest-quality AI accelerator bottleneck, but SA put exposure flags valuation/crowding risk. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| IREN | `asset_analyst.IREN` | HOLD | IREN is a high-priority power/site conversion candidate, but new capital needs verified AI/HPC economics over mining beta. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| NBIS | `asset_analyst.NBIS` | HOLD | Nebius is a post-quarter SA evidence name and a compute-infra candidate, but jurisdiction, customer, and financing risk keep it hold-only. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| ORCL | `asset_analyst.ORCL` | HOLD | Oracle is tracked as SA reported put exposure; it informs capex duration and AI infrastructure risk, not long-only action. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |
| SMH | `asset_analyst.SMH` | HOLD | SMH is useful for interpreting SA semiconductor hedge/crowding risk, not for a long-only ETF trade right now. | Scheduled scan, SA filing change, company filing/IR update, financing/customer contract, guidance change, or detected valuation dip. |

## Controls

- Long-only mandate remains active.
- Reported puts remain signal-only, not trade instructions.
- A future SA full exit forces exit/thesis-correction review.
- A material SA reduction forces high-priority thesis-weight review.
- No technical indicators are used.

## Output Files

- Ticker packets: `research/agent_packets/wave_1/`
- Asset files: `research/assets/{TICKER}.md`
- Decision files: `research/decisions/{TICKER}.md`
- Baseline summary: `reports/initialization/2026-06-20-all-wave-baseline.md`
