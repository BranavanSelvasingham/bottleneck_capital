from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from bottleneck_capital.live_check import _filing_backoff_active


def test_filing_403_backoff_retries_after_configured_window(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("BCAP_FILING_EVENTS_URL", raising=False)
    config = tmp_path / "configs" / "live_sources.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("filings:\n  sec_403_retry_minutes: 60\n", encoding="utf-8")
    now = datetime.now(ZoneInfo("America/Toronto"))
    signal_path = tmp_path / "state" / "signal_events.jsonl"
    signal_path.parent.mkdir(parents=True, exist_ok=True)

    _write_gap(signal_path, now - timedelta(minutes=30))
    assert _filing_backoff_active(tmp_path) is True

    _write_gap(signal_path, now - timedelta(minutes=90))
    assert _filing_backoff_active(tmp_path) is False


def test_configured_filing_feed_bypasses_sec_backoff(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("BCAP_FILING_EVENTS_URL", "https://filings.example.test/feed")
    signal_path = tmp_path / "state" / "signal_events.jsonl"
    signal_path.parent.mkdir(parents=True, exist_ok=True)
    _write_gap(signal_path, datetime.now(ZoneInfo("America/Toronto")))

    assert _filing_backoff_active(tmp_path) is False


def _write_gap(path: Path, detected_at: datetime) -> None:
    path.write_text(
        json.dumps(
            {
                "event_id": "filing-gap",
                "detected_at": detected_at.isoformat(timespec="seconds"),
                "ticker": "BCAP",
                "event_class": "filing_data_gap",
                "summary": "SEC returned 403 Forbidden; backoff is active.",
            }
        )
        + "\n",
        encoding="utf-8",
    )
