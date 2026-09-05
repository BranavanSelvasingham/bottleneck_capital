from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

import bottleneck_capital.ingest as ingest_module
import bottleneck_capital.live_sources as live_sources
from bottleneck_capital.ingest import IngestError, ingest_filings, ingest_market
from bottleneck_capital.io import read_json_events, read_jsonl
from bottleneck_capital.sentinel import run_sentinel


@pytest.fixture(autouse=True)
def _freeze_ingest_date(monkeypatch) -> None:
    monkeypatch.setattr(ingest_module, "_today_date", lambda: date(2026, 6, 22))


def test_market_ingest_writes_latest_events_and_sentinel_classifies_dip(tmp_path: Path) -> None:
    _write_project(tmp_path)
    input_path = tmp_path / "market.json"
    input_path.write_text(
        json.dumps(
            {
                "snapshots": [
                    {
                        "ticker": "AAA",
                        "price": 90,
                        "previous_close": 100,
                        "open": 99,
                        "observed_at": "2026-06-22T10:00:00-04:00",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = ingest_market(tmp_path, input_path=input_path)
    signal_records = run_sentinel(tmp_path)

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    snapshots = read_jsonl(tmp_path / "state" / "market_snapshots.jsonl")
    assert result.event_count == 1
    assert result.output_path.name == "latest_market_events.jsonl"
    assert latest[0]["ticker"] == "AAA"
    assert latest[0]["source"] == "market_input_file"
    assert snapshots[0]["ticker"] == "AAA"
    assert signal_records[0]["event_class"] == "dip_trigger"
    assert signal_records[0]["priority"] == "high"


def test_filing_ingest_writes_latest_events_from_sec_submissions_fixture(tmp_path: Path) -> None:
    _write_project(tmp_path)
    company_tickers = tmp_path / "company_tickers.json"
    company_tickers.write_text(
        json.dumps({"0": {"cik_str": 123456, "ticker": "AAA", "title": "AAA Inc."}}),
        encoding="utf-8",
    )
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()
    (submissions_dir / "CIK0000123456.json").write_text(
        json.dumps(
            {
                "filings": {
                    "recent": {
                        "form": ["8-K"],
                        "accessionNumber": ["0000123456-26-000001"],
                        "filingDate": [date.today().isoformat()],
                        "acceptanceDateTime": ["20260622093000"],
                        "primaryDocument": ["form8k.htm"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = ingest_filings(
        tmp_path,
        company_tickers_input=company_tickers,
        submissions_dir=submissions_dir,
    )

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    assert result.event_count == 1
    assert result.output_path.name == "latest_filings_events.jsonl"
    assert latest[0]["ticker"] == "AAA"
    assert latest[0]["filing_type"] == "8-K"
    assert latest[0]["source"] == "sec_input_file"


def test_filing_ingest_uses_git_email_as_sec_user_agent_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    monkeypatch.delenv("BCAP_SEC_USER_AGENT", raising=False)
    monkeypatch.setattr(live_sources, "_git_config_email", lambda root: "owner@example.com")
    requested_agents: list[str] = []

    def fake_fetch_json(url: str, *, user_agent: str):
        requested_agents.append(user_agent)
        if url == ingest_module.SEC_COMPANY_TICKERS_URL:
            return {"0": {"cik_str": 123456, "ticker": "AAA", "title": "AAA Inc."}}
        return {
            "filings": {
                "recent": {
                    "form": ["8-K"],
                    "accessionNumber": ["0000123456-26-000001"],
                    "filingDate": [date.today().isoformat()],
                    "acceptanceDateTime": ["20260622093000"],
                    "primaryDocument": ["form8k.htm"],
                }
            }
        }

    monkeypatch.setattr(ingest_module, "_fetch_json", fake_fetch_json)

    result = ingest_filings(tmp_path)

    assert result.source == "sec_submissions"
    assert requested_agents
    assert all("Bottleneck Capital research automation" in agent for agent in requested_agents)


def test_filing_ingest_falls_back_to_sec_browse_atom_when_submissions_api_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    monkeypatch.setattr(
        ingest_module,
        "_fetch_json",
        lambda url, *, user_agent: (_ for _ in ()).throw(
            IngestError("HTTP Error 403: Forbidden")
        ),
    )
    monkeypatch.setattr(
        ingest_module,
        "_fetch_sec_atom_feed",
        lambda ticker, *, user_agent: _sec_atom_feed(ticker, "8-K"),
    )

    result = ingest_filings(tmp_path)

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    status = json.loads((tmp_path / "state" / "ingest_status.json").read_text())
    assert result.source == "sec_browse_atom"
    assert result.event_count == 1
    assert latest[0]["ticker"] == "AAA"
    assert latest[0]["source"] == "sec_browse_atom"
    assert latest[0]["filing_href"].startswith("https://www.sec.gov/Archives/")
    assert status["filings"]["source"] == "sec_browse_atom"
    assert status["filings"]["missing_tickers"] == []
    assert any("company tickers JSON unavailable" in warning for warning in result.warnings)


def test_filing_ingest_sec_browse_atom_accepts_foreign_issuer_forms(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    monkeypatch.setattr(
        ingest_module,
        "_fetch_json",
        lambda url, *, user_agent: (_ for _ in ()).throw(
            IngestError("HTTP Error 403: Forbidden")
        ),
    )
    monkeypatch.setattr(
        ingest_module,
        "_fetch_sec_atom_feed",
        lambda ticker, *, user_agent: _sec_atom_feed(ticker, "6-K"),
    )

    result = ingest_filings(tmp_path)

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    assert result.source == "sec_browse_atom"
    assert latest[0]["filing_type"] == "6-K"


def test_filing_ingest_sec_browse_atom_stops_after_repeated_403(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    (tmp_path / "configs" / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
  - ticker: BBB
    name: BBB Inc.
    sleeve: compute_infra
  - ticker: CCC
    name: CCC Inc.
    sleeve: compute_infra
  - ticker: DDD
    name: DDD Inc.
    sleeve: compute_infra
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("BCAP_SEC_USER_AGENT", "Bottleneck Capital test@example.com")
    monkeypatch.setenv("BCAP_SEC_REQUEST_DELAY_SECONDS", "0")
    monkeypatch.setattr(
        ingest_module,
        "_fetch_json",
        lambda url, *, user_agent: (_ for _ in ()).throw(
            IngestError("HTTP Error 403: Forbidden")
        ),
    )
    monkeypatch.setattr(
        ingest_module,
        "_fetch_sec_atom_feed",
        lambda ticker, *, user_agent: (_ for _ in ()).throw(
            IngestError("HTTP Error 403: Forbidden")
        ),
    )

    try:
        ingest_filings(tmp_path)
    except IngestError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected SEC filing ingest to fail with no coverage.")

    assert "stopped after 3 consecutive 403" in message


def test_filing_ingest_uses_live_filing_feed_url(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv("BCAP_FILING_EVENTS_URL", "https://filings.example.test/feed")
    monkeypatch.setattr(
        ingest_module.urllib.request,
        "urlopen",
        lambda request, timeout: _FakeResponse(
            json.dumps(
                {
                    "covered_tickers": ["AAA"],
                    "events": [
                        {
                            "ticker": "AAA",
                            "filing_type": "8-K",
                            "filing_date": date.today().isoformat(),
                            "accession": "0000123456-26-000001",
                            "url": "https://example.test/filing",
                        }
                    ],
                }
            )
        ),
    )

    result = ingest_filings(tmp_path)

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    status = json.loads((tmp_path / "state" / "ingest_status.json").read_text())
    assert result.source == "filing_feed_url"
    assert result.event_count == 1
    assert latest[0]["ticker"] == "AAA"
    assert latest[0]["source"] == "filing_feed_url"
    assert status["filings"]["item_count"] == 1
    assert status["filings"]["missing_tickers"] == []


def test_market_ingest_auto_falls_back_to_yahoo_without_alpaca_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    monkeypatch.delenv("APCA_API_KEY_ID", raising=False)
    monkeypatch.delenv("APCA_API_SECRET_KEY", raising=False)
    monkeypatch.setattr(ingest_module, "_open_json", lambda request: _yahoo_chart_response())

    result = ingest_market(tmp_path, provider="auto")

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    assert result.source == "market_yahoo"
    assert result.warnings == ("Alpaca credentials missing; using Yahoo fallback.",)
    assert result.event_count == 1
    assert latest[0]["ticker"] == "AAA"
    assert latest[0]["source"] == "market_yahoo"


def test_market_ingest_uses_live_source_symbol_override(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    (tmp_path / "configs" / "live_sources.yaml").write_text(
        """market:
  symbol_overrides:
    AAA: BBB
""",
        encoding="utf-8",
    )
    requested_urls: list[str] = []

    def fake_open_json(request):
        requested_urls.append(request.full_url)
        return _yahoo_chart_response(symbol="BBB")

    monkeypatch.delenv("APCA_API_KEY_ID", raising=False)
    monkeypatch.delenv("APCA_API_SECRET_KEY", raising=False)
    monkeypatch.setattr(ingest_module, "_open_json", fake_open_json)

    result = ingest_market(tmp_path, provider="auto")

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    assert result.source == "market_yahoo"
    assert any("/BBB?" in url for url in requested_urls)
    assert latest[0]["ticker"] == "AAA"


def test_market_ingest_uses_stooq_for_yahoo_symbol_miss(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    monkeypatch.delenv("APCA_API_KEY_ID", raising=False)
    monkeypatch.delenv("APCA_API_SECRET_KEY", raising=False)
    monkeypatch.setattr(
        ingest_module,
        "_open_json",
        lambda request: (_ for _ in ()).throw(IngestError("HTTP Error 404: Not Found")),
    )
    monkeypatch.setattr(
        ingest_module,
        "_fetch_stooq_snapshot",
        lambda symbol, **kwargs: {
            "ticker": symbol,
            "price": 90,
            "previous_close": 100,
            "open": 99,
            "observed_at": "2026-06-22T16:00:00-04:00",
            "raw_snapshot": {"source": "stooq_daily"},
        },
    )

    result = ingest_market(tmp_path, provider="auto")

    assert result.source == "market_yahoo"
    assert any("Stooq fallback used" in warning for warning in result.warnings)
    assert result.event_count == 1


def test_market_ingest_emits_gap_event_for_missing_ticker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    (tmp_path / "configs" / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
  - ticker: BBB
    name: BBB Inc.
    sleeve: compute_infra
""",
        encoding="utf-8",
    )

    def fake_open_json(request):
        if "/AAA?" in request.full_url:
            return _yahoo_chart_response()
        raise IngestError("HTTP Error 404: Not Found")

    monkeypatch.setattr(ingest_module, "_open_json", fake_open_json)
    monkeypatch.setattr(
        ingest_module,
        "_fetch_stooq_snapshot",
        lambda symbol, **kwargs: (_ for _ in ()).throw(IngestError("no rows")),
    )

    result = ingest_market(tmp_path, provider="yahoo")
    signal_records = run_sentinel(tmp_path)

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    gap_events = [event for event in latest if event.get("event_type") == "market_data_gap"]
    gap_signals = [
        record for record in signal_records if record.get("event_class") == "market_data_gap"
    ]
    assert result.event_count == 2
    assert gap_events[0]["ticker"] == "BBB"
    assert gap_signals[0]["priority"] == "high"


def test_market_ingest_rejects_stale_live_snapshot(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    (tmp_path / "configs" / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
  - ticker: BBB
    name: BBB Inc.
    sleeve: compute_infra
""",
        encoding="utf-8",
    )

    def fake_open_json(request):
        if "/AAA?" in request.full_url:
            return _yahoo_chart_response(symbol="AAA")
        return _yahoo_chart_response(symbol="BBB", market_time=1721678400)

    monkeypatch.setattr(ingest_module, "_open_json", fake_open_json)
    monkeypatch.setattr(
        ingest_module,
        "_fetch_stooq_snapshot",
        lambda symbol, **kwargs: (_ for _ in ()).throw(IngestError("no rows")),
    )

    result = ingest_market(tmp_path, provider="yahoo")

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    status = json.loads((tmp_path / "state" / "ingest_status.json").read_text())
    gap_events = [event for event in latest if event.get("event_type") == "market_data_gap"]
    assert gap_events[0]["ticker"] == "BBB"
    assert status["market"]["missing_tickers"] == ["BBB"]
    assert any("rejected 1 stale snapshot" in warning for warning in result.warnings)


def test_market_ingest_price_dislocation_dedupe_ignores_pct_drift(tmp_path: Path) -> None:
    _write_project(tmp_path)
    first = tmp_path / "market-1.json"
    first.write_text(
        json.dumps(
            {
                "snapshots": [
                    {"ticker": "AAA", "price": 90, "previous_close": 100, "open": 99}
                ]
            }
        ),
        encoding="utf-8",
    )
    second = tmp_path / "market-2.json"
    second.write_text(
        json.dumps(
            {
                "snapshots": [
                    {"ticker": "AAA", "price": 89, "previous_close": 100, "open": 98}
                ]
            }
        ),
        encoding="utf-8",
    )

    ingest_market(tmp_path, input_path=first)
    first_signals = run_sentinel(tmp_path)
    ingest_market(tmp_path, input_path=second)
    second_signals = run_sentinel(tmp_path)

    assert len(first_signals) == 1
    assert second_signals == []


def test_market_ingest_skips_pre_ipo_research_issuers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_project(tmp_path)
    (tmp_path / "configs" / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
  - ticker: PRIVATE
    name: Private Issuer
    sleeve: compute_infra
    tradable: false
    market_data_required: false
    filing_data_required: false
    coverage_exemption_reason: Pre-IPO research issuer with no confirmed ticker.
""",
        encoding="utf-8",
    )
    requested: list[str] = []

    def fake_open_json(request):
        requested.append(request.full_url)
        return _yahoo_chart_response(symbol="AAA")

    monkeypatch.setattr(ingest_module, "_open_json", fake_open_json)

    result = ingest_market(tmp_path, provider="yahoo")

    status = json.loads((tmp_path / "state" / "ingest_status.json").read_text())
    assert len(requested) == 1
    assert "/AAA?" in requested[0]
    assert status["market"]["expected_item_count"] == 1
    assert status["market"]["missing_tickers"] == []
    assert any("Market coverage exempt for PRIVATE" in warning for warning in result.warnings)


def test_filing_ingest_skips_pre_ipo_research_issuers(tmp_path: Path) -> None:
    _write_project(tmp_path)
    (tmp_path / "configs" / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
  - ticker: PRIVATE
    name: Private Issuer
    sleeve: compute_infra
    tradable: false
    market_data_required: false
    filing_data_required: false
    coverage_exemption_reason: Pre-IPO research issuer with no confirmed ticker.
""",
        encoding="utf-8",
    )
    company_tickers = tmp_path / "company_tickers.json"
    company_tickers.write_text(
        json.dumps({"0": {"cik_str": 123456, "ticker": "AAA", "title": "AAA Inc."}}),
        encoding="utf-8",
    )
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()
    (submissions_dir / "CIK0000123456.json").write_text(
        json.dumps(
            {
                "filings": {
                    "recent": {
                        "form": ["8-K"],
                        "accessionNumber": ["0000123456-26-000001"],
                        "filingDate": [date.today().isoformat()],
                        "acceptanceDateTime": ["20260622093000"],
                        "primaryDocument": ["form8k.htm"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = ingest_filings(
        tmp_path,
        company_tickers_input=company_tickers,
        submissions_dir=submissions_dir,
    )

    status = json.loads((tmp_path / "state" / "ingest_status.json").read_text())
    assert status["filings"]["expected_item_count"] == 1
    assert status["filings"]["missing_tickers"] == []
    assert any("Filing coverage exempt for PRIVATE" in warning for warning in result.warnings)


def test_filing_ingest_uses_symbol_overrides_and_exemptions(tmp_path: Path) -> None:
    _write_project(tmp_path)
    (tmp_path / "configs" / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
  - ticker: OLD
    name: Old Corp.
    sleeve: compute_infra
  - ticker: FUND
    name: Fund Signal
    sleeve: crowded_ai_beta_hedge
""",
        encoding="utf-8",
    )
    (tmp_path / "configs" / "live_sources.yaml").write_text(
        """filings:
  symbol_overrides:
    OLD: NEW
  exempt_tickers:
    FUND: Signal-only fund exposure.
""",
        encoding="utf-8",
    )
    company_tickers = tmp_path / "company_tickers.json"
    company_tickers.write_text(
        json.dumps(
            {
                "0": {"cik_str": 123456, "ticker": "AAA", "title": "AAA Inc."},
                "1": {"cik_str": 456789, "ticker": "NEW", "title": "New Corp."},
            }
        ),
        encoding="utf-8",
    )
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()
    for cik in ["0000123456", "0000456789"]:
        (submissions_dir / f"CIK{cik}.json").write_text(
            json.dumps(
                {
                    "filings": {
                        "recent": {
                            "form": ["8-K"],
                            "accessionNumber": [f"{cik}-26-000001"],
                            "filingDate": [date.today().isoformat()],
                            "acceptanceDateTime": ["20260622093000"],
                            "primaryDocument": ["form8k.htm"],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

    result = ingest_filings(
        tmp_path,
        company_tickers_input=company_tickers,
        submissions_dir=submissions_dir,
    )

    latest = read_json_events(tmp_path / "state" / "latest_events.jsonl")
    status = json.loads((tmp_path / "state" / "ingest_status.json").read_text())
    assert result.event_count == 2
    assert {event["ticker"] for event in latest} == {"AAA", "OLD"}
    assert status["filings"]["item_count"] == 3
    assert status["filings"]["missing_tickers"] == []
    assert any("Filing coverage exempt for FUND" in warning for warning in result.warnings)


def _yahoo_chart_response(symbol: str = "AAA", market_time: int = 1782140400) -> dict:
    return {
        "chart": {
            "result": [
                {
                    "meta": {
                        "symbol": symbol,
                        "currency": "USD",
                        "exchangeName": "NMS",
                        "regularMarketPrice": 90,
                        "previousClose": 100,
                        "regularMarketTime": market_time,
                        "marketState": "REGULAR",
                    },
                    "timestamp": [1782138600, market_time],
                    "indicators": {"quote": [{"open": [99, 98], "close": [91, 90]}]},
                }
            ],
            "error": None,
        }
    }


def _sec_atom_feed(ticker: str, form: str) -> str:
    return f"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <company-info>
    <cik>0000123456</cik>
    <conformed-name>{ticker} Inc.</conformed-name>
  </company-info>
  <entry>
    <category label="form type" scheme="https://www.sec.gov/" term="{form}" />
    <content type="text/xml">
      <accession-number>0000123456-26-000001</accession-number>
      <filing-date>{date.today().isoformat()}</filing-date>
      <filing-href>https://www.sec.gov/Archives/edgar/data/123456/000012345626000001/0000123456-26-000001-index.htm</filing-href>
      <filing-type>{form}</filing-type>
    </content>
    <updated>2026-06-22T09:30:00-04:00</updated>
  </entry>
</feed>
"""


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self._text = text

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self._text.encode("utf-8")


def _write_project(root: Path) -> None:
    configs = root / "configs"
    configs.mkdir(parents=True, exist_ok=True)
    (configs / "watchlist.yaml").write_text(
        """watchlist:
  - ticker: AAA
    name: AAA Inc.
    sleeve: compute_infra
""",
        encoding="utf-8",
    )
    (configs / "signal_thresholds.yaml").write_text(
        """sentinel:
  timezone: America/Toronto
  freshness:
    market_data_max_age_minutes: 20
    filing_data_max_age_minutes: 240
  price_triggers:
    intraday_drop_pct: 5
    one_day_drop_pct: 7
    gap_down_pct: 4
  source_triggers:
    sec_filings:
      - 8-K
      - 10-Q
""",
        encoding="utf-8",
    )
