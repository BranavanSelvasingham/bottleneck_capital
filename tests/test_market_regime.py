from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from bottleneck_capital.market_regime import assess_market_regime
from bottleneck_capital.opportunity import rank_opportunities
from bottleneck_capital.validation import validate_project


def test_latest_geopolitical_state_supersedes_prior_ceasefire(tmp_path: Path) -> None:
    _write_regime_config(tmp_path)
    _write_context_snapshots(tmp_path)
    _write_signals(
        tmp_path,
        [
            _regime_event("ceasefire", "2026-07-08T10:00:00-04:00", 25),
            _regime_event("renewed_escalation", "2026-07-10T10:00:00-04:00", 80),
        ],
    )

    regime = assess_market_regime(
        tmp_path,
        as_of=datetime(2026, 7, 12, tzinfo=ZoneInfo("America/Toronto")),
    )

    assert regime.state == "CONFLICT_ESCALATION"
    assert regime.geopolitical_status == "renewed_escalation"
    assert regime.channel_severity["energy"] == 64
    assert regime.market_confirmation == "MIXED"
    assert regime.fresh is True


def test_regime_adjusts_score_and_gates_entry(tmp_path: Path) -> None:
    _write_regime_config(tmp_path)
    _write_context_snapshots(tmp_path)
    _write_watchlist_and_research(tmp_path)
    _write_signals(
        tmp_path,
        [_regime_event("renewed_escalation", "2026-07-10T10:00:00-04:00", 80)],
    )
    regime = assess_market_regime(
        tmp_path,
        as_of=datetime(2026, 7, 12, tzinfo=ZoneInfo("America/Toronto")),
    )

    candidate = rank_opportunities(tmp_path, regime=regime)[0]

    assert candidate.ticker == "MU"
    assert candidate.regime_adjustment == pytest.approx(-8.8)
    assert candidate.score == pytest.approx(candidate.structural_score - 8.8)
    assert candidate.entry_gate == "WAIT_FOR_STABILIZATION"


def test_missing_context_does_not_clear_buy_gate(tmp_path: Path) -> None:
    _write_regime_config(tmp_path)
    _write_watchlist_and_research(tmp_path)

    regime = assess_market_regime(
        tmp_path,
        as_of=datetime(2026, 7, 12, tzinfo=ZoneInfo("America/Toronto")),
    )
    candidate = rank_opportunities(tmp_path, regime=regime)[0]

    assert regime.state == "UNKNOWN"
    assert regime.fresh is False
    assert candidate.entry_gate == "CONTEXT_INCOMPLETE"


def test_validation_flags_unmapped_sleeve(tmp_path: Path) -> None:
    _write_regime_config(tmp_path)
    watchlist = tmp_path / "configs" / "watchlist.yaml"
    watchlist.write_text(
        """watchlist:
  - ticker: NEW
    name: New Asset
    sleeve: unmapped_sleeve
""",
        encoding="utf-8",
    )

    issues = validate_project(tmp_path)

    assert any(issue.code == "REGIME_EXPOSURE_MAP_GAP" for issue in issues)


def _write_regime_config(root: Path) -> None:
    path = root / "configs" / "regime.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """regime:
  context_snapshot_max_age_days: 4
  geopolitical_event_max_age_days: 14
  required_context_symbols:
    - SPY
    - QQQ
    - USO
    - VIXY
  context_symbols:
    SPY: SPY
    QQQ: QQQ
    USO: USO
    VIXY: VIXY
  entry_gates:
    reduce_tranche_adjustment: -4
    pause_new_buy_adjustment: -8
  sleeve_channel_exposures:
    memory_storage_networking:
      global_risk: -0.10
      energy: -0.05
""",
        encoding="utf-8",
    )


def _write_context_snapshots(root: Path) -> None:
    path = root / "state" / "market_snapshots.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {"ticker": ticker, "price": 100, "previous_close": 100, "observed_at": "2026-07-10T16:00:00-04:00"}
        for ticker in ("SPY", "QQQ", "USO", "VIXY")
    ]
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")


def _write_signals(root: Path, records: list[dict[str, object]]) -> None:
    path = root / "state" / "signal_events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")


def _regime_event(status: str, observed_at: str, severity: int) -> dict[str, object]:
    return {
        "event_id": f"middle-east-{status}",
        "detected_at": observed_at,
        "ticker": "BCAP",
        "event_class": "geopolitical_regime_update",
        "priority": "high",
        "requires_codex": True,
        "resolved": False,
        "summary": status,
        "raw_event": {
            "region": "middle_east",
            "status": status,
            "severity": severity,
            "confidence": 90,
            "observed_at": observed_at,
            "channels": {"global_risk": 70, "energy": severity},
        },
    }


def _write_watchlist_and_research(root: Path) -> None:
    watchlist = root / "configs" / "watchlist.yaml"
    watchlist.parent.mkdir(parents=True, exist_ok=True)
    watchlist.write_text(
        """watchlist:
  - ticker: MU
    name: Micron
    sleeve: memory_storage_networking
""",
        encoding="utf-8",
    )
    metadata = """ticker: MU
name: Micron
sleeve: memory_storage_networking
trade_policy: long_only_after_research
current_decision: ADD_ON_DIP
thesis_health_score: 88
valuation_attractiveness_score: 72
bottleneck_upside_score: 88
confidence_score: 80
max_position_weight_pct: 4
current_position_weight_pct: 0
approved_entry_zone: $925-$950
one_line_rationale: HBM scarcity.
"""
    for directory in ("assets", "decisions"):
        path = root / "research" / directory / "MU.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\n{metadata}---\n# MU\n", encoding="utf-8")
