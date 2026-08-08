from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.io import (
    append_jsonl,
    read_jsonl,
    read_markdown_frontmatter,
    scalar_text,
    write_markdown_with_frontmatter,
)

HANDOFF_RECORD_TYPE = "research_handoff"
APPLICATION_RECORD_TYPE = "research_handoff_application"
ALLOWED_CAUSE_STATUSES = {"BOUNDED", "UNBOUNDED", "UNRESOLVED"}
ALLOWED_THESIS_STATUSES = {"INTACT", "IMPAIRED", "UNRESOLVED"}
ALLOWED_VALUATION_STATUSES = {"ATTRACTIVE", "FAIR", "EXPENSIVE", "UNREVIEWED"}
ALLOWED_PROVISIONAL_BIASES = {
    "HOLD",
    "ADD_ON_DIP_REVIEW",
    "BUY_REVIEW",
    "TRIM_REVIEW",
    "SELL_REVIEW",
    "RESEARCH_REQUIRED",
}
ALLOWED_DECISIONS = {
    "BUY_NOW",
    "ADD_ON_DIP",
    "HOLD",
    "TRIM",
    "SELL",
    "RESEARCH_REQUIRED",
}
PRIVATE_KEYS = {
    "account",
    "account_name",
    "average_cost",
    "cash",
    "cost_basis",
    "current_position_weight_pct",
    "position_value",
    "quantity",
    "shares",
}


class ResearchHandoffError(RuntimeError):
    """Raised when a research-to-PM handoff violates the operating contract."""


def add_research_handoff(
    root: Path,
    *,
    memo_path: Path,
    ticker: str,
    cause_status: str,
    thesis_status: str,
    valuation_status: str,
    provisional_bias: str,
    confidence: float,
    summary: str,
    next_catalyst: str = "",
    event_ids: list[str] | None = None,
    primary_source_checked_at: str = "",
    expires_at: str = "",
    cause_key: str = "",
    primary_evidence_key: str = "",
) -> dict[str, Any]:
    ticker = ticker.upper().strip()
    relative_memo = _relative_memo_path(root, memo_path)
    _require_choice("cause status", cause_status, ALLOWED_CAUSE_STATUSES)
    _require_choice("thesis status", thesis_status, ALLOWED_THESIS_STATUSES)
    _require_choice("valuation status", valuation_status, ALLOWED_VALUATION_STATUSES)
    _require_choice("provisional bias", provisional_bias, ALLOWED_PROVISIONAL_BIASES)
    if not ticker or not (root / "research" / "decisions" / f"{ticker}.md").exists():
        raise ResearchHandoffError(f"Unknown research handoff ticker: {ticker or '<empty>'}")
    if not 0 <= confidence <= 100:
        raise ResearchHandoffError("Handoff confidence must be between 0 and 100.")
    if not summary.strip():
        raise ResearchHandoffError("Handoff summary is required.")

    memo_date = _memo_date(relative_memo)
    path = handoff_path(root)
    records = read_jsonl(path)
    existing = {
        scalar_text(record.get("handoff_id")): record
        for record in records
        if scalar_text(record.get("record_type")) == HANDOFF_RECORD_TYPE
    }
    duplicate = _same_daily_resolution(
        records,
        ticker=ticker,
        memo_date=memo_date,
        cause_key=cause_key,
        primary_evidence_key=primary_evidence_key,
    )
    if duplicate is not None:
        return duplicate

    handoff_id = handoff_id_for(ticker, relative_memo)
    if handoff_id in existing:
        return existing[handoff_id]

    record = {
        "record_type": HANDOFF_RECORD_TYPE,
        "handoff_id": handoff_id,
        "created_at": _now(),
        "memo_date": memo_date,
        "memo_path": relative_memo,
        "ticker": ticker,
        "cause_status": cause_status,
        "thesis_status": thesis_status,
        "valuation_status": valuation_status,
        "provisional_bias": provisional_bias,
        "confidence": round(float(confidence), 1),
        "summary": summary.strip(),
        "next_catalyst": next_catalyst.strip(),
        "event_ids": sorted({item.strip() for item in (event_ids or []) if item.strip()}),
        "primary_source_checked_at": primary_source_checked_at.strip() or memo_date,
        "cause_key": cause_key.strip().lower(),
        "primary_evidence_key": primary_evidence_key.strip(),
        "expires_at": expires_at.strip(),
        "pm_review_required": True,
    }
    _assert_no_private_fields(record)
    append_jsonl(path, record)
    return record


def _same_daily_resolution(
    records: list[dict[str, Any]],
    *,
    ticker: str,
    memo_date: str,
    cause_key: str,
    primary_evidence_key: str,
) -> dict[str, Any] | None:
    normalized_cause = cause_key.strip().lower()
    if not normalized_cause:
        return None
    normalized_evidence = primary_evidence_key.strip()
    matches = [
        record
        for record in records
        if scalar_text(record.get("record_type")) == HANDOFF_RECORD_TYPE
        and scalar_text(record.get("ticker")).upper() == ticker
        and scalar_text(record.get("memo_date")) == memo_date
        and scalar_text(record.get("cause_key")).lower() == normalized_cause
    ]
    if not matches:
        return None
    latest = matches[-1]
    existing_evidence = scalar_text(latest.get("primary_evidence_key"))
    if normalized_evidence and existing_evidence != normalized_evidence:
        return None
    return latest


def apply_research_handoff(
    root: Path,
    *,
    handoff_id: str,
    decision: str,
    reason: str,
    update_research_files: bool = False,
    evidence_quality: str = "RESOLVER_MEMO_PM_REVIEW",
    next_trigger: str = "",
    confidence: float | None = None,
    keep_material_event_open: bool = False,
) -> dict[str, Any]:
    handoff_id = handoff_id.strip()
    decision = decision.upper().strip()
    if decision not in ALLOWED_DECISIONS:
        raise ResearchHandoffError(f"Invalid applied decision: {decision}")
    if not reason.strip():
        raise ResearchHandoffError("Handoff application reason is required.")
    if confidence is not None and not 0 <= confidence <= 100:
        raise ResearchHandoffError("Applied confidence must be between 0 and 100.")

    records = read_jsonl(handoff_path(root))
    handoffs = {
        scalar_text(record.get("handoff_id")): record
        for record in records
        if scalar_text(record.get("record_type")) == HANDOFF_RECORD_TYPE
    }
    handoff = handoffs.get(handoff_id)
    if handoff is None:
        raise ResearchHandoffError(f"Unknown research handoff: {handoff_id}")
    if handoff_id in applied_handoff_ids(records):
        raise ResearchHandoffError(f"Research handoff is already applied: {handoff_id}")

    ticker = scalar_text(handoff.get("ticker")).upper()
    decision_path = root / "research" / "decisions" / f"{ticker}.md"
    if not update_research_files:
        existing_metadata, _ = read_markdown_frontmatter(decision_path)
        existing_decision = scalar_text(
            existing_metadata.get("current_decision")
            or existing_metadata.get("decision")
        ).upper()
        if existing_decision != decision:
            raise ResearchHandoffError(
                f"{ticker} decision file is {existing_decision or 'missing'}, "
                f"not {decision}."
            )

    if decision in {"BUY_NOW", "ADD_ON_DIP"}:
        from bottleneck_capital.validation import has_errors, validate_project

        strict_issues = validate_project(root, strict_live=True)
        if has_errors(strict_issues):
            raise ResearchHandoffError(
                f"{decision} is blocked until bcap validate --strict-live has no errors."
            )
    if update_research_files:
        _update_research_files(
            root,
            handoff=handoff,
            decision=decision,
            rationale=reason,
            evidence_quality=evidence_quality,
            next_trigger=next_trigger,
            confidence=confidence,
            keep_material_event_open=keep_material_event_open,
        )

    metadata, _ = read_markdown_frontmatter(decision_path)
    persisted_decision = scalar_text(
        metadata.get("current_decision") or metadata.get("decision")
    ).upper()
    if persisted_decision != decision:
        raise ResearchHandoffError(
            f"{ticker} decision file is {persisted_decision or 'missing'}, not {decision}."
        )
    last_updated = scalar_text(metadata.get("last_updated"))
    memo_date = scalar_text(handoff.get("memo_date"))
    if memo_date and (not last_updated or last_updated[:10] < memo_date[:10]):
        raise ResearchHandoffError(
            f"{ticker} decision last_updated {last_updated or 'missing'} predates "
            f"handoff memo {memo_date}."
        )

    record = {
        "record_type": APPLICATION_RECORD_TYPE,
        "application_id": _application_id(handoff_id, decision, reason),
        "applied_at": _now(),
        "applied_handoff_id": handoff_id,
        "ticker": ticker,
        "decision": decision,
        "reason": reason.strip(),
        "decision_last_updated": last_updated,
    }
    _assert_no_private_fields(record)
    append_jsonl(handoff_path(root), record)
    return record


def pending_research_handoffs(root: Path) -> list[dict[str, Any]]:
    records = read_jsonl(handoff_path(root))
    applied = applied_handoff_ids(records)
    pending = [
        record
        for record in records
        if scalar_text(record.get("record_type")) == HANDOFF_RECORD_TYPE
        and scalar_text(record.get("handoff_id")) not in applied
    ]
    return sorted(
        pending,
        key=lambda record: (
            scalar_text(record.get("created_at")),
            scalar_text(record.get("ticker")),
        ),
    )


def pending_handoffs_by_ticker(root: Path) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in pending_research_handoffs(root):
        ticker = scalar_text(record.get("ticker")).upper()
        if ticker:
            grouped.setdefault(ticker, []).append(record)
    return grouped


def applied_handoff_ids(records: list[dict[str, Any]]) -> set[str]:
    return {
        scalar_text(record.get("applied_handoff_id"))
        for record in records
        if scalar_text(record.get("record_type")) == APPLICATION_RECORD_TYPE
        and scalar_text(record.get("applied_handoff_id"))
    }


def backfill_research_handoffs(root: Path) -> list[dict[str, Any]]:
    tickers = {
        path.stem.upper()
        for path in (root / "research" / "decisions").glob("*.md")
        if path.stem.lower() != "index"
    }
    written: list[dict[str, Any]] = []
    for memo_path in sorted((root / "research" / "memos").glob("*.md")):
        for ticker in memo_tickers(memo_path, tickers):
            before = len(read_jsonl(handoff_path(root)))
            record = add_research_handoff(
                root,
                memo_path=memo_path,
                ticker=ticker,
                cause_status="UNRESOLVED",
                thesis_status="UNRESOLVED",
                valuation_status="UNREVIEWED",
                provisional_bias="RESEARCH_REQUIRED",
                confidence=0,
                summary=(
                    "Backfilled from an existing resolver memo. Portfolio PM must read "
                    "the memo and record an explicit decision application."
                ),
                primary_source_checked_at=_memo_date(memo_path.name),
            )
            after = len(read_jsonl(handoff_path(root)))
            if after > before:
                written.append(record)
    return written


def memo_tickers(path: Path, universe: set[str]) -> list[str]:
    stem = re.sub(r"^20\d{2}-\d{2}-\d{2}-", "", path.stem)
    allowed = {ticker.upper() for ticker in universe}
    tickers: list[str] = []
    for token in re.split(r"[^A-Za-z0-9]+", stem):
        normalized = token.upper()
        if normalized in allowed:
            tickers.append(normalized)
            continue
        break
    return sorted(set(tickers))


def handoff_id_for(ticker: str, memo_path: str) -> str:
    payload = json.dumps(
        {"ticker": ticker.upper(), "memo_path": memo_path},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def handoff_path(root: Path) -> Path:
    return root / "state" / "research_handoffs.jsonl"


def _relative_memo_path(root: Path, memo_path: Path) -> str:
    candidate = memo_path if memo_path.is_absolute() else root / memo_path
    candidate = candidate.resolve()
    memo_root = (root / "research" / "memos").resolve()
    try:
        relative = candidate.relative_to(root.resolve())
        candidate.relative_to(memo_root)
    except ValueError as exc:
        raise ResearchHandoffError(
            "Research handoff memo must be under research/memos."
        ) from exc
    if not candidate.exists() or candidate.suffix.lower() != ".md":
        raise ResearchHandoffError(f"Research handoff memo does not exist: {candidate}")
    return relative.as_posix()


def _memo_date(value: str) -> str:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", value)
    return match.group(1) if match else ""


def _application_id(handoff_id: str, decision: str, reason: str) -> str:
    payload = f"{handoff_id}|{decision}|{reason.strip()}|{_now()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _require_choice(label: str, value: str, allowed: set[str]) -> None:
    if value not in allowed:
        raise ResearchHandoffError(
            f"Invalid {label}: {value}. Expected one of {', '.join(sorted(allowed))}."
        )


def _assert_no_private_fields(record: dict[str, Any]) -> None:
    private = PRIVATE_KEYS & {key.lower() for key in record}
    if private:
        raise ResearchHandoffError(
            "Research handoff contains private position fields: " + ", ".join(sorted(private))
        )


def _update_research_files(
    root: Path,
    *,
    handoff: dict[str, Any],
    decision: str,
    rationale: str,
    evidence_quality: str,
    next_trigger: str,
    confidence: float | None,
    keep_material_event_open: bool,
) -> None:
    ticker = scalar_text(handoff.get("ticker")).upper()
    checked_at = scalar_text(
        handoff.get("primary_source_checked_at") or handoff.get("memo_date")
    )[:10]
    today = _now()[:10]
    for directory in ("assets", "decisions"):
        path = root / "research" / directory / f"{ticker}.md"
        metadata, body = read_markdown_frontmatter(path)
        if not metadata:
            raise ResearchHandoffError(f"Cannot update missing research metadata: {path}")
        metadata["current_decision"] = decision
        metadata["last_updated"] = today
        metadata["last_primary_source_check"] = max(
            scalar_text(metadata.get("last_primary_source_check"))[:10],
            checked_at,
        )
        metadata["one_line_rationale"] = rationale.strip()
        metadata["evidence_quality"] = evidence_quality.strip() or "RESOLVER_MEMO_PM_REVIEW"
        metadata["unresolved_material_event"] = keep_material_event_open
        metadata["thesis_damage"] = (
            scalar_text(handoff.get("thesis_status")) == "IMPAIRED"
        )
        metadata["action_tier"] = decision
        if next_trigger.strip():
            metadata["next_trigger"] = next_trigger.strip()
        if confidence is not None:
            metadata["confidence_score"] = round(float(confidence), 1)
        write_markdown_with_frontmatter(path, metadata, body)


def _now() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds")
