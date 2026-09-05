from __future__ import annotations

import csv
import io
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import load_watchlist
from bottleneck_capital.io import load_yaml_file, read_json_events, read_jsonl, scalar_text
from bottleneck_capital.live_sources import effective_sec_user_agent

SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_BROWSE_ATOM_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
ALPACA_DATA_BASE_URL = "https://data.alpaca.markets"
YAHOO_CHART_BASE_URL = "https://query1.finance.yahoo.com"
STOOQ_BASE_URL = "https://stooq.com"


class IngestError(RuntimeError):
    """Raised when live ingestion cannot produce a trustworthy input file."""


@dataclass(frozen=True)
class IngestResult:
    channel: str
    source: str
    event_count: int
    output_path: Path
    aggregate_path: Path
    warnings: tuple[str, ...] = ()


def ingest_market(
    root: Path,
    *,
    provider: str = "auto",
    input_path: Path | None = None,
    symbols: list[str] | None = None,
) -> IngestResult:
    from bottleneck_capital.market_regime import context_symbols

    thresholds = load_yaml_file(root / "configs" / "signal_thresholds.yaml")
    watchlist = load_watchlist(root)
    investment_tickers = (
        symbols
        if symbols is not None
        else _coverage_tickers(watchlist, "market_data_required")
    )
    context = context_symbols(root) if symbols is None and input_path is None else {}
    tickers = list(dict.fromkeys([*investment_tickers, *context]))
    symbol_overrides = {**_market_symbol_overrides(root), **context}
    provider = provider.lower()
    source = f"market_{provider}"
    warnings: list[str] = []
    if symbols is None:
        warnings.extend(
            _coverage_exemption_warnings(watchlist, "market_data_required", "Market")
        )
    if input_path is not None:
        snapshots = _load_market_snapshots(input_path)
        source = "market_input_file"
    elif provider == "auto":
        snapshots, source, provider_warnings = _fetch_auto_market_snapshots(
            tickers, symbol_overrides
        )
        warnings.extend(provider_warnings)
    elif provider == "alpaca":
        snapshots = _fetch_alpaca_snapshots(tickers, symbol_overrides)
        source = "market_alpaca"
    elif provider == "yahoo":
        snapshots, provider_warnings = _fetch_yahoo_snapshots(tickers, symbol_overrides)
        warnings.extend(provider_warnings)
        source = "market_yahoo"
    else:
        raise IngestError(f"Unsupported market provider: {provider}")

    if source != "market_input_file":
        snapshots, stale_warnings = _filter_stale_market_snapshots(root, snapshots)
        warnings.extend(stale_warnings)
    snapshots = [snapshot for snapshot in snapshots if snapshot["ticker"] in set(tickers)]
    _append_market_snapshots(root, snapshots, source)
    missing_tickers = sorted(set(tickers) - {snapshot["ticker"] for snapshot in snapshots})
    investment_snapshots = [
        snapshot for snapshot in snapshots if snapshot["ticker"] in set(investment_tickers)
    ]
    investment_missing = sorted(set(investment_tickers) - {item["ticker"] for item in snapshots})
    context_missing = sorted(set(context) & set(missing_tickers))
    if context_missing:
        warnings.append(
            "Market regime context missing: " + ", ".join(context_missing)
        )
    events = _market_events(investment_snapshots, thresholds, source)
    events.extend(_market_coverage_events(investment_missing, source, warnings))
    output = _write_channel_events(root, "market", events)
    aggregate = _refresh_latest_events(root)
    _update_ingest_status(
        root,
        "market",
        source=source,
        event_count=len(events),
        item_count=len(snapshots),
        expected_item_count=len(tickers),
        missing_tickers=missing_tickers,
        warnings=warnings,
    )
    return IngestResult("market", source, len(events), output, aggregate, tuple(warnings))


def ingest_filings(
    root: Path,
    *,
    company_tickers_input: Path | None = None,
    submissions_dir: Path | None = None,
    lookback_days: int = 3,
    sec_user_agent: str = "",
) -> IngestResult:
    thresholds = load_yaml_file(root / "configs" / "signal_thresholds.yaml")
    forms = _configured_sec_forms(thresholds)
    watchlist = load_watchlist(root)
    tickers = _coverage_tickers(watchlist, "filing_data_required")
    symbol_overrides = _filing_symbol_overrides(root)
    exempt_tickers = _filing_exemptions(root)
    user_agent = effective_sec_user_agent(root, sec_user_agent)
    cutoff = _today_date() - timedelta(days=lookback_days)
    events: list[dict[str, Any]] = []
    warnings: list[str] = _coverage_exemption_warnings(
        watchlist,
        "filing_data_required",
        "Filing",
    )
    missing_tickers: list[str] = []
    live_atom_fallback = False
    if company_tickers_input is not None:
        company_tickers = json.loads(company_tickers_input.read_text(encoding="utf-8"))
        source = "sec_input_file"
    elif os.environ.get("BCAP_FILING_EVENTS_URL"):
        events, warnings, missing_tickers = _fetch_filing_feed_events(tickers, forms, cutoff)
        _raise_if_no_filing_coverage(tickers, missing_tickers, warnings)
        source = "filing_feed_url"
        output = _write_channel_events(root, "filings", events)
        aggregate = _refresh_latest_events(root)
        _update_ingest_status(
            root,
            "filings",
            source=source,
            event_count=len(events),
            item_count=len(tickers) - len(missing_tickers),
            expected_item_count=len(tickers),
            missing_tickers=missing_tickers,
            warnings=warnings,
        )
        return IngestResult("filings", source, len(events), output, aggregate, tuple(warnings))
    else:
        if not user_agent:
            raise IngestError(
                "SEC live ingestion requires --sec-user-agent or BCAP_SEC_USER_AGENT."
            )
        try:
            company_tickers = _fetch_json(_sec_company_tickers_url(), user_agent=user_agent)
        except IngestError as exc:
            warnings.append(f"SEC company tickers JSON unavailable; using browse Atom: {exc}")
            events, atom_warnings, missing_tickers = _fetch_sec_atom_events_for_tickers(
                tickers,
                forms,
                cutoff,
                user_agent,
            )
            warnings.extend(atom_warnings)
            _raise_if_no_filing_coverage(tickers, missing_tickers, warnings)
            source = "sec_browse_atom"
            output = _write_channel_events(root, "filings", events)
            aggregate = _refresh_latest_events(root)
            _update_ingest_status(
                root,
                "filings",
                source=source,
                event_count=len(events),
                item_count=len(tickers) - len(missing_tickers),
                expected_item_count=len(tickers),
                missing_tickers=missing_tickers,
                warnings=warnings,
            )
            return IngestResult("filings", source, len(events), output, aggregate, tuple(warnings))
        source = "sec_submissions"

    cik_by_ticker = _cik_map(company_tickers)
    for ticker in tickers:
        provider_ticker = symbol_overrides.get(ticker, ticker)
        if ticker in exempt_tickers:
            warnings.append(
                f"Filing coverage exempt for {ticker}: {exempt_tickers[ticker]}"
            )
            continue
        cik = cik_by_ticker.get(provider_ticker)
        if not cik:
            warnings.append(f"No SEC CIK found for {ticker} using {provider_ticker}.")
            missing_tickers.append(ticker)
            continue
        if submissions_dir is not None:
            submissions_path = submissions_dir / f"CIK{cik}.json"
            if not submissions_path.exists():
                warnings.append(f"Missing submissions fixture for {ticker}: {submissions_path}.")
                missing_tickers.append(ticker)
                continue
            submissions = json.loads(submissions_path.read_text(encoding="utf-8"))
        else:
            try:
                submissions = _fetch_json(
                    _sec_submissions_url(cik),
                    user_agent=user_agent,
                )
            except IngestError as exc:
                live_atom_fallback = True
                warnings.append(f"{ticker} submissions JSON unavailable; using browse Atom: {exc}")
                atom_events, atom_warnings, atom_missing = _fetch_sec_atom_events_for_tickers(
                    [ticker],
                    forms,
                    cutoff,
                    user_agent,
                )
                warnings.extend(atom_warnings)
                if atom_missing:
                    missing_tickers.extend(atom_missing)
                events.extend(atom_events)
                continue
        events.extend(
            _filing_events_for_ticker(
                ticker,
                cik,
                submissions,
                forms,
                cutoff,
                source,
            )
        )
    if live_atom_fallback and source == "sec_submissions":
        source = "sec_submissions+sec_browse_atom"
    _raise_if_no_filing_coverage(tickers, missing_tickers, warnings)

    output = _write_channel_events(root, "filings", events)
    aggregate = _refresh_latest_events(root)
    _update_ingest_status(
        root,
        "filings",
        source=source,
        event_count=len(events),
        item_count=len(tickers) - len(set(missing_tickers)),
        expected_item_count=len(tickers),
        missing_tickers=sorted(set(missing_tickers)),
        warnings=warnings,
    )
    return IngestResult("filings", source, len(events), output, aggregate, tuple(warnings))


def write_manual_event(root: Path, event: dict[str, Any]) -> Path:
    path = root / "state" / "latest_manual_events.jsonl"
    existing = [
        item
        for item in read_json_events(path)
        if scalar_text(item.get("dedupe_key")) != scalar_text(event.get("dedupe_key"))
    ]
    existing.append(event)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in existing),
        encoding="utf-8",
    )
    _refresh_latest_events(root)
    return path


def clear_manual_event(root: Path, dedupe_key: str) -> Path:
    path = root / "state" / "latest_manual_events.jsonl"
    existing = [
        item for item in read_json_events(path) if scalar_text(item.get("dedupe_key")) != dedupe_key
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in existing),
        encoding="utf-8",
    )
    _refresh_latest_events(root)
    return path


def _load_market_snapshots(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        loaded: Any = read_jsonl(path)
    else:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(loaded, dict) and "snapshots" in loaded:
        loaded = loaded["snapshots"]
    elif isinstance(loaded, dict):
        loaded = [{"ticker": ticker, **snapshot} for ticker, snapshot in loaded.items()]
    if not isinstance(loaded, list):
        raise IngestError(f"Market snapshot input must be a list or mapping: {path}")
    return [_normalize_market_snapshot(item) for item in loaded if isinstance(item, dict)]


def _market_symbol_overrides(root: Path) -> dict[str, str]:
    return _symbol_overrides(root, "market")


def _coverage_tickers(watchlist: list[dict[str, Any]], field: str) -> list[str]:
    return [item["ticker"] for item in watchlist if _coverage_required(item, field)]


def _coverage_exemption_warnings(
    watchlist: list[dict[str, Any]],
    field: str,
    channel: str,
) -> list[str]:
    return [
        f"{channel} coverage exempt for {item['ticker']}: "
        f"{scalar_text(item.get('coverage_exemption_reason')) or 'configured exemption'}"
        for item in watchlist
        if not _coverage_required(item, field)
    ]


def _coverage_required(item: dict[str, Any], field: str) -> bool:
    value = item.get(field, True)
    if isinstance(value, bool):
        return value
    return scalar_text(value).lower() not in {"0", "false", "no", "off"}


def _filing_symbol_overrides(root: Path) -> dict[str, str]:
    return _symbol_overrides(root, "filings")


def _symbol_overrides(root: Path, channel: str) -> dict[str, str]:
    config_path = root / "configs" / "live_sources.yaml"
    if not config_path.exists():
        return {}
    config = load_yaml_file(config_path)
    channel_config = config.get(channel, {}) if isinstance(config, dict) else {}
    overrides = (
        channel_config.get("symbol_overrides", {}) if isinstance(channel_config, dict) else {}
    )
    if not isinstance(overrides, dict):
        return {}
    return {
        scalar_text(ticker).upper(): scalar_text(provider_symbol).upper()
        for ticker, provider_symbol in overrides.items()
        if scalar_text(ticker) and scalar_text(provider_symbol)
    }


def _filing_exemptions(root: Path) -> dict[str, str]:
    config_path = root / "configs" / "live_sources.yaml"
    if not config_path.exists():
        return {}
    config = load_yaml_file(config_path)
    filings = config.get("filings", {}) if isinstance(config, dict) else {}
    exempt = filings.get("exempt_tickers", {}) if isinstance(filings, dict) else {}
    if isinstance(exempt, list):
        return {scalar_text(ticker).upper(): "configured filing exemption" for ticker in exempt}
    if not isinstance(exempt, dict):
        return {}
    return {
        scalar_text(ticker).upper(): scalar_text(reason) or "configured filing exemption"
        for ticker, reason in exempt.items()
        if scalar_text(ticker)
    }


def _provider_symbols(symbols: list[str], symbol_overrides: dict[str, str]) -> dict[str, str]:
    return {
        symbol.upper(): symbol_overrides.get(symbol.upper(), symbol.upper())
        for symbol in symbols
    }


def _filter_stale_market_snapshots(
    root: Path,
    snapshots: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    max_age_days = _market_snapshot_max_age_days(root)
    today = _today_date()
    kept: list[dict[str, Any]] = []
    stale: list[str] = []
    for snapshot in snapshots:
        observed_date = _date_prefix_value(scalar_text(snapshot.get("observed_at")))
        if observed_date is not None and (today - observed_date).days > max_age_days:
            stale.append(
                f"{snapshot['ticker']}: observed_at {snapshot.get('observed_at')} "
                f"older than {max_age_days} days"
            )
            continue
        kept.append(snapshot)
    warnings = []
    if stale:
        warnings.append(
            f"Market ingest rejected {len(stale)} stale snapshot(s): {'; '.join(stale[:5])}"
        )
    return kept, warnings


def _market_snapshot_max_age_days(root: Path) -> int:
    config_path = root / "configs" / "live_sources.yaml"
    if not config_path.exists():
        return 7
    config = load_yaml_file(config_path)
    market = config.get("market", {}) if isinstance(config, dict) else {}
    value = market.get("max_snapshot_age_days", 7) if isinstance(market, dict) else 7
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 7


def _normalize_market_snapshot(item: dict[str, Any]) -> dict[str, Any]:
    latest_trade = item.get("latestTrade") if isinstance(item.get("latestTrade"), dict) else {}
    daily_bar = item.get("dailyBar") if isinstance(item.get("dailyBar"), dict) else {}
    prev_daily_bar = item.get("prevDailyBar") if isinstance(item.get("prevDailyBar"), dict) else {}
    ticker = scalar_text(item.get("ticker") or item.get("symbol")).upper()
    price = _float_value(item.get("price") or item.get("latest_price") or latest_trade.get("p"))
    previous_close = _float_value(
        item.get("previous_close") or item.get("prev_close") or prev_daily_bar.get("c")
    )
    open_price = _float_value(item.get("open") or item.get("open_price") or daily_bar.get("o"))
    observed_at = scalar_text(
        item.get("observed_at") or item.get("timestamp") or latest_trade.get("t")
    )
    return {
        "ticker": ticker,
        "price": price,
        "previous_close": previous_close,
        "open": open_price,
        "observed_at": observed_at or _now(),
        "raw_snapshot": item,
    }


def _fetch_alpaca_snapshots(
    symbols: list[str],
    symbol_overrides: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    key = os.environ.get("APCA_API_KEY_ID", "")
    secret = os.environ.get("APCA_API_SECRET_KEY", "")
    if not key or not secret:
        raise IngestError(
            "Alpaca market ingestion requires APCA_API_KEY_ID and APCA_API_SECRET_KEY."
        )
    base_url = os.environ.get("ALPACA_DATA_BASE_URL", ALPACA_DATA_BASE_URL).rstrip("/")
    snapshots: list[dict[str, Any]] = []
    provider_by_ticker = _provider_symbols(symbols, symbol_overrides or {})
    ticker_by_provider = {provider: ticker for ticker, provider in provider_by_ticker.items()}
    for batch in _batches(symbols, 50):
        provider_batch = [provider_by_ticker[symbol] for symbol in batch]
        query = urllib.parse.urlencode({"symbols": ",".join(provider_batch)})
        request = urllib.request.Request(
            f"{base_url}/v2/stocks/snapshots?{query}",
            headers={
                "APCA-API-KEY-ID": key,
                "APCA-API-SECRET-KEY": secret,
            },
        )
        data = _open_json(request)
        if isinstance(data, dict) and "snapshots" in data:
            data = data["snapshots"]
        if not isinstance(data, dict):
            raise IngestError("Alpaca snapshots response was not a symbol mapping.")
        snapshots.extend(
            _normalize_market_snapshot(
                {"ticker": ticker_by_provider.get(ticker, ticker), **snapshot}
            )
            for ticker, snapshot in data.items()
            if isinstance(snapshot, dict)
        )
    return snapshots


def _fetch_auto_market_snapshots(
    symbols: list[str],
    symbol_overrides: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], str, list[str]]:
    warnings: list[str] = []
    if os.environ.get("APCA_API_KEY_ID") and os.environ.get("APCA_API_SECRET_KEY"):
        try:
            return _fetch_alpaca_snapshots(
                symbols,
                symbol_overrides,
            ), "market_alpaca", warnings
        except IngestError as exc:
            warnings.append(f"Alpaca ingest failed; using Yahoo fallback: {exc}")
    else:
        warnings.append("Alpaca credentials missing; using Yahoo fallback.")
    snapshots, yahoo_warnings = _fetch_yahoo_snapshots(symbols, symbol_overrides or {})
    warnings.extend(yahoo_warnings)
    return snapshots, "market_yahoo", warnings


def _fetch_yahoo_snapshots(
    symbols: list[str],
    symbol_overrides: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    snapshots: list[dict[str, Any]] = []
    failures: list[str] = []
    stooq_fallbacks: list[str] = []
    provider_by_ticker = _provider_symbols(symbols, symbol_overrides or {})
    for symbol in symbols:
        provider_symbol = provider_by_ticker[symbol]
        yahoo_symbol = _yahoo_symbol(provider_symbol)
        query = urllib.parse.urlencode(
            {
                "range": "1d",
                "interval": "5m",
                "includePrePost": "true",
            }
        )
        request = urllib.request.Request(
            f"{YAHOO_CHART_BASE_URL}/v8/finance/chart/{yahoo_symbol}?{query}",
            headers={"User-Agent": "Bottleneck Capital market ingest"},
        )
        try:
            data = _open_json(request)
            snapshots.append(_normalize_yahoo_snapshot(symbol, data))
        except (IngestError, KeyError, TypeError, ValueError) as exc:
            try:
                snapshots.append(_fetch_stooq_snapshot(symbol, provider_symbol=provider_symbol))
                stooq_fallbacks.append(symbol)
            except IngestError as stooq_exc:
                failures.append(f"{symbol}: {exc}; Stooq fallback failed: {stooq_exc}")
    if not snapshots:
        raise IngestError(f"Yahoo market ingestion produced no snapshots: {'; '.join(failures)}")
    warnings: list[str] = []
    if stooq_fallbacks:
        warnings.append(
            f"Stooq fallback used for {len(stooq_fallbacks)} symbol(s): "
            f"{', '.join(stooq_fallbacks)}"
        )
    if failures:
        warning = "; ".join(failures[:5])
        if len(failures) > 5:
            warning = f"{warning}; plus {len(failures) - 5} more"
        warnings.append(f"Yahoo market ingestion missed {len(failures)} symbol(s): {warning}")
    return snapshots, warnings


def _fetch_stooq_snapshot(symbol: str, *, provider_symbol: str | None = None) -> dict[str, Any]:
    stooq_symbol = (provider_symbol or symbol).lower()
    query = urllib.parse.urlencode({"s": f"{stooq_symbol}.us", "i": "d"})
    request = urllib.request.Request(
        f"{STOOQ_BASE_URL}/q/d/l/?{query}",
        headers={"User-Agent": "Bottleneck Capital market ingest"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            text = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise IngestError(f"Network request failed: {exc}") from exc
    rows = list(csv.DictReader(io.StringIO(text)))
    valid_rows = [
        row
        for row in rows
        if _float_value(row.get("Close")) > 0 and _float_value(row.get("Open")) > 0
    ]
    if not valid_rows:
        raise IngestError("Stooq returned no usable daily rows.")
    if len(valid_rows) < 2:
        raise IngestError("Stooq returned fewer than two daily rows.")
    latest = valid_rows[-1]
    previous = valid_rows[-2] if len(valid_rows) >= 2 else {}
    latest_date = scalar_text(latest.get("Date"))
    return {
        "ticker": symbol.upper(),
        "price": _float_value(latest.get("Close")),
        "previous_close": _float_value(previous.get("Close")),
        "open": _float_value(latest.get("Open")),
        "observed_at": f"{latest_date}T16:00:00-04:00" if latest_date else _now(),
        "raw_snapshot": {
            "source": "stooq_daily",
            "symbol": f"{stooq_symbol}.us",
        },
    }


def _normalize_yahoo_snapshot(symbol: str, data: dict[str, Any]) -> dict[str, Any]:
    result = data["chart"]["result"][0]
    meta = result.get("meta", {})
    timestamps = result.get("timestamp", [])
    quotes = result.get("indicators", {}).get("quote", [{}])
    quote = quotes[0] if quotes and isinstance(quotes[0], dict) else {}
    opens = quote.get("open", [])
    closes = quote.get("close", [])
    price = _float_value(meta.get("regularMarketPrice"))
    if price <= 0:
        price = _last_positive(closes)
    previous_close = _float_value(meta.get("previousClose") or meta.get("chartPreviousClose"))
    open_price = _first_positive(opens)
    if price <= 0 or previous_close <= 0:
        raise ValueError("Yahoo chart response was missing price or previous close.")
    observed_epoch = int(meta.get("regularMarketTime") or (timestamps[-1] if timestamps else 0))
    observed_at = (
        datetime.fromtimestamp(observed_epoch, ZoneInfo("America/Toronto")).isoformat(
            timespec="seconds"
        )
        if observed_epoch
        else _now()
    )
    return {
        "ticker": symbol.upper(),
        "price": price,
        "previous_close": previous_close,
        "open": open_price,
        "observed_at": observed_at,
        "raw_snapshot": {
            "source": "yahoo_chart",
            "symbol": meta.get("symbol") or _yahoo_symbol(symbol),
            "currency": meta.get("currency", ""),
            "exchange": meta.get("exchangeName", ""),
            "market_state": meta.get("marketState", ""),
        },
    }


def _market_events(
    snapshots: list[dict[str, Any]],
    thresholds: dict[str, Any],
    source: str,
) -> list[dict[str, Any]]:
    price_triggers = thresholds.get("sentinel", {}).get("price_triggers", {})
    one_day_threshold = float(price_triggers.get("one_day_drop_pct", 7))
    intraday_threshold = float(price_triggers.get("intraday_drop_pct", 5))
    gap_threshold = float(price_triggers.get("gap_down_pct", 4))
    events: list[dict[str, Any]] = []
    today = _today()
    for snapshot in snapshots:
        ticker = snapshot["ticker"]
        price = snapshot["price"]
        previous_close = snapshot["previous_close"]
        open_price = snapshot["open"]
        triggers: list[str] = []
        trigger_keys: list[str] = []
        one_day = _pct_change(price, previous_close)
        intraday = _pct_change(price, open_price)
        gap = _pct_change(open_price, previous_close)
        if one_day is not None and one_day <= -one_day_threshold:
            triggers.append(f"one-day {one_day:.1f}%")
            trigger_keys.append("one_day")
        if intraday is not None and intraday <= -intraday_threshold:
            triggers.append(f"intraday {intraday:.1f}%")
            trigger_keys.append("intraday")
        if gap is not None and gap <= -gap_threshold:
            triggers.append(f"gap {gap:.1f}%")
            trigger_keys.append("gap")
        if not triggers:
            continue
        events.append(
            {
                "ticker": ticker,
                "event_type": "price_dislocation",
                "source": source,
                "summary": f"{ticker} price dislocation: {', '.join(triggers)}.",
                "dedupe_key": f"market:{ticker}:{today}:price_dislocation",
                "price": price,
                "previous_close": previous_close,
                "open": open_price,
                "one_day_drop_pct": one_day,
                "intraday_drop_pct": intraday,
                "gap_down_pct": gap,
                "observed_at": snapshot["observed_at"],
            }
        )
    return events


def _market_coverage_events(
    missing_tickers: list[str],
    source: str,
    warnings: list[str],
) -> list[dict[str, Any]]:
    today = _today()
    summary_suffix = f" Provider warnings: {'; '.join(warnings)}" if warnings else ""
    return [
        {
            "ticker": ticker,
            "event_type": "market_data_gap",
            "event_class": "market_data_gap",
            "source": source,
            "summary": (
                f"Market ingest did not return a live snapshot for {ticker}; strict-live "
                f"coverage is incomplete.{summary_suffix}"
            ),
            "dedupe_key": f"market_data_gap:{ticker}:{today}:{source}",
        }
        for ticker in missing_tickers
    ]


def _filing_events_for_ticker(
    ticker: str,
    cik: str,
    submissions: dict[str, Any],
    forms: set[str],
    cutoff: date,
    source: str,
) -> list[dict[str, Any]]:
    recent = submissions.get("filings", {}).get("recent", {})
    if not isinstance(recent, dict):
        return []
    form_values = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    accepted_times = recent.get("acceptanceDateTime", [])
    documents = recent.get("primaryDocument", [])
    events: list[dict[str, Any]] = []
    for index, form in enumerate(form_values):
        form_text = scalar_text(form).upper()
        if not _form_matches(form_text, forms):
            continue
        filing_date = _list_value(filing_dates, index)
        parsed_date = _date_value(filing_date)
        if parsed_date is not None and parsed_date < cutoff:
            continue
        accession = _list_value(accessions, index)
        accepted_at = _list_value(accepted_times, index)
        document = _list_value(documents, index)
        events.append(
            {
                "ticker": ticker,
                "event_type": "sec_filing",
                "source": source,
                "filing_type": form_text,
                "summary": f"New SEC filing {form_text} for {ticker}: {accession}.",
                "dedupe_key": f"sec:{ticker}:{accession or form_text}:{filing_date}",
                "cik": cik,
                "accession": accession,
                "filing_date": filing_date,
                "accepted_at": accepted_at,
                "primary_document": document,
            }
        )
    return events


def _fetch_sec_atom_events_for_tickers(
    tickers: list[str],
    forms: set[str],
    cutoff: date,
    user_agent: str,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    missing_tickers: list[str] = []
    consecutive_forbidden = 0
    for index, ticker in enumerate(tickers):
        if index:
            time.sleep(_sec_request_delay_seconds())
        try:
            feed = _fetch_sec_atom_feed(ticker, user_agent=user_agent)
        except IngestError as exc:
            warnings.append(f"SEC browse Atom failed for {ticker}: {exc}")
            missing_tickers.append(ticker)
            if "HTTP Error 403" in str(exc):
                consecutive_forbidden += 1
                if consecutive_forbidden >= 3:
                    remaining = [
                        item for item in tickers[index + 1 :] if item not in missing_tickers
                    ]
                    missing_tickers.extend(remaining)
                    warnings.append(
                        "SEC browse Atom stopped after 3 consecutive 403 responses; "
                        "backoff or a different filing data path is required."
                    )
                    break
            else:
                consecutive_forbidden = 0
            continue
        consecutive_forbidden = 0
        ticker_events, company_name = _sec_atom_events_for_ticker(
            ticker,
            feed,
            forms,
            cutoff,
        )
        if not company_name:
            warnings.append(f"SEC browse Atom found no company for {ticker}.")
            missing_tickers.append(ticker)
            continue
        events.extend(ticker_events)
    return events, warnings, sorted(set(missing_tickers))


def _fetch_filing_feed_events(
    tickers: list[str],
    forms: set[str],
    cutoff: date,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    feed_url = scalar_text(os.environ.get("BCAP_FILING_EVENTS_URL"))
    if not feed_url:
        raise IngestError("BCAP_FILING_EVENTS_URL is not configured.")
    request = urllib.request.Request(
        feed_url,
        headers=_filing_feed_headers(),
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            text = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise IngestError(f"Filing feed request failed: {exc}") from exc
    records, covered_tickers = _parse_filing_feed_text(text)
    watchlist = {ticker.upper() for ticker in tickers}
    covered = {ticker.upper() for ticker in covered_tickers} if covered_tickers else set(watchlist)
    events = [
        event
        for record in records
        if (
            event := _normalize_filing_feed_event(record, watchlist, forms, cutoff)
        )
        is not None
    ]
    missing_tickers = sorted(watchlist - covered)
    warnings: list[str] = []
    if not covered_tickers:
        warnings.append(
            "Filing feed did not declare covered_tickers; assuming the configured URL covers "
            "the full watchlist."
        )
    return events, warnings, missing_tickers


def _filing_feed_headers() -> dict[str, str]:
    headers = {"User-Agent": "Bottleneck Capital filing feed ingest"}
    auth_header = scalar_text(os.environ.get("BCAP_FILING_EVENTS_AUTH_HEADER"))
    if ":" in auth_header:
        name, value = auth_header.split(":", 1)
        if name.strip() and value.strip():
            headers[name.strip()] = value.strip()
    return headers


def _parse_filing_feed_text(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    stripped = text.strip()
    if not stripped:
        return [], []
    if stripped.startswith("{") or stripped.startswith("["):
        loaded = json.loads(stripped)
    else:
        loaded = [json.loads(line) for line in stripped.splitlines() if line.strip()]
    covered_tickers: list[str] = []
    if isinstance(loaded, dict):
        raw_covered = loaded.get("covered_tickers", [])
        if isinstance(raw_covered, list):
            covered_tickers = [scalar_text(ticker).upper() for ticker in raw_covered]
        loaded = loaded.get("events", [])
    if not isinstance(loaded, list):
        raise IngestError("Filing feed must return an events list, JSON array, or JSONL records.")
    if not all(isinstance(item, dict) for item in loaded):
        raise IngestError("Filing feed events must be JSON objects.")
    return loaded, covered_tickers


def _normalize_filing_feed_event(
    record: dict[str, Any],
    watchlist: set[str],
    forms: set[str],
    cutoff: date,
) -> dict[str, Any] | None:
    ticker = scalar_text(record.get("ticker") or record.get("symbol")).upper()
    if ticker not in watchlist:
        return None
    form_text = scalar_text(record.get("filing_type") or record.get("form")).upper()
    if form_text and not _form_matches(form_text, forms):
        return None
    filing_date = scalar_text(record.get("filing_date") or record.get("date"))
    parsed_date = _date_value(filing_date)
    if parsed_date is not None and parsed_date < cutoff:
        return None
    accession = scalar_text(record.get("accession") or record.get("accession_number"))
    summary = scalar_text(record.get("summary"))
    if not summary:
        summary = f"New filing {form_text or 'UNKNOWN'} for {ticker}: {accession}."
    return {
        "ticker": ticker,
        "event_type": scalar_text(record.get("event_type")) or "sec_filing",
        "source": "filing_feed_url",
        "filing_type": form_text,
        "summary": summary,
        "dedupe_key": scalar_text(record.get("dedupe_key"))
        or f"filing-feed:{ticker}:{accession or form_text}:{filing_date}",
        "cik": scalar_text(record.get("cik")),
        "accession": accession,
        "filing_date": filing_date,
        "accepted_at": scalar_text(record.get("accepted_at") or record.get("updated_at")),
        "filing_href": scalar_text(record.get("filing_href") or record.get("url")),
    }


def _sec_request_delay_seconds() -> float:
    try:
        return max(0.0, float(os.environ.get("BCAP_SEC_REQUEST_DELAY_SECONDS", "0.35")))
    except ValueError:
        return 0.35


def _sec_company_tickers_url() -> str:
    return os.environ.get("BCAP_SEC_COMPANY_TICKERS_URL", SEC_COMPANY_TICKERS_URL)


def _sec_submissions_url(cik: str) -> str:
    template = os.environ.get("BCAP_SEC_SUBMISSIONS_URL_TEMPLATE", SEC_SUBMISSIONS_URL)
    return template.format(cik=cik)


def _sec_browse_atom_url(query: str) -> str:
    base_url = os.environ.get("BCAP_SEC_BROWSE_ATOM_URL", SEC_BROWSE_ATOM_URL).rstrip("?")
    return f"{base_url}?{query}"


def _raise_if_no_filing_coverage(
    tickers: list[str],
    missing_tickers: list[str],
    warnings: list[str],
) -> None:
    expected = {ticker.upper() for ticker in tickers}
    missing = {ticker.upper() for ticker in missing_tickers}
    if expected and expected <= missing:
        detail = "; ".join(warnings[-5:])
        raise IngestError(f"SEC filing ingest produced no ticker coverage. {detail}")


def _fetch_sec_atom_feed(ticker: str, *, user_agent: str) -> str:
    query = urllib.parse.urlencode(
        {
            "action": "getcompany",
            "CIK": ticker,
            "owner": "exclude",
            "count": "40",
            "output": "atom",
        }
    )
    request = urllib.request.Request(
        _sec_browse_atom_url(query),
        headers={
            "User-Agent": user_agent,
            "Accept": "application/atom+xml, text/xml, */*",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise IngestError(f"Network request failed: {exc}") from exc


def _sec_atom_events_for_ticker(
    ticker: str,
    feed_text: str,
    forms: set[str],
    cutoff: date,
) -> tuple[list[dict[str, Any]], str]:
    try:
        feed = ET.fromstring(feed_text)
    except ET.ParseError as exc:
        raise IngestError(f"SEC browse Atom parse failed for {ticker}: {exc}") from exc
    company_info = _first_child(feed, "company-info")
    if company_info is None:
        return [], ""
    cik = _child_text(company_info, "cik")
    company_name = _child_text(company_info, "conformed-name")
    events: list[dict[str, Any]] = []
    for entry in _children(feed, "entry"):
        content = _first_child(entry, "content")
        form_text = _child_text(content, "filing-type") if content is not None else ""
        if not form_text:
            form_text = _category_term(entry)
        form_text = scalar_text(form_text).upper()
        if not _form_matches(form_text, forms):
            continue
        filing_date = _child_text(content, "filing-date") if content is not None else ""
        parsed_date = _date_value(filing_date)
        if parsed_date is not None and parsed_date < cutoff:
            continue
        accession = _child_text(content, "accession-number") if content is not None else ""
        filing_href = _child_text(content, "filing-href") if content is not None else ""
        accepted_at = _child_text(entry, "updated")
        events.append(
            {
                "ticker": ticker.upper(),
                "event_type": "sec_filing",
                "source": "sec_browse_atom",
                "filing_type": form_text,
                "summary": f"New SEC filing {form_text} for {ticker.upper()}: {accession}.",
                "dedupe_key": f"sec:{ticker.upper()}:{accession or form_text}:{filing_date}",
                "cik": cik,
                "company_name": company_name,
                "accession": accession,
                "filing_date": filing_date,
                "accepted_at": accepted_at,
                "filing_href": filing_href or _alternate_link(entry),
            }
        )
    return events, company_name


def _children(element: ET.Element, tag: str) -> list[ET.Element]:
    return [child for child in list(element) if _local_name(child.tag) == tag]


def _first_child(element: ET.Element, tag: str) -> ET.Element | None:
    for child in list(element):
        if _local_name(child.tag) == tag:
            return child
    return None


def _child_text(element: ET.Element | None, tag: str) -> str:
    if element is None:
        return ""
    child = _first_child(element, tag)
    return scalar_text(child.text if child is not None else "")


def _category_term(entry: ET.Element) -> str:
    category = _first_child(entry, "category")
    return scalar_text(category.attrib.get("term") if category is not None else "")


def _alternate_link(entry: ET.Element) -> str:
    for link in _children(entry, "link"):
        if scalar_text(link.attrib.get("rel")) == "alternate":
            return scalar_text(link.attrib.get("href"))
    return ""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _write_channel_events(root: Path, channel: str, events: list[dict[str, Any]]) -> Path:
    path = root / "state" / f"latest_{channel}_events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )
    return path


def _refresh_latest_events(root: Path) -> Path:
    paths = [
        root / "state" / "latest_market_events.jsonl",
        root / "state" / "latest_filings_events.jsonl",
        root / "state" / "latest_manual_events.jsonl",
    ]
    events: list[dict[str, Any]] = []
    for path in paths:
        if path.exists():
            events.extend(read_json_events(path))
    aggregate = root / "state" / "latest_events.jsonl"
    aggregate.parent.mkdir(parents=True, exist_ok=True)
    aggregate.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )
    return aggregate


def _append_market_snapshots(root: Path, snapshots: list[dict[str, Any]], source: str) -> None:
    path = root / "state" / "market_snapshots.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for snapshot in snapshots:
            record = {**snapshot, "source": source, "ingested_at": _now()}
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def _update_ingest_status(
    root: Path,
    channel: str,
    *,
    source: str,
    event_count: int,
    item_count: int,
    expected_item_count: int,
    missing_tickers: list[str],
    warnings: list[str],
) -> None:
    path = root / "state" / "ingest_status.json"
    existing: dict[str, Any] = {}
    if path.exists():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            existing = loaded
    existing[channel] = {
        "last_success_at": _now(),
        "source": source,
        "event_count": event_count,
        "item_count": item_count,
        "expected_item_count": expected_item_count,
        "missing_tickers": missing_tickers,
        "warnings": warnings,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _configured_sec_forms(thresholds: dict[str, Any]) -> set[str]:
    forms = thresholds.get("sentinel", {}).get("source_triggers", {}).get("sec_filings", [])
    normalized = {_normalize_form(scalar_text(form)) for form in forms}
    normalized.update({"4", "6-K", "20-F", "SC 13D", "SC 13G"})
    return {form for form in normalized if form}


def _cik_map(company_tickers: Any) -> dict[str, str]:
    values = company_tickers.values() if isinstance(company_tickers, dict) else company_tickers
    if not isinstance(values, (list, tuple, set)):
        values = list(values)
    mapping: dict[str, str] = {}
    for item in values:
        if not isinstance(item, dict):
            continue
        ticker = scalar_text(item.get("ticker")).upper()
        cik = scalar_text(item.get("cik_str") or item.get("cik"))
        if ticker and cik:
            mapping[ticker] = cik.zfill(10)
    return mapping


def _fetch_json(url: str, *, user_agent: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    return _open_json(request)


def _open_json(request: urllib.request.Request) -> Any:
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise IngestError(f"Network request failed: {exc}") from exc


def _batches(items: list[str], size: int) -> list[list[str]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def _yahoo_symbol(symbol: str) -> str:
    return symbol.upper().replace(".", "-")


def _first_positive(values: Any) -> float:
    if not isinstance(values, list):
        return 0.0
    for value in values:
        number = _float_value(value)
        if number > 0:
            return number
    return 0.0


def _last_positive(values: Any) -> float:
    if not isinstance(values, list):
        return 0.0
    for value in reversed(values):
        number = _float_value(value)
        if number > 0:
            return number
    return 0.0


def _pct_change(current: float, base: float) -> float | None:
    if current <= 0 or base <= 0:
        return None
    return ((current - base) / base) * 100


def _float_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _list_value(values: Any, index: int) -> str:
    if isinstance(values, list) and index < len(values):
        return scalar_text(values[index])
    return ""


def _date_value(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _date_prefix_value(value: str) -> date | None:
    if len(value) < 10:
        return None
    return _date_value(value[:10])


def _form_matches(form: str, forms: set[str]) -> bool:
    normalized = _normalize_form(form)
    return normalized in forms or any(normalized.startswith(f"{candidate}/") for candidate in forms)


def _normalize_form(form: str) -> str:
    text = form.upper().strip()
    if text == "FORM 4":
        return "4"
    return text


def _today() -> str:
    return _today_date().isoformat()


def _today_date() -> date:
    return datetime.now(ZoneInfo("America/Toronto")).date()


def _now() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
