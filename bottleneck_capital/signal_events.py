from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.io import append_jsonl, read_jsonl, scalar_bool, scalar_text

RESOLUTION_EVENT_CLASS = "event_resolution"


class SignalEventError(RuntimeError):
    """Raised when signal event operations cannot be completed."""


def event_id_for_event(event: dict[str, Any], classification: str) -> str:
    dedupe_key = _canonical_dedupe_key(event) or scalar_text(event.get("dedupe_key"))
    if dedupe_key:
        payload = {
            "ticker": scalar_text(event.get("ticker")).upper(),
            "event_class": classification,
            "source": scalar_text(event.get("source") or event.get("event_type") or "mock"),
            "dedupe_key": dedupe_key,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:24]
    payload = {
        "ticker": scalar_text(event.get("ticker")).upper(),
        "event_class": classification,
        "source": scalar_text(event.get("source") or event.get("event_type") or "mock"),
        "summary": scalar_text(event.get("summary") or event.get("headline")),
        "raw_event": event,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:24]


def event_id_for_record(record: dict[str, Any]) -> str:
    event_id = scalar_text(record.get("event_id"))
    if event_id:
        return event_id
    raw_event = record.get("raw_event")
    event_class = scalar_text(record.get("event_class"))
    if isinstance(raw_event, dict) and event_class:
        return event_id_for_event(raw_event, event_class)
    payload = {
        "ticker": scalar_text(record.get("ticker")).upper(),
        "event_class": event_class,
        "source": scalar_text(record.get("source")),
        "summary": scalar_text(record.get("summary")),
        "detected_at": scalar_text(record.get("detected_at")),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:24]


def existing_signal_event_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    for record in read_jsonl(path):
        if scalar_text(record.get("event_class")) == RESOLUTION_EVENT_CLASS:
            continue
        ids.add(event_id_for_record(record))
        raw_event = record.get("raw_event")
        event_class = scalar_text(record.get("event_class"))
        if isinstance(raw_event, dict) and event_class:
            ids.add(event_id_for_event(raw_event, event_class))
    return ids


def active_signal_events(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    resolved_ids = _resolved_event_ids(records)
    active_by_identity: dict[str, dict[str, Any]] = {}
    for record in records:
        if scalar_text(record.get("event_class")) == RESOLUTION_EVENT_CLASS:
            continue
        if scalar_bool(record.get("resolved")):
            continue
        if event_id_for_record(record) in resolved_ids:
            continue
        identity = _event_identity(record)
        if identity in resolved_ids:
            continue
        active_by_identity[identity] = record
    return list(active_by_identity.values())


def group_signal_events(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse repeated alerts while preserving the latest actionable context."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        ticker = scalar_text(record.get("ticker")).upper()
        event_class = scalar_text(record.get("event_class"))
        if not ticker or not event_class:
            continue
        grouped.setdefault((ticker, event_class), []).append(record)

    consolidated: list[dict[str, Any]] = []
    for (ticker, event_class), items in grouped.items():
        ordered = sorted(items, key=lambda item: scalar_text(item.get("detected_at")))
        latest = dict(ordered[-1])
        latest["ticker"] = ticker
        latest["event_class"] = event_class
        latest["event_count"] = len(items)
        latest["first_detected_at"] = scalar_text(ordered[0].get("detected_at"))
        latest["latest_detected_at"] = scalar_text(ordered[-1].get("detected_at"))
        consolidated.append(latest)
    return sorted(
        consolidated,
        key=lambda item: (
            scalar_text(item.get("ticker")),
            scalar_text(item.get("event_class")),
        ),
    )


def resolve_signal_events(
    root: Path,
    *,
    event_id: str = "",
    ticker: str = "",
    event_class: str = "",
    reason: str = "",
) -> list[dict[str, Any]]:
    path = root / "state" / "signal_events.jsonl"
    records = read_jsonl(path)
    active = active_signal_events(records)
    matches = [
        record
        for record in active
        if _matches_resolution_filter(
            record,
            event_id=event_id,
            ticker=ticker,
            event_class=event_class,
        )
    ]
    if not matches:
        raise SignalEventError("No active signal events matched the resolution filter.")

    now = _now()
    resolution_records: list[dict[str, Any]] = []
    for record in matches:
        resolved_event_id = event_id_for_record(record)
        resolution = {
            "event_id": f"resolve-{resolved_event_id}",
            "detected_at": now,
            "ticker": scalar_text(record.get("ticker")).upper(),
            "event_class": RESOLUTION_EVENT_CLASS,
            "priority": "low",
            "requires_codex": False,
            "resolved": True,
            "resolved_event_id": resolved_event_id,
            "source": "signal_resolution",
            "summary": reason or "Resolved after research review.",
        }
        append_jsonl(path, resolution)
        resolution_records.append(resolution)
    return resolution_records


def _resolved_event_ids(records: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for record in records:
        if scalar_text(record.get("event_class")) == RESOLUTION_EVENT_CLASS:
            resolved_event_id = scalar_text(record.get("resolved_event_id"))
            if resolved_event_id:
                ids.add(resolved_event_id)
    return ids


def _matches_resolution_filter(
    record: dict[str, Any],
    *,
    event_id: str,
    ticker: str,
    event_class: str,
) -> bool:
    if event_id and event_id_for_record(record) != event_id:
        return False
    if ticker and scalar_text(record.get("ticker")).upper() != ticker.upper():
        return False
    if event_class and scalar_text(record.get("event_class")) != event_class:
        return False
    return bool(event_id or ticker or event_class)


def _now() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")


def _canonical_dedupe_key(event: dict[str, Any]) -> str:
    if scalar_text(event.get("event_type")) != "price_dislocation":
        return ""
    ticker = scalar_text(event.get("ticker")).upper()
    if not ticker:
        return ""
    dedupe_key = scalar_text(event.get("dedupe_key"))
    event_date = _date_from_dedupe_key(dedupe_key) or scalar_text(event.get("observed_at"))[:10]
    if not event_date:
        return ""
    return f"market:{ticker}:{event_date}:price_dislocation"


def _date_from_dedupe_key(dedupe_key: str) -> str:
    parts = dedupe_key.split(":")
    if len(parts) >= 3 and parts[0] == "market":
        return parts[2]
    return ""


def _event_identity(record: dict[str, Any]) -> str:
    if scalar_text(record.get("reopened_from_event_id")):
        return event_id_for_record(record)
    raw_event = record.get("raw_event")
    event_class = scalar_text(record.get("event_class"))
    if isinstance(raw_event, dict) and event_class:
        canonical = _canonical_dedupe_key(raw_event)
        if canonical:
            return event_id_for_event(raw_event, event_class)
    return event_id_for_record(record)
