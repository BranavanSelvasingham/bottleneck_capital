from __future__ import annotations

from pathlib import Path

from bottleneck_capital.positions import initialize_local_positions, render_exposure


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
