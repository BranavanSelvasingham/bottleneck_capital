from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from bottleneck_capital.cli import main
from bottleneck_capital.io import read_jsonl
from bottleneck_capital.recommendations import (
    LEDGER,
    RecommendationError,
    latest_recommendations,
    record_outcome,
    record_recommendation,
    render_recommendations,
)
from bottleneck_capital.validation import _check_position_privacy

ISSUED = datetime(2026, 9, 28, 12, tzinfo=UTC)
FINISHED = datetime(2026, 10, 3, tzinfo=UTC)


def packet() -> dict:
    return {
        "ticker": "AAA",
        "action": "BUY_NOW",
        "reason": "VALUATION",
        "rationale": "Example normalized cash flow supports a starter.",
        "benchmark": "QQQ",
        "horizon_months": 36,
        "review_by": "2026-10-02T23:00:00+00:00",
        "reference_start_at": "2026-09-28T13:30:00+00:00",
        "confidence": {"thesis": "HIGH", "valuation": "MODERATE", "timing": "LOW"},
        "evidence": ["2026-09-28 primary results, https://example.com/results"],
        "alternatives": [
            {"ticker": "BBB", "case": "More expensive with similar growth."},
            {"ticker": "CASH", "case": "Avoids gaps but risks missing the catalyst."},
        ],
        "invalidation": "Customer cancellations or material per-share cash-flow erosion.",
        "starter_case": "Small starter captures upside; no automatic event gate.",
        "wait_case": "Waiting avoids execution risk but sacrifices possible appreciation.",
        "missed_entry_response": "Refresh assumptions at the review deadline; do not chase.",
        "entry": {"mode": "LIMIT", "limit_price": 100},
    }


def observation(call: dict) -> dict:
    return {
        "recommendation_id": call["id"],
        "window": "5_sessions",
        "start_at": "2026-09-28T13:30:00+00:00",
        "end_at": "2026-10-02T20:00:00+00:00",
        "session_dates": ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02"],
        "currency": "USD",
        "price_basis": "UNADJUSTED_PRICE",
        "prices": [
            {"ticker": "AAA", "start": 100, "end": 120, "source": "dated provider bars"},
            {"ticker": "QQQ", "start": 100, "end": 110, "source": "same-date provider bars"},
        ],
        "entry_observation": "UNVERIFIED",
        "notes": "Reference performance, not a broker fill.",
    }


def test_record_freezes_time_and_preserves_linked_revisions(tmp_path: Path) -> None:
    first = record_recommendation(tmp_path, packet(), now=ISSUED)
    revised = {
        **packet(),
        "supersedes": first["id"],
        "change_kind": "VALUATION_CHANGE",
        "change_reason": "Updated valuation after the new financing terms.",
        "entry": {"mode": "LIMIT", "limit_price": 90},
    }
    second = record_recommendation(tmp_path, revised, now=ISSUED)
    assert first["recorded_at"] == ISSUED.isoformat()
    assert read_jsonl(tmp_path / LEDGER)[0]["entry"]["limit_price"] == 100
    assert latest_recommendations(tmp_path) == [second]


def test_revision_cannot_silently_replace_or_claim_unchanged_advice(tmp_path: Path) -> None:
    first = record_recommendation(tmp_path, packet(), now=ISSUED)
    with pytest.raises(RecommendationError, match="supersedes"):
        record_recommendation(tmp_path, packet(), now=ISSUED)
    changed = {
        **packet(),
        "supersedes": first["id"],
        "change_kind": "REAFFIRMATION",
        "change_reason": "Same evidence.",
        "entry": {"mode": "LIMIT", "limit_price": 90},
    }
    with pytest.raises(RecommendationError, match="not a reaffirmation"):
        record_recommendation(tmp_path, changed, now=ISSUED)
    changed["change_kind"] = "NEW_EVIDENCE"
    with pytest.raises(RecommendationError, match="new dated evidence"):
        record_recommendation(tmp_path, changed, now=ISSUED)


@pytest.mark.parametrize(
    "field,value",
    [
        ("quantity", 10),
        ("account", "private"),
        ("current_position_weight_pct", 50),
        ("recorded_at", "2026-01-01T00:00:00+00:00"),
        ("reference_start_at", "2026-09-28T11:00:00+00:00"),
        ("reference_start_at", "2026-10-28T13:30:00+00:00"),
        ("review_by", "2026-01-01T00:00:00+00:00"),
        ("action", []),
        ("action", "HOLD "),
        ("horizon_months", True),
        ("alternatives", []),
    ],
)
def test_rejects_private_fields_backdating_and_malformed_packets(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    with pytest.raises(RecommendationError):
        record_recommendation(tmp_path, {**packet(), field: value}, now=ISSUED)
    assert not (tmp_path / LEDGER).exists()


def test_hold_does_not_implicitly_clear_order(tmp_path: Path) -> None:
    with pytest.raises(RecommendationError, match="silently authorize"):
        record_recommendation(tmp_path, {**packet(), "action": "HOLD"}, now=ISSUED)


def test_score_uses_matching_intervals_without_claiming_fills(tmp_path: Path) -> None:
    call = record_recommendation(tmp_path, packet(), now=ISSUED)
    score = record_outcome(tmp_path, observation(call), now=FINISHED)
    assert score["returns_pct"]["AAA"] == pytest.approx(20)
    assert score["excess_return_pp"] == pytest.approx(10)
    assert score["measurement"] == "REFERENCE_PRICE_NOT_EXECUTION"
    assert score["entry_observation"] == "UNVERIFIED"


def test_outcome_cannot_choose_a_later_reference_start(tmp_path: Path) -> None:
    call = record_recommendation(tmp_path, packet(), now=ISSUED)
    data = observation(call)
    data["start_at"] = "2026-09-28T15:00:00+00:00"
    with pytest.raises(RecommendationError, match="frozen reference start"):
        record_outcome(tmp_path, data, now=FINISHED)


def test_legacy_call_is_preserved_without_backdated_score(tmp_path: Path) -> None:
    call = record_recommendation(tmp_path, packet(), now=ISSUED)
    legacy = {key: value for key, value in call.items() if key != "reference_start_at"}
    legacy["schema_version"] = 1
    (tmp_path / LEDGER).write_text(json.dumps(legacy) + "\n", encoding="utf-8")
    with pytest.raises(RecommendationError, match="lacks a frozen reference start"):
        record_outcome(tmp_path, observation(call), now=FINISHED)
    assert read_jsonl(tmp_path / LEDGER) == [legacy]
    assert "UNSCORABLE" in render_recommendations(tmp_path, now=FINISHED)


def test_rotation_compares_sale_against_destination_not_only_winner(tmp_path: Path) -> None:
    call = record_recommendation(
        tmp_path,
        {
            **packet(),
            "action": "SELL",
            "reason": "OPPORTUNITY_COST",
            "entry": {"mode": "NEXT_OPEN"},
            "rotation_ticker": "BBB",
            "rotation_case": "Destination expected to offer better returns at equal risk.",
        },
        now=ISSUED,
    )
    data = observation(call)
    with pytest.raises(RecommendationError, match="counterparty"):
        record_outcome(tmp_path, data, now=FINISHED)
    data["prices"].append({"ticker": "BBB", "start": 100, "end": 90, "source": "same-date bars"})
    score = record_outcome(tmp_path, data, now=FINISHED)
    assert score["rotation_advantage_pp"] == pytest.approx(-30)


def test_buy_funded_by_sale_scores_both_sides(tmp_path: Path) -> None:
    call = record_recommendation(
        tmp_path,
        {
            **packet(),
            "rotation_ticker": "BBB",
            "rotation_case": "Better forward return than source.",
        },
        now=ISSUED,
    )
    data = observation(call)
    data["prices"].append({"ticker": "BBB", "start": 100, "end": 150, "source": "same-date bars"})
    assert record_outcome(tmp_path, data, now=FINISHED)["rotation_advantage_pp"] == pytest.approx(
        -30
    )


def test_outcome_rejects_lookahead_and_wrong_session_count(tmp_path: Path) -> None:
    call = record_recommendation(tmp_path, packet(), now=ISSUED)
    data = observation(call)
    data["start_at"] = "2026-09-28T11:00:00+00:00"
    with pytest.raises(RecommendationError, match="before the recommendation"):
        record_outcome(tmp_path, data, now=FINISHED)
    data = observation(call)
    data["session_dates"].pop(1)
    with pytest.raises(RecommendationError, match="number of trading sessions"):
        record_outcome(tmp_path, data, now=FINISHED)
    data = observation(call)
    data["end_at"] = "2026-10-03T20:00:00+00:00"
    with pytest.raises(RecommendationError, match="completed timestamps"):
        record_outcome(tmp_path, data, now=FINISHED)


@pytest.mark.parametrize("price", [0, -1, float("nan"), float("inf"), True])
def test_invalid_price_cannot_generate_score(tmp_path: Path, price: float) -> None:
    call = record_recommendation(tmp_path, packet(), now=ISSUED)
    data = observation(call)
    data["prices"][0]["start"] = price
    with pytest.raises(RecommendationError, match="finite positive"):
        record_outcome(tmp_path, data, now=FINISHED)


def test_touch_needs_post_call_pre_expiry_sourced_price(tmp_path: Path) -> None:
    call = record_recommendation(tmp_path, packet(), now=ISSUED)
    data = observation(call)
    data["entry_observation"] = "PRICE_TOUCHED"
    with pytest.raises(RecommendationError, match="Entry evidence"):
        record_outcome(tmp_path, data, now=FINISHED)
    data["entry_evidence"] = {
        "observed_at": "2026-09-25T14:00:00+00:00",
        "price": 99,
        "source": "bar",
    }
    with pytest.raises(RecommendationError, match="after the call"):
        record_outcome(tmp_path, data, now=FINISHED)
    data["entry_evidence"].update(observed_at="2026-09-28T14:00:00+00:00", price=101)
    with pytest.raises(RecommendationError, match="did not reach"):
        record_outcome(tmp_path, data, now=FINISHED)
    data["entry_evidence"]["price"] = 99
    score = record_outcome(tmp_path, data, now=FINISHED)
    assert score["measurement"] == "REFERENCE_PRICE_NOT_EXECUTION"


def test_no_order_and_unfilled_are_not_portfolio_wins(tmp_path: Path) -> None:
    call = record_recommendation(
        tmp_path, {**packet(), "action": "HOLD", "entry": {"mode": "NO_ORDER"}}, now=ISSUED
    )
    data = observation(call)
    with pytest.raises(RecommendationError, match="no-order"):
        record_outcome(tmp_path, data, now=FINISHED)
    data["entry_observation"] = "NO_ORDER"
    score = record_outcome(tmp_path, data, now=FINISHED)
    assert score["returns_pct"]["AAA"] > 0
    assert score["measurement"] == "REFERENCE_PRICE_NOT_EXECUTION"
    assert "NO_ORDER" in render_recommendations(tmp_path, now=FINISHED)


def test_score_corrections_are_append_only(tmp_path: Path) -> None:
    call = record_recommendation(tmp_path, packet(), now=ISSUED)
    data = observation(call)
    old = record_outcome(tmp_path, data, now=FINISHED)
    with pytest.raises(RecommendationError, match="previous outcome"):
        record_outcome(tmp_path, data, now=FINISHED)
    corrected = deepcopy(data)
    corrected.update(supersedes=old["id"], correction_reason="Provider corrected endpoint.")
    corrected["prices"][0]["end"] = 115
    new = record_outcome(tmp_path, corrected, now=FINISHED)
    rows = read_jsonl(tmp_path / LEDGER)
    assert len(rows) == 3
    assert rows[1]["returns_pct"]["AAA"] == pytest.approx(20)
    assert new["returns_pct"]["AAA"] == pytest.approx(15)


def test_review_shows_superseded_unscored_calls(tmp_path: Path) -> None:
    first = record_recommendation(tmp_path, packet(), now=ISSUED)
    next_call = {
        **packet(),
        "supersedes": first["id"],
        "change_kind": "REAFFIRMATION",
        "change_reason": "Unchanged after the event.",
        "review_by": "2026-10-10T20:00:00+00:00",
        "reference_start_at": "2026-10-05T13:30:00+00:00",
    }
    second = record_recommendation(tmp_path, next_call, now=FINISHED)
    output = render_recommendations(tmp_path, now=FINISHED)
    assert first["id"] in output
    assert second["id"] in output


def test_one_score_does_not_hide_later_checkpoints(tmp_path: Path) -> None:
    call = record_recommendation(tmp_path, packet(), now=ISSUED)
    record_outcome(tmp_path, observation(call), now=FINISHED)
    pending = render_recommendations(tmp_path, now=FINISHED).split("## Pending Checkpoints")[1]
    assert call["id"] in pending
    assert "21_sessions" in pending
    assert "5_sessions" not in pending


def test_cli_records_only_private_journal(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    data = packet()
    data["review_by"] = "2099-01-01T00:00:00+00:00"
    data["reference_start_at"] = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps(data), encoding="utf-8")
    assert main(["--root", str(tmp_path), "recommendation", "record", "--input", "input.json"]) == 0
    assert "Recorded recommendation:" in capsys.readouterr().out
    assert main(["--root", str(tmp_path), "recommendation", "review"]) == 0
    assert "AAA BUY_NOW" in capsys.readouterr().out
    assert (tmp_path / LEDGER).exists()
    assert not (tmp_path / "state/decision_ledger.jsonl").exists()
    assert not (tmp_path / "state/run_ledger.jsonl").exists()


@pytest.mark.parametrize(
    "private_path",
    ["state/local_recommendations.jsonl", "reports/local_recommendations/example.json"],
)
def test_privacy_gate_rejects_force_tracked_journal_data(tmp_path: Path, private_path: str) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    ignore = (Path(__file__).parents[1] / ".gitignore").read_text(encoding="utf-8")
    (tmp_path / ".gitignore").write_text(ignore, encoding="utf-8")
    target = tmp_path / private_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}\n", encoding="utf-8")
    assert (
        subprocess.run(
            ["git", "check-ignore", "-q", private_path], cwd=tmp_path, check=False
        ).returncode
        == 0
    )
    issues = []
    _check_position_privacy(tmp_path, issues)
    assert not issues
    subprocess.run(["git", "add", "-f", private_path], cwd=tmp_path, check=True)
    _check_position_privacy(tmp_path, issues)
    assert any(issue.code == "POSITION_PRIVACY_TRACKED_FILE" for issue in issues)
