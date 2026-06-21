from __future__ import annotations

import argparse
from pathlib import Path

from bottleneck_capital.baseline import write_all_wave_baseline
from bottleneck_capital.decision_engine import (
    compile_decisions,
    create_dip_investigation,
    write_daily_board,
)
from bottleneck_capital.initialize import run_initialization
from bottleneck_capital.sentinel import run_sentinel


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bcap")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sentinel_parser = subparsers.add_parser("sentinel", help="Sentinel commands.")
    sentinel_subparsers = sentinel_parser.add_subparsers(dest="sentinel_command", required=True)
    sentinel_run = sentinel_subparsers.add_parser("run", help="Classify latest mock events.")
    sentinel_run.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON/JSONL event file.",
    )

    subparsers.add_parser("compile-decisions", help="Evaluate and rewrite ticker decision files.")
    subparsers.add_parser("daily-board", help="Write the daily decision board.")
    subparsers.add_parser("initialize-run", help="Write initialization baseline and agent packets.")
    subparsers.add_parser("baseline-decisions", help="Write all-wave baseline ticker decisions.")

    dip_parser = subparsers.add_parser("dip-investigate", help="Create a dip investigation memo.")
    dip_parser.add_argument("--ticker", required=True, help="Ticker to investigate.")

    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.command == "sentinel":
        records = run_sentinel(root, input_path=args.input)
        print(f"Wrote {len(records)} signal event(s) to {root / 'state' / 'signal_events.jsonl'}")
        return 0
    if args.command == "compile-decisions":
        results = compile_decisions(root)
        print(f"Compiled {len(results)} decision file(s).")
        return 0
    if args.command == "daily-board":
        path = write_daily_board(root)
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
    if args.command == "dip-investigate":
        path = create_dip_investigation(root, args.ticker)
        print(path)
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
