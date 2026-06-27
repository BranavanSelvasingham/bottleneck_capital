from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from bottleneck_capital.decision_engine import (
    MissingDecisionFile,
    evaluate_all,
    evaluate_ticker,
    write_action_board,
    write_daily_board,
)
from bottleneck_capital.signal_events import resolve_signal_events


def test_missing_decision_file_fails_validation(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA"])

    with pytest.raises(MissingDecisionFile):
        evaluate_all(tmp_path)


def test_asset_with_thesis_damage_cannot_be_add_on_dip(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        "AAA",
        asset={"thesis_damage": True},
        decision={
            "current_decision": "ADD_ON_DIP",
            "dip_approved": True,
            "valuation_improved": True,
        },
    )

    result = evaluate_ticker(tmp_path, {"ticker": "AAA"})

    assert result.action == "RESEARCH_REQUIRED"
    assert "Thesis damage" in result.rationale


def test_unresolved_material_event_becomes_research_required(tmp_path: Path) -> None:
    _write_project(tmp_path, "AAA", decision={"current_decision": "HOLD"})
    _write_jsonl(
        tmp_path / "state" / "signal_events.jsonl",
        [
            {
                "ticker": "AAA",
                "event_class": "filing_update",
                "priority": "medium",
                "requires_codex": True,
                "resolved": False,
            }
        ],
    )

    result = evaluate_all(tmp_path)[0]

    assert result.action == "RESEARCH_REQUIRED"
    assert "Unresolved material event" in result.rationale


def test_resolved_material_event_no_longer_blocks_decision(tmp_path: Path) -> None:
    _write_project(tmp_path, "AAA", decision={"current_decision": "HOLD"})
    _write_jsonl(
        tmp_path / "state" / "signal_events.jsonl",
        [
            {
                "ticker": "AAA",
                "event_class": "filing_update",
                "priority": "medium",
                "requires_codex": True,
                "resolved": False,
                "raw_event": {
                    "ticker": "AAA",
                    "filing_type": "8-K",
                    "summary": "New customer contract.",
                },
            }
        ],
    )

    resolve_signal_events(tmp_path, ticker="AAA", reason="Reviewed; no thesis damage.")
    result = evaluate_all(tmp_path)[0]

    assert result.action == "HOLD"


def test_directly_resolved_material_event_no_longer_blocks_decision(tmp_path: Path) -> None:
    _write_project(tmp_path, "AAA", decision={"current_decision": "HOLD"})
    _write_jsonl(
        tmp_path / "state" / "signal_events.jsonl",
        [
            {
                "ticker": "AAA",
                "event_class": "filing_update",
                "priority": "medium",
                "requires_codex": True,
                "resolved": True,
            }
        ],
    )

    result = evaluate_all(tmp_path)[0]

    assert result.action == "HOLD"


def test_sa_full_exit_event_becomes_research_required(tmp_path: Path) -> None:
    _write_project(tmp_path, "AAA", decision={"current_decision": "HOLD"})
    _write_jsonl(
        tmp_path / "state" / "signal_events.jsonl",
        [
            {
                "ticker": "AAA",
                "event_class": "sa_exit_update",
                "priority": "high",
                "requires_codex": True,
                "resolved": False,
                "summary": "Future SA filing shows full exit.",
            }
        ],
    )

    result = evaluate_all(tmp_path)[0]

    assert result.action == "RESEARCH_REQUIRED"
    assert "fully exited" in result.rationale


def test_intact_thesis_and_approved_dip_becomes_add_on_dip(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        "AAA",
        asset={"thesis_damage": False},
        decision={
            "current_decision": "ADD_ON_DIP",
            "dip_approved": True,
            "valuation_improved": True,
            "one_line_rationale": "Approved dip with intact thesis and better valuation.",
        },
    )

    result = evaluate_ticker(tmp_path, {"ticker": "AAA"})

    assert result.action == "ADD_ON_DIP"


def test_signal_only_put_exposure_compiles_to_hold(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        "AAA",
        decision={"current_decision": "RESEARCH_REQUIRED"},
    )

    result = evaluate_ticker(
        tmp_path,
        {
            "ticker": "AAA",
            "trade_policy": "signal_only_no_puts_or_shorts",
            "instrument_role": "reported_put_signal",
        },
    )

    assert result.action == "HOLD"
    assert "Signal-only" in result.rationale


def test_sell_requires_named_broken_thesis(tmp_path: Path) -> None:
    _write_project(tmp_path, "AAA", decision={"current_decision": "SELL", "broken_thesis": ""})

    result = evaluate_ticker(tmp_path, {"ticker": "AAA"})

    assert result.action == "RESEARCH_REQUIRED"
    assert "SELL requires" in result.rationale


def test_buy_now_requires_full_decision_discipline(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        "AAA",
        decision={
            "current_decision": "BUY_NOW",
            "buy_thesis": "Clean bottleneck exposure.",
            "valuation_case": "Acceptable valuation.",
            "hedge_or_sizing": "Starter only.",
            "invalidation_trigger": "Named thesis break.",
        },
    )

    result = evaluate_ticker(tmp_path, {"ticker": "AAA"})

    assert result.action == "RESEARCH_REQUIRED"
    assert "anti_thesis" in result.rationale
    assert "evidence_quality" in result.rationale


def test_daily_decision_board_renders_all_tickers(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA", "BBB"])
    _write_decision(tmp_path, "AAA", {"current_decision": "HOLD"})
    _write_decision(tmp_path, "BBB", {"current_decision": "RESEARCH_REQUIRED"})

    report_path = write_daily_board(tmp_path)
    report = report_path.read_text(encoding="utf-8")
    index = (tmp_path / "research" / "decisions" / "index.md").read_text(encoding="utf-8")

    assert report_path.exists()
    assert "AAA" in report
    assert "BBB" in report
    assert "AAA" in index
    assert "BBB" in index


def test_daily_decision_board_renders_buy_now_size(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA"])
    _write_decision(
        tmp_path,
        "AAA",
        {
            "current_decision": "BUY_NOW",
            "buy_thesis": "Clean bottleneck exposure.",
            "anti_thesis": "Customer concentration.",
            "evidence_quality": "PRIMARY",
            "valuation_case": "Acceptable valuation.",
            "hedge_or_sizing": "Starter only.",
            "invalidation_trigger": "Named thesis break.",
            "approved_entry_zone": "BUY_NOW up to a 1.5% starter.",
        },
    )

    report_path = write_daily_board(tmp_path)
    report = report_path.read_text(encoding="utf-8")

    assert "| AAA |" in report
    assert "1.5%" in report


def test_daily_decision_board_ledger_is_idempotent(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA", "BBB"])
    _write_decision(tmp_path, "AAA", {"current_decision": "HOLD"})
    _write_decision(tmp_path, "BBB", {"current_decision": "HOLD"})

    write_daily_board(tmp_path)
    write_daily_board(tmp_path)

    ledger = (tmp_path / "state" / "decision_ledger.jsonl").read_text(encoding="utf-8")
    assert len(ledger.splitlines()) == 2


def test_action_board_surfaces_only_actionable_decisions(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA", "BBB"])
    _write_decision(tmp_path, "AAA", {"current_decision": "HOLD"})
    _write_decision(
        tmp_path,
        "BBB",
        {
            "current_decision": "BUY_NOW",
            "buy_thesis": "Clean bottleneck exposure.",
            "anti_thesis": "Customer concentration.",
            "evidence_quality": "PRIMARY",
            "valuation_case": "Acceptable valuation.",
            "hedge_or_sizing": "Starter only.",
            "invalidation_trigger": "Named thesis break.",
            "approved_entry_zone": "BUY_NOW up to a 1.5% starter.",
        },
    )

    report_path = write_action_board(tmp_path)
    report = report_path.read_text(encoding="utf-8")

    assert "| BBB | BUY_NOW |" in report
    assert "| AAA | HOLD |" not in report


def test_action_board_places_source_gaps_before_actions(tmp_path: Path) -> None:
    _write_watchlist(tmp_path, ["AAA"])
    _write_decision(
        tmp_path,
        "AAA",
        {
            "current_decision": "BUY_NOW",
            "buy_thesis": "Clean bottleneck exposure.",
            "anti_thesis": "Customer concentration.",
            "evidence_quality": "PRIMARY",
            "valuation_case": "Acceptable valuation.",
            "hedge_or_sizing": "Starter only.",
            "invalidation_trigger": "Named thesis break.",
            "approved_entry_zone": "BUY_NOW up to a 1.5% starter.",
        },
    )
    signals = tmp_path / "state" / "signal_events.jsonl"
    signals.parent.mkdir(parents=True, exist_ok=True)
    signals.write_text(
        json.dumps(
            {
                "detected_at": "2026-06-22T13:00:00-04:00",
                "ticker": "BCAP",
                "event_class": "filing_data_gap",
                "priority": "high",
                "requires_codex": True,
                "resolved": False,
                "source": "filing_ingest",
                "summary": "Filing source unavailable.",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report_path = write_action_board(tmp_path)
    report = report_path.read_text(encoding="utf-8")

    assert report.index("## Operational Source Gaps") < report.index("## Actions")
    assert "Do not treat action rows as fully cleared" in report
    assert "| AAA | BUY_NOW |" in report


def _write_project(
    root: Path,
    ticker: str,
    asset: dict[str, Any] | None = None,
    decision: dict[str, Any] | None = None,
) -> None:
    _write_watchlist(root, [ticker])
    _write_asset(root, ticker, asset or {})
    _write_decision(root, ticker, decision or {})


def _write_watchlist(root: Path, tickers: list[str]) -> None:
    config = root / "configs" / "watchlist.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    lines = ["watchlist:"]
    for ticker in tickers:
        lines.extend(
            [
                f"  - ticker: {ticker}",
                f"    name: {ticker} Inc.",
                "    sleeve: test_sleeve",
            ]
        )
    config.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_asset(root: Path, ticker: str, overrides: dict[str, Any]) -> None:
    metadata = {
        "ticker": ticker,
        "name": f"{ticker} Inc.",
        "sleeve": "test_sleeve",
        "current_decision": "RESEARCH_REQUIRED",
        "thesis_damage": False,
        "one_line_rationale": "Test rationale.",
    }
    metadata.update(overrides)
    _write_markdown(root / "research" / "assets" / f"{ticker}.md", metadata)


def _write_decision(root: Path, ticker: str, overrides: dict[str, Any]) -> None:
    metadata = {
        "ticker": ticker,
        "name": f"{ticker} Inc.",
        "sleeve": "test_sleeve",
        "current_decision": "RESEARCH_REQUIRED",
        "dip_approved": False,
        "valuation_improved": False,
        "thesis_damage": False,
        "broken_thesis": "",
        "one_line_rationale": "Test rationale.",
    }
    metadata.update(overrides)
    _write_markdown(root / "research" / "decisions" / f"{ticker}.md", metadata)


def _write_markdown(path: Path, metadata: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = "\n".join(f"{key}: {_yaml_value(value)}" for key, value in metadata.items())
    path.write_text(f"---\n{frontmatter}\n---\n# Test\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _yaml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)
