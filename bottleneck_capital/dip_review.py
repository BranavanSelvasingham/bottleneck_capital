from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import load_watchlist
from bottleneck_capital.io import read_jsonl, scalar_text
from bottleneck_capital.signal_events import active_signal_events, event_id_for_record

_FINANCING_WORDS = {
    "convertible",
    "debt",
    "dilution",
    "financing",
    "notes",
    "offering",
    "senior unsecured",
}

_THESIS_DAMAGE_WORDS = {
    "covenant",
    "customer loss",
    "default",
    "fraud",
    "guidance cut",
    "impairment",
    "liquidity",
    "solvency",
    "withdrawn guidance",
}

_MARKET_WORDS = {
    "ai hardware",
    "ai momentum",
    "broad market",
    "crowded",
    "crowding",
    "de-risking",
    "market selloff",
    "rotation",
    "sector selloff",
    "unwind",
}


@dataclass(frozen=True)
class DipCauseReview:
    ticker: str
    event_count: int
    latest_event_id: str
    latest_summary: str
    severity_pct: float
    cause_status: str
    cause_class: str
    bounded: bool
    evidence: str
    thesis_damage_risk: str
    action_bias: str


def review_active_dips(root: Path) -> list[DipCauseReview]:
    events = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    watchlist = {item["ticker"]: item for item in load_watchlist(root)}
    dip_events = [
        event
        for event in events
        if scalar_text(event.get("event_class")) == "dip_trigger"
        and scalar_text(event.get("ticker")).upper()
    ]
    by_ticker: dict[str, list[dict[str, Any]]] = {}
    for event in dip_events:
        by_ticker.setdefault(scalar_text(event.get("ticker")).upper(), []).append(event)

    dip_dates = [_event_date(event) for event in dip_events if _event_date(event)]
    same_day_counts = {date: dip_dates.count(date) for date in set(dip_dates)}

    reviews = [
        _review_ticker(ticker, ticker_events, events, watchlist, same_day_counts)
        for ticker, ticker_events in sorted(by_ticker.items())
    ]
    return sorted(reviews, key=lambda item: (-item.severity_pct, item.ticker))


def write_dip_review(root: Path) -> Path:
    reviews = review_active_dips(root)
    now = _now()
    path = root / "reports" / "dip_reviews" / f"{now[:10]}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_dip_review(reviews, now), encoding="utf-8")
    return path


def render_dip_review(reviews: list[DipCauseReview], now: str) -> str:
    lines = [
        "# Bottleneck Capital Dip Cause Review",
        "",
        f"Date: {now}",
        "",
        "This report answers whether active dip triggers have a bounded cause. "
        "Bounded cause is not buy approval; it is a prerequisite for ADD_ON_DIP work.",
        "",
        "| Ticker | Bounded? | Cause | Severity | Evidence | Action Bias |",
        "|---|---|---|---:|---|---|",
    ]
    if not reviews:
        lines.append("| - | - | - | - | - | - |")
    for review in reviews:
        lines.append(
            f"| {review.ticker} | {'YES' if review.bounded else 'NO'} | "
            f"{_table(review.cause_class)} | {review.severity_pct:.1f}% | "
            f"{_table(review.evidence)} | {_table(review.action_bias)} |"
        )
    return "\n".join(lines) + "\n"


def render_action_board_dip_reviews(reviews: list[DipCauseReview]) -> list[str]:
    lines = [
        "## Dip Cause Reviews",
        "",
        "| Ticker | Bounded? | Cause | Thesis Damage Risk | Action Bias |",
        "|---|---|---|---|---|",
    ]
    if not reviews:
        lines.append("| - | - | - | - | - |")
        return lines
    for review in reviews[:15]:
        lines.append(
            f"| {review.ticker} | {'YES' if review.bounded else 'NO'} | "
            f"{_table(review.cause_class)} | {_table(review.thesis_damage_risk)} | "
            f"{_table(review.action_bias)} |"
        )
    return lines


def _review_ticker(
    ticker: str,
    ticker_events: list[dict[str, Any]],
    all_events: list[dict[str, Any]],
    watchlist: dict[str, dict[str, Any]],
    same_day_counts: dict[str, int],
) -> DipCauseReview:
    latest = sorted(ticker_events, key=lambda event: scalar_text(event.get("detected_at")))[-1]
    raw = latest.get("raw_event") if isinstance(latest.get("raw_event"), dict) else latest
    summary = scalar_text(latest.get("summary") or raw.get("summary"))
    text = " ".join(
        scalar_text(value).lower()
        for value in (
            latest.get("summary"),
            latest.get("source"),
            raw.get("summary"),
            raw.get("known_cause"),
            raw.get("headline"),
            raw.get("event_type"),
        )
    )
    severity = max((_drop_severity(event) for event in ticker_events), default=0.0)
    same_day_count = max((same_day_counts.get(_event_date(event), 0) for event in ticker_events), default=0)
    same_sleeve_count = _same_sleeve_dips(ticker, ticker_events, all_events, watchlist)
    has_non_dip_event = any(
        scalar_text(event.get("ticker")).upper() == ticker
        and scalar_text(event.get("event_class")) != "dip_trigger"
        for event in all_events
    )

    if _contains_any(text, _THESIS_DAMAGE_WORDS):
        return _review(
            ticker,
            ticker_events,
            latest,
            summary,
            severity,
            "UNBOUNDED",
            "possible_thesis_damage",
            False,
            "Event language contains thesis-damage terms; primary-source review required.",
            "HIGH",
            "DO_NOT_BUY_UNTIL_DAMAGE_CLEARED",
        )
    if _contains_any(text, _FINANCING_WORDS):
        return _review(
            ticker,
            ticker_events,
            latest,
            summary,
            severity,
            "BOUNDED",
            "company_financing_or_dilution",
            True,
            "Explicit financing/debt/offering language bounds the cause, but valuation and dilution must be underwritten.",
            "MEDIUM_HIGH",
            "DILUTION_REVIEW_BEFORE_ANY_ADD",
        )
    if has_non_dip_event:
        return _review(
            ticker,
            ticker_events,
            latest,
            summary,
            severity,
            "PARTIALLY_BOUNDED",
            "company_specific_event",
            True,
            "Ticker has active non-price event(s); cause is company-specific but not yet cleared.",
            "MEDIUM",
            "PRIMARY_EVENT_REVIEW",
        )
    if _contains_any(text, _MARKET_WORDS):
        return _review(
            ticker,
            ticker_events,
            latest,
            summary,
            severity,
            "BOUNDED",
            "market_or_crowded_ai_unwind",
            True,
            "Event text explicitly references market, sector, rotation, or crowding.",
            "LOW",
            "ADD_ON_DIP_CANDIDATE_IF_VALUATION_CLEARS",
        )
    if same_day_count >= 8:
        return _review(
            ticker,
            ticker_events,
            latest,
            summary,
            severity,
            "BOUNDED",
            "broad_cross_book_de_risking",
            True,
            f"{same_day_count} active dip triggers share the same observed/detected date.",
            "LOW",
            "ADD_ON_DIP_CANDIDATE_IF_VALUATION_CLEARS",
        )
    if same_sleeve_count >= 3:
        return _review(
            ticker,
            ticker_events,
            latest,
            summary,
            severity,
            "BOUNDED",
            "same_sleeve_de_risking",
            True,
            f"{same_sleeve_count} active dip triggers in the same sleeve.",
            "LOW_MEDIUM",
            "SLEEVE_RELATIVE_VALUE_REVIEW",
        )
    return _review(
        ticker,
        ticker_events,
        latest,
        summary,
        severity,
        "UNBOUNDED",
        "unknown_single_name_or_sparse_move",
        False,
        "No explicit cause, company event, broad same-day cluster, or same-sleeve cluster found.",
        "UNKNOWN",
        "WAIT_FOR_CAUSE",
    )


def _review(
    ticker: str,
    ticker_events: list[dict[str, Any]],
    latest: dict[str, Any],
    summary: str,
    severity: float,
    cause_status: str,
    cause_class: str,
    bounded: bool,
    evidence: str,
    thesis_damage_risk: str,
    action_bias: str,
) -> DipCauseReview:
    return DipCauseReview(
        ticker=ticker,
        event_count=len(ticker_events),
        latest_event_id=event_id_for_record(latest),
        latest_summary=summary,
        severity_pct=severity,
        cause_status=cause_status,
        cause_class=cause_class,
        bounded=bounded,
        evidence=evidence,
        thesis_damage_risk=thesis_damage_risk,
        action_bias=action_bias,
    )


def _same_sleeve_dips(
    ticker: str,
    ticker_events: list[dict[str, Any]],
    all_events: list[dict[str, Any]],
    watchlist: dict[str, dict[str, Any]],
) -> int:
    sleeve = scalar_text(watchlist.get(ticker, {}).get("sleeve"))
    if not sleeve:
        return 0
    event_dates = {_event_date(event) for event in ticker_events if _event_date(event)}
    tickers: set[str] = set()
    for event in all_events:
        other = scalar_text(event.get("ticker")).upper()
        if not other or scalar_text(event.get("event_class")) != "dip_trigger":
            continue
        if scalar_text(watchlist.get(other, {}).get("sleeve")) != sleeve:
            continue
        if _event_date(event) in event_dates:
            tickers.add(other)
    return len(tickers)


def _event_date(event: dict[str, Any]) -> str:
    raw = event.get("raw_event") if isinstance(event.get("raw_event"), dict) else {}
    dedupe_parts = scalar_text(raw.get("dedupe_key")).split(":")
    dedupe_date = dedupe_parts[2] if len(dedupe_parts) > 2 else ""
    return (
        scalar_text(raw.get("observed_at"))[:10]
        or scalar_text(event.get("detected_at"))[:10]
        or dedupe_date
    )


def _drop_severity(event: dict[str, Any]) -> float:
    raw = event.get("raw_event") if isinstance(event.get("raw_event"), dict) else event
    values = [
        raw.get("intraday_drop_pct"),
        raw.get("one_day_drop_pct"),
        raw.get("five_day_drop_pct"),
        raw.get("twenty_day_drop_pct"),
        raw.get("gap_down_pct"),
        raw.get("post_earnings_move_pct"),
    ]
    return max((abs(value) for value in (_float(value) for value in values) if value < 0), default=0.0)


def _float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(str(value).strip().replace("%", ""))
    except ValueError:
        return 0.0


def _contains_any(text: str, words: set[str]) -> bool:
    return any(word in text for word in words)


def _table(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def _now() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="minutes")
