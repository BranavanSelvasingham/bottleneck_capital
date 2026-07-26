from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from bottleneck_capital.decision_engine import write_action_board
from bottleneck_capital.ingest import (
    IngestError,
    IngestResult,
    clear_manual_event,
    ingest_filings,
    ingest_market,
    write_manual_event,
)
from bottleneck_capital.io import read_jsonl, scalar_text
from bottleneck_capital.positions import LOCAL_POSITIONS_PATH, refresh_position_prices
from bottleneck_capital.sentinel import run_sentinel
from bottleneck_capital.signal_events import (
    SignalEventError,
    active_signal_events,
    event_id_for_record,
    resolve_signal_events,
)
from bottleneck_capital.validation import ValidationIssue, validate_project


@dataclass(frozen=True)
class LiveCheckResult:
    market: IngestResult | None
    filings: IngestResult | None
    signal_count: int
    active_high_priority_count: int
    action_board_path: Path | None
    validation_issues: list[ValidationIssue]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


def run_live_check(
    root: Path,
    *,
    market_provider: str = "auto",
    market_input: Path | None = None,
    market_symbols: list[str] | None = None,
    company_tickers_input: Path | None = None,
    submissions_dir: Path | None = None,
    filing_lookback_days: int = 3,
    sec_user_agent: str = "",
    strict_validate: bool = False,
    write_board: bool = True,
    filing_mode: str = "auto",
) -> LiveCheckResult:
    warnings: list[str] = []
    errors: list[str] = []
    market: IngestResult | None = None
    try:
        market = ingest_market(
            root,
            provider=market_provider,
            input_path=market_input,
            symbols=market_symbols,
        )
        warnings.extend(market.warnings)
        _refresh_local_position_prices(root, warnings)
    except IngestError as exc:
        errors.append(f"market ingest failed: {exc}")

    if filing_mode not in {"auto", "always", "skip"}:
        raise ValueError(f"Unsupported filing mode: {filing_mode}")
    filings: IngestResult | None = None
    skip_filings = filing_mode == "skip" or (
        filing_mode == "auto" and _filing_backoff_active(root)
    )
    if skip_filings:
        warnings.append(
            "filings ingest skipped due to active SEC 403 backoff or explicit collector policy; "
            "configure an approved SEC mirror/proxy or filing feed to recover coverage"
        )
    else:
        try:
            filings = ingest_filings(
                root,
                company_tickers_input=company_tickers_input,
                submissions_dir=submissions_dir,
                lookback_days=filing_lookback_days,
                sec_user_agent=sec_user_agent,
            )
            warnings.extend(filings.warnings)
            clear_manual_event(root, "filing_data_gap:daily")
        except IngestError as exc:
            warning = f"filings ingest skipped: {exc}"
            warnings.append(warning)
            write_manual_event(
                root,
                {
                    "ticker": "BCAP",
                    "event_type": "filing_data_gap",
                    "event_class": "filing_data_gap",
                    "source": "filing_ingest",
                    "summary": (
                        "Filing ingest did not complete; 13F/13G/8-K/10-Q/10-K and "
                        f"company filing coverage is incomplete. {warning}"
                    ),
                    "dedupe_key": "filing_data_gap:daily",
                },
            )

    signal_records = run_sentinel(root)
    _resolve_recovered_data_gaps(root, market=market, filings=filings)
    active_records = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    active_high = [
        record
        for record in active_records
        if scalar_text(record.get("priority")) in {"high", "critical"}
        and scalar_text(record.get("event_class")) != "noise"
    ]
    action_board_path = write_action_board(root) if write_board else None
    validation_issues = validate_project(root, strict_live=strict_validate)
    return LiveCheckResult(
        market=market,
        filings=filings,
        signal_count=len(signal_records),
        active_high_priority_count=len(active_high),
        action_board_path=action_board_path,
        validation_issues=validation_issues,
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def _filing_backoff_active(root: Path) -> bool:
    recovery_env = (
        "BCAP_SEC_COMPANY_TICKERS_URL",
        "BCAP_SEC_SUBMISSIONS_URL_TEMPLATE",
        "BCAP_SEC_BROWSE_ATOM_URL",
        "BCAP_FILING_EVENTS_URL",
    )
    if any(os.environ.get(name) for name in recovery_env):
        return False
    active = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    for record in active:
        if scalar_text(record.get("event_class")) != "filing_data_gap":
            continue
        summary = scalar_text(record.get("summary")).lower()
        raw = record.get("raw_event")
        if isinstance(raw, dict):
            summary += " " + scalar_text(raw.get("summary")).lower()
        if any(marker in summary for marker in ("403", "forbidden", "backoff")):
            return True
    return False


def _resolve_recovered_data_gaps(
    root: Path,
    *,
    market: IngestResult | None,
    filings: IngestResult | None,
) -> None:
    active_records = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    if filings is not None:
        _resolve_matching_gaps(
            root,
            active_records,
            event_class="filing_data_gap",
            reason="Filing ingest succeeded; operational filing data gap recovered.",
        )
    if market is None:
        return
    missing_tickers = _latest_missing_market_tickers(root)
    for record in active_records:
        if scalar_text(record.get("event_class")) != "market_data_gap":
            continue
        ticker = scalar_text(record.get("ticker")).upper()
        if ticker in missing_tickers:
            continue
        _resolve_event_id(
            root,
            event_id_for_record(record),
            "Market ingest now covers this ticker; operational market data gap recovered.",
        )


def _resolve_matching_gaps(
    root: Path,
    records: list[dict],
    *,
    event_class: str,
    reason: str,
) -> None:
    for record in records:
        if scalar_text(record.get("event_class")) == event_class:
            _resolve_event_id(root, event_id_for_record(record), reason)


def _resolve_event_id(root: Path, event_id: str, reason: str) -> None:
    try:
        resolve_signal_events(root, event_id=event_id, reason=reason)
    except SignalEventError:
        return


def _latest_missing_market_tickers(root: Path) -> set[str]:
    path = root / "state" / "ingest_status.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    market = data.get("market")
    if not isinstance(market, dict):
        return set()
    missing = market.get("missing_tickers")
    if not isinstance(missing, list):
        return set()
    return {scalar_text(ticker).upper() for ticker in missing if scalar_text(ticker)}


def _refresh_local_position_prices(root: Path, warnings: list[str]) -> None:
    if not (root / LOCAL_POSITIONS_PATH).exists():
        return
    try:
        result = refresh_position_prices(root)
    except Exception as exc:
        warnings.append(f"position price refresh skipped: {exc}")
        return
    if result.missing_tickers:
        warnings.append(
            "position price refresh missing current prices for "
            f"{', '.join(result.missing_tickers)}"
        )
