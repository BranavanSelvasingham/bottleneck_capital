from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bottleneck_capital.initialize import rank_tickers, run_initialization


def test_initialization_ranks_and_writes_agent_packets(tmp_path: Path) -> None:
    _write_watchlist(tmp_path)
    _write_sa_universe(tmp_path)

    paths = run_initialization(tmp_path)
    ranked = rank_tickers(
        [
            {
                "ticker": "CRWV",
                "name": "CoreWeave",
                "sleeve": "compute_infra",
                "source_classification": "sa_reported_current_13f",
                "instrument_role": "common_equity_and_call_signal",
                "trade_policy": "long_only_after_research",
                "priority": "high",
            },
            {
                "ticker": "AMD",
                "name": "Advanced Micro Devices",
                "sleeve": "crowded_ai_beta_hedge",
                "source_classification": "sa_reported_current_13f",
                "instrument_role": "common_equity_with_put_signal",
                "trade_policy": "long_only_after_research",
                "priority": "high",
            },
            {
                "ticker": "VRT",
                "name": "Vertiv",
                "sleeve": "ai_power_equipment",
                "source_classification": "sa_adjacent_historical_or_thesis_proxy",
                "instrument_role": "common_equity",
                "trade_policy": "long_only_after_research",
                "priority": "medium",
            },
        ]
    )

    by_ticker = {item.ticker: item for item in ranked}
    assert by_ticker["CRWV"].wave == 1
    assert by_ticker["AMD"].wave == 2
    assert by_ticker["VRT"].wave == 3
    assert tmp_path / "research" / "agent_packets" in paths

    roster = (tmp_path / "configs" / "agent_roster.yaml").read_text(encoding="utf-8")
    assert "owner_agent: asset_analyst.CRWV" in roster

    crwv_packet = (
        tmp_path / "research" / "agent_packets" / "wave_1" / "CRWV.md"
    ).read_text(encoding="utf-8")
    assert "Owner agent: `asset_analyst.CRWV`" in crwv_packet
    assert "Underwrite as long-only candidate" in crwv_packet

    wave_plan = (
        tmp_path / "reports" / "initialization" / _today_report_name("wave-plan")
    ).read_text(encoding="utf-8")
    assert "## Wave 1" in wave_plan
    assert "`CRWV`" in wave_plan
    assert "`AMD`" in wave_plan
    assert "`VRT`" in wave_plan


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
  - ticker: AMD
    name: Advanced Micro Devices
    sleeve: crowded_ai_beta_hedge
    source_classification: sa_reported_current_13f
    instrument_role: common_equity_with_put_signal
    trade_policy: long_only_after_research
    priority: high
  - ticker: VRT
    name: Vertiv
    sleeve: ai_power_equipment
    source_classification: sa_adjacent_historical_or_thesis_proxy
    instrument_role: common_equity
    trade_policy: long_only_after_research
    priority: medium
""",
        encoding="utf-8",
    )


def _write_sa_universe(root: Path) -> None:
    path = root / "configs" / "sa_universe.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """source:
  manager: Situational Awareness LP
  latest_public_13f_period: 2026-03-31
  latest_public_13f_filed: 2026-05-18
""",
        encoding="utf-8",
    )


def _today_report_name(suffix: str) -> str:
    today = datetime.now(ZoneInfo("America/Toronto")).date().isoformat()
    return f"{today}-{suffix}.md"
