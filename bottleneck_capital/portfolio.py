from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import evaluate_all, load_watchlist
from bottleneck_capital.io import (
    ConfigError,
    load_yaml_file,
    read_jsonl,
    read_markdown_frontmatter,
    scalar_text,
)
from bottleneck_capital.market_regime import MarketRegime, assess_market_regime
from bottleneck_capital.positions import LOCAL_POSITIONS_PATH, load_local_positions
from bottleneck_capital.signal_events import active_signal_events


@dataclass(frozen=True)
class HoldingAnalysis:
    ticker: str
    sleeve: str
    decision: str
    currency: str
    market_value_base: float
    weight_pct: float
    max_weight_pct: float
    remaining_capacity_pct: float
    factors: dict[str, float]


@dataclass(frozen=True)
class FactorExposure:
    factor: str
    exposure_pct: float
    limit_pct: float


@dataclass(frozen=True)
class ScenarioImpact:
    scenario: str
    name: str
    description: str
    impact_score: float
    affected_weight_pct: float
    posture: str
    primary_factors: tuple[str, ...]


@dataclass(frozen=True)
class DiscountAssessment:
    ticker: str
    classification: str
    confidence: float
    fundamental_status: str
    action_bias: str
    rationale: str


@dataclass(frozen=True)
class PortfolioAnalysis:
    as_of: str
    base_currency: str
    total_capital: float
    invested_pct: float
    cash_pct: float
    required_cash_reserve_pct: float
    deployable_cash_pct: float
    posture: str
    normalization_complete: bool
    holdings: tuple[HoldingAnalysis, ...]
    sleeve_weights: dict[str, float]
    factor_exposures: tuple[FactorExposure, ...]
    scenario_impacts: tuple[ScenarioImpact, ...]
    concentration_alerts: tuple[str, ...]
    capacity_scores: dict[str, float]
    remaining_capacity_pct: dict[str, float]
    diversification_scores: dict[str, float]
    scenario_resilience_scores: dict[str, float]
    discounts: dict[str, DiscountAssessment]
    data_gaps: tuple[str, ...]
    regime: MarketRegime


@dataclass(frozen=True)
class PortfolioPMResult:
    decision_board_path: Path
    portfolio_board_path: Path


def analyze_portfolio(
    root: Path,
    *,
    positions_path: Path | None = None,
    regime: MarketRegime | None = None,
) -> PortfolioAnalysis:
    path = positions_path or root / LOCAL_POSITIONS_PATH
    positions_data, positions = load_local_positions(root, positions_path=path)
    config = _portfolio_config(root)
    watchlist = {item["ticker"]: item for item in load_watchlist(root)}
    decisions = {result.ticker: result for result in evaluate_all(root)}
    current_regime = regime or assess_market_regime(root)
    base_currency = scalar_text(positions_data.get("base_currency") or "CAD").upper()
    snapshots = _latest_snapshots(root)
    data_gaps: list[str] = []
    normalized_values: dict[str, float] = {}
    normalization_complete = True

    for position in positions:
        rate = _fx_rate_to_base(
            positions_data,
            snapshots,
            currency=position.currency,
            base_currency=base_currency,
        )
        if rate is None:
            normalization_complete = False
            rate = 1.0
            data_gaps.append(
                f"Missing {position.currency.upper()} to {base_currency} FX conversion for "
                f"{position.ticker}; weights are provisional."
            )
        normalized_values[position.ticker] = position.market_value * rate

    cash_value = 0.0
    raw_cash = positions_data.get("cash")
    if isinstance(raw_cash, dict):
        for currency, amount in raw_cash.items():
            rate = _fx_rate_to_base(
                positions_data,
                snapshots,
                currency=scalar_text(currency),
                base_currency=base_currency,
            )
            if rate is None:
                normalization_complete = False
                rate = 1.0
                data_gaps.append(
                    f"Missing {scalar_text(currency).upper()} to {base_currency} FX conversion "
                    "for cash; cash capacity is provisional."
                )
            cash_value += _float(amount) * rate

    invested_value = sum(normalized_values.values())
    total_capital = invested_value + cash_value
    invested_pct = 100.0 * invested_value / total_capital if total_capital > 0 else 0.0
    cash_pct = 100.0 * cash_value / total_capital if total_capital > 0 else 0.0
    default_ticker_limit = _float(config.get("default_ticker_limit_pct"), 10.0)
    holdings: list[HoldingAnalysis] = []
    sleeve_weights: dict[str, float] = {}

    for position in positions:
        ticker = position.ticker
        value = normalized_values.get(ticker, 0.0)
        weight = 100.0 * value / total_capital if total_capital > 0 else 0.0
        sleeve = scalar_text(watchlist.get(ticker, {}).get("sleeve")) or "UNTRACKED"
        decision = decisions.get(ticker)
        max_weight = _max_position_weight(root, ticker, default_ticker_limit)
        remaining = max(0.0, max_weight - weight)
        holdings.append(
            HoldingAnalysis(
                ticker=ticker,
                sleeve=sleeve,
                decision=decision.action if decision else "UNTRACKED",
                currency=position.currency.upper(),
                market_value_base=value,
                weight_pct=weight,
                max_weight_pct=max_weight,
                remaining_capacity_pct=remaining,
                factors=_factor_profile(config, ticker, sleeve),
            )
        )
        sleeve_weights[sleeve] = sleeve_weights.get(sleeve, 0.0) + weight

    holdings.sort(key=lambda item: (-item.weight_pct, item.ticker))
    factor_exposures = _factor_exposures(config, holdings)
    scenarios = _scenario_impacts(config, holdings)
    alerts = _concentration_alerts(config, holdings, sleeve_weights, factor_exposures)
    required_reserve = _required_cash_reserve(config, current_regime)
    deployable_cash = max(0.0, cash_pct - required_reserve)
    posture = _portfolio_posture(
        normalization_complete=normalization_complete,
        regime=current_regime,
        alerts=alerts,
        cash_pct=cash_pct,
        required_reserve=required_reserve,
        scenarios=scenarios,
    )

    ticker_weights = {item.ticker: item.weight_pct for item in holdings}
    remaining_capacity: dict[str, float] = {}
    capacity_scores: dict[str, float] = {}
    diversification_scores: dict[str, float] = {}
    resilience_scores: dict[str, float] = {}
    factor_by_name = {item.factor: item.exposure_pct for item in factor_exposures}
    for ticker, item in watchlist.items():
        sleeve = scalar_text(item.get("sleeve")) or "UNTRACKED"
        maximum = _max_position_weight(root, ticker, default_ticker_limit)
        current_weight = ticker_weights.get(ticker, 0.0)
        remaining = max(0.0, maximum - current_weight)
        remaining_capacity[ticker] = remaining
        capacity_scores[ticker] = (
            _capacity_score(maximum, current_weight) if normalization_complete else 60.0
        )
        profile = _factor_profile(config, ticker, sleeve)
        diversification_scores[ticker] = _diversification_score(profile, factor_by_name)
        resilience_scores[ticker] = _scenario_resilience_score(config, profile)

    discounts = _discount_assessments(root, watchlist, current_regime)
    if total_capital <= 0:
        data_gaps.append("No entered portfolio capital is available for portfolio analysis.")
    return PortfolioAnalysis(
        as_of=scalar_text(positions_data.get("as_of")) or _today(),
        base_currency=base_currency,
        total_capital=total_capital,
        invested_pct=invested_pct,
        cash_pct=cash_pct,
        required_cash_reserve_pct=required_reserve,
        deployable_cash_pct=deployable_cash,
        posture=posture,
        normalization_complete=normalization_complete,
        holdings=tuple(holdings),
        sleeve_weights=dict(sorted(sleeve_weights.items())),
        factor_exposures=tuple(factor_exposures),
        scenario_impacts=tuple(scenarios),
        concentration_alerts=tuple(alerts),
        capacity_scores=capacity_scores,
        remaining_capacity_pct=remaining_capacity,
        diversification_scores=diversification_scores,
        scenario_resilience_scores=resilience_scores,
        discounts=discounts,
        data_gaps=tuple(dict.fromkeys(data_gaps)),
        regime=current_regime,
    )


def write_portfolio_board(
    root: Path,
    *,
    positions_path: Path | None = None,
) -> Path:
    analysis = analyze_portfolio(root, positions_path=positions_path)
    path = root / "reports" / "local_portfolio_boards" / f"{_today()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_portfolio_board(root, analysis), encoding="utf-8")
    return path


def run_portfolio_pm(
    root: Path,
    *,
    positions_path: Path | None = None,
) -> PortfolioPMResult:
    from bottleneck_capital.decision_engine import write_daily_board

    decision_board = write_daily_board(root)
    portfolio_board = write_portfolio_board(root, positions_path=positions_path)
    return PortfolioPMResult(decision_board, portfolio_board)


def render_portfolio_board(root: Path, analysis: PortfolioAnalysis) -> str:
    from bottleneck_capital.opportunity import rank_opportunities
    from bottleneck_capital.research_handoffs import pending_research_handoffs

    opportunities = rank_opportunities(root, regime=analysis.regime, portfolio=analysis)
    pending_handoffs = pending_research_handoffs(root)
    lines = [
        "# Bottleneck Capital Local Portfolio Board",
        "",
        f"As of: {analysis.as_of}",
        f"Base currency: {analysis.base_currency}",
        "",
        "Privacy: generated from exact local positions and kept gitignored.",
        "",
        "## Portfolio Posture",
        "",
        "| Posture | Invested | Cash | Required Reserve | Deployable Cash | Regime |",
        "|---|---:|---:|---:|---:|---|",
        (
            f"| {analysis.posture} | {analysis.invested_pct:.1f}% | "
            f"{analysis.cash_pct:.1f}% | {analysis.required_cash_reserve_pct:.1f}% | "
            f"{analysis.deployable_cash_pct:.1f}% | {analysis.regime.state} |"
        ),
        "",
        "## Concentration And Capacity",
        "",
    ]
    if analysis.concentration_alerts:
        lines.extend(f"- {item}" for item in analysis.concentration_alerts)
    else:
        lines.append("- No configured ticker, sleeve, or factor limit is breached.")
    lines.extend(
        [
            "",
            "| Ticker | Sleeve | Decision | Weight | Policy Cap | Remaining Capacity |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for holding in analysis.holdings:
        lines.append(
            f"| {holding.ticker} | {_table(holding.sleeve)} | {holding.decision} | "
            f"{holding.weight_pct:.1f}% | {holding.max_weight_pct:.1f}% | "
            f"{holding.remaining_capacity_pct:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Sleeve Allocation",
            "",
            "| Sleeve | Weight | Policy Limit | Status |",
            "|---|---:|---:|---|",
        ]
    )
    config = _portfolio_config(root)
    sleeve_limits = config.get("sleeve_limits_pct", {})
    default_sleeve_limit = _float(config.get("default_sleeve_limit_pct"), 30.0)
    for sleeve, weight in analysis.sleeve_weights.items():
        limit = _float(
            sleeve_limits.get(sleeve) if isinstance(sleeve_limits, dict) else None,
            default_sleeve_limit,
        )
        status = "OVER_LIMIT" if weight > limit else "WITHIN_LIMIT"
        lines.append(f"| {_table(sleeve)} | {weight:.1f}% | {limit:.1f}% | {status} |")

    lines.extend(
        [
            "",
            "## Factor Concentration",
            "",
            (
                "Factor exposure is overlapping sensitivity, not additive portfolio weight. "
                "It shows how much capital is meaningfully exposed to each transmission channel."
            ),
            "",
            "| Factor | Exposure | Policy Limit | Status |",
            "|---|---:|---:|---|",
        ]
    )
    for item in analysis.factor_exposures:
        status = "OVER_LIMIT" if item.exposure_pct > item.limit_pct else "WITHIN_LIMIT"
        lines.append(
            f"| {_table(item.factor)} | {item.exposure_pct:.1f}% | "
            f"{item.limit_pct:.1f}% | {status} |"
        )

    lines.extend(
        [
            "",
            "## Scenario Vulnerability",
            "",
            (
                "Impact scores are directional sensitivity scores, not predicted returns. "
                "Negative values indicate adverse portfolio transmission."
            ),
            "",
            "| Scenario | Impact Score | Affected Weight | Posture | Primary Factors |",
            "|---|---:|---:|---|---|",
        ]
    )
    for item in analysis.scenario_impacts:
        lines.append(
            f"| {_table(item.name)} | {item.impact_score:+.1f} | "
            f"{item.affected_weight_pct:.1f}% | {item.posture} | "
            f"{_table(', '.join(item.primary_factors))} |"
        )

    lines.extend(
        [
            "",
            "## Pending Research Handoffs",
            "",
            (
                "Capital changes remain blocked until Portfolio PM records an explicit "
                "outcome for each resolver handoff."
            ),
            "",
            "| Ticker | Cause | Thesis | Bias | Memo |",
            "|---|---|---|---|---|",
        ]
    )
    if pending_handoffs:
        for handoff in pending_handoffs:
            lines.append(
                f"| {_table(handoff.get('ticker'))} | "
                f"{_table(handoff.get('cause_status'))} | "
                f"{_table(handoff.get('thesis_status'))} | "
                f"{_table(handoff.get('provisional_bias'))} | "
                f"{_table(handoff.get('memo_path'))} |"
            )
    else:
        lines.append("| - | - | - | - | No pending resolver handoffs. |")

    lines.extend(
        [
            "",
            "## Marginal Capital Priorities",
            "",
            (
                "Ranking combines thesis, valuation, bottleneck upside, evidence, private "
                "capacity, diversification, scenario resilience, and current regime."
            ),
            "",
            (
                "| Rank | Ticker | Decision | Effective Score | Capacity | Diversification | "
                "Resilience | Discount | Entry Gate |"
            ),
            "|---:|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for index, item in enumerate(opportunities[:10], start=1):
        lines.append(
            f"| {index} | {item.ticker} | {item.decision} | {item.score:.1f} | "
            f"{analysis.remaining_capacity_pct.get(item.ticker, 0.0):.1f}% | "
            f"{item.diversification_score:.1f} | {item.scenario_resilience_score:.1f} | "
            f"{_table(item.discount_class)} | {_table(item.entry_gate)} |"
        )

    active_discounts = [
        item
        for item in analysis.discounts.values()
        if item.classification != "NO_ACTIVE_DISLOCATION"
    ]
    lines.extend(
        [
            "",
            "## Discount And Impairment Map",
            "",
            "| Ticker | Classification | Confidence | Fundamentals | Bias | Rationale |",
            "|---|---|---:|---|---|---|",
        ]
    )
    if active_discounts:
        for item in sorted(active_discounts, key=lambda value: value.ticker):
            lines.append(
                f"| {item.ticker} | {_table(item.classification)} | {item.confidence:.0f}% | "
                f"{item.fundamental_status} | {item.action_bias} | "
                f"{_table(item.rationale)} |"
            )
    else:
        lines.append("| - | - | - | - | - | No active dislocation requires classification. |")

    lines.extend(["", "## Data Quality", ""])
    if analysis.data_gaps:
        lines.extend(f"- {item}" for item in analysis.data_gaps)
    else:
        lines.append("- Position values and cash are normalized into the configured base currency.")
    lines.append(
        f"- Regime evidence: {analysis.regime.source_status}; "
        f"fresh={'YES' if analysis.regime.fresh else 'NO'}; "
        f"confidence={analysis.regime.confidence:.0f}%."
    )
    return "\n".join(lines) + "\n"


def _portfolio_config(root: Path) -> dict[str, Any]:
    path = root / "configs" / "portfolio.yaml"
    if not path.exists():
        return {}
    data = load_yaml_file(path)
    config = data.get("portfolio", {}) if isinstance(data, dict) else {}
    return config if isinstance(config, dict) else {}


def _factor_profile(config: dict[str, Any], ticker: str, sleeve: str) -> dict[str, float]:
    sleeve_profiles = config.get("sleeve_factor_profiles", {})
    ticker_profiles = config.get("ticker_factor_overrides", {})
    profile: dict[str, float] = {}
    if isinstance(sleeve_profiles, dict) and isinstance(sleeve_profiles.get(sleeve), dict):
        profile.update(
            {
                scalar_text(key): _bounded(value, 0.0, 1.0)
                for key, value in sleeve_profiles[sleeve].items()
            }
        )
    if isinstance(ticker_profiles, dict) and isinstance(ticker_profiles.get(ticker), dict):
        profile.update(
            {
                scalar_text(key): _bounded(value, 0.0, 1.0)
                for key, value in ticker_profiles[ticker].items()
            }
        )
    return dict(sorted(profile.items()))


def _factor_exposures(
    config: dict[str, Any], holdings: list[HoldingAnalysis]
) -> list[FactorExposure]:
    values: dict[str, float] = {}
    for holding in holdings:
        for factor, sensitivity in holding.factors.items():
            values[factor] = values.get(factor, 0.0) + holding.weight_pct * abs(sensitivity)
    limits = config.get("factor_limits_pct", {})
    return sorted(
        [
            FactorExposure(
                factor=factor,
                exposure_pct=exposure,
                limit_pct=_float(limits.get(factor), 100.0) if isinstance(limits, dict) else 100.0,
            )
            for factor, exposure in values.items()
        ],
        key=lambda item: (-item.exposure_pct, item.factor),
    )


def _scenario_impacts(
    config: dict[str, Any], holdings: list[HoldingAnalysis]
) -> list[ScenarioImpact]:
    raw_scenarios = config.get("scenarios", {})
    if not isinstance(raw_scenarios, dict):
        return []
    impacts: list[ScenarioImpact] = []
    for scenario, raw in raw_scenarios.items():
        if not isinstance(raw, dict):
            continue
        shocks = raw.get("factor_shocks", {})
        if not isinstance(shocks, dict):
            continue
        impact = 0.0
        affected = 0.0
        factor_contributions: dict[str, float] = {}
        for holding in holdings:
            holding_affected = False
            for factor, raw_shock in shocks.items():
                sensitivity = holding.factors.get(scalar_text(factor), 0.0)
                contribution = holding.weight_pct * sensitivity * _float(raw_shock) / 100.0
                impact += contribution
                factor_contributions[scalar_text(factor)] = (
                    factor_contributions.get(scalar_text(factor), 0.0) + contribution
                )
                if abs(sensitivity * _float(raw_shock)) >= 15:
                    holding_affected = True
            if holding_affected:
                affected += holding.weight_pct
        impact = _bounded(impact, -100.0, 100.0)
        primary = tuple(
            factor
            for factor, _ in sorted(
                factor_contributions.items(), key=lambda item: (-abs(item[1]), item[0])
            )[:3]
        )
        impacts.append(
            ScenarioImpact(
                scenario=scalar_text(scenario),
                name=scalar_text(raw.get("name")) or scalar_text(scenario),
                description=scalar_text(raw.get("description")),
                impact_score=impact,
                affected_weight_pct=min(100.0, affected),
                posture=_scenario_posture(impact),
                primary_factors=primary,
            )
        )
    return sorted(impacts, key=lambda item: (item.impact_score, item.scenario))


def _concentration_alerts(
    config: dict[str, Any],
    holdings: list[HoldingAnalysis],
    sleeve_weights: dict[str, float],
    factor_exposures: list[FactorExposure],
) -> list[str]:
    alerts: list[str] = []
    for holding in holdings:
        if holding.weight_pct > holding.max_weight_pct:
            alerts.append(
                f"{holding.ticker} is {holding.weight_pct:.1f}% versus its "
                f"{holding.max_weight_pct:.1f}% policy cap."
            )
    sleeve_limits = config.get("sleeve_limits_pct", {})
    default_limit = _float(config.get("default_sleeve_limit_pct"), 30.0)
    for sleeve, weight in sleeve_weights.items():
        limit = _float(
            sleeve_limits.get(sleeve) if isinstance(sleeve_limits, dict) else None,
            default_limit,
        )
        if weight > limit:
            alerts.append(f"{sleeve} is {weight:.1f}% versus its {limit:.1f}% sleeve limit.")
    for item in factor_exposures:
        if item.exposure_pct > item.limit_pct:
            alerts.append(
                f"{item.factor} sensitivity is {item.exposure_pct:.1f}% versus its "
                f"{item.limit_pct:.1f}% policy limit."
            )
    return alerts


def _discount_assessments(
    root: Path,
    watchlist: dict[str, dict[str, Any]],
    regime: MarketRegime,
) -> dict[str, DiscountAssessment]:
    events = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    by_ticker: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        ticker = scalar_text(event.get("ticker")).upper()
        if ticker and ticker != "BCAP":
            by_ticker.setdefault(ticker, []).append(event)
    safe_dips: set[str] = set()
    try:
        from bottleneck_capital.dip_review import review_active_dips

        safe_dips = {
            item.ticker
            for item in review_active_dips(root)
            if item.bounded and item.thesis_damage_risk in {"LOW", "LOW_MEDIUM"}
        }
    except (ConfigError, ValueError):
        safe_dips = set()

    assessments: dict[str, DiscountAssessment] = {}
    for ticker in watchlist:
        ticker_events = by_ticker.get(ticker, [])
        classes = {scalar_text(event.get("event_class")) for event in ticker_events}
        combined = " ".join(scalar_text(event.get("summary")) for event in ticker_events).lower()
        if not ticker_events:
            assessments[ticker] = _discount(
                ticker,
                "NO_ACTIVE_DISLOCATION",
                100,
                "NO_SIGNAL",
                "NONE",
                "No active material event requires discount classification.",
            )
        elif classes & {"thesis_damage_candidate", "sa_exit_update"}:
            assessments[ticker] = _discount(
                ticker,
                "THESIS_IMPAIRMENT",
                95,
                "IMPAIRED_OR_UNRESOLVED",
                "BLOCK",
                "A thesis-damage or full-exit signal is active; price weakness is not a discount.",
            )
        elif any(word in combined for word in ("financing", "dilution", "liquidity", "default")):
            assessments[ticker] = _discount(
                ticker,
                "FINANCING_LIQUIDITY_IMPAIRMENT",
                85,
                "UNRESOLVED",
                "RESEARCH",
                "The active event may alter financing capacity or per-share economics.",
            )
        elif classes & {"filing_update", "catalyst_update"}:
            assessments[ticker] = _discount(
                ticker,
                "COMPANY_EVENT_UNRESOLVED",
                80,
                "UNRESOLVED",
                "RESEARCH",
                "A company-specific filing or catalyst requires fundamental review.",
            )
        elif ticker in safe_dips:
            assessments[ticker] = _discount(
                ticker,
                "COMPANY_EVENT_THESIS_INTACT",
                80,
                "LIKELY_INTACT",
                "VALUATION_REVIEW",
                "The dip cause is bounded with low thesis-damage risk; valuation still must clear.",
            )
        elif regime.geopolitical_status in {
            "conflict",
            "escalating",
            "renewed_escalation",
        }:
            assessments[ticker] = _discount(
                ticker,
                "GEOPOLITICAL_RISK_PREMIUM",
                70,
                "UNRESOLVED",
                "SCENARIO_REVIEW",
                "An adverse geopolitical regime is active; separate repricing from impairment.",
            )
        elif regime.channel_severity.get("rates", 0.0) >= 35:
            assessments[ticker] = _discount(
                ticker,
                "FACTOR_OR_RATES_DISCOUNT",
                70,
                "LIKELY_INTACT",
                "CAPACITY_REVIEW",
                "Rates or financing transmission is material and may explain the dislocation.",
            )
        elif regime.market_confirmation == "CONFIRMED":
            assessments[ticker] = _discount(
                ticker,
                "BROAD_MARKET_DISCOUNT",
                65,
                "LIKELY_INTACT",
                "VALUATION_REVIEW",
                "Cross-asset risk confirms broad de-risking rather than isolated company damage.",
            )
        else:
            assessments[ticker] = _discount(
                ticker,
                "UNKNOWN",
                35,
                "UNRESOLVED",
                "RESEARCH",
                "The active dislocation lacks a sufficiently supported causal classification.",
            )
    return assessments


def _discount(
    ticker: str,
    classification: str,
    confidence: float,
    fundamental_status: str,
    action_bias: str,
    rationale: str,
) -> DiscountAssessment:
    return DiscountAssessment(
        ticker=ticker,
        classification=classification,
        confidence=confidence,
        fundamental_status=fundamental_status,
        action_bias=action_bias,
        rationale=rationale,
    )


def _required_cash_reserve(config: dict[str, Any], regime: MarketRegime) -> float:
    elevated = regime.state in {"ELEVATED", "MARKET_STRESS", "CONFLICT_ESCALATION", "UNKNOWN"}
    key = "elevated_cash_reserve_pct" if elevated or not regime.fresh else "normal_cash_reserve_pct"
    return _float(config.get(key), 20.0 if elevated else 10.0)


def _portfolio_posture(
    *,
    normalization_complete: bool,
    regime: MarketRegime,
    alerts: list[str],
    cash_pct: float,
    required_reserve: float,
    scenarios: list[ScenarioImpact],
) -> str:
    if not normalization_complete or not regime.fresh:
        return "CONTEXT_INCOMPLETE"
    worst = min((item.impact_score for item in scenarios), default=0.0)
    if regime.state in {"MARKET_STRESS", "CONFLICT_ESCALATION"} or worst <= -25:
        return "DEFENSIVE"
    if alerts or regime.state == "ELEVATED":
        return "SELECTIVE"
    if cash_pct < required_reserve:
        return "CAPITAL_CONSTRAINED"
    return "OPEN_FOR_DEPLOYMENT"


def _capacity_score(maximum: float, current: float) -> float:
    if maximum <= 0:
        return 0.0
    if current >= maximum:
        return 10.0
    return min(100.0, 50.0 + 50.0 * (maximum - current) / maximum)


def _diversification_score(profile: dict[str, float], exposures: dict[str, float]) -> float:
    load = sum(profile.values())
    if load <= 0:
        return 50.0
    overlap = sum(exposures.get(factor, 0.0) * value for factor, value in profile.items()) / load
    return _bounded(100.0 - overlap, 0.0, 100.0)


def _scenario_resilience_score(config: dict[str, Any], profile: dict[str, float]) -> float:
    scenarios = config.get("scenarios", {})
    if not isinstance(scenarios, dict) or not profile:
        return 50.0
    impacts: list[float] = []
    for raw in scenarios.values():
        if not isinstance(raw, dict) or not isinstance(raw.get("factor_shocks"), dict):
            continue
        shocks = raw["factor_shocks"]
        relevant_load = sum(profile.get(scalar_text(factor), 0.0) for factor in shocks)
        if relevant_load <= 0:
            continue
        impact = sum(
            profile.get(scalar_text(factor), 0.0) * _float(shock)
            for factor, shock in shocks.items()
        ) / relevant_load
        impacts.append(impact)
    worst = min(impacts, default=0.0)
    return _bounded(50.0 + worst * 0.5, 0.0, 100.0)


def _scenario_posture(impact: float) -> str:
    if impact <= -25:
        return "HIGH_ADVERSE"
    if impact <= -12:
        return "ADVERSE"
    if impact <= -5:
        return "WATCH"
    if impact >= 12:
        return "BENEFICIAL"
    return "MIXED"


def _max_position_weight(root: Path, ticker: str, default: float) -> float:
    decision, _ = read_markdown_frontmatter(root / "research" / "decisions" / f"{ticker}.md")
    asset, _ = read_markdown_frontmatter(root / "research" / "assets" / f"{ticker}.md")
    configured = asset.get("max_position_weight_pct") or decision.get(
        "max_position_weight_pct"
    )
    return _float(configured, default)


def _latest_snapshots(root: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(root / "state" / "market_snapshots.jsonl"):
        ticker = scalar_text(record.get("ticker")).upper()
        if ticker:
            latest[ticker] = record
    return latest


def _fx_rate_to_base(
    positions_data: dict[str, Any],
    snapshots: dict[str, dict[str, Any]],
    *,
    currency: str,
    base_currency: str,
) -> float | None:
    currency = currency.upper()
    base_currency = base_currency.upper()
    if not currency or currency == base_currency:
        return 1.0
    configured = positions_data.get("fx_to_base")
    if isinstance(configured, dict):
        rate = _float(configured.get(currency))
        if rate > 0:
            return rate
    usd_cad = _float(snapshots.get("USDCAD", {}).get("price"))
    if usd_cad > 0 and currency == "USD" and base_currency == "CAD":
        return usd_cad
    if usd_cad > 0 and currency == "CAD" and base_currency == "USD":
        return 1.0 / usd_cad
    return None


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: Any, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, _float(value)))


def _table(value: Any) -> str:
    return scalar_text(value).replace("|", "\\|").replace("\n", " ")


def _today() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).date().isoformat()
