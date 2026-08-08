from __future__ import annotations

from pathlib import Path

import pytest

from bottleneck_capital.cli import main
from bottleneck_capital.decision_engine import evaluate_ticker
from bottleneck_capital.io import read_markdown_frontmatter
from bottleneck_capital.research_handoffs import (
    ResearchHandoffError,
    add_research_handoff,
    apply_research_handoff,
    backfill_research_handoffs,
    pending_research_handoffs,
)
from bottleneck_capital.validation import validate_project


def test_pending_handoff_blocks_capital_until_pm_applies_decision(tmp_path: Path) -> None:
    _write_project(tmp_path)
    memo = _write_memo(tmp_path, "2026-07-25-AAA-evidence.md")
    handoff = add_research_handoff(
        tmp_path,
        memo_path=memo,
        ticker="AAA",
        cause_status="BOUNDED",
        thesis_status="INTACT",
        valuation_status="UNREVIEWED",
        provisional_bias="HOLD",
        confidence=80,
        summary="Cause is bounded; valuation still requires PM review.",
    )

    result = evaluate_ticker(
        tmp_path,
        {"ticker": "AAA", "name": "AAA Inc.", "sleeve": "compute_infra"},
        [],
        research_handoffs=pending_research_handoffs(tmp_path),
    )

    assert result.action == "RESEARCH_REQUIRED"
    assert handoff["handoff_id"] in result.rationale
    with pytest.raises(ResearchHandoffError, match="predates handoff memo"):
        apply_research_handoff(
            tmp_path,
            handoff_id=handoff["handoff_id"],
            decision="HOLD",
            reason="Reaffirmed after review.",
        )

    _write_decision(tmp_path, "AAA", last_updated="2026-07-25", decision="HOLD")
    application = apply_research_handoff(
        tmp_path,
        handoff_id=handoff["handoff_id"],
        decision="HOLD",
        reason="Reaffirmed after reviewing the primary-source memo.",
    )

    assert application["decision"] == "HOLD"
    assert pending_research_handoffs(tmp_path) == []


def test_validation_detects_missing_pending_and_stale_handoffs(tmp_path: Path) -> None:
    _write_project(tmp_path)
    memo = _write_memo(tmp_path, "2026-07-25-AAA-evidence.md")

    missing = validate_project(tmp_path)
    assert any(issue.code == "RESEARCH_MEMO_HANDOFF_MISSING" for issue in missing)

    handoff = add_research_handoff(
        tmp_path,
        memo_path=memo,
        ticker="AAA",
        cause_status="BOUNDED",
        thesis_status="INTACT",
        valuation_status="UNREVIEWED",
        provisional_bias="HOLD",
        confidence=80,
        summary="No thesis break found.",
    )
    pending = validate_project(tmp_path, strict_live=True)
    assert any(issue.code == "PENDING_RESEARCH_HANDOFF" for issue in pending)
    assert any(issue.code == "RESEARCH_DECISION_STALE" for issue in pending)

    _write_decision(tmp_path, "AAA", last_updated="2026-07-25", decision="HOLD")
    apply_research_handoff(
        tmp_path,
        handoff_id=handoff["handoff_id"],
        decision="HOLD",
        reason="HOLD reaffirmed after PM review.",
    )
    applied = validate_project(tmp_path)
    assert not any(issue.code == "PENDING_RESEARCH_HANDOFF" for issue in applied)
    assert not any(issue.code == "RESEARCH_DECISION_STALE" for issue in applied)


def test_backfill_creates_one_pending_handoff_per_ticker(tmp_path: Path) -> None:
    _write_project(tmp_path, tickers=("AAA", "BBB"))
    _write_memo(tmp_path, "2026-07-25-AAA-BBB-shared-evidence.md")

    written = backfill_research_handoffs(tmp_path)
    repeated = backfill_research_handoffs(tmp_path)

    assert {record["ticker"] for record in written} == {"AAA", "BBB"}
    assert repeated == []
    assert len(pending_research_handoffs(tmp_path)) == 2


def test_handoff_dedupes_same_ticker_cause_day_without_new_primary_evidence(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    first_memo = _write_memo(tmp_path, "2026-07-25-AAA-dip-1.md")
    repeated_memo = _write_memo(tmp_path, "2026-07-25-AAA-dip-2.md")
    new_evidence_memo = _write_memo(tmp_path, "2026-07-25-AAA-dip-3.md")
    common = {
        "ticker": "AAA",
        "cause_status": "BOUNDED",
        "thesis_status": "INTACT",
        "valuation_status": "ATTRACTIVE",
        "provisional_bias": "ADD_ON_DIP_REVIEW",
        "confidence": 80,
        "summary": "The same bounded market-wide dip remains under review.",
        "cause_key": "market-wide-risk-off",
    }

    first = add_research_handoff(
        tmp_path,
        memo_path=first_memo,
        primary_evidence_key="release-1",
        **common,
    )
    repeated = add_research_handoff(
        tmp_path,
        memo_path=repeated_memo,
        primary_evidence_key="release-1",
        **common,
    )
    new_evidence = add_research_handoff(
        tmp_path,
        memo_path=new_evidence_memo,
        primary_evidence_key="filing-2",
        **common,
    )

    assert repeated["handoff_id"] == first["handoff_id"]
    assert new_evidence["handoff_id"] != first["handoff_id"]
    assert len(pending_research_handoffs(tmp_path)) == 2


def test_handoff_application_requires_persisted_matching_decision(tmp_path: Path) -> None:
    _write_project(tmp_path)
    memo = _write_memo(tmp_path, "2026-07-25-AAA-evidence.md")
    handoff = add_research_handoff(
        tmp_path,
        memo_path=memo,
        ticker="AAA",
        cause_status="BOUNDED",
        thesis_status="INTACT",
        valuation_status="ATTRACTIVE",
        provisional_bias="ADD_ON_DIP_REVIEW",
        confidence=75,
        summary="The cause is bounded, but PM must approve valuation and sizing.",
    )
    _write_decision(tmp_path, "AAA", last_updated="2026-07-25", decision="HOLD")

    with pytest.raises(ResearchHandoffError, match="not ADD_ON_DIP"):
        apply_research_handoff(
            tmp_path,
            handoff_id=handoff["handoff_id"],
            decision="ADD_ON_DIP",
            reason="Attempted application without persisting the decision.",
        )


def test_handoff_apply_cli_updates_asset_and_decision_before_application(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    memo = _write_memo(tmp_path, "2026-07-25-AAA-evidence.md")
    handoff = add_research_handoff(
        tmp_path,
        memo_path=memo,
        ticker="AAA",
        cause_status="BOUNDED",
        thesis_status="INTACT",
        valuation_status="UNREVIEWED",
        provisional_bias="HOLD",
        confidence=80,
        summary="No thesis break found.",
    )

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "handoff",
            "apply",
            "--handoff-id",
            handoff["handoff_id"],
            "--decision",
            "HOLD",
            "--reason",
            "HOLD reaffirmed after PM review.",
            "--next-trigger",
            "Next earnings release.",
            "--confidence",
            "82",
        ]
    )

    asset, _ = read_markdown_frontmatter(
        tmp_path / "research" / "assets" / "AAA.md"
    )
    decision, _ = read_markdown_frontmatter(
        tmp_path / "research" / "decisions" / "AAA.md"
    )
    assert exit_code == 0
    assert asset["current_decision"] == "HOLD"
    assert decision["current_decision"] == "HOLD"
    assert asset["last_primary_source_check"] == "2026-07-25"
    assert decision["next_trigger"] == "Next earnings release."
    assert decision["confidence_score"] == 82
    assert pending_research_handoffs(tmp_path) == []


def test_handoff_apply_blocks_new_buy_when_strict_live_is_not_clear(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    memo = _write_memo(tmp_path, "2026-07-25-AAA-evidence.md")
    handoff = add_research_handoff(
        tmp_path,
        memo_path=memo,
        ticker="AAA",
        cause_status="BOUNDED",
        thesis_status="INTACT",
        valuation_status="ATTRACTIVE",
        provisional_bias="BUY_REVIEW",
        confidence=80,
        summary="Valuation may be attractive, subject to strict-live clearance.",
    )

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "handoff",
            "apply",
            "--handoff-id",
            handoff["handoff_id"],
            "--decision",
            "BUY_NOW",
            "--reason",
            "Attempted buy while strict-live is blocked.",
        ]
    )

    assert exit_code == 1
    assert pending_research_handoffs(tmp_path)


def _write_project(root: Path, *, tickers: tuple[str, ...] = ("AAA",)) -> None:
    configs = root / "configs"
    configs.mkdir(parents=True)
    watchlist = ["watchlist:"]
    for ticker in tickers:
        watchlist.extend(
            [
                f"  - ticker: {ticker}",
                f"    name: {ticker} Inc.",
                "    sleeve: compute_infra",
                "    trade_policy: long_only_after_research",
            ]
        )
    (configs / "watchlist.yaml").write_text("\n".join(watchlist) + "\n", encoding="utf-8")
    (configs / "signal_thresholds.yaml").write_text(
        """sentinel:
  research:
    research_required_max_age_days: 5
""",
        encoding="utf-8",
    )
    for ticker in tickers:
        asset = root / "research" / "assets" / f"{ticker}.md"
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_text(
            f"""---
ticker: {ticker}
name: {ticker} Inc.
sleeve: compute_infra
current_decision: HOLD
last_updated: 2026-07-20
trade_policy: long_only_after_research
---
# {ticker}
""",
            encoding="utf-8",
        )
        _write_decision(root, ticker, last_updated="2026-07-20", decision="HOLD")
    state = root / "state"
    state.mkdir(exist_ok=True)
    (state / "signal_events.jsonl").write_text("", encoding="utf-8")


def _write_decision(
    root: Path,
    ticker: str,
    *,
    last_updated: str,
    decision: str,
) -> None:
    path = root / "research" / "decisions" / f"{ticker}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
ticker: {ticker}
name: {ticker} Inc.
sleeve: compute_infra
current_decision: {decision}
last_updated: {last_updated}
trade_policy: long_only_after_research
one_line_rationale: Test decision.
---
# {ticker}
""",
        encoding="utf-8",
    )


def _write_memo(root: Path, name: str) -> Path:
    path = root / "research" / "memos" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Evidence memo\n\nPrimary sources checked. Portfolio PM decision required.\n",
        encoding="utf-8",
    )
    return path
