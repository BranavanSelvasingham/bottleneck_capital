from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import bottleneck_capital.live_sources as live_sources
from bottleneck_capital.validation import has_errors, validate_project


def test_validate_project_warns_when_only_mock_events_exist(tmp_path: Path) -> None:
    _write_minimal_project(tmp_path)
    mock = tmp_path / "mock" / "latest_events.jsonl"
    mock.parent.mkdir(parents=True, exist_ok=True)
    mock.write_text('{"ticker":"AAA","summary":"mock"}\n', encoding="utf-8")

    issues = validate_project(tmp_path)

    assert not has_errors(issues)
    assert any(issue.code == "MOCK_EVENT_FALLBACK_ONLY" for issue in issues)


def test_validate_project_errors_when_private_paths_are_not_ignored(tmp_path: Path) -> None:
    _write_minimal_project(tmp_path)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text(
        "state/local_positions.yaml\nreports/local_exposure.md\n",
        encoding="utf-8",
    )

    issues = validate_project(tmp_path)

    assert any(issue.code == "POSITION_PRIVACY_IGNORE_GAP" for issue in issues)


def test_validate_project_errors_on_committed_current_position_weight(tmp_path: Path) -> None:
    _write_minimal_project(tmp_path)
    (tmp_path / ".gitignore").write_text(
        "state/local_positions.yaml\n"
        "reports/local_exposure.md\n"
        "state/signal_events.jsonl\n"
        "reports/action_boards/\n"
        "reports/daily_decision_boards/\n"
        "reports/sunday_preps/\n",
        encoding="utf-8",
    )
    asset = tmp_path / "research" / "assets" / "AAA.md"
    asset.write_text(
        "---\nticker: AAA\ncurrent_decision: HOLD\ncurrent_position_weight_pct: 4.2\n---\n",
        encoding="utf-8",
    )

    issues = validate_project(tmp_path)

    assert any(issue.code == "POSITION_PRIVACY_TRACKED_WEIGHT" for issue in issues)


def test_validate_project_warns_on_overdue_research_block(tmp_path: Path) -> None:
    _write_minimal_project(tmp_path)
    for kind in ("assets", "decisions"):
        path = tmp_path / "research" / kind / "AAA.md"
        path.write_text(
            """---
ticker: AAA
name: AAA Inc.
sleeve: compute_infra
current_decision: RESEARCH_REQUIRED
last_primary_source_check: 2020-01-01
one_line_rationale: Earnings review unresolved.
---
# AAA
""",
            encoding="utf-8",
        )

    issues = validate_project(tmp_path)

    overdue = [issue for issue in issues if issue.code == "OVERDUE_RESEARCH_BLOCK"]
    assert overdue
    assert overdue[0].severity == "WARN"


def test_validate_project_strict_live_errors_without_live_ingest(tmp_path: Path) -> None:
    _write_minimal_project(tmp_path)
    mock = tmp_path / "mock" / "latest_events.jsonl"
    mock.parent.mkdir(parents=True, exist_ok=True)
    mock.write_text('{"ticker":"AAA","summary":"mock"}\n', encoding="utf-8")

    issues = validate_project(tmp_path, strict_live=True)

    assert has_errors(issues)
    assert any(
        issue.code in {"MOCK_EVENT_FALLBACK_ONLY", "INGEST_STATUS_MISSING"}
        and issue.severity == "ERROR"
        for issue in issues
    )


def test_validate_project_strict_live_rejects_fixture_ingest_sources(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.setenv("APCA_API_KEY_ID", "key")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "secret")
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_input_file",
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_input_file",
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")

    issues = validate_project(tmp_path, strict_live=True)

    assert has_errors(issues)
    assert any(issue.code == "MARKET_INGEST_NOT_LIVE" for issue in issues)
    assert any(issue.code == "FILINGS_INGEST_NOT_LIVE" for issue in issues)


def test_validate_project_strict_live_warns_for_non_actionable_unheld_market_gap(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 2,
                    "missing_tickers": ["BBB"],
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")

    issues = validate_project(tmp_path, strict_live=True)

    partial = [issue for issue in issues if issue.code == "MARKET_INGEST_PARTIAL"]
    assert partial
    assert partial[0].severity == "WARN"


def test_validate_project_strict_live_errors_for_held_market_gap(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_yahoo",
                    "item_count": 0,
                    "expected_item_count": 1,
                    "missing_tickers": ["AAA"],
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "local_positions.yaml").write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 10
    current_price: 10
    currency: USD
""",
        encoding="utf-8",
    )

    issues = validate_project(tmp_path, strict_live=True)

    partial = [issue for issue in issues if issue.code == "MARKET_INGEST_PARTIAL"]
    assert has_errors(issues)
    assert partial
    assert partial[0].severity == "ERROR"


def test_validate_project_strict_live_errors_for_research_required_market_gap(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    decision = tmp_path / "research" / "decisions" / "AAA.md"
    decision.write_text(
        """---
ticker: AAA
name: AAA Inc.
sleeve: compute_infra
current_decision: RESEARCH_REQUIRED
---
# AAA
""",
        encoding="utf-8",
    )
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_yahoo",
                    "item_count": 0,
                    "expected_item_count": 1,
                    "missing_tickers": ["AAA"],
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")

    issues = validate_project(tmp_path, strict_live=True)

    partial = [issue for issue in issues if issue.code == "MARKET_INGEST_PARTIAL"]
    assert has_errors(issues)
    assert partial
    assert partial[0].severity == "ERROR"


def test_validate_project_strict_live_errors_for_held_filing_gap(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_browse_atom",
                    "item_count": 0,
                    "expected_item_count": 1,
                    "missing_tickers": ["AAA"],
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "local_positions.yaml").write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 10
    current_price: 10
    currency: USD
""",
        encoding="utf-8",
    )

    issues = validate_project(tmp_path, strict_live=True)

    partial = [issue for issue in issues if issue.code == "FILINGS_INGEST_PARTIAL"]
    assert has_errors(issues)
    assert partial
    assert partial[0].severity == "ERROR"


def test_validate_project_strict_live_errors_without_local_positions(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")

    issues = validate_project(tmp_path, strict_live=True)

    missing = [issue for issue in issues if issue.code == "LOCAL_POSITIONS_MISSING"]
    assert has_errors(issues)
    assert missing
    assert missing[0].severity == "ERROR"


def test_validate_project_strict_live_errors_for_placeholder_cost_basis(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "local_positions.yaml").write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 0
    current_price: 10
    currency: USD
    notes: pending exact fill
""",
        encoding="utf-8",
    )

    issues = validate_project(tmp_path, strict_live=True)

    missing_cost = [issue for issue in issues if issue.code == "LOCAL_POSITION_COST_BASIS_MISSING"]
    assert has_errors(issues)
    assert missing_cost
    assert missing_cost[0].severity == "ERROR"


def test_validate_project_strict_live_errors_for_position_currency_mismatch(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "market_snapshots.jsonl").write_text(
        '{"ticker":"AAA","price":10,"raw_snapshot":{"currency":"USD"}}\n',
        encoding="utf-8",
    )
    (state / "local_positions.yaml").write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 8
    current_price: 10
    currency: CAD
""",
        encoding="utf-8",
    )

    issues = validate_project(tmp_path, strict_live=True)

    mismatch = [issue for issue in issues if issue.code == "LOCAL_POSITION_CURRENCY_MISMATCH"]
    assert has_errors(issues)
    assert mismatch
    assert mismatch[0].severity == "ERROR"


def test_validate_project_strict_live_accepts_git_email_for_sec_user_agent(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_project(tmp_path)
    monkeypatch.delenv("BCAP_SEC_USER_AGENT", raising=False)
    monkeypatch.setattr(live_sources, "_git_config_email", lambda root: "owner@example.com")
    now = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    state = tmp_path / "state"
    state.mkdir()
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": now,
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
                "filings": {
                    "last_success_at": now,
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")

    issues = validate_project(tmp_path, strict_live=True)

    assert not any(issue.code == "SEC_USER_AGENT_MISSING" for issue in issues)


def _write_minimal_project(root: Path) -> None:
    (root / ".gitignore").write_text(
        "state/local_positions.yaml\n"
        "reports/local_exposure.md\n"
        "state/signal_events.jsonl\n"
        "reports/action_boards/\n"
        "reports/daily_decision_boards/\n"
        "reports/sunday_preps/\n",
        encoding="utf-8",
    )
    watchlist = root / "configs" / "watchlist.yaml"
    watchlist.parent.mkdir(parents=True, exist_ok=True)
    watchlist.write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
""",
        encoding="utf-8",
    )
    thresholds = root / "configs" / "signal_thresholds.yaml"
    thresholds.write_text(
        """sentinel:
  freshness:
    market_data_max_age_minutes: 20
    filing_data_max_age_minutes: 240
""",
        encoding="utf-8",
    )
    roster = root / "configs" / "agent_roster.yaml"
    roster.write_text("ticker_owners:\n  - owner_agent: asset_analyst.AAA\n", encoding="utf-8")
    packet = root / "research" / "agent_packets" / "wave_1" / "AAA.md"
    packet.parent.mkdir(parents=True, exist_ok=True)
    packet.write_text("# AAA\n", encoding="utf-8")
    for kind in ("assets", "decisions"):
        path = root / "research" / kind / "AAA.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            """---
ticker: AAA
name: AAA Inc.
sleeve: compute_infra
current_decision: HOLD
---
# AAA
""",
            encoding="utf-8",
        )
