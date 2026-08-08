from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from bottleneck_capital.baseline import write_all_wave_baseline
from bottleneck_capital.daily_digest import write_daily_digest
from bottleneck_capital.decision_engine import (
    compile_decisions,
    create_dip_investigation,
    write_action_board,
    write_daily_board,
)
from bottleneck_capital.dip_review import write_dip_review
from bottleneck_capital.ingest import (
    IngestError,
    ingest_filings,
    ingest_market,
    write_manual_event,
)
from bottleneck_capital.initialize import run_initialization
from bottleneck_capital.io import read_jsonl, scalar_text
from bottleneck_capital.live_check import LiveCheckResult, run_live_check
from bottleneck_capital.market_structure import MarketStructureError, ingest_market_structure
from bottleneck_capital.portfolio import run_portfolio_pm, write_portfolio_board
from bottleneck_capital.positions import (
    initialize_local_positions,
    refresh_position_prices,
    update_local_position,
    write_exposure_report,
)
from bottleneck_capital.readiness import is_live_ready, write_live_readiness_report
from bottleneck_capital.research_handoffs import (
    ALLOWED_CAUSE_STATUSES,
    ALLOWED_PROVISIONAL_BIASES,
    ALLOWED_THESIS_STATUSES,
    ALLOWED_VALUATION_STATUSES,
    ResearchHandoffError,
    add_research_handoff,
    apply_research_handoff,
    backfill_research_handoffs,
    pending_research_handoffs,
)
from bottleneck_capital.research_handoffs import (
    ALLOWED_DECISIONS as HANDOFF_ALLOWED_DECISIONS,
)
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
    ingest_structure_parser = ingest_subparsers.add_parser(
        "market-structure",
        help="Ingest FINRA short volume or an enriched market-structure feed.",
    )
    ingest_structure_parser.add_argument(
        "--provider",
        choices=("auto", "finra", "feed"),
        default="auto",
    )
    ingest_structure_parser.add_argument("--input", type=Path, default=None)
    ingest_structure_parser.add_argument("--symbols", default="")
    ingest_structure_parser.add_argument(
        "--trade-date",
        default="",
        help="Optional FINRA trade date in YYYY-MM-DD format.",
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
    live_check_parser.add_argument("--market-structure-provider", default="auto")
    live_check_parser.add_argument("--market-structure-input", type=Path, default=None)
    live_check_parser.add_argument(
        "--market-structure-mode",
        choices=("auto", "always", "skip"),
        default="auto",
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
    live_check_parser.add_argument(
        "--filing-mode",
        choices=("auto", "always", "skip"),
        default="auto",
        help="Auto respects active SEC backoff; always retries; skip avoids filing ingest.",
    )

    collector_parser = subparsers.add_parser(
        "collector-check",
        help="Collect live events and classify signals without writing decision boards.",
    )
    collector_parser.add_argument("--market-provider", default="auto")
    collector_parser.add_argument("--market-input", type=Path, default=None)
    collector_parser.add_argument("--market-symbols", default="")
    collector_parser.add_argument("--market-structure-provider", default="auto")
    collector_parser.add_argument("--market-structure-input", type=Path, default=None)
    collector_parser.add_argument(
        "--market-structure-mode",
        choices=("auto", "always", "skip"),
        default="auto",
    )
    collector_parser.add_argument("--company-tickers-input", type=Path, default=None)
    collector_parser.add_argument("--submissions-dir", type=Path, default=None)
    collector_parser.add_argument("--filing-lookback-days", type=int, default=3)
    collector_parser.add_argument("--sec-user-agent", default="")
    collector_parser.add_argument(
        "--filing-mode",
        choices=("auto", "always", "skip"),
        default="auto",
    )
    collector_parser.add_argument("--strict-validate", action="store_true")
    collector_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only new signals or errors; intended for persistent monitoring tasks.",
    )

    subparsers.add_parser("compile-decisions", help="Evaluate and rewrite ticker decision files.")
    subparsers.add_parser("daily-board", help="Write the daily decision board.")
    subparsers.add_parser("daily-digest", help="Write one concise daily decision digest.")
    subparsers.add_parser("action-board", help="Write the current actionable-step board.")
    portfolio_board_parser = subparsers.add_parser(
        "portfolio-board",
        help="Write the private portfolio-first analysis board without changing decisions.",
    )
    portfolio_board_parser.add_argument("--positions", type=Path, default=None)
    portfolio_pm_parser = subparsers.add_parser(
        "portfolio-pm",
        help="Run the sole decision writer and then write the private portfolio board.",
    )
    portfolio_pm_parser.add_argument("--positions", type=Path, default=None)
    regime_event_parser = subparsers.add_parser(
        "regime-event",
        help="Record a structured macro or geopolitical regime heartbeat.",
    )
    regime_event_parser.add_argument("--region", default="global")
    regime_event_parser.add_argument(
        "--status",
        required=True,
        choices=(
            "conflict",
            "renewed_escalation",
            "escalating",
            "elevated",
            "ceasefire",
            "deescalating",
            "resolved",
            "calm",
        ),
    )
    regime_event_parser.add_argument("--severity", required=True, type=float)
    regime_event_parser.add_argument("--confidence", type=float, default=70)
    regime_event_parser.add_argument(
        "--channels",
        required=True,
        help="Comma-separated channel=severity values, such as global_risk=70,energy=80.",
    )
    regime_event_parser.add_argument("--observed-at", required=True)
    regime_event_parser.add_argument("--summary", required=True)
    regime_event_parser.add_argument("--source", default="structured_regime_review")
    regime_event_parser.add_argument("--source-url", default="")
    regime_event_parser.add_argument(
        "--source-quality",
        choices=("official_primary", "primary", "verified_secondary", "unverified"),
        default="primary",
    )
    regime_event_parser.add_argument("--expected-duration", default="unknown")
    regime_event_parser.add_argument("--affected-sleeves", default="")
    regime_event_parser.add_argument("--transmission", default="")
    regime_event_parser.add_argument(
        "--market-confirmation",
        choices=("CONFIRMED", "MIXED", "CONTRADICTED", "UNKNOWN"),
        default="UNKNOWN",
    )
    validate_parser = subparsers.add_parser(
        "validate", help="Validate Bottleneck Capital operating invariants."
    )
    validate_parser.add_argument(
        "--strict-live",
        action="store_true",
        help="Treat live-ingestion gaps as errors.",
    )
    validate_parser.add_argument(
        "--pm-preflight",
        action="store_true",
        help=(
            "Validate structural invariants before PM recovery while leaving research "
            "backlog and live-source gaps visible as warnings."
        ),
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
    handoff_parser = subparsers.add_parser(
        "handoff",
        help="Append-only research resolver to Portfolio PM handoff commands.",
    )
    handoff_subparsers = handoff_parser.add_subparsers(
        dest="handoff_command",
        required=True,
    )
    handoff_add = handoff_subparsers.add_parser(
        "add",
        help="Create a pending structured research handoff for Portfolio PM.",
    )
    handoff_add.add_argument("--memo", type=Path, required=True)
    handoff_add.add_argument("--ticker", required=True)
    handoff_add.add_argument(
        "--cause-status",
        required=True,
        choices=sorted(ALLOWED_CAUSE_STATUSES),
    )
    handoff_add.add_argument(
        "--thesis-status",
        required=True,
        choices=sorted(ALLOWED_THESIS_STATUSES),
    )
    handoff_add.add_argument(
        "--valuation-status",
        required=True,
        choices=sorted(ALLOWED_VALUATION_STATUSES),
    )
    handoff_add.add_argument(
        "--provisional-bias",
        required=True,
        choices=sorted(ALLOWED_PROVISIONAL_BIASES),
    )
    handoff_add.add_argument("--confidence", required=True, type=float)
    handoff_add.add_argument("--summary", required=True)
    handoff_add.add_argument("--next-catalyst", default="")
    handoff_add.add_argument("--event-id", action="append", default=[])
    handoff_add.add_argument("--primary-source-checked-at", default="")
    handoff_add.add_argument(
        "--cause-key",
        default="",
        help="Stable ticker/cause key used to suppress same-day duplicate resolver work.",
    )
    handoff_add.add_argument(
        "--primary-evidence-key",
        default="",
        help="Accession, release ID, or source hash; a new value permits a same-day rerun.",
    )
    handoff_add.add_argument("--expires-at", default="")
    handoff_add.add_argument(
        "--run-pm",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Refresh Portfolio PM boards and the daily digest after creating the handoff.",
    )
    handoff_subparsers.add_parser("list", help="List pending Portfolio PM handoffs.")
    handoff_apply = handoff_subparsers.add_parser(
        "apply",
        help="Record PM application after the persisted ticker decision is updated.",
    )
    handoff_apply.add_argument("--handoff-id", required=True)
    handoff_apply.add_argument(
        "--decision",
        required=True,
        choices=sorted(HANDOFF_ALLOWED_DECISIONS),
    )
    handoff_apply.add_argument("--reason", required=True)
    handoff_apply.add_argument(
        "--evidence-quality",
        default="RESOLVER_MEMO_PM_REVIEW",
    )
    handoff_apply.add_argument("--next-trigger", default="")
    handoff_apply.add_argument("--confidence", type=float, default=None)
    handoff_apply.add_argument(
        "--keep-material-event-open",
        action="store_true",
        help="Keep unresolved_material_event true after PM application.",
    )
    handoff_subparsers.add_parser(
        "backfill",
        help="Create pending PM handoffs for existing resolver memos.",
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
    subparsers.add_parser(
        "dip-review",
        help="Write a bounded-cause review for active dip triggers.",
    )

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
        if args.ingest_command == "market-structure":
            symbols = [
                symbol.strip().upper()
                for symbol in args.symbols.split(",")
                if symbol.strip()
            ]
            try:
                trade_date = date.fromisoformat(args.trade_date) if args.trade_date else None
                result = _logged(
                    root,
                    process="ingest-market-structure",
                    command="ingest market-structure",
                    fn=lambda: ingest_market_structure(
                        root,
                        provider=args.provider,
                        input_path=args.input,
                        symbols=symbols or None,
                        trade_date=trade_date,
                    ),
                )
            except (MarketStructureError, RunLockError, ValueError) as exc:
                print(exc)
                return 1
            for warning in result.warnings:
                print(f"warning: {warning}")
            print(
                f"Wrote {result.record_count} market-structure record(s) to "
                f"{result.snapshot_path}; trade date {result.trade_date}"
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
                    market_structure_provider=args.market_structure_provider,
                    market_structure_input=args.market_structure_input,
                    market_structure_mode=args.market_structure_mode,
                    company_tickers_input=args.company_tickers_input,
                    submissions_dir=args.submissions_dir,
                    filing_lookback_days=args.filing_lookback_days,
                    sec_user_agent=args.sec_user_agent,
                    strict_validate=args.strict_validate,
                    filing_mode=args.filing_mode,
                ),
            )
        except RunLockError as exc:
            print(exc)
            return 1
        print(_render_live_check_result(result), end="")
        return 1 if result.errors or has_errors(result.validation_issues) else 0
    if args.command == "collector-check":
        symbols = [
            symbol.strip().upper()
            for symbol in args.market_symbols.split(",")
            if symbol.strip()
        ]
        try:
            result = _logged(
                root,
                process="collector-check",
                command="collector-check",
                fn=lambda: run_live_check(
                    root,
                    market_provider=args.market_provider,
                    market_input=args.market_input,
                    market_symbols=symbols or None,
                    market_structure_provider=args.market_structure_provider,
                    market_structure_input=args.market_structure_input,
                    market_structure_mode=args.market_structure_mode,
                    company_tickers_input=args.company_tickers_input,
                    submissions_dir=args.submissions_dir,
                    filing_lookback_days=args.filing_lookback_days,
                    sec_user_agent=args.sec_user_agent,
                    strict_validate=args.strict_validate,
                    write_board=False,
                    filing_mode=args.filing_mode,
                ),
            )
        except (RunLockError, ValueError) as exc:
            print(exc)
            return 1
        if not args.quiet or _collector_should_report(result):
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
    if args.command == "daily-digest":
        try:
            path = _logged(
                root,
                process="daily-digest",
                command="daily-digest",
                fn=lambda: write_daily_digest(root),
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
    if args.command == "portfolio-board":
        try:
            path = _logged(
                root,
                process="portfolio-board",
                command="portfolio-board",
                fn=lambda: write_portfolio_board(root, positions_path=args.positions),
            )
        except (RunLockError, ValueError) as exc:
            print(exc)
            return 1
        print(path)
        return 0
    if args.command == "portfolio-pm":
        try:
            result = _logged(
                root,
                process="portfolio-pm",
                command="portfolio-pm",
                fn=lambda: run_portfolio_pm(root, positions_path=args.positions),
            )
        except (RunLockError, ValueError) as exc:
            print(exc)
            return 1
        print(result.decision_board_path)
        print(result.portfolio_board_path)
        print(result.daily_digest_path)
        return 0
    if args.command == "regime-event":
        try:
            path, records = _logged(
                root,
                process="regime-event",
                command="regime-event",
                fn=lambda: _record_regime_event(root, args),
            )
        except (RunLockError, ValueError) as exc:
            print(exc)
            return 1
        print(f"Recorded regime heartbeat in {path}; wrote {len(records)} signal event(s).")
        return 0
    if args.command == "validate":
        if args.strict_live and args.pm_preflight:
            parser.error("--strict-live and --pm-preflight are mutually exclusive")
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
    if args.command == "handoff":
        try:
            if args.handoff_command == "add":
                record = add_research_handoff(
                    root,
                    memo_path=args.memo,
                    ticker=args.ticker,
                    cause_status=args.cause_status,
                    thesis_status=args.thesis_status,
                    valuation_status=args.valuation_status,
                    provisional_bias=args.provisional_bias,
                    confidence=args.confidence,
                    summary=args.summary,
                    next_catalyst=args.next_catalyst,
                    event_ids=args.event_id,
                    primary_source_checked_at=args.primary_source_checked_at,
                    expires_at=args.expires_at,
                    cause_key=args.cause_key,
                    primary_evidence_key=args.primary_evidence_key,
                )
                print(f"Pending handoff {record['handoff_id']} for {record['ticker']}.")
                if args.run_pm:
                    pm_result = _logged(
                        root,
                        process="portfolio-pm",
                        command="portfolio-pm --after-resolver",
                        fn=lambda: run_portfolio_pm(root),
                    )
                    print(f"Portfolio PM refreshed: {pm_result.daily_digest_path}")
                return 0
            if args.handoff_command == "list":
                for record in pending_research_handoffs(root):
                    print(
                        "\t".join(
                            [
                                scalar_text(record.get("handoff_id")),
                                scalar_text(record.get("ticker")),
                                scalar_text(record.get("cause_status")),
                                scalar_text(record.get("thesis_status")),
                                scalar_text(record.get("provisional_bias")),
                                scalar_text(record.get("memo_path")),
                                scalar_text(record.get("summary")),
                            ]
                        )
                    )
                return 0
            if args.handoff_command == "apply":
                record = apply_research_handoff(
                    root,
                    handoff_id=args.handoff_id,
                    decision=args.decision,
                    reason=args.reason,
                    update_research_files=True,
                    evidence_quality=args.evidence_quality,
                    next_trigger=args.next_trigger,
                    confidence=args.confidence,
                    keep_material_event_open=args.keep_material_event_open,
                )
                print(
                    f"Applied handoff {record['applied_handoff_id']} as "
                    f"{record['decision']}."
                )
                return 0
            if args.handoff_command == "backfill":
                records = backfill_research_handoffs(root)
                print(f"Backfilled {len(records)} pending research handoff(s).")
                return 0
        except (ResearchHandoffError, RunLockError, ValueError) as exc:
            print(exc)
            return 1
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
    if args.command == "dip-review":
        path = write_dip_review(root)
        print(path)
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


def _record_regime_event(root: Path, args: argparse.Namespace) -> tuple[Path, list[dict[str, Any]]]:
    channels = _parse_regime_channels(args.channels)
    event_class = (
        "geopolitical_regime_update"
        if args.region.lower() != "global"
        else "macro_regime_update"
    )
    event = {
        "ticker": "BCAP",
        "event_type": "geopolitical_regime" if "geopolitical" in event_class else "macro_regime",
        "event_class": event_class,
        "region": args.region.lower(),
        "status": args.status,
        "severity": max(0.0, min(100.0, args.severity)),
        "confidence": max(0.0, min(100.0, args.confidence)),
        "channels": channels,
        "observed_at": args.observed_at,
        "summary": args.summary,
        "source": args.source,
        "source_url": args.source_url,
        "source_quality": args.source_quality,
        "expected_duration": args.expected_duration,
        "affected_sleeves": [
            item.strip() for item in args.affected_sleeves.split(",") if item.strip()
        ],
        "transmission": args.transmission,
        "market_confirmation": args.market_confirmation,
        "dedupe_key": (
            f"regime:{args.region.lower()}:{args.observed_at[:10]}:{args.status}"
        ),
    }
    path = write_manual_event(root, event)
    return path, run_sentinel(root)


def _parse_regime_channels(value: str) -> dict[str, float]:
    channels: dict[str, float] = {}
    for item in value.split(","):
        if "=" not in item:
            raise ValueError(f"Invalid regime channel {item!r}; expected channel=severity.")
        channel, raw_severity = item.split("=", 1)
        channel = channel.strip().lower()
        if not channel:
            raise ValueError("Regime channel name cannot be blank.")
        channels[channel] = max(0.0, min(100.0, float(raw_severity)))
    if not channels:
        raise ValueError("At least one regime channel is required.")
    return channels


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
    if hasattr(result, "snapshot_path"):
        outputs.append(str(result.snapshot_path))
    if isinstance(result, Path):
        outputs.append(str(result))
    if hasattr(result, "action_board_path") and result.action_board_path is not None:
        outputs.append(str(result.action_board_path))
    if hasattr(result, "decision_board_path"):
        outputs.append(str(result.decision_board_path))
    if hasattr(result, "portfolio_board_path"):
        outputs.append(str(result.portfolio_board_path))
    if hasattr(result, "daily_digest_path"):
        outputs.append(str(result.daily_digest_path))
    if hasattr(result, "market") and result.market is not None:
        outputs.append(str(result.market.output_path))
    if hasattr(result, "market_structure") and result.market_structure is not None:
        outputs.append(str(result.market_structure.snapshot_path))
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
    if result.market_structure is None:
        lines.append("Market-structure ingest: unavailable")
    else:
        lines.append(
            f"Market-structure ingest: {result.market_structure.record_count} record(s), "
            f"{result.market_structure.source}, trade date "
            f"{result.market_structure.trade_date}"
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
    lines.append(
        f"Action board: {result.action_board_path}"
        if result.action_board_path is not None
        else "Action board: not written (collector-only mode)"
    )
    for error in result.errors:
        lines.append(f"error: {error}")
    for warning in result.warnings:
        lines.append(f"warning: {warning}")
    lines.append(render_validation(result.validation_issues).rstrip("\n"))
    return "\n".join(lines) + "\n"


def _collector_should_report(result: LiveCheckResult) -> bool:
    return bool(
        result.signal_count
        or result.errors
        or has_errors(result.validation_issues)
    )


if __name__ == "__main__":
    raise SystemExit(main())
