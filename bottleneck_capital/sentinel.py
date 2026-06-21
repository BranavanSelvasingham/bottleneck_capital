from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.io import append_jsonl, load_yaml_file, read_json_events, scalar_text

EVENT_CLASSES = {
    "dip_trigger",
    "thesis_damage_candidate",
    "filing_update",
    "catalyst_update",
    "hedge_risk_update",
    "sa_exit_update",
    "sa_position_reduction_update",
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

    records = []
    for event in events:
        classification = classify_event(event, thresholds)
        record = {
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
        append_jsonl(output, record)
        records.append(record)
    return records


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
        root / "mock" / "latest_events.jsonl",
        root / "mock" / "latest_events.json",
        root / "state" / "latest_events.jsonl",
        root / "state" / "latest_events.json",
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
    if classification in {"dip_trigger", "thesis_damage_candidate"}:
        return "high"
    if classification in {"filing_update", "catalyst_update", "hedge_risk_update"}:
        return "medium"
    return "low"


def _now_iso(thresholds: dict[str, Any]) -> str:
    timezone = thresholds.get("sentinel", {}).get("timezone", "America/Toronto")
    return datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")
