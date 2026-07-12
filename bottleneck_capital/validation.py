from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import ALLOWED_DECISIONS, load_watchlist
from bottleneck_capital.io import (
    ConfigError,
    load_yaml_file,
    read_jsonl,
    read_markdown_frontmatter,
    scalar_text,
)
from bottleneck_capital.live_sources import effective_sec_user_agent
from bottleneck_capital.signal_events import (
    active_signal_events,
    event_id_for_record,
    group_signal_events,
)


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str


def validate_project(root: Path, *, strict_live: bool = False) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    watchlist = load_watchlist(root)
    tickers = [item["ticker"] for item in watchlist]
    position_items = _load_local_position_items(root, issues)
    _check_duplicates(tickers, issues)
    _check_ticker_files(root, tickers, issues)
    _check_generated_wiring(root, tickers, issues)
    _check_decisions(root, tickers, issues)
    _check_research_blocks(root, issues, strict_live=strict_live)
    _check_signal_events(root, issues)
    _check_event_inputs(root, issues, strict_live=strict_live)
    _check_ingest_freshness(root, issues, strict_live=strict_live, positions=position_items)
    _check_live_environment(root, issues, strict_live=strict_live)
    _check_local_positions(root, tickers, issues, strict_live=strict_live, positions=position_items)
    return issues


def render_validation(issues: list[ValidationIssue]) -> str:
    if not issues:
        return "Validation passed with no issues.\n"
    lines = ["Validation issues:"]
    for issue in issues:
        lines.append(f"- {issue.severity} {issue.code}: {issue.message}")
    return "\n".join(lines) + "\n"


def has_errors(issues: list[ValidationIssue]) -> bool:
    return any(issue.severity == "ERROR" for issue in issues)


def _check_duplicates(tickers: list[str], issues: list[ValidationIssue]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for ticker in tickers:
        if ticker in seen:
            duplicates.add(ticker)
        seen.add(ticker)
    for ticker in sorted(duplicates):
        issues.append(ValidationIssue("ERROR", "DUPLICATE_WATCHLIST_TICKER", ticker))


def _check_ticker_files(root: Path, tickers: list[str], issues: list[ValidationIssue]) -> None:
    for ticker in tickers:
        for kind in ("assets", "decisions"):
            path = root / "research" / kind / f"{ticker}.md"
            if not path.exists():
                issues.append(
                    ValidationIssue("ERROR", "MISSING_TICKER_FILE", f"{ticker}: {path}")
                )


def _check_generated_wiring(root: Path, tickers: list[str], issues: list[ValidationIssue]) -> None:
    roster_path = root / "configs" / "agent_roster.yaml"
    roster = roster_path.read_text(encoding="utf-8") if roster_path.exists() else ""
    for ticker in tickers:
        if f"asset_analyst.{ticker}" not in roster:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "MISSING_AGENT_OWNER",
                    f"{ticker} is missing from configs/agent_roster.yaml",
                )
            )
        if not list((root / "research" / "agent_packets").glob(f"*/{ticker}.md")):
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "MISSING_AGENT_PACKET",
                    f"{ticker} has no research/agent_packets entry",
                )
            )


def _check_decisions(root: Path, tickers: list[str], issues: list[ValidationIssue]) -> None:
    for ticker in tickers:
        decision_path = root / "research" / "decisions" / f"{ticker}.md"
        if not decision_path.exists():
            continue
        metadata, _ = read_markdown_frontmatter(decision_path)
        decision = scalar_text(metadata.get("current_decision")).upper()
        if decision not in ALLOWED_DECISIONS:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "INVALID_DECISION",
                    f"{ticker} has unsupported current_decision {decision or '<blank>'}",
                )
            )
        if decision == "BUY_NOW":
            missing = [
                key
                for key in (
                    "buy_thesis",
                    "anti_thesis",
                    "valuation_case",
                    "hedge_or_sizing",
                    "invalidation_trigger",
                    "evidence_quality",
                )
                if not scalar_text(metadata.get(key))
            ]
            if missing:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "BUY_NOW_DISCIPLINE_GAP",
                        f"{ticker} missing {', '.join(missing)}",
                    )
                )


def _check_signal_events(root: Path, issues: list[ValidationIssue]) -> None:
    path = root / "state" / "signal_events.jsonl"
    records = read_jsonl(path)
    for record in records:
        if not event_id_for_record(record):
            issues.append(
                ValidationIssue("ERROR", "SIGNAL_EVENT_ID_MISSING", scalar_text(record))
            )
    active_high = [
        record
        for record in active_signal_events(records)
        if scalar_text(record.get("priority")) in {"high", "critical"}
        and scalar_text(record.get("event_class")) != "noise"
    ]
    for record in group_signal_events(active_high):
        count = int(record.get("event_count", 1))
        issues.append(
            ValidationIssue(
                "WARN",
                "ACTIVE_HIGH_PRIORITY_SIGNAL",
                f"{record.get('ticker')} {record.get('event_class')} ({count} active): "
                f"{record.get('summary')}",
            )
        )


def _check_research_blocks(
    root: Path,
    issues: list[ValidationIssue],
    *,
    strict_live: bool,
) -> None:
    from bottleneck_capital.opportunity import overdue_research_blocks

    for item in overdue_research_blocks(root):
        issues.append(
            ValidationIssue(
                "ERROR" if strict_live else "WARN",
                "OVERDUE_RESEARCH_BLOCK",
                (
                    f"{item.ticker} has been RESEARCH_REQUIRED for {item.age_days} days "
                    f"since primary-source review (max {item.max_age_days}); opportunity "
                    f"score {item.score:.1f}. Refresh evidence and resolve or reaffirm."
                ),
            )
        )


def _check_event_inputs(
    root: Path,
    issues: list[ValidationIssue],
    *,
    strict_live: bool,
) -> None:
    state_inputs = [
        root / "state" / "latest_events.jsonl",
        root / "state" / "latest_events.json",
    ]
    mock_inputs = [
        root / "mock" / "latest_events.jsonl",
        root / "mock" / "latest_events.json",
    ]
    has_state_input = any(path.exists() for path in state_inputs)
    has_mock_input = any(path.exists() for path in mock_inputs)
    if not has_state_input and has_mock_input:
        issues.append(
            ValidationIssue(
                "ERROR" if strict_live else "WARN",
                "MOCK_EVENT_FALLBACK_ONLY",
                "No state/latest_events input exists; sentinel will fall back to mock data.",
            )
        )


def _check_ingest_freshness(
    root: Path,
    issues: list[ValidationIssue],
    *,
    strict_live: bool,
    positions: list[dict[str, Any]],
) -> None:
    path = root / "state" / "ingest_status.json"
    if not path.exists():
        severity = "ERROR" if strict_live else "WARN"
        issues.append(
            ValidationIssue(
                severity,
                "INGEST_STATUS_MISSING",
                "state/ingest_status.json is absent; live ingestion freshness is unknown.",
            )
        )
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(ValidationIssue("ERROR", "INGEST_STATUS_PARSE_ERROR", str(exc)))
        return
    thresholds = _freshness_thresholds(root)
    for channel, max_age_minutes in thresholds.items():
        item = data.get(channel)
        if not isinstance(item, dict):
            issues.append(
                ValidationIssue(
                    "ERROR" if strict_live else "WARN",
                    f"{channel.upper()}_INGEST_MISSING",
                    f"{channel} ingest has never succeeded.",
                )
            )
            continue
        age = _age_minutes(scalar_text(item.get("last_success_at")))
        if age is None:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    f"{channel.upper()}_INGEST_BAD_TIMESTAMP",
                    f"{channel} ingest has invalid last_success_at.",
                )
            )
            continue
        if age > max_age_minutes:
            issues.append(
                ValidationIssue(
                    "ERROR" if strict_live else "WARN",
                    f"{channel.upper()}_INGEST_STALE",
                    f"{channel} ingest is {age:.1f} minutes old; max {max_age_minutes}.",
                )
            )
        if strict_live and _fixture_source(channel, scalar_text(item.get("source"))):
            issues.append(
                ValidationIssue(
                    "ERROR",
                    f"{channel.upper()}_INGEST_NOT_LIVE",
                    f"{channel} ingest source is fixture/manual input, not a live provider.",
                )
            )
        if channel == "market":
            item_count = int(_float_value(item.get("item_count")))
            expected_item_count = int(_float_value(item.get("expected_item_count")))
            if expected_item_count > 0 and item_count < expected_item_count:
                missing = _string_list(item.get("missing_tickers"))
                blocking_missing = _blocking_live_gap_tickers(root, missing, positions)
                issues.append(
                    ValidationIssue(
                        "ERROR" if strict_live and blocking_missing else "WARN",
                        "MARKET_INGEST_PARTIAL",
                        (
                            f"market ingest covered {item_count}/{expected_item_count} tickers"
                            f"; missing {', '.join(missing) or 'unknown'}."
                        ),
                    )
                )
        if channel == "filings":
            item_count = int(_float_value(item.get("item_count")))
            expected_item_count = int(_float_value(item.get("expected_item_count")))
            if expected_item_count > 0 and item_count < expected_item_count:
                missing = _string_list(item.get("missing_tickers"))
                blocking_missing = _blocking_live_gap_tickers(root, missing, positions)
                issues.append(
                    ValidationIssue(
                        "ERROR" if strict_live and blocking_missing else "WARN",
                        "FILINGS_INGEST_PARTIAL",
                        (
                            f"filings ingest covered {item_count}/{expected_item_count} tickers"
                            f"; missing {', '.join(missing) or 'unknown'}."
                        ),
                    )
                )


def _check_live_environment(
    root: Path,
    issues: list[ValidationIssue],
    *,
    strict_live: bool,
) -> None:
    if not strict_live:
        return
    market_source = _ingest_source(root, "market")
    if market_source == "market_alpaca" and not _has_alpaca_credentials():
        issues.append(
            ValidationIssue(
                "ERROR",
                "ALPACA_CREDENTIALS_MISSING",
                "Latest market ingest used Alpaca; APCA_API_KEY_ID and APCA_API_SECRET_KEY "
                "are required for unattended reuse.",
            )
        )
    if not effective_sec_user_agent(root):
        issues.append(
            ValidationIssue(
                "ERROR",
                "SEC_USER_AGENT_MISSING",
                "BCAP_SEC_USER_AGENT or git config user.email is required for unattended "
                "SEC filing ingest.",
            )
        )


def _fixture_source(channel: str, source: str) -> bool:
    return source in {
        f"{channel}_input_file",
        "market_input_file",
        "sec_input_file",
        "mock",
    }


def _ingest_source(root: Path, channel: str) -> str:
    path = root / "state" / "ingest_status.json"
    if not path.exists():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    item = data.get(channel)
    if not isinstance(item, dict):
        return ""
    return scalar_text(item.get("source"))


def _has_alpaca_credentials() -> bool:
    import os

    return bool(os.environ.get("APCA_API_KEY_ID") and os.environ.get("APCA_API_SECRET_KEY"))


def _check_local_positions(
    root: Path,
    tickers: list[str],
    issues: list[ValidationIssue],
    *,
    strict_live: bool,
    positions: list[dict[str, Any]] | None = None,
) -> None:
    if positions is None:
        positions = _load_local_position_items(root, issues)
    if not positions:
        path = root / "state" / "local_positions.yaml"
        if path.exists():
            return
        issues.append(
            ValidationIssue(
                "ERROR" if strict_live else "WARN",
                "LOCAL_POSITIONS_MISSING",
                "state/local_positions.yaml is absent; exposure-aware sizing is unavailable.",
            )
        )
        return
    watchlist = set(tickers)
    market_currencies = _latest_market_currencies(root)
    for item in positions:
        if not isinstance(item, dict):
            continue
        ticker = scalar_text(item.get("ticker")).upper()
        if not ticker:
            continue
        if ticker not in watchlist:
            issues.append(
                ValidationIssue(
                    "WARN",
                    "LOCAL_POSITION_OFF_WATCHLIST",
                    f"{ticker} appears in local positions but not watchlist.",
                )
            )
        if _position_has_value(item) and _position_current_price_missing(item):
            issues.append(
                ValidationIssue(
                    "ERROR" if strict_live else "WARN",
                    "LOCAL_POSITION_PRICE_MISSING",
                    f"{ticker} has exposure but missing current price.",
                )
            )
        if _position_has_value(item) and _position_cost_basis_missing(item):
            issues.append(
                ValidationIssue(
                    "ERROR" if strict_live else "WARN",
                    "LOCAL_POSITION_COST_BASIS_MISSING",
                    f"{ticker} has exposure but missing exact cost basis.",
                )
            )
        if _position_has_value(item):
            position_currency = scalar_text(item.get("currency")).upper()
            market_currency = market_currencies.get(ticker, "")
            if not position_currency:
                issues.append(
                    ValidationIssue(
                        "ERROR" if strict_live else "WARN",
                        "LOCAL_POSITION_CURRENCY_MISSING",
                        f"{ticker} has exposure but missing local position currency.",
                    )
                )
            elif market_currency and position_currency != market_currency:
                issues.append(
                    ValidationIssue(
                        "ERROR" if strict_live else "WARN",
                        "LOCAL_POSITION_CURRENCY_MISMATCH",
                        (
                            f"{ticker} local position currency {position_currency} does not "
                            f"match latest market snapshot currency {market_currency}."
                        ),
                    )
                )


def _position_has_value(item: dict[str, Any]) -> bool:
    quantity = _float_value(item.get("quantity"))
    current_price = _float_value(item.get("current_price"))
    return quantity > 0 or current_price > 0


def _position_uses_placeholder(item: dict[str, Any]) -> bool:
    average_cost = _float_value(item.get("average_cost"))
    current_price = _float_value(item.get("current_price"))
    notes = scalar_text(item.get("notes")).lower()
    return average_cost <= 0 or current_price <= 0 or "placeholder" in notes or "pending" in notes


def _position_current_price_missing(item: dict[str, Any]) -> bool:
    return _float_value(item.get("quantity")) > 0 and _float_value(item.get("current_price")) <= 0


def _position_cost_basis_missing(item: dict[str, Any]) -> bool:
    if _float_value(item.get("quantity")) <= 0:
        return False
    notes = scalar_text(item.get("notes")).lower()
    return (
        _float_value(item.get("average_cost")) <= 0
        or "placeholder" in notes
        or "pending" in notes
    )


def _load_local_position_items(root: Path, issues: list[ValidationIssue]) -> list[dict[str, Any]]:
    path = root / "state" / "local_positions.yaml"
    if not path.exists():
        return []
    try:
        data = load_yaml_file(path)
    except ConfigError as exc:
        issues.append(ValidationIssue("ERROR", "LOCAL_POSITIONS_PARSE_ERROR", str(exc)))
        return []
    positions = data.get("positions", []) if isinstance(data, dict) else []
    if not isinstance(positions, list):
        issues.append(
            ValidationIssue("ERROR", "LOCAL_POSITIONS_PARSE_ERROR", "positions must be a list")
        )
        return []
    return [item for item in positions if isinstance(item, dict)]


def _latest_market_currencies(root: Path) -> dict[str, str]:
    currencies: dict[str, str] = {}
    for record in read_jsonl(root / "state" / "market_snapshots.jsonl"):
        ticker = scalar_text(record.get("ticker")).upper()
        raw_snapshot = record.get("raw_snapshot")
        if not ticker or not isinstance(raw_snapshot, dict):
            continue
        currency = scalar_text(raw_snapshot.get("currency")).upper()
        if currency:
            currencies[ticker] = currency
    return currencies


def _blocking_live_gap_tickers(
    root: Path, missing: list[str], positions: list[dict[str, Any]]
) -> list[str]:
    if not missing:
        return ["unknown"]
    held = {
        scalar_text(item.get("ticker")).upper()
        for item in positions
        if _float_value(item.get("quantity")) > 0 or _float_value(item.get("current_price")) > 0
    }
    blocking: list[str] = []
    for ticker in missing:
        if ticker in held or _is_actionable_decision(root, ticker):
            blocking.append(ticker)
    return blocking


def _is_actionable_decision(root: Path, ticker: str) -> bool:
    metadata, _ = read_markdown_frontmatter(root / "research" / "decisions" / f"{ticker}.md")
    decision = scalar_text(metadata.get("current_decision")).upper()
    return decision in {"BUY_NOW", "ADD_ON_DIP", "TRIM", "SELL", "RESEARCH_REQUIRED"}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [scalar_text(item).upper() for item in value if scalar_text(item)]


def _float_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _freshness_thresholds(root: Path) -> dict[str, int]:
    try:
        config = load_yaml_file(root / "configs" / "signal_thresholds.yaml")
    except ConfigError:
        return {"market": 20, "filings": 240}
    freshness = config.get("sentinel", {}).get("freshness", {})
    if not isinstance(freshness, dict):
        freshness = {}
    return {
        "market": int(freshness.get("market_data_max_age_minutes", 20)),
        "filings": int(freshness.get("filing_data_max_age_minutes", 240)),
    }


def _age_minutes(value: str) -> float | None:
    if not value:
        return None
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        return None
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=ZoneInfo("America/Toronto"))
    return (datetime.now(ZoneInfo("America/Toronto")) - timestamp).total_seconds() / 60
