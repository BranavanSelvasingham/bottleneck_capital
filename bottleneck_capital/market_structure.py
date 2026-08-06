from __future__ import annotations

import json
import os
import ssl
import statistics
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import load_watchlist
from bottleneck_capital.io import load_yaml_file, read_jsonl, scalar_bool, scalar_text

FINRA_DAILY_URL = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{date}.txt"
STRUCTURE_FIELDS = (
    "reported_short_interest_shares",
    "float_shares",
    "short_interest_pct_float",
    "days_to_cover",
    "short_volume",
    "short_exempt_volume",
    "total_reported_volume",
    "daily_short_volume_ratio_pct",
    "short_exempt_ratio_pct",
    "borrow_fee_pct",
    "borrow_utilization_pct",
    "shares_available_to_borrow",
    "put_call_open_interest_ratio",
    "put_call_volume_ratio",
    "implied_volatility_percentile",
    "dealer_gamma_state",
    "eligible_supply_shares",
    "unlock_date",
    "active_atm_or_secondary",
    "catalyst_within_days",
)


class MarketStructureError(RuntimeError):
    """Raised when market-structure ingestion cannot produce trustworthy data."""


@dataclass(frozen=True)
class MarketStructureIngestResult:
    source: str
    record_count: int
    snapshot_path: Path
    trade_date: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketStructureAssessment:
    ticker: str
    data_status: str
    observed_at: str
    flow_classification: str
    execution_gate: str
    score_adjustment: float
    short_pressure_score: float
    squeeze_potential_score: float
    short_interest_pct_float: float | None
    days_to_cover: float | None
    daily_short_volume_ratio_pct: float | None
    short_exempt_ratio_pct: float | None
    finra_volume_vs_20d_median: float | None
    borrow_fee_pct: float | None
    borrow_utilization_pct: float | None
    supply_overhang_pct_float: float | None
    evidence: tuple[str, ...]


def ingest_market_structure(
    root: Path,
    *,
    provider: str = "auto",
    input_path: Path | None = None,
    symbols: list[str] | None = None,
    trade_date: date | None = None,
) -> MarketStructureIngestResult:
    tickers = symbols or [item["ticker"] for item in load_watchlist(root)]
    symbol_overrides = _symbol_overrides(root)
    provider = provider.lower()
    warnings: list[str] = []
    covered_tickers: set[str] | None = None

    if input_path is not None:
        records, covered_tickers = _load_structure_input(input_path)
        source = "market_structure_input_file"
    elif provider in {"auto", "feed"} and os.environ.get("BCAP_MARKET_STRUCTURE_URL"):
        records, covered_tickers = _fetch_structure_feed(
            os.environ["BCAP_MARKET_STRUCTURE_URL"]
        )
        source = "market_structure_feed"
    elif provider in {"auto", "finra"}:
        provider_by_ticker = {
            ticker.upper(): symbol_overrides.get(ticker.upper(), ticker.upper())
            for ticker in tickers
        }
        ticker_by_provider = {
            provider_ticker: ticker for ticker, provider_ticker in provider_by_ticker.items()
        }
        records, selected_date = _fetch_latest_finra(
            list(provider_by_ticker.values()), trade_date=trade_date
        )
        for record in records:
            provider_ticker = scalar_text(record.get("ticker")).upper()
            record["ticker"] = ticker_by_provider.get(provider_ticker, provider_ticker)
        source = "finra_consolidated_short_volume"
        covered_tickers = {scalar_text(item.get("ticker")).upper() for item in records}
        warnings.append(
            "FINRA daily short volume is transaction flow, not end-of-day short interest; "
            "it can include market making, hedging, and intraday-covered shorts."
        )
        trade_date = selected_date
    else:
        raise MarketStructureError(f"Unsupported market-structure provider: {provider}")

    allowed = {ticker.upper() for ticker in tickers}
    normalized = [
        record
        for item in records
        if (record := _normalize_record(item, source=source)) is not None
        and scalar_text(record.get("ticker")).upper() in allowed
    ]
    if not normalized:
        raise MarketStructureError("Market-structure ingest returned no covered records.")

    path = root / "state" / "market_structure_snapshots.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in normalized:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    covered = covered_tickers or {scalar_text(item.get("ticker")).upper() for item in normalized}
    missing = sorted(allowed - covered)
    if missing:
        warnings.append("Market-structure coverage missing: " + ", ".join(missing))
    _update_ingest_status(
        root,
        source=source,
        item_count=len(normalized),
        expected_item_count=len(allowed),
        missing_tickers=missing,
        warnings=warnings,
    )
    observed_dates = [scalar_text(item.get("trade_date")) for item in normalized]
    return MarketStructureIngestResult(
        source=source,
        record_count=len(normalized),
        snapshot_path=path,
        trade_date=max(observed_dates, default=(trade_date or _today()).isoformat()),
        warnings=tuple(warnings),
    )


def assess_market_structure(
    root: Path,
    ticker: str,
    *,
    as_of: datetime | None = None,
) -> MarketStructureAssessment:
    now = as_of or datetime.now(ZoneInfo("America/Toronto"))
    ticker = ticker.upper()
    records = [
        item
        for item in read_jsonl(root / "state" / "market_structure_snapshots.jsonl")
        if scalar_text(item.get("ticker")).upper() == ticker
    ]
    if not records:
        return _missing_assessment(ticker)

    values, observed_by_field = _latest_values(records)
    observed_at = max(observed_by_field.values(), default="")
    config = market_structure_config(root)
    values, fresh_observed = _fresh_values(values, observed_by_field, now, config)
    fresh = bool(fresh_observed)
    daily_ratio = _optional_float(values.get("daily_short_volume_ratio_pct"))
    exempt_ratio = _optional_float(values.get("short_exempt_ratio_pct"))
    short_interest = _short_interest_pct(values)
    days_to_cover = _optional_float(values.get("days_to_cover"))
    borrow_fee = _optional_float(values.get("borrow_fee_pct"))
    utilization = _optional_float(values.get("borrow_utilization_pct"))
    supply_overhang = _supply_overhang_pct(values)
    volume_multiple = _finra_volume_multiple(records)
    price_return = _latest_price_return(root, ticker)
    active_supply = _active_supply_overhang(values, now.date(), supply_overhang, config)
    catalyst_days = _optional_float(values.get("catalyst_within_days"))

    pressure, pressure_inputs = _short_pressure_score(
        daily_ratio=daily_ratio,
        exempt_ratio=exempt_ratio,
        short_interest=short_interest,
        borrow_fee=borrow_fee,
        utilization=utilization,
        volume_multiple=volume_multiple,
        price_return=price_return,
        config=config,
    )
    squeeze, squeeze_inputs = _squeeze_score(
        short_interest=short_interest,
        days_to_cover=days_to_cover,
        borrow_fee=borrow_fee,
        utilization=utilization,
        put_call_oi=_optional_float(values.get("put_call_open_interest_ratio")),
        catalyst_days=catalyst_days,
        active_supply=active_supply,
        config=config,
    )
    classification, gate, adjustment = _classify_structure(
        fresh=fresh,
        pressure=pressure,
        pressure_inputs=pressure_inputs,
        squeeze=squeeze,
        squeeze_inputs=squeeze_inputs,
        active_supply=active_supply,
        price_return=price_return,
    )
    evidence = _assessment_evidence(
        daily_ratio=daily_ratio,
        exempt_ratio=exempt_ratio,
        short_interest=short_interest,
        days_to_cover=days_to_cover,
        borrow_fee=borrow_fee,
        utilization=utilization,
        volume_multiple=volume_multiple,
        supply_overhang=supply_overhang,
        active_supply=active_supply,
        price_return=price_return,
    )
    data_status = "FRESH" if fresh else "STALE"
    if len(fresh_observed) < 3:
        data_status = "PARTIAL" if fresh else "STALE_PARTIAL"
    return MarketStructureAssessment(
        ticker=ticker,
        data_status=data_status,
        observed_at=observed_at or "missing",
        flow_classification=classification,
        execution_gate=gate,
        score_adjustment=adjustment,
        short_pressure_score=pressure,
        squeeze_potential_score=squeeze,
        short_interest_pct_float=short_interest,
        days_to_cover=days_to_cover,
        daily_short_volume_ratio_pct=daily_ratio,
        short_exempt_ratio_pct=exempt_ratio,
        finra_volume_vs_20d_median=volume_multiple,
        borrow_fee_pct=borrow_fee,
        borrow_utilization_pct=utilization,
        supply_overhang_pct_float=supply_overhang,
        evidence=evidence,
    )


def market_structure_config(root: Path) -> dict[str, Any]:
    path = root / "configs" / "market_structure.yaml"
    if not path.exists():
        return {}
    data = load_yaml_file(path)
    config = data.get("market_structure", {}) if isinstance(data, dict) else {}
    return config if isinstance(config, dict) else {}


def _symbol_overrides(root: Path) -> dict[str, str]:
    path = root / "configs" / "live_sources.yaml"
    if not path.exists():
        return {}
    data = load_yaml_file(path)
    if not isinstance(data, dict):
        return {}
    market = data.get("market", {})
    structure = data.get("market_structure", {})
    values: dict[str, Any] = {}
    if isinstance(market, dict) and isinstance(market.get("symbol_overrides"), dict):
        values.update(market["symbol_overrides"])
    if isinstance(structure, dict) and isinstance(structure.get("symbol_overrides"), dict):
        values.update(structure["symbol_overrides"])
    return {
        scalar_text(ticker).upper(): scalar_text(provider).upper()
        for ticker, provider in values.items()
        if scalar_text(ticker) and scalar_text(provider)
    }


def _fetch_latest_finra(
    tickers: list[str], *, trade_date: date | None
) -> tuple[list[dict[str, Any]], date]:
    candidates = [trade_date] if trade_date else _recent_weekdays(_today(), 8)
    failures: list[str] = []
    for candidate in candidates:
        if candidate is None:
            continue
        url = FINRA_DAILY_URL.format(date=candidate.strftime("%Y%m%d"))
        request = urllib.request.Request(url, headers={"User-Agent": "BottleneckCapital/1.0"})
        try:
            with urllib.request.urlopen(
                request, timeout=20, context=_ssl_context()
            ) as response:
                text = response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as exc:
            failures.append(f"{candidate}: {exc}")
            continue
        records = _parse_finra_file(text, tickers=tickers, source_url=url)
        if records:
            return records, candidate
        failures.append(f"{candidate}: no covered symbols")
    raise MarketStructureError(
        "FINRA daily short-volume data was unavailable for recent sessions: "
        + "; ".join(failures[:4])
    )


def _parse_finra_file(
    text: str, *, tickers: list[str], source_url: str
) -> list[dict[str, Any]]:
    covered = {ticker.upper() for ticker in tickers}
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        parts = line.strip().split("|")
        if len(parts) < 6 or parts[0] == "Date":
            continue
        raw_date, ticker, short, exempt, total, venues = parts[:6]
        ticker = ticker.upper()
        if ticker not in covered:
            continue
        short_volume = _float(short)
        short_exempt = _float(exempt)
        total_volume = _float(total)
        if total_volume <= 0:
            continue
        records.append(
            {
                "ticker": ticker,
                "trade_date": _finra_date(raw_date),
                "observed_at": _finra_date(raw_date),
                "short_volume": short_volume,
                "short_exempt_volume": short_exempt,
                "total_reported_volume": total_volume,
                "daily_short_volume_ratio_pct": short_volume / total_volume * 100.0,
                "short_exempt_ratio_pct": short_exempt / total_volume * 100.0,
                "reporting_venues": venues,
                "source_url": source_url,
                "source_quality": "official_primary",
            }
        )
    return records


def _fetch_structure_feed(url: str) -> tuple[list[dict[str, Any]], set[str] | None]:
    headers = {"User-Agent": "BottleneckCapital/1.0"}
    raw_auth = os.environ.get("BCAP_MARKET_STRUCTURE_AUTH_HEADER", "")
    if raw_auth:
        name, separator, value = raw_auth.partition(":")
        if not separator or not name.strip() or not value.strip():
            raise MarketStructureError(
                "BCAP_MARKET_STRUCTURE_AUTH_HEADER must use 'Header-Name: value'."
            )
        headers[name.strip()] = value.strip()
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20, context=_ssl_context()) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise MarketStructureError(f"Market-structure feed failed: {exc}") from exc
    return _records_from_payload(payload)


def _load_structure_input(path: Path) -> tuple[list[dict[str, Any]], set[str] | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MarketStructureError(f"Invalid market-structure input {path}: {exc}") from exc
    return _records_from_payload(payload)


def _records_from_payload(payload: Any) -> tuple[list[dict[str, Any]], set[str] | None]:
    covered: set[str] | None = None
    if isinstance(payload, dict):
        raw_covered = payload.get("covered_tickers")
        if isinstance(raw_covered, list):
            covered = {scalar_text(item).upper() for item in raw_covered if scalar_text(item)}
        records = payload.get("records") or payload.get("snapshots")
        if records is None:
            records = [
                {"ticker": ticker, **value}
                for ticker, value in payload.items()
                if isinstance(value, dict)
            ]
    else:
        records = payload
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise MarketStructureError(
            "Market-structure input must be a list or contain records/snapshots."
        )
    return records, covered


def _normalize_record(item: dict[str, Any], *, source: str) -> dict[str, Any] | None:
    ticker = scalar_text(item.get("ticker") or item.get("symbol")).upper()
    if not ticker:
        return None
    observed_at = scalar_text(
        item.get("observed_at") or item.get("trade_date") or item.get("settlement_date")
    )
    record: dict[str, Any] = {
        "ticker": ticker,
        "observed_at": observed_at or _now(),
        "ingested_at": _now(),
        "source": scalar_text(item.get("source")) or source,
        "source_url": scalar_text(item.get("source_url")),
        "source_quality": scalar_text(item.get("source_quality")) or "unverified",
    }
    for key in ("trade_date", "settlement_date", *STRUCTURE_FIELDS):
        if key in item and item[key] not in {None, ""}:
            record[key] = item[key]
    return record


def _latest_values(
    records: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, str]]:
    values: dict[str, Any] = {}
    observed: dict[str, str] = {}
    ordered = sorted(records, key=lambda item: scalar_text(item.get("observed_at")))
    for record in ordered:
        timestamp = scalar_text(record.get("observed_at"))
        for field in STRUCTURE_FIELDS:
            if field in record and record[field] not in {None, ""}:
                values[field] = record[field]
                observed[field] = timestamp
    return values, observed


def _fresh_values(
    values: dict[str, Any],
    observed: dict[str, str],
    now: datetime,
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    ages = config.get("field_max_age_days", {}) if isinstance(config, dict) else {}
    groups = {
        "daily": {
            "short_volume",
            "short_exempt_volume",
            "total_reported_volume",
            "daily_short_volume_ratio_pct",
            "short_exempt_ratio_pct",
        },
        "short_interest": {
            "reported_short_interest_shares",
            "short_interest_pct_float",
            "days_to_cover",
        },
        "borrow": {
            "borrow_fee_pct",
            "borrow_utilization_pct",
            "shares_available_to_borrow",
        },
        "options": {
            "put_call_open_interest_ratio",
            "put_call_volume_ratio",
            "implied_volatility_percentile",
            "dealer_gamma_state",
        },
        "supply": {
            "float_shares",
            "eligible_supply_shares",
            "unlock_date",
            "active_atm_or_secondary",
            "catalyst_within_days",
        },
    }
    defaults = {
        "daily": 5.0,
        "short_interest": 21.0,
        "borrow": 3.0,
        "options": 3.0,
        "supply": 120.0,
    }
    max_age_by_field: dict[str, float] = {}
    for group, fields in groups.items():
        max_age = _float(ages.get(group), defaults[group])
        for field in fields:
            max_age_by_field[field] = max_age
    fresh_values: dict[str, Any] = {}
    fresh_observed: dict[str, str] = {}
    for field, value in values.items():
        max_age = max_age_by_field.get(field, 5.0)
        timestamp = observed.get(field, "")
        if _age_days(timestamp, now) <= max_age:
            fresh_values[field] = value
            fresh_observed[field] = timestamp
    return fresh_values, fresh_observed


def _short_pressure_score(
    *,
    daily_ratio: float | None,
    exempt_ratio: float | None,
    short_interest: float | None,
    borrow_fee: float | None,
    utilization: float | None,
    volume_multiple: float | None,
    price_return: float | None,
    config: dict[str, Any],
) -> tuple[float, int]:
    thresholds = config.get("thresholds", {}) if isinstance(config, dict) else {}
    score = 0.0
    inputs = 0
    if daily_ratio is not None:
        inputs += 1
        score += _scaled(daily_ratio, _float(thresholds.get("high_short_volume_ratio_pct"), 65), 15)
    if exempt_ratio is not None:
        inputs += 1
        score += _scaled(exempt_ratio, _float(thresholds.get("high_short_exempt_ratio_pct"), 3), 12)
    if short_interest is not None:
        inputs += 1
        score += _scaled(
            short_interest,
            _float(thresholds.get("high_short_interest_pct_float"), 15),
            20,
        )
    if borrow_fee is not None:
        inputs += 1
        score += _scaled(borrow_fee, _float(thresholds.get("high_borrow_fee_pct"), 10), 15)
    if utilization is not None:
        inputs += 1
        score += _scaled(utilization, _float(thresholds.get("high_borrow_utilization_pct"), 90), 13)
    if volume_multiple is not None:
        inputs += 1
        score += _scaled(
            volume_multiple,
            _float(thresholds.get("finra_volume_surge_multiple"), 2),
            15,
        )
    if price_return is not None and price_return <= -5 and score >= 30:
        score += min(10.0, abs(price_return))
    return min(100.0, score), inputs


def _squeeze_score(
    *,
    short_interest: float | None,
    days_to_cover: float | None,
    borrow_fee: float | None,
    utilization: float | None,
    put_call_oi: float | None,
    catalyst_days: float | None,
    active_supply: bool,
    config: dict[str, Any],
) -> tuple[float, int]:
    thresholds = config.get("thresholds", {}) if isinstance(config, dict) else {}
    score = 0.0
    inputs = 0
    if short_interest is not None or days_to_cover is not None:
        inputs += 1
    if short_interest is not None:
        score += _scaled(
            short_interest,
            _float(thresholds.get("high_short_interest_pct_float"), 15),
            25,
        )
    if days_to_cover is not None:
        score += _scaled(days_to_cover, _float(thresholds.get("high_days_to_cover"), 5), 20)
    if borrow_fee is not None or utilization is not None:
        inputs += 1
    if borrow_fee is not None:
        score += _scaled(borrow_fee, _float(thresholds.get("high_borrow_fee_pct"), 10), 15)
    if utilization is not None:
        score += _scaled(utilization, _float(thresholds.get("high_borrow_utilization_pct"), 90), 15)
    if put_call_oi is not None:
        inputs += 1
        if put_call_oi <= _float(thresholds.get("call_heavy_put_call_oi_ratio"), 0.7):
            score += 10.0
    if catalyst_days is not None:
        inputs += 1
        if 0 <= catalyst_days <= 14:
            score += 15.0
    if active_supply:
        score -= 30.0
    return max(0.0, min(100.0, score)), inputs


def _classify_structure(
    *,
    fresh: bool,
    pressure: float,
    pressure_inputs: int,
    squeeze: float,
    squeeze_inputs: int,
    active_supply: bool,
    price_return: float | None,
) -> tuple[str, str, float]:
    if not fresh:
        return "STALE_STRUCTURE_DATA", "REFRESH_STRUCTURE_DATA", -2.0
    if active_supply:
        return "ACTIVE_SUPPLY_OVERHANG", "WAIT_FOR_SUPPLY_ABSORPTION", -8.0
    if squeeze >= 60 and squeeze_inputs >= 3:
        return "SQUEEZE_SETUP", "REDUCE_SIZE_FOR_SQUEEZE_VOLATILITY", -1.0
    if pressure >= 55 and pressure_inputs >= 3 and (price_return or 0.0) <= -5:
        return "FLOW_DISLOCATION_CANDIDATE", "CONFIRM_FLOW_ABSORPTION", -1.0
    if pressure >= 45 and pressure_inputs >= 2:
        return "ELEVATED_SHORT_PRESSURE", "SMALLER_TRANCHES", -3.0
    if pressure >= 25 and pressure_inputs < 3:
        return "SHORT_VOLUME_ONLY_AMBIGUOUS", "DO_NOT_INFER_SHORT_INTEREST", -1.0
    return "BALANCED", "OPEN", 0.0


def _assessment_evidence(**values: Any) -> tuple[str, ...]:
    evidence: list[str] = []
    labels = {
        "daily_ratio": "FINRA short-volume ratio",
        "exempt_ratio": "short-exempt ratio",
        "short_interest": "reported short interest / float",
        "days_to_cover": "days to cover",
        "borrow_fee": "borrow fee",
        "utilization": "borrow utilization",
        "volume_multiple": "FINRA volume / 20d median",
        "supply_overhang": "eligible supply / float",
        "price_return": "latest price move",
    }
    for key, label in labels.items():
        value = values.get(key)
        if value is not None:
            suffix = "x" if key == "volume_multiple" else "%"
            evidence.append(f"{label}: {value:.1f}{suffix}")
    if values.get("active_supply"):
        evidence.append("A dated unlock, offering, or ATM supply event is active.")
    return tuple(evidence)


def _finra_volume_multiple(records: list[dict[str, Any]]) -> float | None:
    daily = [
        (_record_date(item), _optional_float(item.get("total_reported_volume")))
        for item in records
        if _optional_float(item.get("total_reported_volume")) is not None
    ]
    daily = sorted((item for item in daily if item[0]), key=lambda item: item[0])
    if len(daily) < 4:
        return None
    latest = daily[-1][1]
    history = [value for _, value in daily[-21:-1] if value is not None and value > 0]
    if latest is None or not history:
        return None
    median = statistics.median(history)
    return latest / median if median > 0 else None


def _short_interest_pct(values: dict[str, Any]) -> float | None:
    direct = _optional_float(values.get("short_interest_pct_float"))
    if direct is not None:
        return direct
    short = _optional_float(values.get("reported_short_interest_shares"))
    float_shares = _optional_float(values.get("float_shares"))
    if short is None or float_shares is None or float_shares <= 0:
        return None
    return short / float_shares * 100.0


def _supply_overhang_pct(values: dict[str, Any]) -> float | None:
    eligible = _optional_float(values.get("eligible_supply_shares"))
    float_shares = _optional_float(values.get("float_shares"))
    if eligible is None or float_shares is None or float_shares <= 0:
        return None
    return eligible / float_shares * 100.0


def _active_supply_overhang(
    values: dict[str, Any],
    as_of: date,
    supply_overhang: float | None,
    config: dict[str, Any],
) -> bool:
    if scalar_bool(values.get("active_atm_or_secondary")):
        return True
    unlock = _date_value(scalar_text(values.get("unlock_date")))
    threshold = _float(
        (config.get("thresholds", {}) if isinstance(config, dict) else {}).get(
            "material_supply_overhang_pct_float"
        ),
        10.0,
    )
    if unlock is None or supply_overhang is None or supply_overhang < threshold:
        return False
    days = (unlock - as_of).days
    return -5 <= days <= 7


def _latest_price_return(root: Path, ticker: str) -> float | None:
    latest: dict[str, Any] | None = None
    for record in read_jsonl(root / "state" / "market_snapshots.jsonl"):
        if scalar_text(record.get("ticker")).upper() == ticker:
            latest = record
    if latest is None:
        return None
    price = _optional_float(latest.get("price"))
    previous = _optional_float(latest.get("previous_close"))
    if price is None or previous is None or previous <= 0:
        return None
    return (price / previous - 1.0) * 100.0


def _missing_assessment(ticker: str) -> MarketStructureAssessment:
    return MarketStructureAssessment(
        ticker=ticker,
        data_status="MISSING",
        observed_at="missing",
        flow_classification="DATA_INCOMPLETE",
        execution_gate="STRUCTURE_DATA_INCOMPLETE",
        score_adjustment=0.0,
        short_pressure_score=0.0,
        squeeze_potential_score=0.0,
        short_interest_pct_float=None,
        days_to_cover=None,
        daily_short_volume_ratio_pct=None,
        short_exempt_ratio_pct=None,
        finra_volume_vs_20d_median=None,
        borrow_fee_pct=None,
        borrow_utilization_pct=None,
        supply_overhang_pct_float=None,
        evidence=("No current market-structure record is available.",),
    )


def _update_ingest_status(
    root: Path,
    *,
    source: str,
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
    existing["market_structure"] = {
        "last_success_at": _now(),
        "source": source,
        "item_count": item_count,
        "expected_item_count": expected_item_count,
        "missing_tickers": missing_tickers,
        "warnings": warnings,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _recent_weekdays(start: date, count: int) -> list[date]:
    values: list[date] = []
    current = start
    while len(values) < count:
        if current.weekday() < 5:
            values.append(current)
        current -= timedelta(days=1)
    return values


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi
    except ModuleNotFoundError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def _scaled(value: float, threshold: float, maximum: float) -> float:
    if threshold <= 0:
        return 0.0
    return min(maximum, max(0.0, value / threshold * maximum))


def _record_date(record: dict[str, Any]) -> str:
    return scalar_text(record.get("trade_date") or record.get("observed_at"))[:10]


def _finra_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y%m%d").date().isoformat()
    except ValueError:
        return value


def _date_value(value: str) -> date | None:
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _age_days(value: str, now: datetime) -> float:
    if not value:
        return 999.0
    parsed_date = _date_value(value)
    if parsed_date is not None and len(value) <= 10:
        return max(0.0, float((now.date() - parsed_date).days))
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return 999.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=now.tzinfo)
    return max(0.0, (now - parsed.astimezone(now.tzinfo)).total_seconds() / 86400.0)


def _optional_float(value: Any) -> float | None:
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _float(value: Any, default: float = 0.0) -> float:
    parsed = _optional_float(value)
    return default if parsed is None else parsed


def _today() -> date:
    return datetime.now(ZoneInfo("America/Toronto")).date()


def _now() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
