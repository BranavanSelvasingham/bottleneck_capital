from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bottleneck_capital.decision_engine import write_action_board
from bottleneck_capital.dip_review import review_active_dips


def test_broad_same_day_cluster_bounds_dip_cause(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, [f"T{i}" for i in range(8)])
    _write_signals(
        tmp_path,
        [
            _dip_event(f"T{i}", one_day_drop_pct=-8, observed_at="2026-06-26T10:00:00-04:00")
            for i in range(8)
        ],
    )

    reviews = {review.ticker: review for review in review_active_dips(tmp_path)}

    assert reviews["T0"].bounded is True
    assert reviews["T0"].cause_class == "broad_cross_book_de_risking"
    assert "8 active dip triggers" in reviews["T0"].evidence


def test_unknown_single_name_dip_is_not_bounded(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA"])
    _write_signals(tmp_path, [_dip_event("AAA", one_day_drop_pct=-8)])

    review = review_active_dips(tmp_path)[0]

    assert review.bounded is False
    assert review.cause_class == "unknown_single_name_or_sparse_move"
    assert review.action_bias == "WAIT_FOR_CAUSE"


def test_financing_language_bounds_but_blocks_buy_bias(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA"])
    _write_signals(
        tmp_path,
        [
            _dip_event(
                "AAA",
                one_day_drop_pct=-12,
                summary="AAA price dislocation after convertible notes financing.",
            )
        ],
    )

    review = review_active_dips(tmp_path)[0]

    assert review.bounded is True
    assert review.cause_class == "company_financing_or_dilution"
    assert review.action_bias == "DILUTION_REVIEW_BEFORE_ANY_ADD"


def test_action_board_includes_dip_cause_reviews(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA"])
    _write_decision(tmp_path, "AAA", {"current_decision": "HOLD"})
    _write_signals(tmp_path, [_dip_event("AAA", one_day_drop_pct=-8)])

    report = write_action_board(tmp_path).read_text(encoding="utf-8")

    assert "## Dip Cause Reviews" in report
    assert "| AAA | NO | unknown_single_name_or_sparse_move" in report


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


def _write_decision(root: Path, ticker: str, overrides: dict[str, Any]) -> None:
    metadata = {
        "ticker": ticker,
        "name": f"{ticker} Inc.",
        "sleeve": "test_sleeve",
        "current_decision": "HOLD",
        "thesis_damage": False,
        "one_line_rationale": "Test hold.",
    }
    metadata.update(overrides)
    frontmatter = "\n".join(f"{key}: {_yaml_value(value)}" for key, value in metadata.items())
    for directory in ("assets", "decisions"):
        path = root / "research" / directory / f"{ticker}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\n{frontmatter}\n---\n# {ticker}\n", encoding="utf-8")


def _write_signals(root: Path, records: list[dict[str, Any]]) -> None:
    path = root / "state" / "signal_events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _dip_event(
    ticker: str,
    *,
    one_day_drop_pct: float,
    observed_at: str = "2026-06-26T09:45:00-04:00",
    summary: str = "",
) -> dict[str, Any]:
    event_summary = summary or f"{ticker} price dislocation: one-day {one_day_drop_pct:.1f}%."
    return {
        "event_id": f"{ticker.lower()}-dip",
        "detected_at": observed_at,
        "ticker": ticker,
        "event_class": "dip_trigger",
        "priority": "high",
        "requires_codex": True,
        "resolved": False,
        "source": "market_yahoo",
        "summary": event_summary,
        "raw_event": {
            "ticker": ticker,
            "event_type": "price_dislocation",
            "observed_at": observed_at,
            "one_day_drop_pct": one_day_drop_pct,
            "summary": event_summary,
        },
    }


def _yaml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)
