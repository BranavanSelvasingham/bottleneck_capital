from __future__ import annotations

from pathlib import Path

from bottleneck_capital.positions import (
    initialize_local_positions,
    refresh_position_prices,
    render_exposure,
    update_local_position,
)


def test_positions_init_creates_gitignored_ledger_shape(tmp_path: Path) -> None:
    _write_project(tmp_path)

    path = initialize_local_positions(tmp_path)

    text = path.read_text(encoding="utf-8")
    assert "ticker: BE" in text
    assert "ticker: MRVL" in text
    assert "quantity: 0" in text


def test_render_exposure_groups_local_positions(tmp_path: Path) -> None:
    _write_project(tmp_path)
    positions = tmp_path / "state" / "local_positions.yaml"
    positions.parent.mkdir(parents=True, exist_ok=True)
    positions.write_text(
        """as_of: 2026-06-20
base_currency: CAD
cash:
  CAD: 5
positions:
  - ticker: BE
    quantity: 2
    average_cost: 2
    current_price: 3
    currency: USD
    account: test
    notes: power
  - ticker: MRVL
    quantity: 3
    average_cost: 1
    current_price: 2
    currency: USD
    account: test
    notes: networking
""",
        encoding="utf-8",
    )

    report = render_exposure(tmp_path)

    assert "| BE | power_bottleneck | HOLD | 2 | 3.00 | 6.00 | 50.0%" in report
    assert "| MRVL | ai_networking_optical | HOLD | 3 | 2.00 | 6.00 | 50.0%" in report
    assert "| HOLD | 12.00 | 100.0% |" in report


def test_refresh_position_prices_updates_held_positions_from_market_snapshots(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    positions = state / "local_positions.yaml"
    positions.write_text(
        """as_of: 2026-06-20
positions:
  - ticker: BE
    quantity: 2
    average_cost: 0
    current_price: 0
  - ticker: MRVL
    quantity: 0
    average_cost: 0
    current_price: 0
""",
        encoding="utf-8",
    )
    (state / "market_snapshots.jsonl").write_text(
        '{"ticker":"BE","price":3.5}\n{"ticker":"MRVL","price":7}\n',
        encoding="utf-8",
    )

    result = refresh_position_prices(tmp_path)

    text = positions.read_text(encoding="utf-8")
    assert result.updated_count == 1
    assert not result.missing_tickers
    assert "current_price: 3.5" in text
    assert "ticker: MRVL" in text


def test_refresh_position_prices_updates_currency_from_market_snapshots(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    positions = state / "local_positions.yaml"
    positions.write_text(
        """as_of: 2026-06-20
positions:
  - ticker: BE
    quantity: 2
    average_cost: 1
    current_price: 0
    currency: CAD
""",
        encoding="utf-8",
    )
    (state / "market_snapshots.jsonl").write_text(
        '{"ticker":"BE","price":3.5,"raw_snapshot":{"currency":"USD"}}\n',
        encoding="utf-8",
    )

    result = refresh_position_prices(tmp_path)

    text = positions.read_text(encoding="utf-8")
    assert result.updated_count == 2
    assert "current_price: 3.5" in text
    assert "currency: USD" in text


def test_update_local_position_sets_exact_fill_fields(tmp_path: Path) -> None:
    _write_project(tmp_path)
    positions = tmp_path / "state" / "local_positions.yaml"
    positions.parent.mkdir(parents=True, exist_ok=True)
    positions.write_text(
        """as_of: 2026-06-20
positions:
  - ticker: BE
    quantity: 2
    average_cost: 0
    current_price: 3
    currency: USD
    account: ""
    notes: pending
""",
        encoding="utf-8",
    )

    result = update_local_position(
        tmp_path,
        ticker="BE",
        quantity=4,
        average_cost=12.34,
        current_price=14.56,
        currency="usd",
        account="taxable",
        notes="",
    )

    text = positions.read_text(encoding="utf-8")
    assert result.path == positions
    assert result.ticker == "BE"
    assert result.created is False
    assert "quantity: 4" in text
    assert "average_cost: 12.34" in text
    assert "current_price: 14.56" in text
    assert "currency: USD" in text
    assert "account: taxable" in text
    assert 'notes: ""' in text


def test_update_local_position_can_create_missing_ticker_row(tmp_path: Path) -> None:
    _write_project(tmp_path)
    positions = tmp_path / "state" / "local_positions.yaml"
    positions.parent.mkdir(parents=True, exist_ok=True)
    positions.write_text("positions: []\n", encoding="utf-8")

    result = update_local_position(
        tmp_path,
        ticker="tsla",
        quantity=1,
        average_cost=400,
        currency="usd",
    )

    text = positions.read_text(encoding="utf-8")
    assert result.ticker == "TSLA"
    assert result.created is True
    assert "ticker: TSLA" in text
    assert "quantity: 1" in text
    assert "average_cost: 400" in text
    assert "currency: USD" in text


def _write_project(root: Path) -> None:
    watchlist = root / "configs" / "watchlist.yaml"
    watchlist.parent.mkdir(parents=True, exist_ok=True)
    watchlist.write_text(
        """watchlist:
  - ticker: BE
    name: Bloom Energy
    sleeve: power_bottleneck
  - ticker: MRVL
    name: Marvell Technology
    sleeve: ai_networking_optical
""",
        encoding="utf-8",
    )
    for ticker, sleeve in {"BE": "power_bottleneck", "MRVL": "ai_networking_optical"}.items():
        path = root / "research" / "decisions" / f"{ticker}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"""---
ticker: {ticker}
name: {ticker}
sleeve: {sleeve}
current_decision: HOLD
---
# {ticker}
""",
            encoding="utf-8",
        )
