from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.io import (
    load_yaml_file,
    read_jsonl,
    read_markdown_frontmatter,
    scalar_bool,
    scalar_text,
)
from bottleneck_capital.market_regime import (
    MarketRegime,
    assess_market_regime,
    regime_adjustment,
    regime_entry_gate,
)


@dataclass(frozen=True)
class OpportunityCandidate:
    ticker: str
    decision: str
    score: float
    structural_score: float
    regime_adjustment: float
    entry_gate: str
    current_price: float
    entry_zone: str
    rationale: str
    thesis_score: float
    valuation_score: float
    bottleneck_score: float
    confidence_score: float
    portfolio_capacity_score: float
    diversification_score: float
    scenario_resilience_score: float
    discount_class: str


@dataclass(frozen=True)
class OverdueResearchBlock:
    ticker: str
    age_days: int
    max_age_days: int
    score: float
    rationale: str
    last_primary_source_check: str


def rank_opportunities(
    root: Path,
    *,
    decision_overrides: dict[str, str] | None = None,
    regime: MarketRegime | None = None,
    portfolio: Any | None = None,
) -> list[OpportunityCandidate]:
    prices = _latest_prices(root)
    current_regime = regime or assess_market_regime(root)
    portfolio_context = portfolio or _private_portfolio_context(root, current_regime)
    candidates: list[OpportunityCandidate] = []
    for ticker in _watchlist_tickers(root):
        data = _asset_decision_data(root, ticker)
        decision = scalar_text(
            (decision_overrides or {}).get(ticker) or data.get("current_decision")
        ).upper()
        if scalar_text(data.get("trade_policy")) == "signal_only_no_puts_or_shorts":
            continue
        if decision in {"SELL", "TRIM"}:
            continue

        thesis = _score(data.get("thesis_health_score"), 50.0)
        valuation = _score(data.get("valuation_attractiveness_score"), 40.0)
        confidence = _score(data.get("confidence_score"), 50.0)
        bottleneck = _score(data.get("bottleneck_upside_score"), thesis)
        capacity = _portfolio_score(
            data,
            _portfolio_metric(portfolio_context, "capacity_scores", ticker, 60.0),
        )
        diversification = _portfolio_metric(
            portfolio_context,
            "diversification_scores",
            ticker,
            50.0,
        )
        resilience = _portfolio_metric(
            portfolio_context,
            "scenario_resilience_scores",
            ticker,
            50.0,
        )
        discount = _discount_class(portfolio_context, ticker)
        action_bonus = {
            "BUY_NOW": 10.0,
            "ADD_ON_DIP": 5.0,
            "HOLD": 0.0,
            "RESEARCH_REQUIRED": -10.0,
        }.get(decision, 0.0)
        structural_score = min(
            100.0,
            max(
                0.0,
                0.25 * thesis
                + 0.25 * valuation
                + 0.15 * bottleneck
                + 0.10 * confidence
                + 0.10 * capacity
                + 0.10 * diversification
                + 0.05 * resilience
                + action_bonus,
            ),
        )
        adjustment = regime_adjustment(
            root,
            ticker=ticker,
            sleeve=scalar_text(data.get("sleeve")),
            regime=current_regime,
        )
        score = min(100.0, max(0.0, structural_score + adjustment))
        candidates.append(
            OpportunityCandidate(
                ticker=ticker,
                decision=decision or "RESEARCH_REQUIRED",
                score=score,
                structural_score=structural_score,
                regime_adjustment=adjustment,
                entry_gate=regime_entry_gate(
                    root,
                    decision=decision,
                    adjustment=adjustment,
                    regime=current_regime,
                ),
                current_price=prices.get(ticker, 0.0),
                entry_zone=scalar_text(data.get("approved_entry_zone")) or "Not armed",
                rationale=scalar_text(data.get("one_line_rationale"))
                or "No current rationale.",
                thesis_score=thesis,
                valuation_score=valuation,
                bottleneck_score=bottleneck,
                confidence_score=confidence,
                portfolio_capacity_score=capacity,
                diversification_score=diversification,
                scenario_resilience_score=resilience,
                discount_class=discount,
            )
        )
    return sorted(candidates, key=lambda item: (-item.score, item.ticker))


def overdue_research_blocks(
    root: Path,
    *,
    decision_overrides: dict[str, str] | None = None,
    as_of: date | None = None,
) -> list[OverdueResearchBlock]:
    today = as_of or datetime.now(ZoneInfo("America/Toronto")).date()
    max_age = _research_required_max_age_days(root)
    ranked = {
        item.ticker: item
        for item in rank_opportunities(root, decision_overrides=decision_overrides)
    }
    handoff_checks = _latest_handoff_check_by_ticker(root)
    overdue: list[OverdueResearchBlock] = []
    for ticker in _watchlist_tickers(root):
        data = _asset_decision_data(root, ticker)
        decision = scalar_text(
            (decision_overrides or {}).get(ticker) or data.get("current_decision")
        ).upper()
        if decision != "RESEARCH_REQUIRED":
            continue
        checked = max(
            (
                scalar_text(data.get("last_primary_source_check"))[:10],
                scalar_text(data.get("last_updated"))[:10],
                handoff_checks.get(ticker, ""),
            )
        )
        checked_date = _date_value(checked)
        age_days = (today - checked_date).days if checked_date is not None else 999
        if age_days <= max_age:
            continue
        candidate = ranked.get(ticker)
        overdue.append(
            OverdueResearchBlock(
                ticker=ticker,
                age_days=age_days,
                max_age_days=max_age,
                score=candidate.score if candidate else 0.0,
                rationale=scalar_text(data.get("one_line_rationale"))
                or "Research block has no rationale.",
                last_primary_source_check=checked or "missing",
            )
        )
    return sorted(overdue, key=lambda item: (-item.score, -item.age_days, item.ticker))


def _latest_handoff_check_by_ticker(root: Path) -> dict[str, str]:
    latest: dict[str, str] = {}
    for record in read_jsonl(root / "state" / "research_handoffs.jsonl"):
        if scalar_text(record.get("record_type")) != "research_handoff":
            continue
        ticker = scalar_text(record.get("ticker")).upper()
        checked = scalar_text(
            record.get("primary_source_checked_at") or record.get("memo_date")
        )[:10]
        if ticker and checked and checked > latest.get(ticker, ""):
            latest[ticker] = checked
    return latest


def opportunity_board_limit(root: Path) -> int:
    research = _research_config(root)
    try:
        return max(1, int(research.get("opportunity_board_limit", 10)))
    except (TypeError, ValueError):
        return 10


def _asset_decision_data(root: Path, ticker: str) -> dict[str, Any]:
    decision, _ = read_markdown_frontmatter(
        root / "research" / "decisions" / f"{ticker}.md"
    )
    asset, _ = read_markdown_frontmatter(root / "research" / "assets" / f"{ticker}.md")
    return {**decision, **asset}


def _watchlist_tickers(root: Path) -> list[str]:
    data = load_yaml_file(root / "configs" / "watchlist.yaml")
    items = data.get("watchlist", []) if isinstance(data, dict) else data
    if not isinstance(items, list):
        return []
    return [
        scalar_text(item.get("ticker")).upper()
        for item in items
        if isinstance(item, dict) and scalar_text(item.get("ticker"))
    ]


def _latest_prices(root: Path) -> dict[str, float]:
    prices: dict[str, float] = {}
    for record in read_jsonl(root / "state" / "market_snapshots.jsonl"):
        ticker = scalar_text(record.get("ticker")).upper()
        if ticker:
            prices[ticker] = _float(record.get("price"))
    return prices


def _portfolio_score(data: dict[str, Any], private_capacity: float) -> float:
    if not scalar_bool(data.get("portfolio_risk_allows_add", True)):
        return 0.0
    return min(100.0, max(0.0, private_capacity))


def _private_portfolio_context(root: Path, regime: MarketRegime) -> Any | None:
    from bottleneck_capital.positions import LOCAL_POSITIONS_PATH

    if not (root / LOCAL_POSITIONS_PATH).exists():
        return None
    try:
        from bottleneck_capital.portfolio import analyze_portfolio

        return analyze_portfolio(root, regime=regime)
    except (OSError, ValueError):
        return None


def _portfolio_metric(
    portfolio: Any | None,
    field: str,
    ticker: str,
    default: float,
) -> float:
    values = getattr(portfolio, field, {}) if portfolio is not None else {}
    if not isinstance(values, dict):
        return default
    return _score(values.get(ticker), default)


def _discount_class(portfolio: Any | None, ticker: str) -> str:
    discounts = getattr(portfolio, "discounts", {}) if portfolio is not None else {}
    if not isinstance(discounts, dict) or ticker not in discounts:
        return "NOT_CLASSIFIED"
    return scalar_text(getattr(discounts[ticker], "classification", "")) or "NOT_CLASSIFIED"


def _research_required_max_age_days(root: Path) -> int:
    research = _research_config(root)
    try:
        return max(1, int(research.get("research_required_max_age_days", 5)))
    except (TypeError, ValueError):
        return 5


def _research_config(root: Path) -> dict[str, Any]:
    path = root / "configs" / "signal_thresholds.yaml"
    if not path.exists():
        return {}
    data = load_yaml_file(path)
    sentinel = data.get("sentinel", {}) if isinstance(data, dict) else {}
    research = sentinel.get("research", {}) if isinstance(sentinel, dict) else {}
    return research if isinstance(research, dict) else {}


def _date_value(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _score(value: Any, default: float) -> float:
    if value is None or value == "":
        return default
    return min(100.0, max(0.0, _float(value)))


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
