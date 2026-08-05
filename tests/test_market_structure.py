from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bottleneck_capital.market_structure import (
    assess_market_structure,
    ingest_market_structure,
)


def test_ingest_market_structure_normalizes_flow_without_calling_it_short_interest(
    tmp_path: Path,
) -> None:
    _write_watchlist(tmp_path, ["AAA"])
    input_path = tmp_path / "structure.json"
    input_path.write_text(
        json.dumps(
            {
                "covered_tickers": ["AAA"],
                "records": [
                    {
                        "ticker": "AAA",
                        "trade_date": date.today().isoformat(),
                        "short_volume": 70,
                        "short_exempt_volume": 5,
                        "total_reported_volume": 100,
                        "daily_short_volume_ratio_pct": 70,
                        "short_exempt_ratio_pct": 5,
                        "source_quality": "official_primary",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = ingest_market_structure(tmp_path, input_path=input_path)
    assessment = assess_market_structure(tmp_path, "AAA")

    assert result.record_count == 1
    assert assessment.daily_short_volume_ratio_pct == 70
    assert assessment.short_interest_pct_float is None
    assert assessment.flow_classification == "SHORT_VOLUME_ONLY_AMBIGUOUS"
    assert assessment.execution_gate == "DO_NOT_INFER_SHORT_INTEREST"


def test_squeeze_setup_requires_correlated_borrow_interest_options_and_catalyst(
    tmp_path: Path,
) -> None:
    _write_structure_records(
        tmp_path,
        [
            {
                "ticker": "AAA",
                "observed_at": _now(),
                "short_interest_pct_float": 30,
                "days_to_cover": 8,
                "borrow_fee_pct": 25,
                "borrow_utilization_pct": 98,
                "put_call_open_interest_ratio": 0.5,
                "catalyst_within_days": 5,
            }
        ],
    )

    assessment = assess_market_structure(tmp_path, "AAA")

    assert assessment.flow_classification == "SQUEEZE_SETUP"
    assert assessment.squeeze_potential_score >= 60
    assert assessment.execution_gate == "REDUCE_SIZE_FOR_SQUEEZE_VOLATILITY"
    assert assessment.score_adjustment < 0


def test_active_unlock_overrides_squeeze_and_blocks_entry(tmp_path: Path) -> None:
    as_of = datetime(2026, 8, 5, 12, tzinfo=ZoneInfo("America/Toronto"))
    _write_structure_records(
        tmp_path,
        [
            {
                "ticker": "AAA",
                "observed_at": "2026-08-05",
                "short_interest_pct_float": 35,
                "days_to_cover": 7,
                "borrow_fee_pct": 30,
                "borrow_utilization_pct": 99,
                "float_shares": 100,
                "eligible_supply_shares": 50,
                "unlock_date": "2026-08-06",
                "catalyst_within_days": 1,
            }
        ],
    )

    assessment = assess_market_structure(tmp_path, "AAA", as_of=as_of)

    assert assessment.flow_classification == "ACTIVE_SUPPLY_OVERHANG"
    assert assessment.execution_gate == "WAIT_FOR_SUPPLY_ABSORPTION"
    assert assessment.supply_overhang_pct_float == 50
    assert assessment.score_adjustment == -8


def test_stale_borrow_data_cannot_create_squeeze(tmp_path: Path) -> None:
    as_of = datetime(2026, 8, 20, 12, tzinfo=ZoneInfo("America/Toronto"))
    _write_structure_records(
        tmp_path,
        [
            {
                "ticker": "AAA",
                "observed_at": "2026-08-01",
                "short_interest_pct_float": 30,
                "days_to_cover": 8,
                "borrow_fee_pct": 40,
                "borrow_utilization_pct": 99,
                "put_call_open_interest_ratio": 0.5,
                "catalyst_within_days": 5,
            }
        ],
    )

    assessment = assess_market_structure(tmp_path, "AAA", as_of=as_of)

    assert assessment.borrow_fee_pct is None
    assert assessment.borrow_utilization_pct is None
    assert assessment.flow_classification != "SQUEEZE_SETUP"


def _write_watchlist(root: Path, tickers: list[str]) -> None:
    path = root / "configs" / "watchlist.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "watchlist:\n"
        + "".join(
            f"  - ticker: {ticker}\n    name: {ticker} Inc.\n    sleeve: test\n"
            for ticker in tickers
        ),
        encoding="utf-8",
    )


def _write_structure_records(root: Path, records: list[dict]) -> None:
    path = root / "state" / "market_structure_snapshots.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _now() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
