from __future__ import annotations

import json
from pathlib import Path

from bottleneck_capital.io import read_jsonl
from bottleneck_capital.sentinel import run_sentinel
from bottleneck_capital.signal_events import (
    active_signal_events,
    event_id_for_event,
    group_signal_events,
)


def test_sentinel_dedupes_identical_events(tmp_path: Path) -> None:
    _write_thresholds(tmp_path)
    events = tmp_path / "events.jsonl"
    events.write_text(
        json.dumps(
            {
                "ticker": "CRWV",
                "event_type": "watchlist_heartbeat",
                "summary": "No material mock event.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    first = run_sentinel(tmp_path, input_path=events)
    second = run_sentinel(tmp_path, input_path=events)

    records = read_jsonl(tmp_path / "state" / "signal_events.jsonl")
    assert len(first) == 1
    assert second == []
    assert len(records) == 1
    assert records[0]["event_id"]


def test_sentinel_dedupes_legacy_price_dislocation_pct_drift(tmp_path: Path) -> None:
    _write_thresholds(tmp_path)
    signal_path = tmp_path / "state" / "signal_events.jsonl"
    signal_path.parent.mkdir(parents=True, exist_ok=True)
    signal_path.write_text(
        json.dumps(
            {
                "event_id": "legacy-id",
                "ticker": "CRWV",
                "event_class": "dip_trigger",
                "priority": "high",
                "resolved": False,
                "raw_event": {
                    "ticker": "CRWV",
                    "event_type": "price_dislocation",
                    "source": "market_yahoo",
                    "summary": "CRWV price dislocation: intraday -7.1%.",
                    "dedupe_key": "market:CRWV:2026-06-22:intraday -7.1%",
                    "intraday_drop_pct": -7.1,
                    "observed_at": "2026-06-22T13:00:00-04:00",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    events = tmp_path / "events.jsonl"
    events.write_text(
        json.dumps(
            {
                "ticker": "CRWV",
                "event_type": "price_dislocation",
                "source": "market_yahoo",
                "summary": "CRWV price dislocation: intraday -7.2%.",
                "dedupe_key": "market:CRWV:2026-06-22:intraday",
                "intraday_drop_pct": -7.2,
                "observed_at": "2026-06-22T13:15:00-04:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    records = run_sentinel(tmp_path, input_path=events)

    assert records == []


def test_sentinel_reopens_resolved_price_dislocation_when_materially_worse(
    tmp_path: Path,
) -> None:
    _write_thresholds(tmp_path)
    original_event = {
        "ticker": "CRWV",
        "event_type": "price_dislocation",
        "source": "market_yahoo",
        "summary": "CRWV price dislocation: intraday -7.1%.",
        "dedupe_key": "market:CRWV:2026-06-22:intraday -7.1%",
        "intraday_drop_pct": -7.1,
        "observed_at": "2026-06-22T13:00:00-04:00",
    }
    original_id = event_id_for_event(original_event, "dip_trigger")
    signal_path = tmp_path / "state" / "signal_events.jsonl"
    signal_path.parent.mkdir(parents=True, exist_ok=True)
    signal_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_id": original_id,
                        "ticker": "CRWV",
                        "event_class": "dip_trigger",
                        "priority": "high",
                        "resolved": False,
                        "raw_event": original_event,
                    },
                    sort_keys=True,
                ),
                json.dumps(
                    {
                        "event_id": f"resolve-{original_id}",
                        "ticker": "CRWV",
                        "event_class": "event_resolution",
                        "priority": "low",
                        "resolved": True,
                        "resolved_event_id": original_id,
                    },
                    sort_keys=True,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    events = tmp_path / "events.jsonl"
    events.write_text(
        json.dumps(
            {
                "ticker": "CRWV",
                "event_type": "price_dislocation",
                "source": "market_yahoo",
                "summary": "CRWV price dislocation: intraday -13.0%.",
                "dedupe_key": "market:CRWV:2026-06-22:intraday",
                "intraday_drop_pct": -13.0,
                "observed_at": "2026-06-22T14:00:00-04:00",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    records = run_sentinel(tmp_path, input_path=events)

    all_records = read_jsonl(signal_path)
    active = active_signal_events(all_records)
    assert len(records) == 1
    assert records[0]["event_id"] != original_id
    assert records[0]["reopened_from_event_id"] == original_id
    assert [record for record in active if record.get("event_id") == records[0]["event_id"]]


def test_reopened_price_dislocation_is_quiet_within_same_severity_band(
    tmp_path: Path,
) -> None:
    _write_thresholds(tmp_path)
    original_event = {
        "ticker": "CRWV",
        "event_type": "price_dislocation",
        "source": "market_yahoo",
        "summary": "CRWV price dislocation: intraday -7.0%.",
        "dedupe_key": "market:CRWV:2026-06-22:intraday",
        "intraday_drop_pct": -7.0,
        "observed_at": "2026-06-22T13:00:00-04:00",
    }
    original_id = event_id_for_event(original_event, "dip_trigger")
    signal_path = tmp_path / "state" / "signal_events.jsonl"
    signal_path.parent.mkdir(parents=True, exist_ok=True)
    signal_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_id": original_id,
                        "detected_at": "2026-06-22T13:00:00-04:00",
                        "ticker": "CRWV",
                        "event_class": "dip_trigger",
                        "priority": "high",
                        "resolved": False,
                        "raw_event": original_event,
                    }
                ),
                json.dumps(
                    {
                        "event_id": f"resolve-{original_id}",
                        "detected_at": "2026-06-22T13:05:00-04:00",
                        "ticker": "CRWV",
                        "event_class": "event_resolution",
                        "resolved": True,
                        "resolved_event_id": original_id,
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    events = tmp_path / "events.jsonl"
    first_worse = {**original_event, "intraday_drop_pct": -13.0}
    first_worse["observed_at"] = "2026-06-22T14:00:00-04:00"
    events.write_text(json.dumps(first_worse) + "\n", encoding="utf-8")
    first = run_sentinel(tmp_path, input_path=events)
    same_band = {**first_worse, "intraday_drop_pct": -14.9}
    same_band["observed_at"] = "2026-06-22T15:00:00-04:00"
    events.write_text(json.dumps(same_band) + "\n", encoding="utf-8")

    repeated = run_sentinel(tmp_path, input_path=events)

    assert len(first) == 1
    assert repeated == []


def test_active_events_keep_only_latest_reopen_and_latest_regime_per_region() -> None:
    records = [
        {
            "event_id": "reopen-10",
            "detected_at": "2026-08-08T10:00:00-04:00",
            "ticker": "SPCX",
            "event_class": "dip_trigger",
            "reopened_from_event_id": "base-price-event",
        },
        {
            "event_id": "reopen-15",
            "detected_at": "2026-08-08T11:00:00-04:00",
            "ticker": "SPCX",
            "event_class": "dip_trigger",
            "reopened_from_event_id": "base-price-event",
        },
        {
            "event_id": "middle-east-ceasefire",
            "detected_at": "2026-08-08T09:00:00-04:00",
            "ticker": "BCAP",
            "event_class": "geopolitical_regime_update",
            "raw_event": {"region": "middle_east", "status": "ceasefire"},
        },
        {
            "event_id": "middle-east-escalation",
            "detected_at": "2026-08-08T12:00:00-04:00",
            "ticker": "BCAP",
            "event_class": "geopolitical_regime_update",
            "raw_event": {"region": "middle_east", "status": "renewed_escalation"},
        },
        {
            "event_id": "taiwan-update",
            "detected_at": "2026-08-08T11:30:00-04:00",
            "ticker": "BCAP",
            "event_class": "geopolitical_regime_update",
            "raw_event": {"region": "taiwan", "status": "elevated"},
        },
    ]

    active = active_signal_events(records)
    grouped = group_signal_events(active)

    assert {record["event_id"] for record in active} == {
        "reopen-15",
        "middle-east-escalation",
        "taiwan-update",
    }
    assert len(grouped) == 3


def test_sentinel_does_not_reopen_resolved_price_dislocation_for_small_drift(
    tmp_path: Path,
) -> None:
    _write_thresholds(tmp_path)
    original_event = {
        "ticker": "CRWV",
        "event_type": "price_dislocation",
        "source": "market_yahoo",
        "summary": "CRWV price dislocation: intraday -7.1%.",
        "dedupe_key": "market:CRWV:2026-06-22:intraday -7.1%",
        "intraday_drop_pct": -7.1,
        "observed_at": "2026-06-22T13:00:00-04:00",
    }
    original_id = event_id_for_event(original_event, "dip_trigger")
    signal_path = tmp_path / "state" / "signal_events.jsonl"
    signal_path.parent.mkdir(parents=True, exist_ok=True)
    signal_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_id": original_id,
                        "ticker": "CRWV",
                        "event_class": "dip_trigger",
                        "priority": "high",
                        "resolved": False,
                        "raw_event": original_event,
                    },
                    sort_keys=True,
                ),
                json.dumps(
                    {
                        "event_id": f"resolve-{original_id}",
                        "ticker": "CRWV",
                        "event_class": "event_resolution",
                        "priority": "low",
                        "resolved": True,
                        "resolved_event_id": original_id,
                    },
                    sort_keys=True,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    events = tmp_path / "events.jsonl"
    events.write_text(
        json.dumps(
            {
                "ticker": "CRWV",
                "event_type": "price_dislocation",
                "source": "market_yahoo",
                "summary": "CRWV price dislocation: intraday -8.0%.",
                "dedupe_key": "market:CRWV:2026-06-22:intraday",
                "intraday_drop_pct": -8.0,
                "observed_at": "2026-06-22T14:00:00-04:00",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    records = run_sentinel(tmp_path, input_path=events)

    assert records == []


def test_sa_exit_and_reduction_are_high_priority(tmp_path: Path) -> None:
    _write_thresholds(tmp_path)
    events = tmp_path / "events.jsonl"
    events.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ticker": "TSM",
                        "summary": "Situational Awareness exited the reported position.",
                    }
                ),
                json.dumps(
                    {
                        "ticker": "CRWV",
                        "summary": "Situational Awareness reduced the position materially.",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    records = run_sentinel(tmp_path, input_path=events)

    by_ticker = {record["ticker"]: record for record in records}
    assert by_ticker["TSM"]["event_class"] == "sa_exit_update"
    assert by_ticker["TSM"]["priority"] == "high"
    assert by_ticker["TSM"]["requires_codex"] is True
    assert by_ticker["CRWV"]["event_class"] == "sa_position_reduction_update"
    assert by_ticker["CRWV"]["priority"] == "high"
    assert by_ticker["CRWV"]["requires_codex"] is True


def test_data_gap_events_are_high_priority(tmp_path: Path) -> None:
    _write_thresholds(tmp_path)
    events = tmp_path / "events.jsonl"
    events.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ticker": "BITF",
                        "event_class": "market_data_gap",
                        "summary": "Market data missing.",
                    }
                ),
                json.dumps(
                    {
                        "ticker": "BCAP",
                        "event_class": "filing_data_gap",
                        "summary": "Filing data missing.",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    records = run_sentinel(tmp_path, input_path=events)

    by_class = {record["event_class"]: record for record in records}
    assert by_class["market_data_gap"]["priority"] == "high"
    assert by_class["filing_data_gap"]["priority"] == "high"


def test_geopolitical_regime_event_is_high_priority(tmp_path: Path) -> None:
    _write_thresholds(tmp_path)
    events = tmp_path / "events.jsonl"
    events.write_text(
        json.dumps(
            {
                "ticker": "BCAP",
                "summary": "Renewed retaliatory strikes after the ceasefire.",
                "region": "middle_east",
                "status": "renewed_escalation",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    record = run_sentinel(tmp_path, input_path=events)[0]

    assert record["event_class"] == "geopolitical_regime_update"
    assert record["priority"] == "high"


def test_data_gap_summary_update_appends_latest_active_record(tmp_path: Path) -> None:
    _write_thresholds(tmp_path)
    events = tmp_path / "events.jsonl"
    events.write_text(
        json.dumps(
            {
                "ticker": "BCAP",
                "event_class": "filing_data_gap",
                "dedupe_key": "filing_data_gap:daily",
                "summary": "Filing data missing: first failure.",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    first = run_sentinel(tmp_path, input_path=events)
    events.write_text(
        json.dumps(
            {
                "ticker": "BCAP",
                "event_class": "filing_data_gap",
                "dedupe_key": "filing_data_gap:daily",
                "summary": "Filing data missing: second failure detail.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    second = run_sentinel(tmp_path, input_path=events)

    records = read_jsonl(tmp_path / "state" / "signal_events.jsonl")
    assert len(first) == 1
    assert len(second) == 1
    assert len(records) == 2
    assert records[0]["event_id"] == records[1]["event_id"]
    assert records[-1]["summary"] == "Filing data missing: second failure detail."


def test_sentinel_prefers_state_latest_events_over_mock(tmp_path: Path) -> None:
    _write_thresholds(tmp_path)
    mock = tmp_path / "mock" / "latest_events.jsonl"
    mock.parent.mkdir(parents=True, exist_ok=True)
    mock.write_text(
        json.dumps(
            {
                "ticker": "CRWV",
                "event_type": "watchlist_heartbeat",
                "summary": "No material mock event.",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    state = tmp_path / "state" / "latest_events.jsonl"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(
        json.dumps(
            {
                "ticker": "TSM",
                "summary": "Guidance cut creates thesis damage.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    records = run_sentinel(tmp_path)

    assert len(records) == 1
    assert records[0]["ticker"] == "TSM"
    assert records[0]["event_class"] == "thesis_damage_candidate"


def _write_thresholds(root: Path) -> None:
    path = root / "configs" / "signal_thresholds.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """sentinel:
  timezone: America/Toronto
  price_triggers:
    intraday_drop_pct: 5
""",
        encoding="utf-8",
    )
