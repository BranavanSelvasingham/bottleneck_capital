from __future__ import annotations

from pathlib import Path

from bottleneck_capital.baseline import write_all_wave_baseline
from bottleneck_capital.decision_engine import evaluate_all


def test_all_wave_baseline_writes_actionable_hold_files(tmp_path: Path) -> None:
    _write_watchlist(tmp_path)

    written = write_all_wave_baseline(tmp_path)
    results = evaluate_all(tmp_path)

    assert len(written) == 8
    assert {result.ticker: result.action for result in results} == {
        "CRWV": "HOLD",
        "AVGO": "HOLD",
    }

    crwv = (tmp_path / "research" / "decisions" / "CRWV.md").read_text(encoding="utf-8")
    avgo = (tmp_path / "research" / "decisions" / "AVGO.md").read_text(encoding="utf-8")
    report = next((tmp_path / "reports" / "initialization").glob("*-all-wave-baseline.md"))
    wave_report = next((tmp_path / "reports" / "initialization").glob("*-wave-1-execution.md"))

    assert "Initial scaffold" not in crwv
    assert "Evidence quality:" in crwv
    assert "No puts or shorts" in avgo
    assert "CRWV" in report.read_text(encoding="utf-8")
    assert "CRWV" in wave_report.read_text(encoding="utf-8")


def _write_watchlist(root: Path) -> None:
    path = root / "configs" / "watchlist.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """watchlist:
  - ticker: CRWV
    name: CoreWeave
    sleeve: compute_infra
    source_classification: sa_reported_current_13f
    instrument_role: common_equity_and_call_signal
    trade_policy: long_only_after_research
    priority: high
  - ticker: AVGO
    name: Broadcom
    sleeve: crowded_ai_beta_hedge
    source_classification: sa_reported_current_13f
    instrument_role: reported_put_signal
    trade_policy: signal_only_no_puts_or_shorts
    priority: high
""",
        encoding="utf-8",
    )
