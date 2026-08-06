from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.opportunity import overdue_research_blocks, rank_opportunities


def test_rank_opportunities_surfaces_valuation_and_bottleneck_candidate(
    tmp_path: Path,
) -> None:
    _write_watchlist(tmp_path, ["MU", "CEG"])
    _write_ticker(
        tmp_path,
        "MU",
        {
            "current_decision": "ADD_ON_DIP",
            "thesis_health_score": 88,
            "valuation_attractiveness_score": 72,
            "bottleneck_upside_score": 88,
            "confidence_score": 80,
            "max_position_weight_pct": 4,
            "current_position_weight_pct": 0,
            "approved_entry_zone": "$925-$950",
            "one_line_rationale": "HBM scarcity with cycle-aware sizing.",
        },
    )
    _write_ticker(
        tmp_path,
        "CEG",
        {
            "current_decision": "HOLD",
            "thesis_health_score": 58,
            "valuation_attractiveness_score": 28,
            "bottleneck_upside_score": 72,
            "confidence_score": 42,
            "approved_entry_zone": "$235-$240",
            "one_line_rationale": "Power scarcity watch.",
        },
    )
    state = tmp_path / "state"
    state.mkdir(parents=True)
    (state / "market_snapshots.jsonl").write_text(
        '{"ticker":"MU","price":979.3}\n{"ticker":"CEG","price":251.38}\n',
        encoding="utf-8",
    )

    ranked = rank_opportunities(tmp_path)

    assert ranked[0].ticker == "MU"
    assert ranked[0].decision == "ADD_ON_DIP"
    assert ranked[0].score > ranked[1].score
    assert ranked[0].current_price == 979.3


def test_overdue_research_block_uses_primary_source_age(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["MU"])
    _write_ticker(
        tmp_path,
        "MU",
        {
            "current_decision": "RESEARCH_REQUIRED",
            "last_primary_source_check": "2026-07-01",
            "one_line_rationale": "Earnings review is unresolved.",
        },
    )
    config = tmp_path / "configs" / "signal_thresholds.yaml"
    config.write_text(
        """sentinel:
  research:
    research_required_max_age_days: 5
""",
        encoding="utf-8",
    )

    overdue = overdue_research_blocks(tmp_path, as_of=date(2026, 7, 12))

    assert len(overdue) == 1
    assert overdue[0].ticker == "MU"
    assert overdue[0].age_days == 11
    assert overdue[0].max_age_days == 5


def test_rank_opportunities_penalizes_active_supply_without_inflating_squeeze(
    tmp_path: Path,
) -> None:
    _write_watchlist(tmp_path, ["AAA", "BBB"])
    common = {
        "current_decision": "ADD_ON_DIP",
        "thesis_health_score": 85,
        "valuation_attractiveness_score": 75,
        "bottleneck_upside_score": 85,
        "confidence_score": 80,
        "approved_entry_zone": "$10-$12",
        "one_line_rationale": "Equivalent structural opportunity.",
    }
    _write_ticker(tmp_path, "AAA", common)
    _write_ticker(tmp_path, "BBB", common)
    state = tmp_path / "state"
    state.mkdir(parents=True)
    today = datetime.now(ZoneInfo("America/Toronto")).date()
    records = [
        {
            "ticker": "AAA",
            "observed_at": today.isoformat(),
            "float_shares": 100,
            "eligible_supply_shares": 50,
            "unlock_date": (today + timedelta(days=1)).isoformat(),
            "short_interest_pct_float": 30,
        },
        {
            "ticker": "BBB",
            "observed_at": today.isoformat(),
            "short_interest_pct_float": 30,
            "days_to_cover": 7,
            "borrow_fee_pct": 20,
            "borrow_utilization_pct": 97,
            "put_call_open_interest_ratio": 0.5,
            "catalyst_within_days": 5,
        },
    ]
    (state / "market_structure_snapshots.jsonl").write_text(
        "".join(json.dumps(item) + "\n" for item in records),
        encoding="utf-8",
    )

    ranked = rank_opportunities(tmp_path)
    by_ticker = {item.ticker: item for item in ranked}

    assert by_ticker["AAA"].market_structure_adjustment == -8
    assert by_ticker["AAA"].market_structure_gate == "WAIT_FOR_SUPPLY_ABSORPTION"
    assert by_ticker["BBB"].flow_classification == "SQUEEZE_SETUP"
    assert by_ticker["BBB"].market_structure_adjustment <= 0
    assert ranked[0].ticker == "BBB"


def _write_watchlist(root: Path, tickers: list[str]) -> None:
    path = root / "configs" / "watchlist.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["watchlist:"]
    for ticker in tickers:
        lines.extend(
            [
                f"  - ticker: {ticker}",
                f"    name: {ticker} Inc.",
                "    sleeve: test_sleeve",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_ticker(root: Path, ticker: str, metadata: dict[str, Any]) -> None:
    values = {
        "ticker": ticker,
        "name": f"{ticker} Inc.",
        "sleeve": "test_sleeve",
        "trade_policy": "long_only_after_research",
        **metadata,
    }
    frontmatter = "\n".join(f"{key}: {_yaml(value)}" for key, value in values.items())
    for directory in ("assets", "decisions"):
        path = root / "research" / directory / f"{ticker}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\n{frontmatter}\n---\n# {ticker}\n", encoding="utf-8")


def _yaml(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str) and (":" in value or value.startswith("$") or "#" in value):
        return f'"{value}"'
    return str(value)
