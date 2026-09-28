from __future__ import annotations

import math
import re
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from bottleneck_capital.io import append_jsonl, read_jsonl
from bottleneck_capital.lessons import application_snapshots, render_lessons
from bottleneck_capital.runtime import run_lock

LEDGER = Path("state/local_recommendations.jsonl")
ACTIONS = {"BUY_NOW", "ADD_ON_DIP", "HOLD", "TRIM", "SELL", "RESEARCH_REQUIRED"}
REASONS = {"THESIS", "VALUATION", "CAPACITY", "EVENT", "RISK", "OPPORTUNITY_COST"}
CHANGE_KINDS = {
    "NEW_EVIDENCE",
    "VALUATION_CHANGE",
    "CONSTRAINT_CHANGE",
    "ERROR_CORRECTION",
    "REAFFIRMATION",
}
CALL_FIELDS = {
    "ticker",
    "action",
    "reason",
    "rationale",
    "benchmark",
    "horizon_months",
    "review_by",
    "reference_start_at",
    "confidence",
    "evidence",
    "alternatives",
    "invalidation",
    "starter_case",
    "wait_case",
    "missed_entry_response",
    "entry",
    "lesson_applications",
    "lesson_test",
    "rotation_ticker",
    "rotation_case",
    "supersedes",
    "change_kind",
    "change_reason",
}
OUTCOME_FIELDS = {
    "recommendation_id",
    "window",
    "start_at",
    "end_at",
    "session_dates",
    "currency",
    "price_basis",
    "prices",
    "entry_observation",
    "entry_evidence",
    "notes",
    "supersedes",
    "correction_reason",
    "lesson_assessment",
}
WINDOWS = {"5_sessions": 5, "21_sessions": 21, "63_sessions": 63, "252_sessions": 252}


class RecommendationError(ValueError):
    """A recommendation or outcome cannot be audited as supplied."""


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecommendationError(f"{label} must be nonempty text")
    return value.strip()


def _fields(value: Any, allowed: set[str], required: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) - allowed or required - set(value):
        raise RecommendationError(f"{label} has missing or unsupported fields; use the template")


def _choice(value: Any, allowed: set[str], label: str) -> None:
    if _text(value, label) != value or value not in allowed:
        raise RecommendationError(f"Unsupported {label}")


def _symbol(value: Any) -> str:
    symbol = _text(value, "ticker")
    if symbol != value or not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,14}", symbol):
        raise RecommendationError("Use an uppercase ticker, not account or position data")
    return symbol


def _time(value: Any) -> datetime:
    try:
        parsed = datetime.fromisoformat(_text(value, "timestamp"))
    except ValueError as exc:
        raise RecommendationError("Use an ISO timestamp with timezone") from exc
    if parsed.tzinfo is None:
        raise RecommendationError("Timestamp requires a timezone")
    return parsed.astimezone(UTC)


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise RecommendationError("Prices must be finite positive numbers")
    if not math.isfinite(value) or value <= 0:
        raise RecommendationError("Prices must be finite positive numbers")
    return float(value)


def latest_recommendations(root: Path) -> list[dict[str, Any]]:
    latest = {}
    for record in read_jsonl(root / LEDGER):
        if record.get("kind") == "recommendation":
            latest[record["ticker"]] = record
    return list(latest.values())


def record_recommendation(
    root: Path,
    payload: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(UTC)
    required = CALL_FIELDS - {
        "rotation_ticker",
        "rotation_case",
        "supersedes",
        "change_kind",
        "change_reason",
        "lesson_test",
    }
    _fields(payload, CALL_FIELDS, required, "Recommendation")
    snapshots = application_snapshots(root, payload["lesson_applications"])
    if "lesson_test" in payload:
        test = payload["lesson_test"]
        fields = {
            "id",
            "version",
            "old_approach",
            "new_approach",
            "window",
            "success_criterion",
            "failure_criterion",
            "cohort_key",
        }
        _fields(test, fields | {"event_deadline"}, fields, "Lesson test")
        if (
            not any(
                test["id"] == item["id"] and test["version"] == item["version"]
                for item in snapshots
            )
            or type(test["version"]) is not int
        ):
            raise RecommendationError("Lesson test must reference an application in this call")
        _choice(test["window"], {*WINDOWS, "EVENT"}, "lesson test window")
        for field in (
            "old_approach",
            "new_approach",
            "success_criterion",
            "failure_criterion",
            "cohort_key",
        ):
            _text(test[field], field)
        if test["window"] == "EVENT":
            if _time(test.get("event_deadline")) <= now:
                raise RecommendationError("Freeze a future lesson event deadline")
        elif "event_deadline" in test:
            raise RecommendationError("Only EVENT tests specify an event_deadline")
    ticker = _symbol(payload["ticker"])
    _symbol(payload["benchmark"])
    if ticker == payload["benchmark"]:
        raise RecommendationError("Benchmark must differ from the recommendation ticker")
    _choice(payload["action"], ACTIONS, "action")
    _choice(payload["reason"], REASONS, "reason")
    months = payload["horizon_months"]
    if type(months) is not int or not 1 <= months <= 120:
        raise RecommendationError("horizon_months must be an integer from 1 to 120")
    if _time(payload["review_by"]) <= now:
        raise RecommendationError("review_by must be in the future")
    reference_start = _time(payload["reference_start_at"])
    if not now <= reference_start <= now + timedelta(days=7):
        raise RecommendationError("Freeze a reference start within the next seven days")
    if payload.get("lesson_test", {}).get("window") == "EVENT" and (
        _time(payload["lesson_test"]["event_deadline"]) <= reference_start
    ):
        raise RecommendationError("Lesson event must end after the frozen reference start")
    for key in ("rationale", "invalidation", "starter_case", "wait_case", "missed_entry_response"):
        _text(payload[key], key)
    confidence = payload["confidence"]
    keys = {"thesis", "valuation", "timing"}
    _fields(confidence, keys, keys, "Confidence")
    for value in confidence.values():
        _choice(value, {"LOW", "MODERATE", "HIGH"}, "qualitative confidence")
    evidence = payload["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise RecommendationError("At least one dated evidence reference is required")
    for reference in evidence:
        _text(reference, "evidence")
    alternatives = payload["alternatives"]
    if not isinstance(alternatives, list) or len(alternatives) < 2:
        raise RecommendationError(
            "Compare at least two alternatives, including cash if appropriate"
        )
    symbols = set()
    for alternative in alternatives:
        _fields(alternative, {"ticker", "case"}, {"ticker", "case"}, "Alternative")
        symbols.add(_symbol(alternative["ticker"]))
        _text(alternative["case"], "alternative case")
    if len(symbols) != len(alternatives) or ticker in symbols:
        raise RecommendationError("Alternatives must be distinct and exclude the subject ticker")
    entry = payload["entry"]
    _fields(entry, {"mode", "limit_price"}, {"mode"}, "Entry")
    _choice(entry["mode"], {"NO_ORDER", "NEXT_OPEN", "LIMIT"}, "entry mode")
    if entry["mode"] == "LIMIT":
        _number(entry.get("limit_price"))
    elif "limit_price" in entry:
        raise RecommendationError("Only a LIMIT can include limit_price")
    if payload["action"] in {"HOLD", "RESEARCH_REQUIRED"} and entry["mode"] != "NO_ORDER":
        raise RecommendationError("HOLD/research cannot silently authorize an order")
    if payload["action"] in {"BUY_NOW", "ADD_ON_DIP"} and entry["mode"] == "NO_ORDER":
        raise RecommendationError("A buy recommendation requires an explicit entry rule")
    if payload["action"] == "ADD_ON_DIP" and entry["mode"] != "LIMIT":
        raise RecommendationError("ADD_ON_DIP requires a priced limit, not an assumed future dip")
    rotation = payload.get("rotation_ticker")
    if "rotation_ticker" in payload:
        if _symbol(rotation) not in symbols:
            raise RecommendationError("Rotation counterparty must be an explicit alternative")
        _text(payload.get("rotation_case"), "rotation_case")
    elif "rotation_case" in payload:
        raise RecommendationError("rotation_case requires a counterparty ticker")
    if payload["reason"] == "OPPORTUNITY_COST" and not rotation:
        raise RecommendationError("Opportunity-cost rotation requires a named counterparty")

    # Freeze the original call. Revisions append a linked record, never overwrite it.
    with run_lock(root, "recommendations"):
        for old in read_jsonl(root / LEDGER):
            for snapshot in old.get("lesson_snapshots", []):
                for current in snapshots:
                    if (
                        snapshot["id"] == current["id"]
                        and snapshot["version"] == current["version"]
                        and snapshot != current
                    ):
                        raise RecommendationError(
                            "Increment the lesson version after a rule change"
                        )
        previous = next((r for r in latest_recommendations(root) if r["ticker"] == ticker), None)
        if previous:
            if payload.get("supersedes") != previous["id"]:
                raise RecommendationError(
                    "Link supersedes to the latest recommendation for this ticker"
                )
            _choice(payload.get("change_kind"), CHANGE_KINDS, "change_kind")
            _text(payload.get("change_reason"), "change_reason")
            if payload["change_kind"] == "NEW_EVIDENCE" and not set(evidence) - set(
                previous["evidence"]
            ):
                raise RecommendationError("NEW_EVIDENCE requires a new dated evidence reference")
            if payload["change_kind"] == "REAFFIRMATION":
                for field in (
                    "action",
                    "reason",
                    "entry",
                    "rotation_ticker",
                    "benchmark",
                    "horizon_months",
                    "confidence",
                    "invalidation",
                ):
                    if payload.get(field) != previous.get(field):
                        raise RecommendationError(
                            "Changed action/entry/funding is not a reaffirmation"
                        )
        elif any(key in payload for key in ("supersedes", "change_kind", "change_reason")):
            raise RecommendationError("An initial recommendation cannot supersede an unknown call")
        record = {
            **payload,
            "id": str(uuid4()),
            "kind": "recommendation",
            "recorded_at": now.isoformat(),
            "schema_version": 3,
            "lesson_snapshots": snapshots,
        }
        append_jsonl(root / LEDGER, record)
    return record


def record_outcome(
    root: Path,
    payload: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(UTC)
    _fields(
        payload,
        OUTCOME_FIELDS,
        OUTCOME_FIELDS - {"supersedes", "correction_reason", "entry_evidence", "lesson_assessment"},
        "Outcome",
    )
    start, end = _time(payload["start_at"]), _time(payload["end_at"])
    if not start < end <= now:
        raise RecommendationError("Outcome requires ordered, completed timestamps")
    _choice(payload["price_basis"], {"UNADJUSTED_PRICE", "TOTAL_RETURN_INDEX"}, "price_basis")
    _choice(payload["currency"], {"USD", "CAD"}, "currency")
    _choice(payload["window"], {*WINDOWS, "EVENT", "INTERIM"}, "window")
    dates = payload["session_dates"]
    if not isinstance(dates, list) or not dates:
        raise RecommendationError("Provide the actual provider trading-session dates")
    try:
        sessions = [date.fromisoformat(d) for d in dates]
    except (ValueError, TypeError) as exc:
        raise RecommendationError("Invalid trading-session date") from exc
    if sessions != sorted(set(sessions)):
        raise RecommendationError("Session dates must be unique and ordered")
    if any(session.weekday() > 4 for session in sessions):
        raise RecommendationError("US/Canadian equity sessions cannot fall on a weekend")
    if sessions[0] != start.date() or sessions[-1] != end.date():
        raise RecommendationError("Session dates must match the common start/end interval in UTC")
    if payload["window"] in WINDOWS and len(sessions) != WINDOWS[payload["window"]]:
        raise RecommendationError("Outcome window does not match the number of trading sessions")
    _choice(
        payload["entry_observation"],
        {"UNVERIFIED", "PRICE_TOUCHED", "NOT_TOUCHED", "NO_ORDER"},
        "entry_observation",
    )
    _text(payload["notes"], "notes")
    prices = payload["prices"]
    if not isinstance(prices, list):
        raise RecommendationError("prices must contain matching-date observations")
    returns = {}
    for item in prices:
        fields = {"ticker", "start", "end", "source"}
        _fields(item, fields, fields, "Price observation")
        symbol = _symbol(item["ticker"])
        if symbol in returns:
            raise RecommendationError("Duplicate price observation")
        _text(item["source"], "price source")
        returns[symbol] = 100 * (_number(item["end"]) / _number(item["start"]) - 1)
        if not math.isfinite(returns[symbol]):
            raise RecommendationError("Return calculation overflowed")

    with run_lock(root, "recommendations"):
        records = read_jsonl(root / LEDGER)
        call = next(
            (
                r
                for r in records
                if r.get("kind") == "recommendation" and r["id"] == payload["recommendation_id"]
            ),
            None,
        )
        if not call:
            raise RecommendationError("Unknown recommendation")
        if "lesson_assessment" in payload:
            test = call.get("lesson_test")
            if not test:
                raise RecommendationError("Cannot assess a lesson without a prospective test")
            assessment = payload["lesson_assessment"]
            fields = {"conclusion", "old_result", "new_result", "evidence", "reason"}
            _fields(assessment, fields, fields, "Lesson assessment")
            _choice(
                assessment["conclusion"],
                {"SUPPORTS", "CONTRADICTS", "INCONCLUSIVE"},
                "lesson assessment",
            )
            for field in ("old_result", "new_result", "reason"):
                _text(assessment[field], field)
            if not isinstance(assessment["evidence"], list) or not assessment["evidence"]:
                raise RecommendationError("Lesson assessment requires comparison evidence")
            for source in assessment["evidence"]:
                _text(source, "comparison evidence")
            if assessment["conclusion"] != "INCONCLUSIVE" and (
                payload["window"] != test["window"]
                or (test["window"] == "EVENT" and end != _time(test["event_deadline"]))
            ):
                raise RecommendationError("Score the frozen lesson window; otherwise INCONCLUSIVE")
        if start < _time(call["recorded_at"]):
            raise RecommendationError("Cannot credit prices before the recommendation was recorded")
        if not call.get("reference_start_at"):
            raise RecommendationError(
                "Recommendation lacks a frozen reference start; keep it unscored"
            )
        if start != _time(call["reference_start_at"]):
            raise RecommendationError(
                "Outcome must use the recommendation's frozen reference start"
            )
        required = {call["ticker"], call["benchmark"]}
        if call.get("rotation_ticker"):
            required.add(call["rotation_ticker"])
        if not required <= returns.keys():
            raise RecommendationError(
                "Missing same-date ticker, benchmark, or rotation-counterparty prices"
            )
        if call["entry"]["mode"] == "NO_ORDER" and payload["entry_observation"] != "NO_ORDER":
            raise RecommendationError("A no-order call cannot be credited with an entry")
        if payload["entry_observation"] == "PRICE_TOUCHED":
            proof = payload.get("entry_evidence")
            _fields(
                proof,
                {"observed_at", "price", "source"},
                {"observed_at", "price", "source"},
                "Entry evidence",
            )
            observed, price = _time(proof["observed_at"]), _number(proof["price"])
            _text(proof["source"], "entry evidence source")
            if call["entry"]["mode"] != "LIMIT":
                raise RecommendationError("PRICE_TOUCHED applies only to a specified limit")
            if not _time(call["recorded_at"]) <= observed <= min(end, _time(call["review_by"])):
                raise RecommendationError("Price touch must occur after the call and before expiry")
            limit = call["entry"]["limit_price"]
            if (call["action"] in {"BUY_NOW", "ADD_ON_DIP"} and price > limit) or (
                call["action"] in {"SELL", "TRIM"} and price < limit
            ):
                raise RecommendationError("Observed price did not reach the specified limit")
        elif "entry_evidence" in payload:
            raise RecommendationError("Entry evidence requires a PRICE_TOUCHED observation")
        prior = [
            r
            for r in records
            if r.get("kind") == "outcome"
            and r["recommendation_id"] == call["id"]
            and r["window"] == payload["window"]
        ]
        if prior:
            if payload.get("supersedes") != prior[-1]["id"]:
                raise RecommendationError("An outcome revision must link the previous outcome")
            _text(payload.get("correction_reason"), "correction_reason")
        elif "supersedes" in payload or "correction_reason" in payload:
            raise RecommendationError("Cannot supersede an unknown outcome")
        asset_return = returns[call["ticker"]]
        rotation_advantage = None
        if call.get("rotation_ticker"):
            rotation_advantage = asset_return - returns[call["rotation_ticker"]]
            if call["action"] in {"SELL", "TRIM"}:
                rotation_advantage *= -1
        record = {
            **payload,
            "id": str(uuid4()),
            "kind": "outcome",
            "schema_version": 2,
            "recorded_at": now.isoformat(),
            "returns_pct": returns,
            "excess_return_pp": asset_return - returns[call["benchmark"]],
            "rotation_advantage_pp": rotation_advantage,
            "measurement": "REFERENCE_PRICE_NOT_EXECUTION",
        }
        append_jsonl(root / LEDGER, record)
    return record


def render_recommendations(root: Path, *, now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    rows = ["# Local Recommendation Review", "", "Reference outcomes are not portfolio P&L.", ""]
    rows.extend(render_lessons(root))
    calls = latest_recommendations(root)
    if not calls:
        return "\n".join([*rows, "No recommendations recorded yet.\n"])
    for call in calls:
        status = "REVIEW_DUE" if _time(call["review_by"]) <= now else "CURRENT"
        rows.append(
            f"- {call['ticker']} {call['action']} / {call['reason']} / {status} / {call['id']}"
        )
        if not call.get("reference_start_at"):
            rows.append("  UNSCORABLE: no prospective reference start was frozen.")
        if not call.get("lesson_applications"):
            rows.append("  Legacy call: no lesson application was recorded; do not infer one.")
        rows.extend(
            [
                f"  Issued {call['recorded_at']}; review by {call['review_by']}.",
                f"  Entry {call['entry']}; confidence {call['confidence']}.",
                f"  Rationale: {call['rationale']}",
                f"  If no dip: {call['missed_entry_response']}",
                f"  Invalidation: {call['invalidation']}",
            ]
        )
        if call.get("supersedes"):
            rows.append(
                f"  Revises {call['supersedes']} / {call['change_kind']}: {call['change_reason']}"
            )
        for item in call.get("lesson_applications", []):
            rows.append(
                f"  Lesson {item['id']} v{item['version']} / "
                f"{item['disposition']}: {item['effect']}"
            )
    rows.extend(["", "## Recorded Outcomes", ""])
    outcomes = [r for r in read_jsonl(root / LEDGER) if r.get("kind") == "outcome"]
    replaced = {r.get("supersedes") for r in outcomes}
    for outcome in outcomes:
        if outcome["id"] in replaced:
            continue
        rows.append(
            f"- {outcome['recommendation_id']} / {outcome['window']} / "
            f"{outcome['entry_observation']} / reference excess "
            f"{outcome['excess_return_pp']:+.2f} pp / "
            f"rotation advantage {outcome['rotation_advantage_pp']}"
        )
        if outcome.get("lesson_assessment"):
            assessment = outcome["lesson_assessment"]
            rows.append(
                f"  Recorded lesson comparison: {assessment['conclusion']} / {assessment['reason']}"
            )
    rows.extend(
        [
            "",
            "## Pending Checkpoints",
            "",
            "Score only when enough provider trading sessions have elapsed; no calendar-day proxy.",
        ]
    )
    for call in read_jsonl(root / LEDGER):
        if call.get("kind") != "recommendation":
            continue
        if not call.get("reference_start_at"):
            rows.append(f"- {call['ticker']} / {call['id']} / UNSCORABLE: missing reference start")
            continue
        measured = {r["window"] for r in outcomes if r["recommendation_id"] == call["id"]}
        missing = [window for window in WINDOWS if window not in measured]
        if missing:
            rows.append(f"- {call['ticker']} / {call['id']} / {', '.join(missing)}")
        if call.get("lesson_test") and not any(
            r["recommendation_id"] == call["id"]
            and r["id"] not in replaced
            and r["window"] == call["lesson_test"]["window"]
            and r.get("lesson_assessment")
            for r in outcomes
        ):
            test = call["lesson_test"]
            rows.append(
                f"  Lesson test pending: {test['id']} v{test['version']} / "
                f"{test['window']} / cohort {test['cohort_key']}"
            )
    return "\n".join(rows) + "\n"
