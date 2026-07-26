from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bottleneck_capital.opportunity import rank_opportunities
from bottleneck_capital.portfolio import analyze_portfolio, write_portfolio_board


def test_portfolio_analysis_normalizes_fx_and_calculates_capacity(tmp_path: Path) -> None:
    _write_project(tmp_path)

    analysis = analyze_portfolio(tmp_path)

    aaa = next(item for item in analysis.holdings if item.ticker == "AAA")
    assert analysis.normalization_complete is True
    assert analysis.total_capital == 150
    assert analysis.cash_pct == 16.666666666666668
    assert aaa.weight_pct == 83.33333333333333
    assert aaa.remaining_capacity_pct == 6.666666666666671
    assert analysis.capacity_scores["AAA"] < analysis.capacity_scores["BBB"]
    assert analysis.capacity_scores["BBB"] == 100


def test_portfolio_analysis_aggregates_factors_and_scenario_vulnerability(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)

    analysis = analyze_portfolio(tmp_path)

    ai_capex = next(item for item in analysis.factor_exposures if item.factor == "ai_capex")
    slowdown = next(
        item for item in analysis.scenario_impacts if item.scenario == "ai_capex_slowdown"
    )
    assert ai_capex.exposure_pct == 83.33333333333333
    assert slowdown.impact_score == -75
    assert slowdown.posture == "HIGH_ADVERSE"
    assert analysis.posture == "DEFENSIVE"
    assert any("ai_capex sensitivity" in item for item in analysis.concentration_alerts)


def test_opportunity_ranking_uses_private_capacity_without_persisted_weight(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    analysis = analyze_portfolio(tmp_path)

    ranked = rank_opportunities(tmp_path, regime=analysis.regime, portfolio=analysis)

    assert ranked[0].ticker == "BBB"
    assert ranked[0].portfolio_capacity_score == 100
    assert ranked[1].ticker == "AAA"
    assert ranked[1].portfolio_capacity_score < 60


def test_discount_classifier_blocks_thesis_damage(tmp_path: Path) -> None:
    _write_project(tmp_path)
    signal_path = tmp_path / "state" / "signal_events.jsonl"
    signal_path.write_text(
        json.dumps(
            {
                "event_id": "aaa-damage",
                "ticker": "AAA",
                "event_class": "thesis_damage_candidate",
                "priority": "high",
                "resolved": False,
                "summary": "Customer loss may break the thesis.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    analysis = analyze_portfolio(tmp_path)

    discount = analysis.discounts["AAA"]
    assert discount.classification == "THESIS_IMPAIRMENT"
    assert discount.action_bias == "BLOCK"


def test_portfolio_board_is_private_and_portfolio_first(tmp_path: Path) -> None:
    _write_project(tmp_path)

    path = write_portfolio_board(tmp_path)
    report = path.read_text(encoding="utf-8")

    assert path.parent.name == "local_portfolio_boards"
    assert "Privacy: generated from exact local positions" in report
    assert report.index("## Portfolio Posture") < report.index("## Marginal Capital Priorities")
    assert "## Scenario Vulnerability" in report
    assert "## Discount And Impairment Map" in report


def _write_project(root: Path) -> None:
    configs = root / "configs"
    configs.mkdir(parents=True)
    (configs / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
    trade_policy: long_only_after_research
  - ticker: BBB
    name: BBB Inc.
    sleeve: compute_infra
    trade_policy: long_only_after_research
""",
        encoding="utf-8",
    )
    (configs / "signal_thresholds.yaml").write_text(
        """sentinel:
  research:
    research_required_max_age_days: 5
""",
        encoding="utf-8",
    )
    (configs / "regime.yaml").write_text(
        """regime:
  context_snapshot_max_age_days: 4
  required_context_symbols:
    - SPY
    - QQQ
    - USO
    - VIXY
  context_symbols:
    SPY: SPY
    QQQ: QQQ
    USO: USO
    VIXY: VIXY
    USDCAD: CAD=X
  sleeve_channel_exposures:
    compute_infra:
      global_risk: -0.10
""",
        encoding="utf-8",
    )
    (configs / "portfolio.yaml").write_text(
        """portfolio:
  default_ticker_limit_pct: 90
  default_sleeve_limit_pct: 100
  normal_cash_reserve_pct: 10
  elevated_cash_reserve_pct: 20
  factor_limits_pct:
    ai_capex: 70
    rates_duration: 100
  sleeve_factor_profiles:
    compute_infra:
      ai_capex: 1.0
      rates_duration: 0.5
  scenarios:
    ai_capex_slowdown:
      name: AI capex slows
      description: Demand falls below expectations.
      factor_shocks:
        ai_capex: -90
""",
        encoding="utf-8",
    )
    metadata = """name: {ticker} Inc.
sleeve: compute_infra
trade_policy: long_only_after_research
current_decision: HOLD
thesis_health_score: 80
valuation_attractiveness_score: 70
bottleneck_upside_score: 80
confidence_score: 75
max_position_weight_pct: 90
approved_entry_zone: $90-$100
one_line_rationale: Test opportunity.
"""
    for ticker in ("AAA", "BBB"):
        for directory in ("assets", "decisions"):
            path = root / "research" / directory / f"{ticker}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                f"---\nticker: {ticker}\n{metadata.format(ticker=ticker)}---\n# {ticker}\n",
                encoding="utf-8",
            )
    state = root / "state"
    state.mkdir()
    (state / "local_positions.yaml").write_text(
        """as_of: 2026-07-15
base_currency: CAD
cash:
  CAD: 25
positions:
  - ticker: AAA
    quantity: 10
    average_cost: 8
    current_price: 10
    currency: USD
""",
        encoding="utf-8",
    )
    observed_at = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    snapshots = [
        {
            "ticker": ticker,
            "price": 1.25 if ticker == "USDCAD" else 100,
            "previous_close": 100,
            "observed_at": observed_at,
        }
        for ticker in ("SPY", "QQQ", "USO", "VIXY", "USDCAD")
    ]
    (state / "market_snapshots.jsonl").write_text(
        "\n".join(json.dumps(item) for item in snapshots) + "\n",
        encoding="utf-8",
    )
    (state / "signal_events.jsonl").write_text("", encoding="utf-8")
