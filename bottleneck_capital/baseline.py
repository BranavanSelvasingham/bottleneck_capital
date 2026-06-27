from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import load_watchlist
from bottleneck_capital.initialize import rank_tickers
from bottleneck_capital.io import write_markdown_with_frontmatter

SA_13F_SOURCE = "Situational Awareness LP public 13F-HR, 2026-03-31 period, filed 2026-05-18"


@dataclass(frozen=True)
class BaselineNote:
    role: str
    thesis: str
    anti_thesis: str
    upside: str
    risk: str
    invalidation: str
    valuation_frame: str
    quality_score: int
    thesis_health: int
    confidence: int
    valuation_score: int


TICKER_BASELINES: dict[str, BaselineNote] = {
    "ASML": BaselineNote(
        "Lithography and leading-edge semicap bottleneck.",
        "ASML is the cleanest tooling scarcity asset in leading-edge chips, but the SA put "
        "signal makes valuation and China/export-control risk central.",
        "Semicap cycle, export controls, or customer capex digestion can overpower monopoly "
        "quality for long periods.",
        "EUV demand, advanced packaging/foundry intensity, and scarcity economics.",
        "Order weakness, geopolitics, capex cycle drawdown, or put-signal crowding risk.",
        "Sustained leading-edge order/backlog deterioration or export controls that impair "
        "the core EUV growth runway.",
        "relative semicap quality plus order/backlog durability",
        42,
        70,
        55,
        35,
    ),
    "AMD": BaselineNote(
        "AI accelerator challenger and crowded-beta risk map.",
        "AMD is a second-source AI accelerator candidate, but SA put exposure says the long "
        "case must clear high valuation and execution hurdles.",
        "NVIDIA ecosystem strength, software lock-in, or gross-margin pressure may keep AMD "
        "from becoming a true bottleneck.",
        "MI accelerator adoption, datacenter share gains, and customer second-sourcing.",
        "Crowded AI beta, product execution, software ecosystem, and margin dilution.",
        "AI accelerator roadmap fails to gain durable datacenter traction at acceptable margins.",
        "relative AI accelerator share and datacenter margin scenario value",
        31,
        52,
        45,
        30,
    ),
    "APLD": BaselineNote(
        "AI datacenter conversion and power-site optionality.",
        "Applied Digital may monetize power and sites into AI/HPC datacenter capacity, but "
        "the underwriting hinges on contract quality and financing.",
        "The company may be more financing-sensitive development exposure than durable "
        "infrastructure scarcity.",
        "Signed customer demand, power access, and funded datacenter buildout.",
        "Customer concentration, project finance, dilution, power delivery, and execution.",
        "Major customer/financing failure or evidence that sites cannot support contracted "
        "AI load.",
        "contracted backlog value plus power-site replacement cost",
        27,
        48,
        40,
        28,
    ),
    "AVGO": BaselineNote(
        "Signal-only AI networking/custom-silicon risk map.",
        "Broadcom is tracked as SA reported put exposure, not as a long candidate under the "
        "current mandate.",
        "A strong AI networking/custom-silicon business does not make a trade if the signal "
        "is only downside/crowding risk.",
        "Risk read-through for AI networking, custom silicon, VMware leverage, and semis.",
        "Crowded AI expectations, integration risk, and valuation sensitivity.",
        "Separate long-only thesis documented with valuation, sizing, and invalidation.",
        "signal-only risk map, not an entry valuation",
        25,
        45,
        35,
        20,
    ),
    "BE": BaselineNote(
        "Onsite power solution for AI datacenter scarcity.",
        "Bloom may be a direct answer to grid-constrained AI campuses if customers value "
        "rapid onsite power deployment.",
        "Fuel-cell economics, warranty risk, financing needs, or loose energy-transition "
        "exposure may swamp datacenter upside.",
        "Datacenter customer wins, backlog conversion, margin improvement, and financing access.",
        "Contract quality, product reliability, cash needs, customer concentration, and margins.",
        "Datacenter backlog fails to convert or financing/product risk impairs delivery economics.",
        "backlog quality, gross-margin path, and funded growth scenario value",
        30,
        55,
        45,
        32,
    ),
    "BITF": BaselineNote(
        "Miner-to-datacenter optionality.",
        "Bitfarms is a power/site option that could benefit from AI conversion, but current "
        "evidence is not strong enough for new capital.",
        "The equity may remain mostly Bitcoin beta with dilution rather than datacenter scarcity.",
        "Power portfolio monetization, AI/HPC conversion, or strategic site value.",
        "Bitcoin price beta, dilution, conversion capex, and weak customer evidence.",
        "No credible AI/HPC path emerges and economics remain dominated by mining exposure.",
        "power-site value versus mining NAV and funding dilution",
        22,
        40,
        35,
        24,
    ),
    "BTDR": BaselineNote(
        "Bitcoin miner, ASIC, and datacenter optionality.",
        "Bitdeer offers power and infrastructure optionality, but the thesis is mixed across "
        "mining, ASICs, and possible HPC capacity.",
        "The business may be too exposed to crypto cycles and hardware execution to be a clean "
        "AI bottleneck.",
        "AI/HPC site conversion, power monetization, and infrastructure optionality.",
        "Crypto beta, capital intensity, ASIC execution, and funding risk.",
        "AI/HPC conversion remains immaterial while mining/hardware cyclicality drives value.",
        "power-site value plus mining/hardware scenario value",
        24,
        42,
        35,
        24,
    ),
    "BW": BaselineNote(
        "Power equipment and industrial turnaround exposure.",
        "Babcock & Wilcox may fit the power bottleneck sleeve, but leverage and backlog "
        "quality make it a watch-only position until evidence improves.",
        "This could be a levered industrial turnaround rather than an AI power solution.",
        "Backlog tied to power reliability, clean generation, or datacenter-adjacent demand.",
        "Debt, project execution, margins, and thesis purity.",
        "Liquidity or backlog deterioration removes any credible power-bottleneck expression.",
        "backlog, liquidity, and normalized EBITDA scenario value",
        20,
        38,
        32,
        22,
    ),
    "CEG": BaselineNote(
        "Adjacent nuclear/generation power proxy.",
        "Constellation is a high-quality power scarcity proxy, but it is not latest-current "
        "SA exposure and should stay watch-only absent promotion or a priced entry.",
        "Power scarcity may already be recognized, and utility/regulatory risk can limit upside.",
        "Nuclear fleet scarcity, datacenter PPAs, and rising reliable-power value.",
        "Regulation, valuation, contract repricing, and non-SA source status.",
        "Datacenter/power thesis weakens or SA/current evidence does not support promotion.",
        "generation fleet value, PPA economics, and relative power scarcity",
        35,
        58,
        42,
        28,
    ),
    "CLSK": BaselineNote(
        "Miner-to-datacenter watchlist candidate.",
        "CleanSpark may own useful power/site optionality, but current posture is watch-only "
        "until AI datacenter economics become primary-source visible.",
        "The stock may remain a Bitcoin miner with limited AI conversion relevance.",
        "Site optionality, power access, and possible strategic conversion value.",
        "Mining beta, capex, dilution, and lack of contracted AI demand.",
        "No credible conversion route and mining economics remain the dominant value driver.",
        "mining NAV plus power-site option value",
        23,
        40,
        34,
        23,
    ),
    "CORZ": BaselineNote(
        "HPC hosting conversion candidate.",
        "Core Scientific is one of the cleaner miner-to-HPC conversion candidates because "
        "contracted hosting can separate value from Bitcoin beta.",
        "Customer concentration, post-restructuring capital needs, or power delivery risk can "
        "still make the equity fragile.",
        "HPC contract durability, CoreWeave-related demand, and site/power monetization.",
        "Counterparty concentration, financing, mining residual exposure, and execution.",
        "HPC contracts weaken or financing prevents profitable conversion of sites.",
        "contracted HPC backlog plus power capacity value",
        29,
        52,
        42,
        30,
    ),
    "CRWV": BaselineNote(
        "Scarce contracted AI cloud compute.",
        "CoreWeave is a direct compute scarcity expression, but customer concentration, leverage, "
        "and GPU supply commitments make valuation discipline mandatory.",
        "It may be a highly financed GPU-capacity trade rather than durable infrastructure value.",
        "Contracted AI demand, power-secured capacity, and faster deployment than hyperscalers.",
        "Customer concentration, debt/refinancing, GPU supply, and utilization durability.",
        "Large customer demand weakens, refinancing risk rises, or contracted utilization breaks.",
        "contracted revenue, capacity economics, and leverage-adjusted scenario value",
        31,
        55,
        43,
        30,
    ),
    "GLW": BaselineNote(
        "AI optical/fiber beneficiary with put-signal caution.",
        "Corning may benefit from datacenter optical/fiber demand, but the put signal and "
        "non-AI end markets keep it watch-only.",
        "The AI link may be too diluted by consumer, display, or telecom cycles.",
        "Optical communications demand, datacenter fiber, and margin recovery.",
        "End-market dilution, cyclicality, and ambiguity of SA put exposure.",
        "AI/datacenter optical demand does not become material enough to change earnings power.",
        "segment recovery and AI optical contribution scenario value",
        28,
        48,
        38,
        27,
    ),
    "HIVE": BaselineNote(
        "Miner with GPU/HPC pivot optionality.",
        "HIVE has a plausible HPC pivot, but the equity remains too tied to mining until "
        "GPU/HPC revenue and contracts are clearer.",
        "The company may remain crypto beta with small AI optionality.",
        "GPU/HPC revenue, power/site monetization, and AI hosting progress.",
        "Mining cyclicality, jurisdiction, financing, and limited contract proof.",
        "HPC revenue remains immaterial and mining economics dominate value.",
        "mining NAV plus verified HPC revenue option value",
        22,
        39,
        34,
        22,
    ),
    "INFY": BaselineNote(
        "Signal-only IT-services disruption risk map.",
        "Infosys is tracked as SA reported put exposure and should inform AI services "
        "disruption risk, not long-only action.",
        "A defensive services business does not matter if the signal is AI disruption risk.",
        "Read-through to enterprise AI services margin pressure and labor substitution.",
        "AI cannibalization, pricing pressure, and demand slowdown.",
        "Separate long-only thesis documented with valuation, sizing, and invalidation.",
        "signal-only risk map, not an entry valuation",
        20,
        35,
        32,
        18,
    ),
    "INTC": BaselineNote(
        "Foundry and domestic semiconductor capacity turnaround.",
        "Intel is a possible strategic foundry bottleneck, but execution, capital intensity, "
        "and put exposure keep the stock on hold.",
        "The turnaround may consume capital without proving process or foundry competitiveness.",
        "Foundry progress, process roadmap execution, subsidies, and strategic customer wins.",
        "Execution delays, balance sheet strain, foundry losses, and competitive pressure.",
        "Foundry roadmap slips further or capital needs overwhelm strategic value.",
        "sum-of-the-parts foundry/product scenario value",
        26,
        45,
        38,
        25,
    ),
    "IREN": BaselineNote(
        "Power-rich miner-to-AI datacenter conversion.",
        "IREN is a high-priority power/site conversion candidate, but new capital needs "
        "verified AI/HPC economics over mining beta.",
        "The stock may still be a Bitcoin miner with expensive AI optionality.",
        "Power-secured sites, AI/HPC customer demand, and datacenter conversion economics.",
        "Bitcoin beta, funding needs, power delivery, and customer contract risk.",
        "AI/HPC conversion fails to become material or financing dilutes away site value.",
        "power capacity value plus contracted AI/HPC scenario value",
        28,
        50,
        40,
        28,
    ),
    "LITE": BaselineNote(
        "Adjacent optical/networking proxy.",
        "Lumentum can benefit if AI optical components tighten, but it is not current SA "
        "exposure and should remain a watchlist proxy.",
        "Telecom cyclicality may dominate any datacenter optical upside.",
        "AI transceiver/optical demand and datacom mix improvement.",
        "Telecom weakness, customer concentration, and non-SA status.",
        "AI/datacom demand fails to offset telecom cyclicality.",
        "datacom recovery and optical component scenario value",
        25,
        42,
        34,
        24,
    ),
    "MRVL": BaselineNote(
        "Adjacent AI networking/custom silicon proxy.",
        "Marvell is a plausible AI networking and custom silicon beneficiary, but not current "
        "SA exposure in this system.",
        "Custom silicon wins may be lumpy and valuation may already discount AI upside.",
        "AI custom silicon, electro-optics/networking, and datacenter revenue mix.",
        "Customer concentration, cycle risk, margin execution, and non-SA status.",
        "AI custom silicon/networking fails to drive durable earnings growth.",
        "AI datacenter revenue and margin scenario value",
        29,
        48,
        38,
        27,
    ),
    "MU": BaselineNote(
        "HBM and AI memory bottleneck.",
        "Micron is a direct HBM/memory scarcity expression, but the memory cycle and SA put "
        "signal make entry discipline crucial.",
        "The upside may be cyclical pricing rather than durable structural scarcity.",
        "HBM demand, DRAM/NAND recovery, supply discipline, and AI server content growth.",
        "Memory cycle reversal, oversupply, capex response, and customer concentration.",
        "HBM leadership or memory pricing breaks while valuation remains elevated.",
        "cycle-normalized earnings plus HBM scarcity scenario value",
        34,
        60,
        48,
        34,
    ),
    "NBIS": BaselineNote(
        "Post-quarter SA clue in AI cloud infrastructure.",
        "Nebius is a post-quarter SA evidence name and a compute-infra candidate, but "
        "jurisdiction, customer, and financing risk keep it hold-only.",
        "AI cloud ambition may require capital faster than contracts and utilization mature.",
        "Power-secured AI cloud capacity, customer demand, and infrastructure buildout.",
        "Jurisdiction, financing, customer concentration, and execution.",
        "AI cloud utilization, funding, or jurisdiction risk invalidates durable "
        "infrastructure value.",
        "capacity economics and funding-adjusted AI cloud scenario value",
        28,
        50,
        40,
        28,
    ),
    "NVDA": BaselineNote(
        "AI accelerator platform leader and crowded-beta anchor.",
        "NVIDIA remains the highest-quality AI accelerator bottleneck, but SA put exposure "
        "flags valuation/crowding risk.",
        "Valuation, export controls, customer concentration, or accelerator competition may "
        "compress returns despite strong fundamentals.",
        "GPU/platform demand, networking/software attach, and durable ecosystem advantage.",
        "Crowding, valuation, export controls, supply chain, and hyperscaler capex digestion.",
        "Datacenter growth or platform margins break enough to impair the accelerator thesis.",
        "datacenter earnings power and platform durability scenario value",
        43,
        72,
        55,
        35,
    ),
    "ONTO": BaselineNote(
        "Adjacent process-control and advanced-packaging proxy.",
        "Onto is a plausible advanced packaging/process-control bottleneck proxy, but not "
        "current SA exposure.",
        "The company may be a cyclical semicap beneficiary rather than a unique AI bottleneck.",
        "Advanced packaging, HBM/process control, and semicap recovery.",
        "Capex cycle, customer concentration, and non-SA status.",
        "Advanced packaging/process-control demand fails to create differentiated growth.",
        "semicap cycle-normalized earnings plus advanced-packaging contribution",
        28,
        46,
        36,
        26,
    ),
    "ORCL": BaselineNote(
        "Signal-only enterprise AI infrastructure risk map.",
        "Oracle is tracked as SA reported put exposure; it informs capex duration and AI "
        "infrastructure risk, not long-only action.",
        "OCI growth can be real while equity risk remains valuation/debt/capex sensitive.",
        "Read-through to AI cloud demand, capex burden, debt, and contracted backlog quality.",
        "Capex intensity, leverage, customer concentration, and crowded AI infrastructure "
        "expectations.",
        "Separate long-only thesis documented with valuation, sizing, and invalidation.",
        "signal-only risk map, not an entry valuation",
        24,
        42,
        34,
        20,
    ),
    "PSIX": BaselineNote(
        "Onsite power equipment candidate.",
        "Power Solutions International may supply engines/gensets into power scarcity, but "
        "the proof point is durable datacenter/customer backlog.",
        "It may be a small industrial cyclical rather than a scalable AI power bottleneck.",
        "Backlog tied to onsite power, datacenter demand, and margin expansion.",
        "Customer concentration, emissions/regulatory risk, supply chain, and liquidity.",
        "Backlog or customer evidence fails to connect power equipment demand to AI load growth.",
        "backlog, normalized margin, and customer-quality scenario value",
        24,
        43,
        34,
        25,
    ),
    "PUMP": BaselineNote(
        "Power-bottleneck purity test.",
        "ProPetro requires caution because the AI power link is less direct than other sleeve "
        "names and may be oilfield-services exposure.",
        "Oilfield services cyclicality may dominate any power-equipment read-through.",
        "Electric fleet or distributed power capabilities that translate into broader power "
        "demand.",
        "Thesis purity, oilfield cycle, customer concentration, and capex.",
        "No primary-source evidence ties the business to durable AI power bottlenecks.",
        "normalized oilfield-services earnings plus any verified power-equipment option",
        18,
        35,
        30,
        20,
    ),
    "RIOT": BaselineNote(
        "Power-heavy miner-to-datacenter option.",
        "Riot has power and site optionality, but the current long-only case is not clean "
        "enough without stronger AI conversion evidence.",
        "Bitcoin mining economics may remain the overwhelming driver of returns.",
        "Power portfolio monetization, AI conversion option, and strategic site value.",
        "Mining beta, execution, capex, dilution, and unclear AI customer demand.",
        "AI/datacenter conversion remains speculative and mining economics dominate value.",
        "mining NAV plus power-site option value",
        23,
        40,
        34,
        23,
    ),
    "SEI": BaselineNote(
        "Distributed/mobile power infrastructure candidate.",
        "Solaris Energy Infrastructure could fit AI power scarcity if contracted distributed "
        "power demand scales beyond legacy end markets.",
        "The company may remain energy-services cyclicality rather than durable datacenter power.",
        "Customer contracts, mobile power fleet growth, and margin expansion.",
        "End-market cyclicality, customer concentration, capex, and contract duration.",
        "Contracted power demand fails to scale or margins do not support fleet expansion.",
        "contracted fleet economics and normalized EBITDA scenario value",
        24,
        43,
        34,
        25,
    ),
    "SHAZ": BaselineNote(
        "Small compute-infra SA holding requiring high evidence threshold.",
        "SharonAI is tracked because it appears in current public SA exposure, but liquidity, "
        "governance, and asset verification keep it hold-only.",
        "It may be an illiquid/speculative proxy without enough public evidence for capital.",
        "Verified compute assets, customer contracts, and financing discipline.",
        "Liquidity, governance, related-party risk, financing, and contract verification.",
        "Public evidence fails to verify durable compute assets or customer economics.",
        "verified asset value, contract economics, and governance discount",
        15,
        30,
        25,
        15,
    ),
    "SMH": BaselineNote(
        "Signal-only semiconductor beta and crowding map.",
        "SMH is useful for interpreting SA semiconductor hedge/crowding risk, not for a "
        "long-only ETF trade right now.",
        "ETF exposure is too broad to express Bottleneck Capital's best single-name theses.",
        "Read-through to semiconductor crowding, index concentration, and AI beta risk.",
        "Crowded semicap/semi valuation, broad ETF exposure, and hedge-signal ambiguity.",
        "Separate long-only ETF thesis documented with valuation, sizing, and invalidation.",
        "signal-only risk map, not an entry valuation",
        24,
        40,
        34,
        20,
    ),
    "SNDK": BaselineNote(
        "AI storage/NAND scarcity candidate.",
        "SanDisk may express NAND/storage scarcity after separation, but the memory cycle and "
        "balance sheet need discipline.",
        "The case may be cyclical NAND beta rather than durable AI storage scarcity.",
        "NAND recovery, AI storage demand, and separation-driven operating focus.",
        "Memory cyclicality, leverage/separation issues, and pricing power uncertainty.",
        "NAND/storage recovery fails or balance sheet risk overwhelms AI storage upside.",
        "cycle-normalized NAND earnings and AI storage scenario value",
        27,
        48,
        38,
        27,
    ),
    "SPCX": BaselineNote(
        "Space infrastructure adjacent proxy and local-position tracker.",
        "SPCX is tracked as a user-held adjacent proxy for SpaceX-style launch, satellite, "
        "connectivity, and defense infrastructure scarcity, not as current public SA exposure.",
        "The ticker/listing path, liquidity, valuation, and actual instrument exposure may be "
        "unclear or non-actionable.",
        "Reusable launch, satellite communications, defense demand, and space logistics scarcity.",
        "Private-market access, listing uncertainty, liquidity, valuation, custody, and "
        "headline risk.",
        "SPCX does not represent investable SpaceX/space-infra exposure or listing/liquidity risk "
        "becomes unacceptable.",
        "private-market infrastructure scarcity and listing/liquidity-adjusted scenario value",
        24,
        42,
        28,
        18,
    ),
    "TE": BaselineNote(
        "Power supply/manufacturing thesis candidate.",
        "T1 Energy is tracked as a current SA holding, but business-model and financing "
        "clarity are not strong enough for new capital.",
        "It may be policy/manufacturing cyclicality rather than an AI power bottleneck.",
        "Manufacturing capacity, offtake/customer demand, and policy-supported power supply.",
        "Funding, customer demand, policy risk, and thesis purity.",
        "Business model, capacity funding, or customer demand fails to support "
        "power-bottleneck role.",
        "capacity value, offtake quality, and funding-adjusted scenario value",
        18,
        35,
        30,
        20,
    ),
    "TLNE": BaselineNote(
        "Adjacent generation/power scarcity proxy.",
        "Talen is a power scarcity proxy, but it is not latest-current SA exposure and should "
        "stay watch-only pending promotion or better entry evidence.",
        "Datacenter power upside may already be capitalized or limited by contract/regulatory "
        "risk.",
        "Datacenter PPAs, generation scarcity, and interconnection value.",
        "Regulatory risk, contract quality, leverage, and non-SA status.",
        "Datacenter power contract thesis weakens or source evidence does not support promotion.",
        "generation fleet value and contracted datacenter power economics",
        30,
        50,
        38,
        25,
    ),
    "TSM": BaselineNote(
        "Foundry and advanced packaging bottleneck.",
        "TSMC is a core foundry/advanced packaging scarcity asset, but geopolitics, customer "
        "concentration, and SA put exposure require sizing discipline.",
        "Geopolitical risk or capex cyclicality can dominate even a strong structural moat.",
        "Advanced-node foundry demand, CoWoS/packaging scarcity, and AI accelerator volume.",
        "Taiwan geopolitical risk, customer concentration, capex cycle, and put-signal risk.",
        "Leading-edge foundry/packaging share or geopolitical risk invalidates ownership quality.",
        "foundry earnings power plus advanced-packaging scarcity scenario value",
        44,
        72,
        55,
        36,
    ),
    "VRT": BaselineNote(
        "Adjacent AI power and thermal equipment proxy.",
        "Vertiv is a clear datacenter power/thermal equipment beneficiary, but it is not "
        "latest-current SA exposure in this system.",
        "Valuation may already discount AI datacenter order strength.",
        "Datacenter power/thermal backlog, capacity expansion, and margin durability.",
        "Order normalization, supply chain, competition, valuation, and non-SA status.",
        "AI datacenter orders or margins normalize faster than expected.",
        "backlog, margin durability, and datacenter capex scenario value",
        34,
        58,
        42,
        28,
    ),
    "VST": BaselineNote(
        "Adjacent generation and power scarcity proxy.",
        "Vistra is a strong power scarcity proxy, but not current public SA exposure and not "
        "an automatic long-only buy.",
        "Power scarcity and nuclear/generation value may already be priced.",
        "Generation scarcity, datacenter PPAs, nuclear value, and power price exposure.",
        "Regulatory risk, valuation, commodity power prices, and non-SA status.",
        "Datacenter/generation scarcity thesis weakens or valuation offers no margin of safety.",
        "generation fleet value, PPA economics, and power scarcity scenario value",
        35,
        58,
        42,
        28,
    ),
    "WTS": BaselineNote(
        "Low-priority adjacent water/thermal infrastructure proxy.",
        "Watts is a possible datacenter water/thermal infrastructure read-through, but the "
        "AI link is not yet material enough for action.",
        "Core business exposure may be too far from the AI bottleneck thesis.",
        "Datacenter water, thermal, and infrastructure demand becoming material.",
        "Thesis remoteness, valuation, cyclicality, and non-SA status.",
        "No evidence that datacenter infrastructure materially changes earnings power.",
        "end-market mix and datacenter contribution scenario value",
        20,
        34,
        28,
        18,
    ),
    "WYFI": BaselineNote(
        "Small compute-infra current SA holding.",
        "WhiteFiber is tracked because it appears in current public SA exposure, but public "
        "evidence, liquidity, and financing quality need caution.",
        "The asset may be a narrow/illiquid listing with financing sensitivity rather than "
        "durable compute infrastructure.",
        "Verified datacenter/compute contracts, power access, and asset quality.",
        "Liquidity, governance, financing, customer contracts, and asset verification.",
        "Public evidence fails to verify durable compute assets or contract economics.",
        "verified asset value and contract economics with liquidity discount",
        16,
        32,
        26,
        16,
    ),
}


def write_all_wave_baseline(root: Path) -> list[Path]:
    watchlist = load_watchlist(root)
    ranked = rank_tickers(watchlist)
    wave_by_ticker = {item.ticker: item.wave for item in ranked}
    written: list[Path] = []
    report_lines = [
        "# All-Wave Baseline Underwrite",
        "",
        f"Date: {_today()}",
        "",
        "Scope: conservative first-pass decisions for every tracked ticker before the next "
        "scheduled market process. This pass does not create BUY_NOW or ADD_ON_DIP actions.",
        "",
        "| Ticker | Wave | Decision | Rationale |",
        "|---|---:|---|---|",
    ]
    for item in watchlist:
        ticker = item["ticker"]
        note = _baseline_for(ticker)
        wave = wave_by_ticker[ticker]
        decision = "HOLD"
        paths = _write_ticker(root, item, note, wave, decision)
        written.extend(paths)
        report_lines.append(
            f"| {ticker} | {wave} | {decision} | {note.thesis} |"
        )

    report_path = root / "reports" / "initialization" / f"{_today()}-all-wave-baseline.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    written.append(report_path)
    written.extend(_write_wave_execution_reports(root, ranked))
    return written


def _write_ticker(
    root: Path,
    item: dict[str, Any],
    note: BaselineNote,
    wave: int,
    decision: str,
) -> list[Path]:
    ticker = item["ticker"]
    signal_only = item.get("trade_policy") == "signal_only_no_puts_or_shorts"
    urgency = _urgency(item, wave)
    dip_decision = "NOT_ARMED" if signal_only else "RESEARCH_FIRST"
    hedge = _hedge_or_sizing(signal_only, item)
    next_trigger = (
        "Next scheduled market/filing scan, SA filing change, company filing/IR update, "
        "financing or customer-contract news, guidance change, or a detected valuation dip."
    )
    rationale = (
        "Signal-only SA exposure; no long-only trade is authorized."
        if signal_only
        else f"Hold/watch only: {note.thesis}"
    )
    common_frontmatter = {
        "ticker": ticker,
        "name": item.get("name", ticker),
        "sleeve": item.get("sleeve", "unassigned"),
        "last_updated": _today(),
        "source_classification": item.get("source_classification", ""),
        "instrument_role": item.get("instrument_role", ""),
        "trade_policy": item.get("trade_policy", ""),
        "thesis_damage": False,
        "unresolved_material_event": False,
        "evidence_quality": "SA_FILING_AND_LOCAL_BASELINE",
        "thesis_expressed": note.thesis,
        "anti_thesis": note.anti_thesis,
        "hedge_or_sizing": hedge,
        "invalidation_trigger": note.invalidation,
        "next_trigger": next_trigger,
        "one_line_rationale": rationale,
    }

    asset_path = root / "research" / "assets" / f"{ticker}.md"
    asset_frontmatter = {
        **common_frontmatter,
        "asset_role": note.role,
        "default_holding_period": "multi_year",
        "current_decision": decision,
        "dip_decision": dip_decision,
        "sell_decision": "NOT_TRIGGERED",
        "research_priority": item.get("priority", "medium").upper(),
        "last_primary_source_check": _today(),
        "thesis_health_score": note.thesis_health,
        "confidence_score": note.confidence,
        "valuation_attractiveness_score": note.valuation_score,
        "urgency_score": _urgency_score(urgency),
        "max_position_weight_pct": 0,
        "current_position_weight_pct": 0,
        "approved_entry_zone": "No new capital until scheduled scan validates valuation.",
        "do_not_buy_zone": "Any price without thesis, valuation, sizing, and invalidation.",
        "sell_trigger_status": False,
        "hedge_required": True,
        "main_hedge": hedge,
        "open_questions_count": 0,
        "broken_thesis": "",
    }
    decision_path = root / "research" / "decisions" / f"{ticker}.md"
    decision_frontmatter = {
        **common_frontmatter,
        "current_decision": decision,
        "dip_decision": dip_decision,
        "sell_status": "NOT_TRIGGERED",
        "confidence_score": note.confidence,
        "urgency": urgency,
        "dip_approved": False,
        "valuation_improved": False,
        "portfolio_risk_allows_add": True,
        "buy_thesis": note.thesis,
        "valuation_case": note.valuation_frame,
        "broken_thesis": "",
    }
    write_markdown_with_frontmatter(asset_path, asset_frontmatter, _asset_body(item, note, wave))
    write_markdown_with_frontmatter(
        decision_path,
        decision_frontmatter,
        _decision_body(item, note, decision, dip_decision, urgency, hedge, next_trigger),
    )
    return [asset_path, decision_path]


def _write_wave_execution_reports(root: Path, ranked: list[Any]) -> list[Path]:
    paths: list[Path] = []
    wave_titles = {
        1: "core / highest-signal names",
        2: "remaining strict public 13F names",
        3: "adjacent proxies",
    }
    for wave in (1, 2, 3):
        items = [item for item in ranked if item.wave == wave]
        lines = [
            f"# Wave {wave} Execution Memo - Baseline Applied",
            "",
            f"Date: {_today()}",
            "",
            f"Scope: {wave_titles[wave]}. The earlier triage questions have been resolved "
            "into the all-wave baseline decision files.",
            "",
            "Current posture: HOLD/watch for every ticker. No BUY_NOW, ADD_ON_DIP, TRIM, or "
            "SELL action is authorized before the next scheduled market/filing process or a "
            "material event.",
            "",
            "| Ticker | Agent id | Decision | Baseline rationale | Next trigger |",
            "|---|---|---|---|---|",
        ]
        for item in items:
            note = _baseline_for(item.ticker)
            lines.append(
                f"| {item.ticker} | `asset_analyst.{item.ticker}` | HOLD | "
                f"{note.thesis} | Scheduled scan, SA filing change, company filing/IR "
                "update, financing/customer contract, guidance change, or detected "
                "valuation dip. |"
            )
        lines.extend(
            [
                "",
                "## Controls",
                "",
                "- Long-only mandate remains active.",
                "- Reported puts remain signal-only, not trade instructions.",
                "- A future SA full exit forces exit/thesis-correction review.",
                "- A material SA reduction forces high-priority thesis-weight review.",
                "- No technical indicators are used.",
                "",
                "## Output Files",
                "",
                f"- Ticker packets: `research/agent_packets/wave_{wave}/`",
                "- Asset files: `research/assets/{TICKER}.md`",
                "- Decision files: `research/decisions/{TICKER}.md`",
                f"- Baseline summary: `reports/initialization/{_today()}-all-wave-baseline.md`",
            ]
        )
        path = root / "reports" / "initialization" / f"{_today()}-wave-{wave}-execution.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def _asset_body(item: dict[str, Any], note: BaselineNote, wave: int) -> str:
    ticker = item["ticker"]
    signal_only = item.get("trade_policy") == "signal_only_no_puts_or_shorts"
    buy_on_dip = "NO" if signal_only else "RESEARCH_FIRST"
    ownership_candidate = "NO / SIGNAL ONLY" if signal_only else "POSSIBLE, NOT APPROVED"
    dip_command = f"`bcap dip-investigate --ticker {ticker}`"
    source_line = (
        f"{SA_13F_SOURCE}; configs/watchlist.yaml; configs/sa_universe.yaml; "
        f"research/agent_packets/wave_{wave}/{ticker}.md; wave execution memo."
    )
    return f"""# {ticker} - {item.get("name", ticker)}

## 0. Current Decision

### Simple decision

Current action: HOLD

### One-line decision

{note.thesis}

### Decision table

| Field | Status |
|---|---|
| Long-term ownership candidate? | {ownership_candidate} |
| Buy today? | NO |
| Add on dip? | {buy_on_dip} |
| Sell / exit? | NO, unless invalidation triggers |
| Hedge required? | YES, via sizing/no-action discipline |
| Main risk today | {note.risk} |
| Main upside driver today | {note.upside} |
| Next review trigger | Scheduled scan or new primary-source event |

## 1. Role in Bottleneck Capital

Sleeve: `{item.get("sleeve", "unassigned")}`

Why this asset belongs here: {note.role}

What this asset is actually a bet on:

1. {note.upside}
2. The SA/public-filing signal being informative for the bottleneck thesis.
3. Long-only discipline being stricter than SA's reported options exposure.

What this asset is not a bet on:

- {note.anti_thesis}
- No puts, shorts, or technical indicators under the current mandate.

## 2. Thesis Stack

### Thesis A - Primary thesis

Status: {"SIGNAL_ONLY" if signal_only else "ACTIVE WATCH"}
Confidence: {note.confidence}
Time horizon: multi-year
Importance: HIGH

Claim: {note.thesis}

Evidence for:
- {source_line}
- Sleeve thesis: `{item.get("sleeve", "unassigned")}`.

Evidence against:
- {note.anti_thesis}
- {note.risk}

What would break it:
- {note.invalidation}

Decision impact:
HOLD. Do not add capital until a scheduled scan or fresh primary-source event clears thesis,
valuation, and sizing.

Hedge implication:
{_hedge_or_sizing(signal_only, item)}

### Thesis B - Valuation thesis

Status: UNPROVEN FOR NEW CAPITAL
Claim: {note.valuation_frame}. Current baseline does not approve a buy.

### Thesis C - Catalyst thesis

Status: EVENT-DRIVEN
Claim: New SEC filing, IR update, financing, customer contract, guidance change, SA filing
change, or detected dip can reopen the decision.

## 3. Market-Implied View vs Variant View

What the market seems to believe:
- AI infrastructure scarcity matters, but quality, timing, and valuation vary by ticker.
- Crowded AI beta and financing risk can overwhelm a correct high-level theme.

Our variant view:
- The SA signal is useful for prioritization, not a trade instruction.
- HOLD is the right baseline until valuation and primary-source evidence justify a stronger action.

Why we may be wrong:
- The company may already be a cleaner bottleneck expression than the baseline allows.
- The risk signal may be stale or purely hedge-related.

Is the variant view big enough to matter?
UNCLEAR until a scheduled scan updates primary evidence and valuation.

## 4. Long-Term Ownership Quality

| Dimension | Score | Notes |
|---|---:|---|
| Thesis purity | {_score(note.quality_score, 0)} | {note.role} |
| Durability | {_score(note.quality_score, 1)} | Requires scheduled evidence refresh. |
| Balance sheet resilience | {_score(note.quality_score, 2)} | Main risk: {note.risk} |
| Management / execution | {_score(note.quality_score, 3)} | Execution still matters. |
| Strategic scarcity | {_score(note.quality_score, 4)} | Upside: {note.upside} |
| Contract quality | {_score(note.quality_score, 5)} | Needs source-event verification. |
| Customer quality | {_score(note.quality_score, 6)} | Needs source-event verification. |
| Pricing power | {_score(note.quality_score, 7)} | Valuation frame: {note.valuation_frame}. |
| Downside survivability | {_score(note.quality_score, 8)} | Invalidation: {note.invalidation} |
| Hedgeability | {_score(note.quality_score, 9)} | Long-only hedge is sizing/no action. |

Long-term owner score: {note.quality_score} / 50

## 5. Valuation and Entry Discipline

Valuation frame: {note.valuation_frame}

| Zone | Meaning | Action |
|---|---|---|
| Approved entry | Not armed in this baseline | No buy |
| Dip investigation | Material drop with no thesis damage | Run {dip_command} |
| Do-not-buy | Thesis, valuation, or sizing not explicit | Hold/watch |

## 6. Dip Protocol

Dip status: {buy_on_dip}

A dip is buyable only if the cause is bounded, no thesis damage is found, valuation improves,
and portfolio risk allows adding.

## 7. Sell / Exit Protocol

Sell is not triggered. Exit review is triggered by:

- {note.invalidation}
- Future SA full exit from a tracked current/public evidence name.
- Material SA reduction that weakens thesis weight.
- Unacceptable financing, customer, regulatory, or governance risk.

## 8. Failure Modes

- {note.risk}
- {note.anti_thesis}
- Overpaying for a correct bottleneck theme.

## 9. Hedge Map

{_hedge_or_sizing(signal_only, item)}

## 10. Latest Signals

- Wave: {wave}
- Source classification: `{item.get("source_classification", "")}`
- Instrument role: `{item.get("instrument_role", "")}`
- Trade policy: `{item.get("trade_policy", "")}`

## 11. Source Register

- {SA_13F_SOURCE}
- `configs/sa_universe.yaml`
- `configs/watchlist.yaml`
- `research/agent_packets/wave_{wave}/{ticker}.md`
- `reports/initialization/2026-06-20-wave-{wave}-execution.md`

Evidence quality: SA filing and local baseline. No unscheduled market action is authorized
before the next scheduled process.

## 12. Open Questions

- None blocking before the next scheduled scan. Future work is event/schedule-driven.

## 13. Latest Agent Notes

All-wave baseline completed. Current action is HOLD, with no BUY_NOW, ADD_ON_DIP, TRIM, or
SELL action authorized.
"""


def _decision_body(
    item: dict[str, Any],
    note: BaselineNote,
    decision: str,
    dip_decision: str,
    urgency: str,
    hedge: str,
    next_trigger: str,
) -> str:
    return f"""# {item["ticker"]} Decision

Updated: {_today()}

Decision: {decision}
Dip decision: {dip_decision}
Sell status: NOT_TRIGGERED
Confidence: {note.confidence} / 100
Urgency: {urgency}

One-line rationale:
{note.thesis}

Thesis expressed:
{note.thesis}

Anti-thesis:
{note.anti_thesis}

Evidence quality:
SA filing and local baseline; no unscheduled buy/sell action is authorized.

Hedge or sizing:
{hedge}

Invalidation trigger:
{note.invalidation}

Buy now?
NO

Buy on dip?
{dip_decision}

Sell?
NO

Next trigger:
{next_trigger}

Human action:
No immediate action before the next scheduled market/filing process unless a material event appears.
"""


def _baseline_for(ticker: str) -> BaselineNote:
    try:
        return TICKER_BASELINES[ticker]
    except KeyError as exc:  # pragma: no cover - config/test guard.
        raise KeyError(f"Missing all-wave baseline for {ticker}") from exc


def _hedge_or_sizing(signal_only: bool, item: dict[str, Any]) -> str:
    if signal_only:
        return "No puts or shorts; use as risk signal only and do not allocate capital."
    if "put_signal" in str(item.get("instrument_role", "")):
        return (
            "No puts or shorts; require smaller sizing, higher valuation hurdle, and explicit "
            "invalidation."
        )
    return (
        "No puts or shorts; use no-action discipline until valuation and thesis evidence "
        "justify capital."
    )


def _urgency(item: dict[str, Any], wave: int) -> str:
    priority = str(item.get("priority", "")).lower()
    if priority == "high" or wave == 1:
        return "HIGH"
    if priority == "low":
        return "LOW"
    return "MEDIUM"


def _urgency_score(urgency: str) -> int:
    return {"HIGH": 90, "MEDIUM": 60, "LOW": 30}.get(urgency, 50)


def _score(total: int, index: int) -> int:
    base = total // 10
    remainder = total % 10
    return min(5, base + (1 if index < remainder else 0))


def _today() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).date().isoformat()
