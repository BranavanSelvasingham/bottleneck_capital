from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.io import load_yaml_file, read_jsonl, scalar_text
from bottleneck_capital.signal_events import active_signal_events

REGIME_EVENT_CLASSES = {"geopolitical_regime_update", "macro_regime_update"}
ADVERSE_GEOPOLITICAL_STATES = {"conflict", "escalating", "renewed_escalation"}
DEESCALATING_STATES = {"ceasefire", "deescalating", "resolved"}


@dataclass(frozen=True)
class MarketRegime:
    state: str
    confidence: float
    fresh: bool
    source_status: str
    geopolitical_status: str
    market_confirmation: str
    channel_severity: dict[str, float]
    evidence: tuple[str, ...]
    latest_context_at: str


def assess_market_regime(
    root: Path,
    *,
    as_of: datetime | None = None,
) -> MarketRegime:
    now = as_of or datetime.now(ZoneInfo("America/Toronto"))
    config = regime_config(root)
    channels: dict[str, float] = {}
    evidence: list[str] = []

    snapshots = _latest_context_snapshots(root, config)
    latest_context = max(
        (scalar_text(item.get("observed_at")) for item in snapshots.values()),
        default="",
    )
    required = {
        scalar_text(item).upper()
        for item in config.get("required_context_symbols", [])
        if scalar_text(item)
    }
    coverage = len(required & set(snapshots)) / len(required) if required else 1.0
    context_fresh = bool(latest_context) and _age_days(latest_context, now) <= _float(
        config.get("context_snapshot_max_age_days"), 4.0
    )
    _apply_market_context(snapshots, channels, evidence)
    market_confirmation = _market_confirmation(snapshots)

    geopolitical_status = "unknown"
    event_confidence = 0.0
    applied_event_count = 0
    latest_events = _latest_regime_events_by_region(root)
    for event in latest_events:
        raw = event.get("raw_event") if isinstance(event.get("raw_event"), dict) else event
        observed_at = scalar_text(raw.get("observed_at") or event.get("detected_at"))
        if _age_days(observed_at, now) > _float(
            config.get("geopolitical_event_max_age_days"), 14.0
        ):
            continue
        applied_event_count += 1
        status = scalar_text(raw.get("status") or raw.get("direction")).lower()
        severity = _bounded(raw.get("severity"), _status_severity(status))
        confidence = _bounded(raw.get("confidence"), 70.0)
        event_confidence = max(event_confidence, confidence)
        if scalar_text(event.get("event_class")) == "geopolitical_regime_update":
            geopolitical_status = status or "elevated"
        event_channels = raw.get("channels")
        if not isinstance(event_channels, dict):
            event_channels = {"global_risk": severity, "energy": severity * 0.8}
        confirmation_multiplier = (
            _confirmation_multiplier(market_confirmation)
            if status in ADVERSE_GEOPOLITICAL_STATES
            else 1.0
        )
        for channel, value in event_channels.items():
            _raise_channel(
                channels,
                scalar_text(channel),
                _bounded(value, severity) * confirmation_multiplier,
            )
        evidence.append(
            scalar_text(event.get("summary"))
            or f"{scalar_text(event.get('event_class'))}: {status or 'elevated'}"
        )
        if status in ADVERSE_GEOPOLITICAL_STATES:
            evidence.append(
                f"Cross-asset confirmation of escalation: {market_confirmation}."
            )

    has_event = applied_event_count > 0
    fresh = context_fresh and coverage >= 0.75
    if snapshots and has_event:
        source_status = "CROSS_ASSET_AND_EVENT"
    elif snapshots:
        source_status = "CROSS_ASSET_ONLY"
    elif has_event:
        source_status = "EVENT_ONLY"
    else:
        source_status = "MISSING"

    peak = max(channels.values(), default=0.0)
    if geopolitical_status in ADVERSE_GEOPOLITICAL_STATES:
        state = "CONFLICT_ESCALATION" if peak >= 60 else "ELEVATED"
    elif peak >= 70:
        state = "MARKET_STRESS"
    elif peak >= 35:
        state = "ELEVATED"
    elif geopolitical_status in DEESCALATING_STATES:
        state = "DE_ESCALATING"
    elif snapshots or has_event:
        state = "NORMAL"
    else:
        state = "UNKNOWN"

    market_confidence = 100.0 * coverage if snapshots else 0.0
    if has_event and snapshots:
        confidence = 0.6 * event_confidence + 0.4 * market_confidence
    elif has_event:
        confidence = event_confidence
    else:
        confidence = market_confidence
    if not fresh:
        confidence = min(confidence, 75.0)
    return MarketRegime(
        state=state,
        confidence=confidence,
        fresh=fresh,
        source_status=source_status,
        geopolitical_status=geopolitical_status,
        market_confirmation=market_confirmation,
        channel_severity=dict(sorted(channels.items())),
        evidence=tuple(dict.fromkeys(item for item in evidence if item)),
        latest_context_at=latest_context or "missing",
    )


def regime_adjustment(
    root: Path,
    *,
    ticker: str,
    sleeve: str,
    regime: MarketRegime,
) -> float:
    config = regime_config(root)
    sleeve_map = config.get("sleeve_channel_exposures", {})
    ticker_map = config.get("ticker_channel_exposures", {})
    exposures = dict(sleeve_map.get(sleeve, {})) if isinstance(sleeve_map, dict) else {}
    if isinstance(ticker_map, dict) and isinstance(ticker_map.get(ticker), dict):
        exposures.update(ticker_map[ticker])
    adjustment = sum(
        severity / 100.0 * _float(exposures.get(channel), 0.0) * 100.0
        for channel, severity in regime.channel_severity.items()
    )
    return max(-30.0, min(12.0, adjustment))


def regime_entry_gate(
    root: Path,
    *,
    decision: str,
    adjustment: float,
    regime: MarketRegime,
) -> str:
    if decision not in {"BUY_NOW", "ADD_ON_DIP"}:
        return "NOT_ARMED"
    if not regime.fresh:
        return "CONTEXT_INCOMPLETE"
    gates = regime_config(root).get("entry_gates", {})
    pause = _float(gates.get("pause_new_buy_adjustment"), -8.0)
    reduce = _float(gates.get("reduce_tranche_adjustment"), -4.0)
    if adjustment <= pause:
        return "WAIT_FOR_STABILIZATION"
    if adjustment <= reduce:
        return "HALF_TRANCHE_ONLY"
    return "OPEN"


def regime_config(root: Path) -> dict[str, Any]:
    path = root / "configs" / "regime.yaml"
    if not path.exists():
        return {}
    data = load_yaml_file(path)
    regime = data.get("regime", {}) if isinstance(data, dict) else {}
    return regime if isinstance(regime, dict) else {}


def context_symbols(root: Path) -> dict[str, str]:
    configured = regime_config(root).get("context_symbols", {})
    if not isinstance(configured, dict):
        return {}
    return {
        scalar_text(ticker).upper(): scalar_text(provider)
        for ticker, provider in configured.items()
        if scalar_text(ticker) and scalar_text(provider)
    }


def _latest_context_snapshots(
    root: Path,
    config: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    symbols = {
        scalar_text(item).upper()
        for item in config.get("context_symbols", {})
        if scalar_text(item)
    }
    symbols.add("SMH")
    latest: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(root / "state" / "market_snapshots.jsonl"):
        ticker = scalar_text(record.get("ticker")).upper()
        if ticker in symbols:
            latest[ticker] = record
    return latest


def _latest_regime_events_by_region(root: Path) -> list[dict[str, Any]]:
    records = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        event_class = scalar_text(record.get("event_class"))
        if event_class not in REGIME_EVENT_CLASSES:
            continue
        raw = record.get("raw_event") if isinstance(record.get("raw_event"), dict) else record
        region = scalar_text(raw.get("region") or "global").lower()
        key = (event_class, region)
        observed = scalar_text(raw.get("observed_at") or record.get("detected_at"))
        current = latest.get(key)
        current_raw = (
            current.get("raw_event")
            if current and isinstance(current.get("raw_event"), dict)
            else current or {}
        )
        current_observed = scalar_text(
            current_raw.get("observed_at") or (current or {}).get("detected_at")
        )
        if not current or observed >= current_observed:
            latest[key] = record
    return list(latest.values())


def _apply_market_context(
    snapshots: dict[str, dict[str, Any]],
    channels: dict[str, float],
    evidence: list[str],
) -> None:
    moves = {ticker: _snapshot_move(record) for ticker, record in snapshots.items()}
    risk_moves = [moves.get("SPY"), moves.get("QQQ"), moves.get("SMH")]
    downside = min((move for move in risk_moves if move is not None), default=0.0)
    if downside <= -1.0:
        _raise_channel(channels, "global_risk", min(100.0, abs(downside) * 18.0))
        evidence.append(f"Cross-asset risk proxy downside reached {downside:.1f}%.")
    volatility = moves.get("VIXY")
    if volatility is not None and volatility >= 2.0:
        _raise_channel(channels, "global_risk", min(100.0, volatility * 10.0))
        evidence.append(f"VIXY volatility proxy rose {volatility:.1f}%.")
    oil = moves.get("USO")
    if oil is not None and abs(oil) >= 1.5:
        _raise_channel(channels, "energy", min(100.0, abs(oil) * 12.0))
        evidence.append(f"USO oil proxy moved {oil:+.1f}%.")
    dollar = moves.get("UUP")
    if dollar is not None and dollar >= 0.7:
        _raise_channel(channels, "global_risk", min(70.0, dollar * 25.0))
        evidence.append(f"UUP dollar proxy rose {dollar:.1f}%.")
    bonds = moves.get("TLT")
    if bonds is not None and bonds <= -1.0:
        _raise_channel(channels, "rates", min(100.0, abs(bonds) * 20.0))
        evidence.append(f"TLT rate proxy fell {bonds:.1f}%.")


def _market_confirmation(snapshots: dict[str, dict[str, Any]]) -> str:
    moves = {ticker: _snapshot_move(record) for ticker, record in snapshots.items()}
    confirmations = sum(
        condition
        for condition in (
            (moves.get("SPY") or 0.0) <= -1.0,
            (moves.get("QQQ") or 0.0) <= -1.0,
            (moves.get("VIXY") or 0.0) >= 2.0,
            (moves.get("USO") or 0.0) >= 1.5,
            (moves.get("UUP") or 0.0) >= 0.7,
        )
    )
    contradictions = sum(
        condition
        for condition in (
            (moves.get("SPY") or 0.0) >= 0.2,
            (moves.get("QQQ") or 0.0) >= 0.2,
            (moves.get("VIXY") or 0.0) <= -1.0,
            (moves.get("USO") or 0.0) <= 0.0,
        )
    )
    if confirmations >= 2:
        return "CONFIRMED"
    if confirmations == 0 and contradictions >= 2:
        return "CONTRADICTED"
    if snapshots:
        return "MIXED"
    return "UNKNOWN"


def _confirmation_multiplier(confirmation: str) -> float:
    return {
        "CONFIRMED": 1.0,
        "MIXED": 0.8,
        "CONTRADICTED": 0.6,
        "UNKNOWN": 0.85,
    }.get(confirmation, 0.85)


def _snapshot_move(record: dict[str, Any]) -> float | None:
    price = _float(record.get("price"), 0.0)
    previous = _float(record.get("previous_close"), 0.0)
    if price <= 0 or previous <= 0:
        return None
    return (price / previous - 1.0) * 100.0


def _raise_channel(channels: dict[str, float], channel: str, severity: float) -> None:
    if channel:
        channels[channel] = max(channels.get(channel, 0.0), severity)


def _status_severity(status: str) -> float:
    return {
        "conflict": 90.0,
        "renewed_escalation": 80.0,
        "escalating": 70.0,
        "elevated": 50.0,
        "ceasefire": 25.0,
        "deescalating": 20.0,
        "resolved": 5.0,
    }.get(status, 45.0)


def _age_days(value: str, now: datetime) -> float:
    if not value:
        return 999.0
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return 999.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=now.tzinfo)
    return max(0.0, (now - parsed.astimezone(now.tzinfo)).total_seconds() / 86400.0)


def _bounded(value: Any, default: float) -> float:
    return max(0.0, min(100.0, _float(value, default)))


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
