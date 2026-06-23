from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path
from typing import Any

from bottleneck_capital.baseline import write_all_wave_baseline
from bottleneck_capital.decision_engine import (
    compile_decisions,
    create_dip_investigation,
    write_action_board,
    write_daily_board,
)
from bottleneck_capital.ingest import IngestError, ingest_filings, ingest_market
from bottleneck_capital.initialize import run_initialization
from bottleneck_capital.io import read_jsonl
from bottleneck_capital.live_check import LiveCheckResult, run_live_check
from bottleneck_capital.positions import (
    initialize_local_positions,
    refresh_position_prices,
    update_local_position,
    write_exposure_report,
)
from bottleneck_capital.readiness import is_live_ready, write_live_readiness_report
from bottleneck_capital.runtime import RunLockError, record_run, run_lock
from bottleneck_capital.sentinel import run_sentinel
from bottleneck_capital.signal_events import (
    SignalEventError,
    active_signal_events,
    event_id_for_record,
    resolve_signal_events,
)
from bottleneck_capital.validation import has_errors, render_validation, validate_project
from bottleneck_capital.value_chain import (
    serve_value_chain_visualizer,
    write_value_chain_visualizer,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bcap")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sentinel_parser = subparsers.add_parser("sentinel", help="Sentinel commands.")
    sentinel_subparsers = sentinel_parser.add_subparsers(dest="sentinel_command", required=True)
    sentinel_run = sentinel_subparsers.add_parser("run", help="Classify latest event data.")
    sentinel_run.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON/JSONL event file.",
    )

    ingest_parser = subparsers.add_parser("ingest", help="Live/input ingestion commands.")
    ingest_subparsers = ingest_parser.add_subparsers(dest="ingest_command", required=True)
    ingest_market_parser = ingest_subparsers.add_parser(
        "market", help="Ingest market snapshots into state/latest_events.jsonl."
    )
    ingest_market_parser.add_argument("--provider", default="auto", help="Market provider.")
    ingest_market_parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional market snapshot JSON/JSONL fixture or manual input.",
    )
    ingest_market_parser.add_argument(
        "--symbols",
        default="",
        help="Optional comma-separated ticker subset.",
    )
    ingest_filings_parser = ingest_subparsers.add_parser(
        "filings", help="Ingest SEC filings into state/latest_events.jsonl."
    )
    ingest_filings_parser.add_argument(
        "--company-tickers-input",
        type=Path,
        default=None,
        help="Optional SEC company_tickers.json fixture.",
    )
    ingest_filings_parser.add_argument(
        "--submissions-dir",
        type=Path,
        default=None,
        help="Optional directory of SEC CIK##########.json submission fixtures.",
    )
    ingest_filings_parser.add_argument("--lookback-days", type=int, default=3)
    ingest_filings_parser.add_argument(
        "--sec-user-agent",
        default="",
        help="SEC-compliant User-Agent. Defaults to BCAP_SEC_USER_AGENT.",
    )
    live_check_parser = subparsers.add_parser(
        "live-check",
        help="Run market ingest, filing ingest, sentinel, action board, and validation.",
    )
    live_check_parser.add_argument("--market-provider", default="auto")
    live_check_parser.add_argument(
        "--market-input",
        type=Path,
        default=None,
        help="Optional market snapshot fixture/manual input.",
    )
    live_check_parser.add_argument(
        "--market-symbols",
        default="",
        help="Optional comma-separated ticker subset for market ingest.",
    )
    live_check_parser.add_argument(
        "--company-tickers-input",
        type=Path,
        default=None,
        help="Optional SEC company_tickers.json fixture.",
    )
    live_check_parser.add_argument(
        "--submissions-dir",
        type=Path,
        default=None,
        help="Optional directory of SEC CIK##########.json submission fixtures.",
    )
    live_check_parser.add_argument("--filing-lookback-days", type=int, default=3)
    live_check_parser.add_argument(
        "--sec-user-agent",
        default="",
        help="SEC-compliant User-Agent. Defaults to BCAP_SEC_USER_AGENT.",
    )
    live_check_parser.add_argument(
        "--strict-validate",
        action="store_true",
        help="Treat live-ingestion gaps as validation errors.",
    )

    subparsers.add_parser("compile-decisions", help="Evaluate and rewrite ticker decision files.")
    subparsers.add_parser("daily-board", help="Write the daily decision board.")
    subparsers.add_parser("action-board", help="Write the current actionable-step board.")
    validate_parser = subparsers.add_parser(
        "validate", help="Validate Bottleneck Capital operating invariants."
    )
    validate_parser.add_argument(
        "--strict-live",
        action="store_true",
        help="Treat live-ingestion gaps as errors.",
    )
    subparsers.add_parser(
        "live-readiness",
        help="Write a strict-live readiness report with recovery actions.",
    )
    subparsers.add_parser(
        "resume-check",
        help="Write readiness and exit 0 only when market-day automation can resume.",
    )

    signal_parser = subparsers.add_parser("signal", help="Signal event commands.")
    signal_subparsers = signal_parser.add_subparsers(dest="signal_command", required=True)
    signal_subparsers.add_parser("list", help="List active signal events.")
    signal_resolve = signal_subparsers.add_parser("resolve", help="Resolve active signal events.")
    signal_resolve.add_argument("--event-id", default="", help="Specific event id to resolve.")
    signal_resolve.add_argument("--ticker", default="", help="Resolve active events for ticker.")
    signal_resolve.add_argument("--event-class", default="", help="Resolve only this event class.")
    signal_resolve.add_argument(
        "--reason",
        required=True,
        help="Resolution rationale to append to state/signal_events.jsonl.",
    )
    value_chain_parser = subparsers.add_parser(
        "value-chain", help="Write the Jensen five-layer value-chain visualizer."
    )
    value_chain_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional HTML output path. Relative paths are resolved from the project root.",
    )
    value_chain_parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve the visualizer locally with an in-page update endpoint.",
    )
    value_chain_parser.add_argument("--host", default="127.0.0.1", help="Host for --serve.")
    value_chain_parser.add_argument("--port", type=int, default=8765, help="Port for --serve.")
    subparsers.add_parser("initialize-run", help="Write initialization baseline and agent packets.")
    subparsers.add_parser("baseline-decisions", help="Write all-wave baseline ticker decisions.")
    positions_init = subparsers.add_parser(
        "positions-init", help="Create the gitignored local positions ledger."
    )
    positions_init.add_argument("--overwrite", action="store_true", help="Replace existing ledger.")
    positions_refresh = subparsers.add_parser(
        "positions-refresh-prices",
        help="Refresh current prices in the local positions ledger from market snapshots.",
    )
    positions_refresh.add_argument(
        "--positions",
        type=Path,
        default=None,
        help="Optional positions YAML path.",
    )
    positions_set = subparsers.add_parser(
        "positions-set",
        help="Update one ticker in the local positions ledger.",
    )
    positions_set.add_argument("--ticker", required=True)
    positions_set.add_argument("--quantity", type=float, default=None)
    positions_set.add_argument("--average-cost", type=float, default=None)
    positions_set.add_argument("--current-price", type=float, default=None)
    positions_set.add_argument("--currency", default=None)
    positions_set.add_argument("--account", default=None)
    positions_set.add_argument("--notes", default=None)
    positions_set.add_argument(
        "--positions",
        type=Path,
        default=None,
        help="Optional positions YAML path.",
    )
    exposure_parser = subparsers.add_parser(
        "exposure", help="Write a local exposure report from gitignored positions."
    )
    exposure_parser.add_argument(
        "--positions",
        type=Path,
        default=None,
        help="Optional positions YAML path.",
    )

    dip_parser = subparsers.add_parser("dip-investigate", help="Create a dip investigation memo.")
    dip_parser.add_argument("--ticker", required=True, help="Ticker to investigate.")

    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.command == "sentinel":
        try:
            records = _logged(
                root,
                process="sentinel",
                command="sentinel run",
                fn=lambda: run_sentinel(root, input_path=args.input),
            )
        except RunLockError as exc:
            print(exc)
            return 1
        print(f"Wrote {len(records)} signal event(s) to {root / 'state' / 'signal_events.jsonl'}")
        return 0
    if args.command == "ingest":
        if args.ingest_command == "market":
            symbols = [
                symbol.strip().upper()
                for symbol in args.symbols.split(",")
                if symbol.strip()
            ]
            try:
                result = _logged(
                    root,
                    process="ingest-market",
                    command="ingest market",
                    fn=lambda: ingest_market(
                        root,
                        provider=args.provider,
                        input_path=args.input,
                        symbols=symbols or None,
                    ),
                )
            except (IngestError, RunLockError) as exc:
                print(exc)
                return 1
            print(
                f"Wrote {result.event_count} market event(s) to {result.output_path}; "
                f"aggregate {result.aggregate_path}"
            )
            return 0
        if args.ingest_command == "filings":
            try:
                result = _logged(
                    root,
                    process="ingest-filings",
                    command="ingest filings",
                    fn=lambda: ingest_filings(
                        root,
                        company_tickers_input=args.company_tickers_input,
                        submissions_dir=args.submissions_dir,
                        lookback_days=args.lookback_days,
                        sec_user_agent=args.sec_user_agent,
                    ),
                )
            except (IngestError, RunLockError) as exc:
                print(exc)
                return 1
            for warning in result.warnings:
                print(f"warning: {warning}")
            print(
                f"Wrote {result.event_count} filing event(s) to {result.output_path}; "
                f"aggregate {result.aggregate_path}"
            )
            return 0
    if args.command == "live-check":
        symbols = [
            symbol.strip().upper()
            for symbol in args.market_symbols.split(",")
            if symbol.strip()
        ]
        try:
            result = _logged(
                root,
                process="live-check",
                command="live-check",
                fn=lambda: run_live_check(
                    root,
                    market_provider=args.market_provider,
                    market_input=args.market_input,
                    market_symbols=symbols or None,
                    company_tickers_input=args.company_tickers_input,
                    submissions_dir=args.submissions_dir,
                    filing_lookback_days=args.filing_lookback_days,
                    sec_user_agent=args.sec_user_agent,
                    strict_validate=args.strict_validate,
                ),
            )
        except RunLockError as exc:
            print(exc)
            return 1
        print(_render_live_check_result(result), end="")
        return 1 if result.errors or has_errors(result.validation_issues) else 0
    if args.command == "compile-decisions":
        results = compile_decisions(root)
        print(f"Compiled {len(results)} decision file(s).")
        return 0
    if args.command == "daily-board":
        try:
            path = _logged(
                root,
                process="daily-board",
                command="daily-board",
                fn=lambda: write_daily_board(root),
            )
        except RunLockError as exc:
            print(exc)
            return 1
        print(path)
        return 0
    if args.command == "action-board":
        try:
            path = _logged(
                root,
                process="action-board",
                command="action-board",
                fn=lambda: write_action_board(root),
            )
        except RunLockError as exc:
            print(exc)
            return 1
        print(path)
        return 0
    if args.command == "validate":
        issues = validate_project(root, strict_live=args.strict_live)
        print(render_validation(issues), end="")
        return 1 if has_errors(issues) else 0
    if args.command == "live-readiness":
        path = write_live_readiness_report(root)
        print(path)
        return 0
    if args.command == "resume-check":
        path = write_live_readiness_report(root)
        ready = is_live_ready(root)
        print(path)
        print("READY" if ready else "NOT_READY")
        return 0 if ready else 1
    if args.command == "signal":
        signal_path = root / "state" / "signal_events.jsonl"
        if args.signal_command == "list":
            for record in active_signal_events(read_jsonl(signal_path)):
                print(
                    "\t".join(
                        [
                            event_id_for_record(record),
                            str(record.get("ticker", "")),
                            str(record.get("event_class", "")),
                            str(record.get("priority", "")),
                            str(record.get("summary", "")),
                        ]
                    )
                )
            return 0
        if args.signal_command == "resolve":
            try:
                records = resolve_signal_events(
                    root,
                    event_id=args.event_id,
                    ticker=args.ticker,
                    event_class=args.event_class,
                    reason=args.reason,
                )
            except SignalEventError as exc:
                print(exc)
                return 1
            print(f"Resolved {len(records)} signal event(s).")
            return 0
    if args.command == "value-chain":
        if args.serve:
            serve_value_chain_visualizer(root, host=args.host, port=args.port)
            return 0
        path = write_value_chain_visualizer(root, output_path=args.output)
        print(path)
        return 0
    if args.command == "initialize-run":
        paths = run_initialization(root)
        for path in paths:
            print(path)
        return 0
    if args.command == "baseline-decisions":
        paths = write_all_wave_baseline(root)
        print(f"Wrote {len(paths)} baseline file(s).")
        return 0
    if args.command == "positions-init":
        path = initialize_local_positions(root, overwrite=args.overwrite)
        print(path)
        return 0
    if args.command == "positions-refresh-prices":
        result = refresh_position_prices(root, positions_path=args.positions)
        print(
            f"{result.path}\n"
            f"updated={result.updated_count}\n"
            f"missing={','.join(result.missing_tickers)}"
        )
        return 1 if result.missing_tickers else 0
    if args.command == "positions-set":
        result = update_local_position(
            root,
            ticker=args.ticker,
            quantity=args.quantity,
            average_cost=args.average_cost,
            current_price=args.current_price,
            currency=args.currency,
            account=args.account,
            notes=args.notes,
            positions_path=args.positions,
        )
        print(
            f"{result.path}\n"
            f"ticker={result.ticker}\n"
            f"created={str(result.created).lower()}"
        )
        return 0
    if args.command == "exposure":
        path = write_exposure_report(root, positions_path=args.positions)
        print(path)
        return 0
    if args.command == "dip-investigate":
        path = create_dip_investigation(root, args.ticker)
        print(path)
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


def _logged(
    root: Path,
    *,
    process: str,
    command: str,
    fn: Callable[[], Any],
) -> Any:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    started_at = datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
    try:
        with run_lock(root, "scheduled-write"), run_lock(root, process):
            result = fn()
    except RunLockError as exc:
        record_run(
            root,
            process=process,
            command=command,
            status="conflict",
            started_at=started_at,
            error=str(exc),
        )
        raise
    except Exception as exc:
        record_run(
            root,
            process=process,
            command=command,
            status="error",
            started_at=started_at,
            error=str(exc),
        )
        raise
    outputs = []
    if hasattr(result, "output_path"):
        outputs.append(str(result.output_path))
    if hasattr(result, "aggregate_path"):
        outputs.append(str(result.aggregate_path))
    if isinstance(result, Path):
        outputs.append(str(result))
    if hasattr(result, "action_board_path"):
        outputs.append(str(result.action_board_path))
    if hasattr(result, "market") and result.market is not None:
        outputs.append(str(result.market.output_path))
    if hasattr(result, "filings") and result.filings is not None:
        outputs.append(str(result.filings.output_path))
    warnings = []
    if hasattr(result, "warnings"):
        warnings = [str(warning) for warning in result.warnings]
    errors = []
    if hasattr(result, "errors"):
        errors = [str(error) for error in result.errors]
    validation_error = False
    if hasattr(result, "validation_issues"):
        validation_error = has_errors(result.validation_issues)
        if validation_error and not errors:
            errors.append("validation errors present")
    record_run(
        root,
        process=process,
        command=command,
        status="error" if errors else "success",
        started_at=started_at,
        outputs=outputs,
        warnings=warnings,
        error="; ".join(errors),
    )
    return result


def _render_live_check_result(result: LiveCheckResult) -> str:
    lines = []
    if result.market is None:
        lines.append("Market ingest: failed")
    else:
        lines.append(
            f"Market ingest: {result.market.event_count} event(s), "
            f"{result.market.output_path}"
        )
    if result.filings is None:
        lines.append("Filing ingest: skipped")
    else:
        lines.append(
            f"Filing ingest: {result.filings.event_count} event(s), "
            f"{result.filings.output_path}"
        )
    lines.append(f"Sentinel: {result.signal_count} new signal event(s)")
    lines.append(f"Active high-priority signals: {result.active_high_priority_count}")
    lines.append(f"Action board: {result.action_board_path}")
    for error in result.errors:
        lines.append(f"error: {error}")
    for warning in result.warnings:
        lines.append(f"warning: {warning}")
    lines.append(render_validation(result.validation_issues).rstrip("\n"))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
