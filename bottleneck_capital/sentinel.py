from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.io import (
    append_jsonl,
    load_yaml_file,
    read_json_events,
    read_jsonl,
    scalar_text,
)
from bottleneck_capital.signal_events import (
    event_id_for_event,
    event_id_for_record,
    existing_signal_event_ids,
)

EVENT_CLASSES = {
    "dip_trigger",
    "thesis_damage_candidate",
    "filing_update",
    "catalyst_update",
    "hedge_risk_update",
    "sa_exit_update",
    "sa_position_reduction_update",
    "market_data_gap",
    "filing_data_gap",
    "geopolitical_regime_update",
    "macro_regime_update",
    "noise",
}

_DAMAGE_KEYWORDS = {
    "customer loss",
    "contract loss",
    "covenant",
    "default",
    "dilution",
    "financing stress",
    "fraud",
    "guidance cut",
    "impairment",
    "liquidity risk",
    "solvency",
    "thesis damage",
    "withdrawn guidance",
}

_HEDGE_KEYWORDS = {
    "ai beta",
    "correlation",
    "crowded",
    "crowding",
    "hedge",
    "index risk",
    "sector beta",
}

_GEOPOLITICAL_KEYWORDS = {
    "air strike",
    "ceasefire",
    "hostilities",
    "missile strike",
    "retaliatory strike",
    "strait of hormuz",
    "war escalation",
}

_MACRO_REGIME_KEYWORDS = {
    "credit stress",
    "energy shock",
    "liquidity shock",
    "rate shock",
    "risk-off",
}

_SA_EXIT_KEYWORDS = {
    "situational awareness exited",
    "sa exited",
    "full exit",
    "position exited",
    "removed from 13f",
    "zero position",
}

_SA_REDUCTION_KEYWORDS = {
    "situational awareness reduced",
    "sa reduced",
    "large reduction",
    "material reduction",
    "position reduction",
    "trimmed materially",
}


def run_sentinel(
    root: Path,
    input_path: Path | None = None,
    output_path: Path | None = None,
) -> list[dict[str, Any]]:
    thresholds = load_yaml_file(root / "configs" / "signal_thresholds.yaml")
    events = _load_latest_events(root, input_path)
    output = output_path or root / "state" / "signal_events.jsonl"
    detected_at = _now_iso(thresholds)
    existing_records = read_jsonl(output)
    existing_event_ids = existing_signal_event_ids(output)
    resolved_event_ids = {
        scalar_text(record.get("resolved_event_id"))
        for record in existing_records
        if scalar_text(record.get("event_class")) == "event_resolution"
        and scalar_text(record.get("resolved_event_id"))
    }
    existing_by_id = {
        event_id_for_record(record): record
        for record in existing_records
        if scalar_text(record.get("event_class")) != "event_resolution"
    }

    records = []
    for event in events:
        classification = classify_event(event, thresholds)
        event_id = event_id_for_event(event, classification)
        record_event_id = event_id
        reopened_from_event_id = ""
        if event_id in existing_event_ids:
            existing_record = existing_by_id.get(event_id)
            if _should_append_update(classification, event, existing_record):
                pass
            elif _should_reopen_resolved_price_dislocation(
                thresholds,
                classification,
                event,
                existing_record,
                event_id,
                resolved_event_ids,
            ):
                reopened_from_event_id = event_id
                record_event_id = _reopened_price_event_id(event_id, event)
                if record_event_id in existing_event_ids:
                    continue
            else:
                continue
        record = {
            "event_id": record_event_id,
            "detected_at": detected_at,
            "ticker": scalar_text(event.get("ticker")).upper(),
            "event_class": classification,
            "priority": _priority_for(classification),
            "requires_codex": classification != "noise",
            "resolved": False,
            "source": scalar_text(event.get("source") or event.get("event_type") or "mock"),
            "summary": scalar_text(
                event.get("summary") or event.get("headline") or "No summary provided."
            ),
            "raw_event": event,
        }
        if reopened_from_event_id:
            record["reopened_from_event_id"] = reopened_from_event_id
        append_jsonl(output, record)
        existing_event_ids.add(record_event_id)
        records.append(record)
    return records


def _should_append_update(
    classification: str,
    event: dict[str, Any],
    existing_record: dict[str, Any] | None,
) -> bool:
    if classification not in {"market_data_gap", "filing_data_gap"}:
        return False
    if not existing_record:
        return False
    summary = scalar_text(event.get("summary") or event.get("headline") or "No summary provided.")
    return summary != scalar_text(existing_record.get("summary"))


def _should_reopen_resolved_price_dislocation(
    thresholds: dict[str, Any],
    classification: str,
    event: dict[str, Any],
    existing_record: dict[str, Any] | None,
    event_id: str,
    resolved_event_ids: set[str],
) -> bool:
    if classification != "dip_trigger" or event_id not in resolved_event_ids:
        return False
    if scalar_text(event.get("event_type")) != "price_dislocation":
        return False
    if not existing_record:
        return False
    existing_event = existing_record.get("raw_event")
    if not isinstance(existing_event, dict):
        return False
    worsening = _max_price_drop_pct(event) - _max_price_drop_pct(existing_event)
    threshold = (
        thresholds.get("sentinel", {})
        .get("price_triggers", {})
        .get("reopen_worsening_pct", 5)
    )
    return worsening >= float(threshold)


def _max_price_drop_pct(event: dict[str, Any]) -> float:
    drops = [
        abs(value)
        for key in (
            "intraday_drop_pct",
            "one_day_drop_pct",
            "five_day_drop_pct",
            "twenty_day_drop_pct",
            "gap_down_pct",
            "post_earnings_move_pct",
        )
        if (value := _pct_value(event.get(key))) is not None and value < 0
    ]
    return max(drops, default=0.0)


def _reopened_price_event_id(event_id: str, event: dict[str, Any]) -> str:
    severity_bucket = int(_max_price_drop_pct(event) // 5 * 5)
    suffix = f"{event_id}:reopen:{severity_bucket}"
    return hashlib.sha256(suffix.encode("utf-8")).hexdigest()[:24]


def classify_event(event: dict[str, Any], thresholds: dict[str, Any]) -> str:
    explicit = scalar_text(event.get("event_class")).lower()
    if explicit in EVENT_CLASSES:
        return explicit

    text = " ".join(
        scalar_text(event.get(key)).lower()
        for key in ("event_type", "source", "summary", "headline", "known_cause", "filing_type")
    )
    if scalar_text(event.get("source_classification")) == "sa_public_filing_exit" or _contains_any(
        text, _SA_EXIT_KEYWORDS
    ):
        return "sa_exit_update"
    if (
        scalar_text(event.get("source_classification")) == "sa_public_filing_reduction"
        or _contains_any(text, _SA_REDUCTION_KEYWORDS)
    ):
        return "sa_position_reduction_update"
    if _contains_any(text, _DAMAGE_KEYWORDS):
        return "thesis_damage_candidate"
    if _contains_any(text, _GEOPOLITICAL_KEYWORDS):
        return "geopolitical_regime_update"
    if _contains_any(text, _MACRO_REGIME_KEYWORDS):
        return "macro_regime_update"
    if _is_price_drop_event(event, thresholds):
        return "dip_trigger"
    if scalar_text(event.get("filing_type")) or "sec filing" in text or "8-k" in text:
        return "filing_update"
    if _has_truthy_event_flag(
        event,
        (
            "company_ir_update",
            "customer_contract_announcement",
            "guidance_change",
            "investor_presentation",
            "earnings_release",
        ),
    ):
        return "catalyst_update"
    if _has_truthy_event_flag(event, ("financing_announcement",)):
        return "catalyst_update"
    if _contains_any(text, _HEDGE_KEYWORDS):
        return "hedge_risk_update"
    return "noise"


def _load_latest_events(root: Path, input_path: Path | None) -> list[dict[str, Any]]:
    candidates = [
        input_path,
        root / "state" / "latest_events.jsonl",
        root / "state" / "latest_events.json",
        root / "mock" / "latest_events.jsonl",
        root / "mock" / "latest_events.json",
    ]
    for candidate in candidates:
        if candidate is not None and candidate.exists():
            return read_json_events(candidate)
    return []


def _is_price_drop_event(event: dict[str, Any], thresholds: dict[str, Any]) -> bool:
    price_triggers = thresholds.get("sentinel", {}).get("price_triggers", {})
    checks = {
        "intraday_drop_pct": price_triggers.get("intraday_drop_pct", 5),
        "one_day_drop_pct": price_triggers.get("one_day_drop_pct", 7),
        "five_day_drop_pct": price_triggers.get("five_day_drop_pct", 12),
        "twenty_day_drop_pct": price_triggers.get("twenty_day_drop_pct", 20),
        "gap_down_pct": price_triggers.get("gap_down_pct", 4),
        "post_earnings_move_pct": price_triggers.get("post_earnings_move_pct", 8),
    }
    for key, threshold in checks.items():
        value = _pct_value(event.get(key))
        if value is not None and abs(value) >= float(threshold) and value < 0:
            return True
    return False


def _pct_value(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, int | float):
        return float(value)
    text = str(value).strip().replace("%", "")
    try:
        return float(text)
    except ValueError:
        return None


def _has_truthy_event_flag(event: dict[str, Any], keys: tuple[str, ...]) -> bool:
    for key in keys:
        value = event.get(key)
        if value is True:
            return True
        if isinstance(value, str) and value.strip().lower() in {"true", "yes", "y", "1"}:
            return True
        if key.replace("_", " ") in scalar_text(event.get("event_type")).lower():
            return True
    return False


def _contains_any(text: str, needles: set[str]) -> bool:
    return any(needle in text for needle in needles)


def _priority_for(classification: str) -> str:
    if classification in {
        "dip_trigger",
        "thesis_damage_candidate",
        "sa_exit_update",
        "sa_position_reduction_update",
        "geopolitical_regime_update",
        "macro_regime_update",
    }:
        return "high"
    if classification in {"market_data_gap", "filing_data_gap"}:
        return "high"
    if classification in {"filing_update", "catalyst_update", "hedge_risk_update"}:
        return "medium"
    return "low"


def _now_iso(thresholds: dict[str, Any]) -> str:
    timezone = thresholds.get("sentinel", {}).get("timezone", "America/Toronto")
    return datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")
