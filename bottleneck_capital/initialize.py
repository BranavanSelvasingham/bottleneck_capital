from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import load_watchlist
from bottleneck_capital.io import dump_yaml_mapping, load_yaml_file, scalar_text

WAVE_1 = {
    "CRWV",
    "NBIS",
    "BE",
    "IREN",
    "ASML",
    "NVDA",
    "MU",
    "TSM",
    "ORCL",
    "SMH",
}

SLEEVE_THESES = {
    "compute_infra": {
        "title": "Compute Infrastructure",
        "thesis": (
            "AI model demand creates durable scarcity in contracted, power-secured compute "
            "capacity, especially where supply can be delivered faster than hyperscaler "
            "build cycles."
        ),
        "questions": [
            "Is capacity genuinely scarce and contracted, or just speculative GPU exposure?",
            "Does financing risk overwhelm the scarcity thesis?",
            "Does customer concentration improve or impair durability?",
        ],
    },
    "power_bottleneck": {
        "title": "Power Bottleneck",
        "thesis": (
            "AI datacenter demand shifts value toward reliable generation, grid access, "
            "onsite power, and equipment that can solve interconnection and load-growth "
            "constraints."
        ),
        "questions": [
            "Is the asset a direct power bottleneck solution or a loose energy proxy?",
            "Are contracts, interconnection rights, and balance sheet resilience strong enough?",
            "What breaks if AI load growth is delayed?",
        ],
    },
    "miner_to_datacenter": {
        "title": "Miner to Datacenter Conversion",
        "thesis": (
            "Some miners own power, land, and electrical infrastructure that may be "
            "repurposed into higher-value AI/HPC datacenter capacity."
        ),
        "questions": [
            "Is the company truly converting to AI/HPC or still mostly Bitcoin beta?",
            "Are power assets and sites suitable for contracted datacenter loads?",
            "Does capex and financing risk make conversion value unreachable?",
        ],
    },
    "memory_storage_networking": {
        "title": "Memory, Storage, Foundry, and Networking",
        "thesis": (
            "AI infrastructure bottlenecks extend beyond GPUs into HBM, NAND/storage, "
            "advanced packaging, foundry capacity, and high-performance networking."
        ),
        "questions": [
            "Which part of the AI supply chain is actually scarce?",
            "Is this cyclical pricing or durable structural demand?",
            "Does the current valuation already price the bottleneck?",
        ],
    },
    "semicap_equipment": {
        "title": "Semicap Equipment",
        "thesis": (
            "Critical tooling, lithography, process control, and foundry enablement can "
            "become durable bottleneck assets when AI chip demand stresses leading-edge "
            "capacity."
        ),
        "questions": [
            "Is the company a monopoly-like bottleneck or just a cyclical capex beneficiary?",
            "Why does SA report put exposure alongside any long exposure?",
            "What geopolitical or capex-cycle risk would impair the thesis?",
        ],
    },
    "crowded_ai_beta_hedge": {
        "title": "Crowded AI Beta and Hedge Signals",
        "thesis": (
            "SA's reported put exposure is a signal about crowded AI downside, valuation "
            "risk, or portfolio hedge pressure, not an instruction for this long-only "
            "system to short or buy puts."
        ),
        "questions": [
            "Which long holdings are most exposed to crowded AI beta?",
            "What is the put signal warning us not to overpay for?",
            "How should position sizing substitute for puts in a long-only mandate?",
        ],
    },
    "ai_networking_optical": {
        "title": "AI Networking and Optical",
        "thesis": (
            "AI scale-out can create scarcity in optical interconnect, switching, and "
            "networking components needed to move data inside and between clusters."
        ),
        "questions": [
            "Is the asset directly tied to AI cluster networking?",
            "Is the bottleneck optical, switching silicon, or general telecom cyclicality?",
            "Does SA exposure imply long thesis, hedge signal, or adjacent proxy?",
        ],
    },
    "ai_power_equipment": {
        "title": "AI Power Equipment",
        "thesis": (
            "Datacenter power constraints can favor electrical, thermal, water, and "
            "power-management equipment vendors with direct AI campus exposure."
        ),
        "questions": [
            "Is AI datacenter demand material enough to change the earnings base?",
            "Is valuation already discounting the power equipment thesis?",
            "Is the name current SA exposure or only an adjacent proxy?",
        ],
    },
    "space_infra": {
        "title": "Space Infrastructure",
        "thesis": (
            "Reusable launch, satellite networks, secure communications, and space logistics "
            "can become strategic infrastructure bottlenecks adjacent to AI, defense, and "
            "compute connectivity."
        ),
        "questions": [
            "Is the exposure actually investable or only a ticker/private-market signal?",
            "Does space infrastructure reinforce AI, defense, data, or communications scarcity?",
            "What liquidity, listing, custody, and valuation constraints make it non-actionable?",
        ],
    },
    "enterprise_ai_infra": {
        "title": "Enterprise AI Infrastructure Signal",
        "thesis": (
            "Reported SA put exposure in enterprise AI infrastructure names may indicate "
            "concern about capex duration, valuation, or crowded expectations."
        ),
        "questions": [
            "Is this only a downside signal, or is there a separate long-only thesis?",
            "What does this signal imply for related compute infrastructure holdings?",
            "What evidence would move this from signal-only to investable?",
        ],
    },
    "ai_services_put_signal": {
        "title": "AI Services Put Signal",
        "thesis": (
            "Reported puts on IT services exposure may signal AI disruption risk or broad "
            "enterprise technology downside rather than an investable long thesis."
        ),
        "questions": [
            "What risk does this signal map to in the rest of the book?",
            "Does the signal alter any long thesis or hedge map?",
            "Should the name stay signal-only?",
        ],
    },
}


@dataclass(frozen=True)
class RankedTicker:
    ticker: str
    name: str
    sleeve: str
    source_classification: str
    instrument_role: str
    trade_policy: str
    priority: str
    wave: int
    score: int
    reason: str


def run_initialization(root: Path) -> list[Path]:
    watchlist = load_watchlist(root)
    sa_universe = load_yaml_file(root / "configs" / "sa_universe.yaml")
    ranked = rank_tickers(watchlist)
    today = _today()
    paths = [
        _write_agent_roster(root, watchlist),
        _write_automation_routing(root),
        _write_sleeve_theses(root, watchlist),
        _write_task_packets(root, ranked),
        _write_wave_plan(root, ranked, today),
        _write_initialization_report(root, ranked, sa_universe, today),
    ]
    return paths


def rank_tickers(watchlist: list[dict[str, Any]]) -> list[RankedTicker]:
    ranked = [_rank_one(item) for item in watchlist]
    return sorted(ranked, key=lambda item: (item.wave, -item.score, item.ticker))


def _rank_one(item: dict[str, Any]) -> RankedTicker:
    ticker = scalar_text(item["ticker"]).upper()
    source = scalar_text(item.get("source_classification"))
    role = scalar_text(item.get("instrument_role"))
    policy = scalar_text(item.get("trade_policy"))
    priority = scalar_text(item.get("priority")) or "medium"
    sleeve = scalar_text(item.get("sleeve"))

    score = 0
    if source == "sa_reported_current_13f":
        score += 40
    elif source == "sa_post_quarter_13g":
        score += 35
    elif source.startswith("sa_adjacent"):
        score += 10

    score += {"high": 30, "medium": 18, "low": 8}.get(priority, 12)
    if "call_signal" in role:
        score += 8
    if "put_signal" in role:
        score += 4
    if policy == "signal_only_no_puts_or_shorts":
        score -= 12
    if ticker in WAVE_1:
        score += 35

    if ticker in WAVE_1:
        wave = 1
        reason = "Core or highest-signal initialization name."
    elif source == "sa_reported_current_13f":
        wave = 2
        reason = "Remaining strict current public SA 13F name."
    else:
        wave = 3
        reason = "SA-adjacent, historical, or thesis-proxy name."

    return RankedTicker(
        ticker=ticker,
        name=scalar_text(item.get("name")),
        sleeve=sleeve,
        source_classification=source,
        instrument_role=role,
        trade_policy=policy,
        priority=priority,
        wave=wave,
        score=score,
        reason=reason,
    )


def _write_agent_roster(root: Path, watchlist: list[dict[str, Any]]) -> Path:
    roster = {
        "agent_types": {
            "asset_analyst": {
                "purpose": "Ticker-scoped research and decision-file updates.",
                "owner_id_format": "asset_analyst.{TICKER}",
            },
            "sleeve_analyst": {
                "purpose": "Cross-ticker thesis, hedge, and relative-value synthesis.",
                "owner_id_format": "sleeve_analyst.{SLEEVE}",
            },
            "hedge_analyst": {
                "purpose": "Interpret SA put exposure and crowded-AI risk without trading puts.",
            },
            "portfolio_pm": {
                "purpose": "Compile ticker decisions into the daily board and backlog.",
            },
            "filing_analyst": {
                "purpose": "Track 13F, 13G, SEC, IR, guidance, financing, and contract updates.",
            },
        },
        "ticker_owners": [
            {
                "ticker": item["ticker"],
                "owner_agent": f"asset_analyst.{item['ticker']}",
                "sleeve_agent": f"sleeve_analyst.{item.get('sleeve', 'unassigned')}",
            }
            for item in watchlist
        ],
    }
    path = root / "configs" / "agent_roster.yaml"
    path.write_text(dump_yaml_mapping(roster), encoding="utf-8")
    return path


def _write_automation_routing(root: Path) -> Path:
    routing = {
        "event_routes": {
            "dip_trigger": ["asset_analyst.{ticker}", "sleeve_analyst.{sleeve}"],
            "thesis_damage_candidate": [
                "asset_analyst.{ticker}",
                "sleeve_analyst.{sleeve}",
                "portfolio_pm",
            ],
            "sa_exit_update": [
                "asset_analyst.{ticker}",
                "sleeve_analyst.{sleeve}",
                "portfolio_pm",
            ],
            "sa_position_reduction_update": [
                "asset_analyst.{ticker}",
                "sleeve_analyst.{sleeve}",
            ],
            "filing_update": ["filing_analyst", "asset_analyst.{ticker}"],
            "hedge_risk_update": ["hedge_analyst", "portfolio_pm"],
            "catalyst_update": ["asset_analyst.{ticker}"],
        },
        "limits": {
            "max_concurrent_asset_agents": 6,
            "max_concurrent_write_agents": 3,
            "default_task_timeout_minutes": 45,
        },
        "write_discipline": {
            "asset_agent_write_scope": [
                "research/assets/{ticker}.md",
                "research/decisions/{ticker}.md",
                "research/memos/{date}-{ticker}-*.md",
            ],
            "portfolio_pm_write_scope": [
                "research/decisions/index.md",
                "reports/daily_decision_boards/{date}.md",
            ],
        },
    }
    path = root / "configs" / "automation_routing.yaml"
    path.write_text(dump_yaml_mapping(routing), encoding="utf-8")
    return path


def _write_sleeve_theses(root: Path, watchlist: list[dict[str, Any]]) -> Path:
    out_dir = root / "research" / "theses"
    out_dir.mkdir(parents=True, exist_ok=True)
    by_sleeve: dict[str, list[str]] = defaultdict(list)
    for item in watchlist:
        by_sleeve[scalar_text(item.get("sleeve"))].append(item["ticker"])

    for sleeve, tickers in sorted(by_sleeve.items()):
        thesis = SLEEVE_THESES.get(
            sleeve,
            {
                "title": sleeve.replace("_", " ").title(),
                "thesis": "Sleeve thesis requires initialization.",
                "questions": ["What bottleneck does this sleeve express?"],
            },
        )
        body = [
            f"# {thesis['title']}",
            "",
            f"Sleeve: `{sleeve}`",
            "",
            "## Baseline Thesis",
            "",
            thesis["thesis"],
            "",
            "## Current Tickers",
            "",
        ]
        body.extend(f"- `{ticker}`" for ticker in sorted(tickers))
        body.extend(["", "## Initialization Questions", ""])
        body.extend(f"- {question}" for question in thesis["questions"])
        body.extend(
            [
                "",
                "## Decision Discipline",
                "",
                "- BUY requires thesis, valuation, hedge or sizing response, and invalidation.",
                "- ADD_ON_DIP requires no thesis damage and improved valuation.",
                "- SELL requires a named thesis break or unacceptable risk.",
                "- Reported puts are signal-only unless the user changes the mandate.",
            ]
        )
        (out_dir / f"{sleeve}.md").write_text("\n".join(body) + "\n", encoding="utf-8")

    return out_dir


def _write_task_packets(root: Path, ranked: list[RankedTicker]) -> Path:
    out_dir = root / "research" / "agent_packets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for item in ranked:
        wave_dir = out_dir / f"wave_{item.wave}"
        wave_dir.mkdir(parents=True, exist_ok=True)
        (wave_dir / f"{item.ticker}.md").write_text(_task_packet(item), encoding="utf-8")
    return out_dir


def _task_packet(item: RankedTicker) -> str:
    action = (
        "Keep signal-only unless a separate long-only thesis emerges."
        if item.trade_policy == "signal_only_no_puts_or_shorts"
        else "Underwrite as long-only candidate before any BUY or ADD_ON_DIP."
    )
    return f"""# {item.ticker} Agent Task Packet

Ticker: `{item.ticker}`  
Name: {item.name}  
Wave: {item.wave}  
Owner agent: `asset_analyst.{item.ticker}`  
Sleeve agent: `sleeve_analyst.{item.sleeve}`  
Sleeve: `{item.sleeve}`  
Source classification: `{item.source_classification}`  
Instrument role: `{item.instrument_role}`  
Trade policy: `{item.trade_policy}`  
Priority: `{item.priority}`  
Initialization score: {item.score}  

## Job

{action}

## Read

- `AGENTS.md`
- `configs/sa_universe.yaml`
- `configs/agent_roster.yaml`
- `configs/automation_routing.yaml`
- `research/theses/{item.sleeve}.md`
- `research/assets/{item.ticker}.md`
- `research/decisions/{item.ticker}.md`

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

- `research/assets/{item.ticker}.md`
- `research/decisions/{item.ticker}.md`
- ticker-specific memo under `research/memos/`

Do not edit other ticker files.
"""


def _write_wave_plan(root: Path, ranked: list[RankedTicker], today: str) -> Path:
    path = root / "reports" / "initialization" / f"{today}-wave-plan.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Bottleneck Capital Initialization Wave Plan",
        "",
        f"Date: {today}",
        "",
    ]
    for wave in (1, 2, 3):
        lines.extend([f"## Wave {wave}", ""])
        lines.extend(
            f"- `{item.ticker}` - {item.name} ({item.reason}; score {item.score})"
            for item in ranked
            if item.wave == wave
        )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_initialization_report(
    root: Path, ranked: list[RankedTicker], sa_universe: dict[str, Any], today: str
) -> Path:
    path = root / "reports" / "initialization" / f"{today}-initialization.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    by_wave = {wave: [item for item in ranked if item.wave == wave] for wave in (1, 2, 3)}
    strict = [item for item in ranked if item.source_classification == "sa_reported_current_13f"]
    signal_only = [item for item in ranked if item.trade_policy == "signal_only_no_puts_or_shorts"]
    post_quarter = [
        item for item in ranked if item.source_classification == "sa_post_quarter_13g"
    ]
    adjacent = [
        item for item in ranked if item.source_classification.startswith("sa_adjacent")
    ]

    lines = [
        "# Bottleneck Capital Initialization Run",
        "",
        f"Date: {today}",
        "",
        "## Universe Baseline",
        "",
        f"- Total tracked tickers: {len(ranked)}",
        f"- Strict current public SA 13F / signal names: {len(strict)}",
        f"- Post-quarter public clues: {len(post_quarter)}",
        f"- Adjacent or historical thesis proxies: {len(adjacent)}",
        f"- Signal-only no-puts/no-shorts names: {len(signal_only)}",
        "",
        "Source metadata:",
        f"- Manager: {sa_universe.get('source', {}).get('manager', 'TBD')}",
        f"- Public period: {sa_universe.get('source', {}).get('latest_public_13f_period', 'TBD')}",
        f"- Filed: {sa_universe.get('source', {}).get('latest_public_13f_filed', 'TBD')}",
        "",
        "## Ranked Tickers",
        "",
        "| Rank | Ticker | Wave | Sleeve | Source | Role | Policy | Score |",
        "|---:|---|---:|---|---|---|---|---:|",
    ]
    for rank, item in enumerate(ranked, start=1):
        lines.append(
            f"| {rank} | {item.ticker} | {item.wave} | {item.sleeve} | "
            f"{item.source_classification} | {item.instrument_role} | "
            f"{item.trade_policy} | {item.score} |"
        )
    lines.extend(["", "## Agent Waves", ""])
    for wave, items in by_wave.items():
        lines.extend([f"### Wave {wave}", ""])
        lines.extend(f"- `{item.ticker}` - {item.reason}" for item in items)
        lines.append("")
    lines.extend(
        [
            "## Task Packet Location",
            "",
            "- Wave 1: `research/agent_packets/wave_1/`",
            "- Wave 2: `research/agent_packets/wave_2/`",
            "- Wave 3: `research/agent_packets/wave_3/`",
            "",
            "## Initial Control Rules",
            "",
            "- No ticker moves to BUY_NOW without thesis, valuation, hedge/sizing, "
            "and invalidation.",
            "- No ADD_ON_DIP without no thesis damage and improved valuation.",
            "- SA full exit forces RESEARCH_REQUIRED and exit/thesis-correction review.",
            "- SA material reduction forces thesis-weight review.",
            "- Reported puts remain signal-only under the current long-only mandate.",
            "",
            "## Next Research Tasks",
            "",
            "1. Run Wave 1 underwrites from task packets.",
            "2. Build primary-source register for all strict current SA names.",
            "3. Underwrite signal-only puts as risk maps, not trade recommendations.",
            "4. Use Wave 2 to complete remaining strict 13F coverage.",
            "5. Use Wave 3 only after strict-current coverage has a coherent spine.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _today() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).date().isoformat()
