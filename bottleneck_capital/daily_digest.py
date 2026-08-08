from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.io import read_jsonl, read_markdown_frontmatter, scalar_text
from bottleneck_capital.opportunity import OpportunityCandidate, rank_opportunities
from bottleneck_capital.research_handoffs import pending_research_handoffs
from bottleneck_capital.signal_events import active_signal_events, group_signal_events
from bottleneck_capital.validation import has_errors, validate_project

_ACTIONABLE_DECISIONS = {"BUY_NOW", "ADD_ON_DIP"}
_OPEN_REGIME_GATES = {"OPEN", "HALF_TRANCHE_ONLY"}
_BLOCKED_STRUCTURE_GATES = {
    "CONFIRM_FLOW_ABSORPTION",
    "REFRESH_STRUCTURE_DATA",
    "WAIT_FOR_SUPPLY_ABSORPTION",
}


def write_daily_digest(root: Path) -> Path:
    path = root / "reports" / "local_daily_digests" / f"{_today()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_daily_digest(root), encoding="utf-8")
    return path


def render_daily_digest(root: Path) -> str:
    today = _today()
    opportunities = rank_opportunities(root)
    pending = pending_research_handoffs(root)
    pending_tickers = {
        scalar_text(record.get("ticker")).upper() for record in pending
    }
    strict_issues = validate_project(root, strict_live=True)
    strict_blocked = has_errors(strict_issues)
    best = _best_executable(opportunities, pending_tickers, strict_blocked)
    leader = best or (opportunities[0] if opportunities else None)

    lines = [
        "# Bottleneck Capital Daily Digest",
        "",
        f"As of: {today}",
        "",
        "## What Changed",
        "",
    ]
    changes = _today_changes(root, today)
    lines.extend(f"- {item}" for item in changes)

    lines.extend(["", "## Best Action", ""])
    if best is not None:
        size = "half tranche" if best.entry_gate == "HALF_TRANCHE_ONLY" else "policy tranche"
        lines.append(
            f"- {best.decision} {best.ticker} with a {size} only inside "
            f"{best.entry_zone}; score {best.score:.1f}."
        )
        lines.append(f"- Why: {best.rationale}")
    elif leader is not None:
        block = _leader_block(leader, pending_tickers, strict_blocked)
        lines.append(f"- WAIT. Leading setup: {leader.ticker} ({leader.decision}). {block}")
        lines.append(f"- Why it still leads: {leader.rationale}")
    else:
        lines.append("- WAIT. No ranked long candidate is available.")

    lines.extend(["", "## Entry Levels", ""])
    for candidate in opportunities[:3]:
        data = _decision_data(root, candidate.ticker)
        trigger = _fragment(data.get("promotion_trigger") or data.get("next_trigger"))
        current = (
            f"${candidate.current_price:,.2f}"
            if candidate.current_price > 0
            else "unavailable"
        )
        lines.append(
            f"- {candidate.ticker}: current {current}; approved zone "
            f"{_fragment(candidate.entry_zone)}; trigger: {trigger or 'not armed'}."
        )
    if not opportunities:
        lines.append("- No entry levels available.")

    lines.extend(["", "## Invalidation", ""])
    if leader is not None:
        invalidation = scalar_text(_decision_data(root, leader.ticker).get("invalidation_trigger"))
        lines.append(f"- {leader.ticker}: {invalidation or 'No explicit invalidation recorded.'}")
    else:
        lines.append("- No candidate selected.")

    data_gaps = [
        issue.message for issue in strict_issues if issue.severity.lower() == "error"
    ]
    lines.extend(["", "## Data Quality", ""])
    lines.append(f"- Pending resolver handoffs: {len(pending)}.")
    if data_gaps:
        lines.append(f"- Strict-live blockers: {len(data_gaps)}. First: {data_gaps[0]}")
    else:
        lines.append("- Strict-live gate: clear.")
    return "\n".join(lines) + "\n"


def _best_executable(
    opportunities: list[OpportunityCandidate],
    pending_tickers: set[str],
    strict_blocked: bool,
) -> OpportunityCandidate | None:
    if strict_blocked:
        return None
    for candidate in opportunities:
        if candidate.ticker in pending_tickers:
            continue
        if candidate.decision not in _ACTIONABLE_DECISIONS:
            continue
        if candidate.entry_gate not in _OPEN_REGIME_GATES:
            continue
        if candidate.market_structure_gate in _BLOCKED_STRUCTURE_GATES:
            continue
        if candidate.current_price <= 0:
            continue
        return candidate
    return None


def _leader_block(
    leader: OpportunityCandidate,
    pending_tickers: set[str],
    strict_blocked: bool,
) -> str:
    if strict_blocked:
        return "Strict-live validation is not clear, so no new buy is authorized."
    if leader.ticker in pending_tickers:
        return "A resolver handoff still requires Portfolio PM review."
    if leader.decision not in _ACTIONABLE_DECISIONS:
        return f"The current decision is {leader.decision}, not an armed buy."
    if leader.entry_gate not in _OPEN_REGIME_GATES:
        return f"The macro gate is {leader.entry_gate}."
    if leader.market_structure_gate in _BLOCKED_STRUCTURE_GATES:
        return f"The market-structure gate is {leader.market_structure_gate}."
    return "The current price is unavailable."


def _today_changes(root: Path, today: str) -> list[str]:
    changes: list[str] = []
    previous: dict[str, str] = {}
    for record in read_jsonl(root / "state" / "decision_ledger.jsonl"):
        ticker = scalar_text(record.get("ticker")).upper()
        decision = scalar_text(record.get("decision")).upper()
        recorded_at = scalar_text(record.get("recorded_at"))
        if ticker and recorded_at[:10] == today and previous.get(ticker) != decision:
            changes.append(f"{ticker} moved to {decision}.")
        if ticker and decision:
            previous[ticker] = decision

    active = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    for record in group_signal_events(active):
        if scalar_text(record.get("latest_detected_at") or record.get("detected_at"))[:10] != today:
            continue
        ticker = scalar_text(record.get("ticker")).upper()
        event_class = scalar_text(record.get("event_class")).replace("_", " ")
        summary = scalar_text(record.get("summary"))
        changes.append(f"{ticker}: {event_class}. {summary}")
    return changes[:5] or ["No material decision or signal change recorded today."]


def _decision_data(root: Path, ticker: str) -> dict[str, Any]:
    decision, _ = read_markdown_frontmatter(
        root / "research" / "decisions" / f"{ticker}.md"
    )
    asset, _ = read_markdown_frontmatter(root / "research" / "assets" / f"{ticker}.md")
    return {**decision, **asset}


def _fragment(value: Any) -> str:
    return scalar_text(value).rstrip(". ;")


def _today() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).date().isoformat()
