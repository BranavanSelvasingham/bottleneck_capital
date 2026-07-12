from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bottleneck_capital.cli import main
from bottleneck_capital.io import read_jsonl
from bottleneck_capital.runtime import run_lock
from bottleneck_capital.signal_events import active_signal_events


def test_ingest_market_cli_records_run_ledger(tmp_path: Path) -> None:
    _write_project(tmp_path)
    input_path = tmp_path / "market.json"
    input_path.write_text(
        json.dumps(
            {
                "snapshots": [
                    {
                        "ticker": "AAA",
                        "price": 90,
                        "previous_close": 100,
                        "open": 99,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "ingest",
            "market",
            "--input",
            str(input_path),
        ]
    )

    ledger = read_jsonl(tmp_path / "state" / "run_ledger.jsonl")
    assert exit_code == 0
    assert ledger[-1]["process"] == "ingest-market"
    assert ledger[-1]["status"] == "success"
    assert ledger[-1]["outputs"]


def test_live_check_cli_runs_market_sentinel_action_board_and_validation(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    positions = tmp_path / "state" / "local_positions.yaml"
    positions.parent.mkdir(parents=True, exist_ok=True)
    positions.write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 80
    current_price: 0
    currency: USD
""",
        encoding="utf-8",
    )
    input_path = tmp_path / "market.json"
    input_path.write_text(
        json.dumps(
            {
                "snapshots": [
                    {
                        "ticker": "AAA",
                        "price": 90,
                        "previous_close": 100,
                        "open": 99,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "live-check",
            "--market-input",
            str(input_path),
        ]
    )

    ledger = read_jsonl(tmp_path / "state" / "run_ledger.jsonl")
    refreshed_positions = positions.read_text(encoding="utf-8")
    action_board = next((tmp_path / "reports" / "action_boards").glob("*.md"))
    assert exit_code == 0
    assert (tmp_path / "reports" / "action_boards").exists()
    assert "## Opportunity Ranking" in action_board.read_text(encoding="utf-8")
    assert ledger[-1]["process"] == "live-check"
    assert ledger[-1]["status"] == "success"
    assert ledger[-1]["warnings"]
    assert "current_price: 90" in refreshed_positions


def test_live_check_cli_records_strict_validation_failure(tmp_path: Path) -> None:
    _write_project(tmp_path)
    input_path = tmp_path / "market.json"
    input_path.write_text(
        json.dumps(
            {
                "snapshots": [
                    {
                        "ticker": "AAA",
                        "price": 90,
                        "previous_close": 100,
                        "open": 99,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "live-check",
            "--market-input",
            str(input_path),
            "--strict-validate",
        ]
    )

    ledger = read_jsonl(tmp_path / "state" / "run_ledger.jsonl")
    assert exit_code == 1
    assert ledger[-1]["process"] == "live-check"
    assert ledger[-1]["status"] == "error"
    assert ledger[-1]["error"] == "validation errors present"


def test_live_check_cli_writes_action_board_when_market_ingest_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    monkeypatch.delenv("APCA_API_KEY_ID", raising=False)
    monkeypatch.delenv("APCA_API_SECRET_KEY", raising=False)
    monkeypatch.delenv("BCAP_SEC_USER_AGENT", raising=False)

    exit_code = main(["--root", str(tmp_path), "live-check", "--market-provider", "alpaca"])

    ledger = read_jsonl(tmp_path / "state" / "run_ledger.jsonl")
    signals = read_jsonl(tmp_path / "state" / "signal_events.jsonl")
    assert exit_code == 1
    assert (tmp_path / "reports" / "action_boards").exists()
    assert ledger[-1]["process"] == "live-check"
    assert ledger[-1]["status"] == "error"
    assert "market ingest failed" in ledger[-1]["error"]
    assert ledger[-1]["outputs"]
    assert any(record["event_class"] == "filing_data_gap" for record in signals)


def test_live_check_cli_resolves_recovered_filing_gap(tmp_path: Path) -> None:
    _write_project(tmp_path)
    market_input = tmp_path / "market.json"
    market_input.write_text(
        json.dumps(
            {
                "snapshots": [
                    {
                        "ticker": "AAA",
                        "price": 90,
                        "previous_close": 100,
                        "open": 99,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    company_tickers = tmp_path / "company_tickers.json"
    company_tickers.write_text(
        json.dumps({"0": {"cik_str": 123456, "ticker": "AAA", "title": "AAA Inc."}}),
        encoding="utf-8",
    )
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()
    (submissions_dir / "CIK0000123456.json").write_text(
        json.dumps(
            {
                "filings": {
                    "recent": {
                        "form": ["8-K"],
                        "accessionNumber": ["0000123456-26-000001"],
                        "filingDate": [date.today().isoformat()],
                        "acceptanceDateTime": ["20260622093000"],
                        "primaryDocument": ["form8k.htm"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    state = tmp_path / "state"
    state.mkdir()
    (state / "signal_events.jsonl").write_text(
        json.dumps(
            {
                "event_id": "gap1",
                "detected_at": "2026-06-22T09:00:00-04:00",
                "ticker": "BCAP",
                "event_class": "filing_data_gap",
                "priority": "high",
                "requires_codex": True,
                "resolved": False,
                "source": "filing_ingest",
                "summary": "Filing coverage blind.",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (state / "latest_manual_events.jsonl").write_text(
        json.dumps(
            {
                "ticker": "BCAP",
                "event_type": "filing_data_gap",
                "event_class": "filing_data_gap",
                "dedupe_key": "filing_data_gap:daily",
                "summary": "Filing coverage blind.",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "live-check",
            "--market-input",
            str(market_input),
            "--company-tickers-input",
            str(company_tickers),
            "--submissions-dir",
            str(submissions_dir),
        ]
    )

    signals = read_jsonl(state / "signal_events.jsonl")
    manual_events = read_jsonl(state / "latest_manual_events.jsonl")
    active = active_signal_events(signals)
    assert exit_code == 0
    assert any(record.get("resolved_event_id") == "gap1" for record in signals)
    assert not [record for record in active if record.get("event_class") == "filing_data_gap"]
    assert manual_events == []


def test_scheduled_write_lock_blocks_overlapping_write_commands(tmp_path: Path) -> None:
    _write_project(tmp_path)
    input_path = tmp_path / "market.json"
    input_path.write_text(
        json.dumps(
            {
                "snapshots": [
                    {
                        "ticker": "AAA",
                        "price": 90,
                        "previous_close": 100,
                        "open": 99,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with run_lock(tmp_path, "scheduled-write"):
        exit_code = main(
            [
                "--root",
                str(tmp_path),
                "ingest",
                "market",
                "--input",
                str(input_path),
            ]
        )

    ledger = read_jsonl(tmp_path / "state" / "run_ledger.jsonl")
    assert exit_code == 1
    assert ledger[-1]["process"] == "ingest-market"
    assert ledger[-1]["status"] == "conflict"


def test_live_readiness_cli_writes_recovery_report(tmp_path: Path, monkeypatch) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    state = tmp_path / "state"
    state.mkdir()
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": "2026-06-22T10:00:00-04:00",
                    "source": "market_yahoo",
                    "item_count": 0,
                    "expected_item_count": 1,
                    "missing_tickers": ["AAA"],
                }
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path), "live-readiness"])

    report = _live_readiness_report(tmp_path)
    text = report.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "Status: NOT_READY" in text
    assert "## Strict-Live Warnings" in text
    assert "LOCAL_POSITIONS_MISSING" in text
    assert "Resolve market coverage for AAA" in text
    assert "Restore filing coverage" in text


def test_live_readiness_marks_active_high_signals_not_ready(
    tmp_path: Path, monkeypatch
) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    state = tmp_path / "state"
    state.mkdir()
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "local_positions.yaml").write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 80
    current_price: 90
    currency: USD
""",
        encoding="utf-8",
    )
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": _fresh_timestamp(),
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                    "missing_tickers": [],
                },
                "filings": {
                    "last_success_at": _fresh_timestamp(),
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                    "missing_tickers": [],
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "signal_events.jsonl").write_text(
        json.dumps(
            {
                "detected_at": "2026-06-22T13:00:00-04:00",
                "ticker": "AAA",
                "event_class": "catalyst_update",
                "priority": "high",
                "requires_codex": True,
                "resolved": False,
                "source": "filing_ingest",
                "summary": "Material filing needs review.",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path), "live-readiness"])

    report = _live_readiness_report(tmp_path)
    text = report.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "Status: NOT_READY" in text
    assert "## Strict-Live Errors\n\n- None" in text
    assert "`AAA` `catalyst_update`" in text


def test_live_readiness_blocks_missing_position_cost_basis(
    tmp_path: Path, monkeypatch
) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    state = tmp_path / "state"
    state.mkdir()
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "local_positions.yaml").write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 0
    current_price: 90
    currency: USD
""",
        encoding="utf-8",
    )
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": _fresh_timestamp(),
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                    "missing_tickers": [],
                },
                "filings": {
                    "last_success_at": _fresh_timestamp(),
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                    "missing_tickers": [],
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path), "live-readiness"])

    report = _live_readiness_report(tmp_path)
    text = report.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "Status: NOT_READY" in text
    assert "LOCAL_POSITION_COST_BASIS_MISSING" in text


def test_resume_check_exits_nonzero_when_not_ready(tmp_path: Path, monkeypatch) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    state = tmp_path / "state"
    state.mkdir()
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "local_positions.yaml").write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 0
    current_price: 90
    currency: USD
""",
        encoding="utf-8",
    )
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": _fresh_timestamp(),
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                    "missing_tickers": [],
                },
                "filings": {
                    "last_success_at": _fresh_timestamp(),
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                    "missing_tickers": [],
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path), "resume-check"])

    report = _live_readiness_report(tmp_path)
    assert exit_code == 1
    assert "Status: NOT_READY" in report.read_text(encoding="utf-8")


def test_resume_check_exits_zero_when_ready(tmp_path: Path, monkeypatch) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    state = tmp_path / "state"
    state.mkdir()
    (state / "latest_events.jsonl").write_text("", encoding="utf-8")
    (state / "local_positions.yaml").write_text(
        """positions:
  - ticker: AAA
    quantity: 1
    average_cost: 80
    current_price: 90
    currency: USD
""",
        encoding="utf-8",
    )
    (state / "ingest_status.json").write_text(
        json.dumps(
            {
                "market": {
                    "last_success_at": _fresh_timestamp(),
                    "source": "market_yahoo",
                    "item_count": 1,
                    "expected_item_count": 1,
                    "missing_tickers": [],
                },
                "filings": {
                    "last_success_at": _fresh_timestamp(),
                    "source": "sec_submissions",
                    "item_count": 1,
                    "expected_item_count": 1,
                    "missing_tickers": [],
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path), "resume-check"])

    report = _live_readiness_report(tmp_path)
    assert exit_code == 0
    assert "Status: READY" in report.read_text(encoding="utf-8")


def test_positions_set_cli_updates_local_position(tmp_path: Path) -> None:
    _write_project(tmp_path)
    positions = tmp_path / "state" / "local_positions.yaml"
    positions.parent.mkdir(parents=True, exist_ok=True)
    positions.write_text("positions:\n  - ticker: AAA\n    quantity: 0\n", encoding="utf-8")

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "positions-set",
            "--ticker",
            "AAA",
            "--quantity",
            "2",
            "--average-cost",
            "80.5",
            "--currency",
            "usd",
            "--notes",
            "",
        ]
    )

    text = positions.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "ticker: AAA" in text
    assert "quantity: 2.0" in text
    assert "average_cost: 80.5" in text
    assert "currency: USD" in text
    assert 'notes: ""' in text


def _live_readiness_report(root: Path) -> Path:
    today = datetime.now(ZoneInfo("America/Toronto")).date().isoformat()
    return root / "reports" / "live_readiness" / f"{today}.md"


def _write_project(root: Path) -> None:
    configs = root / "configs"
    configs.mkdir(parents=True, exist_ok=True)
    (configs / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
""",
        encoding="utf-8",
    )
    (configs / "signal_thresholds.yaml").write_text(
        """sentinel:
  timezone: America/Toronto
  freshness:
    market_data_max_age_minutes: 20
    filing_data_max_age_minutes: 240
  price_triggers:
    intraday_drop_pct: 5
    one_day_drop_pct: 7
    gap_down_pct: 4
""",
        encoding="utf-8",
    )
    (configs / "agent_roster.yaml").write_text(
        "ticker_owners:\n  - owner_agent: asset_analyst.AAA\n",
        encoding="utf-8",
    )
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


def _fresh_timestamp() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
