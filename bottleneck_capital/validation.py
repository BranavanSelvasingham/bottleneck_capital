from __future__ import annotations

import json
import subprocess
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
from bottleneck_capital.research_handoffs import (
    ALLOWED_CAUSE_STATUSES,
    ALLOWED_PROVISIONAL_BIASES,
    ALLOWED_THESIS_STATUSES,
    ALLOWED_VALUATION_STATUSES,
    APPLICATION_RECORD_TYPE,
    HANDOFF_RECORD_TYPE,
    PRIVATE_KEYS,
    applied_handoff_ids,
    handoff_id_for,
    memo_tickers,
)
from bottleneck_capital.research_handoffs import (
    ALLOWED_DECISIONS as HANDOFF_ALLOWED_DECISIONS,
)
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
    _check_position_privacy(root, issues)
    _check_duplicates(tickers, issues)
    _check_ticker_files(root, tickers, issues)
    _check_generated_wiring(root, tickers, issues)
    _check_decisions(root, tickers, issues)
    _check_research_handoffs(root, tickers, issues, strict_live=strict_live)
    _check_research_blocks(root, issues, strict_live=strict_live)
    _check_market_regime(root, issues, strict_live=strict_live)
    _check_portfolio_model(root, watchlist, issues)
    _check_signal_events(root, issues)
    _check_event_inputs(root, issues, strict_live=strict_live)
    _check_ingest_freshness(root, issues, strict_live=strict_live, positions=position_items)
    _check_live_environment(root, issues, strict_live=strict_live)
    _check_local_positions(root, tickers, issues, strict_live=strict_live, positions=position_items)
    return issues


def _check_position_privacy(root: Path, issues: list[ValidationIssue]) -> None:
    private_paths = (
        "state/local_positions.yaml",
        "reports/local_exposure.md",
        "reports/local_portfolio_boards",
        "state/signal_events.jsonl",
        "reports/action_boards",
        "reports/daily_decision_boards",
        "reports/sunday_preps",
    )
    is_git_worktree = (root / ".git").exists()
    ignore_path = root / ".gitignore"
    ignore_text = ignore_path.read_text(encoding="utf-8") if ignore_path.exists() else ""
    required_patterns = (
        "state/local_positions.yaml",
        "reports/local_exposure.md",
        "reports/local_portfolio_boards/",
        "state/signal_events.jsonl",
        "reports/action_boards/",
        "reports/daily_decision_boards/",
        "reports/sunday_preps/",
    )
    missing = (
        [pattern for pattern in required_patterns if pattern not in ignore_text]
        if is_git_worktree
        else []
    )
    if missing:
        issues.append(
            ValidationIssue(
                "ERROR",
                "POSITION_PRIVACY_IGNORE_GAP",
                "Missing private-path ignore rules: " + ", ".join(missing),
            )
        )

    try:
        result = (
            subprocess.run(
                ["git", "ls-files", "--", *private_paths],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
            if is_git_worktree
            else None
        )
    except OSError:
        result = None
    tracked = result.stdout.splitlines() if result and result.returncode == 0 else []
    if tracked:
        issues.append(
            ValidationIssue(
                "ERROR",
                "POSITION_PRIVACY_TRACKED_FILE",
                "Private position-derived files are tracked: " + ", ".join(tracked),
            )
        )

    for directory in ("assets", "decisions"):
        for path in sorted((root / "research" / directory).glob("*.md")):
            metadata, _ = read_markdown_frontmatter(path)
            try:
                weight = float(metadata.get("current_position_weight_pct") or 0)
            except (TypeError, ValueError):
                weight = 0
            if weight > 0:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "POSITION_PRIVACY_TRACKED_WEIGHT",
                        f"{directory}/{path.name} contains a committed current position weight.",
                    )
                )


def _check_portfolio_model(
    root: Path,
    watchlist: list[dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    path = root / "configs" / "portfolio.yaml"
    if not path.exists():
        return
    data = load_yaml_file(path)
    config = data.get("portfolio", {}) if isinstance(data, dict) else {}
    if not isinstance(config, dict):
        issues.append(
            ValidationIssue(
                "ERROR",
                "PORTFOLIO_CONFIG_INVALID",
                "configs/portfolio.yaml must define a portfolio mapping.",
            )
        )
        return
    profiles = config.get("sleeve_factor_profiles", {})
    mapped = set(profiles) if isinstance(profiles, dict) else set()
    missing = sorted(
        {
            scalar_text(item.get("sleeve"))
            for item in watchlist
            if scalar_text(item.get("sleeve")) not in mapped
        }
    )
    if missing:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PORTFOLIO_FACTOR_MAP_GAP",
                "Missing sleeve factor profiles: " + ", ".join(missing),
            )
        )
    scenarios = config.get("scenarios", {})
    if not isinstance(scenarios, dict) or not scenarios:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PORTFOLIO_SCENARIOS_MISSING",
                "configs/portfolio.yaml must define at least one scenario.",
            )
        )


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


def _check_research_handoffs(
    root: Path,
    tickers: list[str],
    issues: list[ValidationIssue],
    *,
    strict_live: bool,
) -> None:
    path = root / "state" / "research_handoffs.jsonl"
    records = read_jsonl(path)
    handoffs: dict[str, dict[str, Any]] = {}
    applications: list[dict[str, Any]] = []
    ticker_set = {ticker.upper() for ticker in tickers}
    for record in records:
        record_type = scalar_text(record.get("record_type"))
        if record_type == HANDOFF_RECORD_TYPE:
            handoff_id = scalar_text(record.get("handoff_id"))
            if not handoff_id:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "RESEARCH_HANDOFF_ID_MISSING",
                        "Research handoff record has no handoff_id.",
                    )
                )
                continue
            if handoff_id in handoffs:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "RESEARCH_HANDOFF_DUPLICATE",
                        f"Duplicate research handoff id: {handoff_id}",
                    )
                )
            handoffs[handoff_id] = record
            _check_research_handoff_record(root, ticker_set, record, issues)
        elif record_type == APPLICATION_RECORD_TYPE:
            applications.append(record)
        else:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "RESEARCH_HANDOFF_RECORD_TYPE_INVALID",
                    f"Unknown research handoff record type: {record_type or '<missing>'}",
                )
            )

    for application in applications:
        applied_id = scalar_text(application.get("applied_handoff_id"))
        decision = scalar_text(application.get("decision")).upper()
        if applied_id not in handoffs:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "RESEARCH_HANDOFF_APPLICATION_ORPHANED",
                    f"Application references unknown handoff: {applied_id or '<missing>'}",
                )
            )
        if decision not in HANDOFF_ALLOWED_DECISIONS:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "RESEARCH_HANDOFF_APPLICATION_DECISION_INVALID",
                    f"Application for {applied_id} has invalid decision {decision or '<missing>'}.",
                )
            )
        _check_private_handoff_fields(application, issues)

    applied = applied_handoff_ids(records)
    for handoff_id, record in handoffs.items():
        if handoff_id in applied:
            continue
        issues.append(
            ValidationIssue(
                "ERROR" if strict_live else "WARN",
                "PENDING_RESEARCH_HANDOFF",
                (
                    f"{record.get('ticker')} has unapplied research handoff {handoff_id} "
                    f"from {record.get('memo_path')}; Portfolio PM must record an outcome."
                ),
            )
        )

    for memo_path in sorted((root / "research" / "memos").glob("*.md")):
        relative = memo_path.relative_to(root).as_posix()
        for ticker in memo_tickers(memo_path, ticker_set):
            expected_id = handoff_id_for(ticker, relative)
            if expected_id not in handoffs:
                issues.append(
                    ValidationIssue(
                        "ERROR" if strict_live else "WARN",
                        "RESEARCH_MEMO_HANDOFF_MISSING",
                        f"{relative} has no structured Portfolio PM handoff for {ticker}.",
                    )
                )

    if handoffs:
        _check_pm_board_freshness(root, handoffs, issues, strict_live=strict_live)


def _check_research_handoff_record(
    root: Path,
    tickers: set[str],
    record: dict[str, Any],
    issues: list[ValidationIssue],
) -> None:
    handoff_id = scalar_text(record.get("handoff_id"))
    ticker = scalar_text(record.get("ticker")).upper()
    memo_path_text = scalar_text(record.get("memo_path"))
    if ticker not in tickers:
        issues.append(
            ValidationIssue(
                "ERROR",
                "RESEARCH_HANDOFF_TICKER_INVALID",
                f"Handoff {handoff_id} references unknown ticker {ticker or '<missing>'}.",
            )
        )
    _check_handoff_choice(
        handoff_id,
        "cause_status",
        scalar_text(record.get("cause_status")),
        ALLOWED_CAUSE_STATUSES,
        issues,
    )
    _check_handoff_choice(
        handoff_id,
        "thesis_status",
        scalar_text(record.get("thesis_status")),
        ALLOWED_THESIS_STATUSES,
        issues,
    )
    _check_handoff_choice(
        handoff_id,
        "valuation_status",
        scalar_text(record.get("valuation_status")),
        ALLOWED_VALUATION_STATUSES,
        issues,
    )
    _check_handoff_choice(
        handoff_id,
        "provisional_bias",
        scalar_text(record.get("provisional_bias")),
        ALLOWED_PROVISIONAL_BIASES,
        issues,
    )
    if not scalar_text(record.get("summary")):
        issues.append(
            ValidationIssue(
                "ERROR",
                "RESEARCH_HANDOFF_SUMMARY_MISSING",
                f"Handoff {handoff_id} has no summary.",
            )
        )
    try:
        confidence = float(record.get("confidence"))
    except (TypeError, ValueError):
        confidence = -1
    if not 0 <= confidence <= 100:
        issues.append(
            ValidationIssue(
                "ERROR",
                "RESEARCH_HANDOFF_CONFIDENCE_INVALID",
                f"Handoff {handoff_id} confidence must be between 0 and 100.",
            )
        )
    memo_path = (root / memo_path_text).resolve()
    memo_root = (root / "research" / "memos").resolve()
    try:
        memo_path.relative_to(memo_root)
    except ValueError:
        issues.append(
            ValidationIssue(
                "ERROR",
                "RESEARCH_HANDOFF_MEMO_PATH_INVALID",
                f"Handoff {handoff_id} memo is outside research/memos: {memo_path_text}",
            )
        )
    else:
        if not memo_path.exists():
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "RESEARCH_HANDOFF_MEMO_MISSING",
                    f"Handoff {handoff_id} memo does not exist: {memo_path_text}",
                )
            )
    if ticker:
        decision_path = root / "research" / "decisions" / f"{ticker}.md"
        metadata, _ = read_markdown_frontmatter(decision_path)
        last_updated = scalar_text(metadata.get("last_updated"))[:10]
        memo_date = scalar_text(record.get("memo_date"))[:10]
        if memo_date and (not last_updated or last_updated < memo_date):
            issues.append(
                ValidationIssue(
                    "WARN",
                    "RESEARCH_DECISION_STALE",
                    (
                        f"{ticker} decision last_updated {last_updated or 'missing'} predates "
                        f"research handoff memo {memo_date}."
                    ),
                )
            )
    _check_private_handoff_fields(record, issues)


def _check_handoff_choice(
    handoff_id: str,
    field: str,
    value: str,
    allowed: set[str],
    issues: list[ValidationIssue],
) -> None:
    if value not in allowed:
        issues.append(
            ValidationIssue(
                "ERROR",
                "RESEARCH_HANDOFF_FIELD_INVALID",
                (
                    f"Handoff {handoff_id} has invalid {field} {value or '<missing>'}; "
                    f"expected one of {', '.join(sorted(allowed))}."
                ),
            )
        )


def _check_private_handoff_fields(
    record: dict[str, Any],
    issues: list[ValidationIssue],
) -> None:
    private = PRIVATE_KEYS & {str(key).lower() for key in record}
    if private:
        issues.append(
            ValidationIssue(
                "ERROR",
                "RESEARCH_HANDOFF_PRIVACY_GAP",
                "Research handoff contains private position fields: "
                + ", ".join(sorted(private)),
            )
        )


def _check_pm_board_freshness(
    root: Path,
    handoffs: dict[str, dict[str, Any]],
    issues: list[ValidationIssue],
    *,
    strict_live: bool,
) -> None:
    boards = sorted((root / "reports" / "daily_decision_boards").glob("*.md"))
    latest_board_date = boards[-1].stem[:10] if boards else ""
    latest_handoff_date = max(
        scalar_text(record.get("created_at"))[:10]
        or scalar_text(record.get("memo_date"))[:10]
        for record in handoffs.values()
    )
    if not latest_board_date or latest_board_date < latest_handoff_date:
        issues.append(
            ValidationIssue(
                "ERROR" if strict_live else "WARN",
                "PORTFOLIO_PM_BOARD_STALE",
                (
                    f"Latest decision board {latest_board_date or 'missing'} predates "
                    f"research handoffs through {latest_handoff_date}."
                ),
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


def _check_market_regime(
    root: Path,
    issues: list[ValidationIssue],
    *,
    strict_live: bool,
) -> None:
    from bottleneck_capital.market_regime import assess_market_regime, regime_config

    if not (root / "configs" / "regime.yaml").exists():
        return
    config = regime_config(root)
    exposures = config.get("sleeve_channel_exposures", {})
    configured_sleeves = set(exposures) if isinstance(exposures, dict) else set()
    missing_sleeves = sorted(
        {
            scalar_text(item.get("sleeve"))
            for item in load_watchlist(root)
            if scalar_text(item.get("sleeve")) not in configured_sleeves
        }
    )
    if missing_sleeves:
        issues.append(
            ValidationIssue(
                "ERROR" if strict_live else "WARN",
                "REGIME_EXPOSURE_MAP_GAP",
                "Missing regime channel exposures for sleeves: "
                + ", ".join(missing_sleeves),
            )
        )
    regime = assess_market_regime(root)
    if regime.source_status in {"CROSS_ASSET_ONLY", "MISSING"}:
        issues.append(
            ValidationIssue(
                "ERROR" if strict_live else "WARN",
                "GEOPOLITICAL_CONTEXT_GAP",
                (
                    "No fresh structured geopolitical regime heartbeat is active. "
                    "Record the latest escalation, ceasefire, de-escalation, or calm review "
                    "before clearing new entries."
                ),
            )
        )
    if regime.state == "UNKNOWN" or not regime.fresh:
        issues.append(
            ValidationIssue(
                "ERROR" if strict_live else "WARN",
                "MARKET_REGIME_CONTEXT_GAP",
                (
                    f"Market regime is {regime.state} with {regime.source_status} sources; "
                    f"latest context {regime.latest_context_at}. New BUY_NOW/ADD_ON_DIP "
                    "entries must remain gated until cross-asset context is fresh."
                ),
            )
        )
    if regime.state in {"CONFLICT_ESCALATION", "MARKET_STRESS"} or (
        regime.geopolitical_status in {"conflict", "escalating", "renewed_escalation"}
    ):
        issues.append(
            ValidationIssue(
                "WARN",
                "ADVERSE_MARKET_REGIME",
                (
                    f"{regime.state} regime is active at {regime.confidence:.0f}% confidence "
                    f"with {regime.market_confirmation} market confirmation; "
                    "apply ticker channel exposures and entry gates before deploying capital."
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
