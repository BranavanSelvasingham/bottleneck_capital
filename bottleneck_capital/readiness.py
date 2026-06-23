from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bottleneck_capital.io import read_jsonl, scalar_text
from bottleneck_capital.signal_events import active_signal_events, event_id_for_record
from bottleneck_capital.validation import has_errors, validate_project

BLOCKING_WARNING_CODES = {
    "LOCAL_POSITIONS_MISSING",
    "LOCAL_POSITION_PRICE_MISSING",
    "LOCAL_POSITION_COST_BASIS_MISSING",
    "LOCAL_POSITION_CURRENCY_MISSING",
    "LOCAL_POSITION_CURRENCY_MISMATCH",
}


def write_live_readiness_report(root: Path) -> Path:
    path = root / "reports" / "live_readiness" / f"{_today()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_live_readiness(root), encoding="utf-8")
    return path


def is_live_ready(root: Path) -> bool:
    issues = validate_project(root, strict_live=True)
    active_high = _active_high_priority_signals(root)
    blocking_warnings = [issue for issue in issues if issue.code in BLOCKING_WARNING_CODES]
    return not (has_errors(issues) or active_high or blocking_warnings)


def render_live_readiness(root: Path) -> str:
    issues = validate_project(root, strict_live=True)
    active_high = _active_high_priority_signals(root)
    blocking_warnings = [issue for issue in issues if issue.code in BLOCKING_WARNING_CODES]
    status = "NOT_READY" if has_errors(issues) or active_high or blocking_warnings else "READY"
    lines = [
        "# Bottleneck Capital Live Readiness",
        "",
        f"Generated: {_now()}",
        f"Status: {status}",
        "",
        "## Strict-Live Errors",
        "",
    ]
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    if errors:
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in errors)
    else:
        lines.append("- None")
    lines.extend(["", "## Strict-Live Warnings", ""])
    warnings = [
        issue
        for issue in issues
        if issue.severity == "WARN" and issue.code != "ACTIVE_HIGH_PRIORITY_SIGNAL"
    ]
    if warnings:
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in warnings)
    else:
        lines.append("- None")
    lines.extend(["", "## Active High-Priority Signals", ""])
    if active_high:
        lines.extend(
            f"- `{event_id_for_record(record)}` `{record.get('ticker')}` "
            f"`{record.get('event_class')}`: {record.get('summary')}"
            for record in active_high
        )
    else:
        lines.append("- None")
    lines.extend(["", "## Recovery Actions", ""])
    lines.extend(_recovery_actions(root, issues))
    lines.extend(["", "## Resume Gate", ""])
    lines.append(
        "Keep automation paused until `bcap validate --strict-live` has no ERROR issues "
        "including missing or placeholder local position data, and all active high-priority "
        "RESEARCH_REQUIRED/source-gap signals have either been reviewed or intentionally "
        "accepted for scheduled monitoring."
    )
    return "\n".join(lines) + "\n"


def _active_high_priority_signals(root: Path) -> list[dict]:
    return [
        record
        for record in active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
        if scalar_text(record.get("priority")) in {"high", "critical"}
        and scalar_text(record.get("event_class")) != "noise"
    ]


def _recovery_actions(root: Path, issues) -> list[str]:
    actions: list[str] = []
    ingest_status = _ingest_status(root)
    for issue in issues:
        if issue.code == "MARKET_INGEST_PARTIAL":
            missing = _missing_tickers(ingest_status, "market")
            actions.append(
                "- Resolve market coverage for "
                f"{', '.join(missing) or 'unknown'}: verify current symbol/corporate action, "
                "then update `configs/live_sources.yaml` `market.symbol_overrides`, or correct "
                "the watchlist/universe if the exposure no longer maps to the thesis."
            )
        elif issue.code == "FILINGS_INGEST_MISSING":
            actions.append(
                "- Restore filing coverage: wait/back off if SEC is blocking requests, configure "
                "`BCAP_SEC_*` mirror/proxy variables, or configure `BCAP_FILING_EVENTS_URL` "
                "for an approved live filing vendor/proxy feed with `covered_tickers`."
            )
        elif issue.code == "FILINGS_INGEST_PARTIAL":
            missing = _missing_tickers(ingest_status, "filings")
            actions.append(
                "- Resolve filing coverage for "
                f"{', '.join(missing) or 'unknown'} by correcting CIK/ticker mapping or filing "
                "provider coverage."
            )
        elif issue.code == "LOCAL_POSITIONS_MISSING":
            actions.append(
                "- Add `state/local_positions.yaml` so sizing and held-ticker live coverage checks "
                "use the actual portfolio."
            )
        elif issue.code == "LOCAL_POSITION_PRICE_MISSING":
            actions.append(
                "- Run `bcap live-check` or `bcap positions-refresh-prices` after market ingest so "
                "held-position current prices are populated."
            )
        elif issue.code == "LOCAL_POSITION_COST_BASIS_MISSING":
            actions.append(
                "- Fill exact local position cost basis for held names; keep placeholder or "
                "pending cost basis visible until corrected."
            )
        elif issue.code in {"LOCAL_POSITION_CURRENCY_MISSING", "LOCAL_POSITION_CURRENCY_MISMATCH"}:
            actions.append(
                "- Correct held-position currency fields so local position prices and cost basis "
                "use the same currency as the latest market snapshot."
            )
        elif issue.code == "MARKET_INGEST_STALE":
            actions.append("- Run `bcap live-check` with network access to refresh market ingest.")
        elif issue.code == "FILINGS_INGEST_STALE":
            actions.append("- Run `bcap live-check` with filing-source access to refresh filings.")
    if not actions:
        actions.append("- None")
    return _dedupe(actions)


def _ingest_status(root: Path) -> dict:
    path = root / "state" / "ingest_status.json"
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _missing_tickers(ingest_status: dict, channel: str) -> list[str]:
    item = ingest_status.get(channel)
    if not isinstance(item, dict):
        return []
    missing = item.get("missing_tickers")
    if not isinstance(missing, list):
        return []
    return [scalar_text(ticker).upper() for ticker in missing if scalar_text(ticker)]


def _dedupe(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for line in lines:
        if line not in seen:
            deduped.append(line)
            seen.add(line)
    return deduped


def _today() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).date().isoformat()


def _now() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="minutes")
