from __future__ import annotations

from pathlib import Path
from typing import Any

from bottleneck_capital.value_chain import build_value_chain_data, write_value_chain_visualizer


def test_value_chain_maps_every_watchlist_ticker_once(tmp_path: Path) -> None:
    _write_watchlist(tmp_path)
    _write_decision(tmp_path, "NVDA", {"sleeve": "crowded_ai_beta_hedge"})
    _write_decision(tmp_path, "CRWV", {"sleeve": "compute_infra"})
    _write_decision(tmp_path, "BE", {"sleeve": "power_bottleneck"})
    _write_decision(tmp_path, "TSLA", {"sleeve": "autonomy_energy"})

    data = build_value_chain_data(tmp_path)

    mapped_tickers = [
        ticker["ticker"] for layer in data["layers"] for ticker in layer["tickers"]
    ]
    assert sorted(mapped_tickers) == ["BE", "CRWV", "NVDA", "TSLA"]
    assert len(mapped_tickers) == len(set(mapped_tickers))


def test_value_chain_visualizer_writes_static_html(tmp_path: Path) -> None:
    _write_watchlist(tmp_path)
    for ticker, sleeve in {
        "NVDA": "crowded_ai_beta_hedge",
        "CRWV": "compute_infra",
        "BE": "power_bottleneck",
        "TSLA": "autonomy_energy",
    }.items():
        _write_decision(tmp_path, ticker, {"sleeve": sleeve})

    path = write_value_chain_visualizer(tmp_path)
    html = path.read_text(encoding="utf-8")

    assert path == tmp_path / "reports" / "value_chain_visualizer.html"
    assert "Bottleneck Capital Visualizer" in html
    assert "Energy -> chips -> infrastructure -> models -> applications" in html
    assert 'id="updateButton"' in html
    assert "/__bcap_update" in html
    assert '"ticker": "NVDA"' in html
    assert '"ticker": "TSLA"' in html


def _write_watchlist(root: Path) -> None:
    path = root / "configs" / "watchlist.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """watchlist:
  - ticker: NVDA
    name: NVIDIA
    sleeve: crowded_ai_beta_hedge
    source_classification: sa_reported_current_13f
    instrument_role: common_equity_with_put_signal
    trade_policy: long_only_after_research
    priority: high
  - ticker: CRWV
    name: CoreWeave
    sleeve: compute_infra
    source_classification: sa_reported_current_13f
    instrument_role: common_equity_and_call_signal
    trade_policy: long_only_after_research
    priority: high
  - ticker: BE
    name: Bloom Energy
    sleeve: power_bottleneck
    source_classification: sa_reported_current_13f
    instrument_role: common_equity_and_call_signal
    trade_policy: long_only_after_research
    priority: high
  - ticker: TSLA
    name: Tesla
    sleeve: autonomy_energy
    source_classification: sa_adjacent_thesis_proxy
    instrument_role: local_position_adjacent_proxy
    trade_policy: long_only_after_research
    priority: high
""",
        encoding="utf-8",
    )


def _write_decision(root: Path, ticker: str, overrides: dict[str, Any]) -> None:
    metadata = {
        "ticker": ticker,
        "name": f"{ticker} Inc.",
        "sleeve": "test_sleeve",
        "current_decision": "HOLD",
        "dip_decision": "RESEARCH_FIRST",
        "confidence_score": 55,
        "source_classification": "sa_reported_current_13f",
        "instrument_role": "common_equity",
        "trade_policy": "long_only_after_research",
        "thesis_expressed": "Test thesis.",
        "anti_thesis": "Test anti-thesis.",
        "hedge_or_sizing": "Test sizing.",
        "invalidation_trigger": "Test invalidation.",
        "one_line_rationale": "Test rationale.",
    }
    metadata.update(overrides)
    _write_markdown(root / "research" / "decisions" / f"{ticker}.md", metadata)
    _write_markdown(root / "research" / "assets" / f"{ticker}.md", metadata)


def _write_markdown(path: Path, metadata: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = "\n".join(f"{key}: {_yaml_value(value)}" for key, value in metadata.items())
    path.write_text(f"---\n{frontmatter}\n---\n# Test\n", encoding="utf-8")


def _yaml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)
