from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.io import (
    append_jsonl,
    load_yaml_file,
    read_jsonl,
    read_markdown_frontmatter,
    scalar_bool,
    scalar_text,
    write_markdown_with_frontmatter,
)
from bottleneck_capital.signal_events import (
    active_signal_events,
    event_id_for_record,
    group_signal_events,
)

ALLOWED_DECISIONS = {
    "BUY_NOW",
    "ADD_ON_DIP",
    "HOLD",
    "TRIM",
    "SELL",
    "RESEARCH_REQUIRED",
}

BOARD_SECTIONS = [
    ("BUY_NOW", "Buy Now"),
    ("ADD_ON_DIP", "Add on Dip"),
    ("HOLD", "Hold"),
    ("TRIM", "Trim / Sell Watch"),
    ("SELL", "Sell"),
    ("RESEARCH_REQUIRED", "Research Required"),
]

MATERIAL_EVENT_CLASSES = {
    "dip_trigger",
    "thesis_damage_candidate",
    "filing_update",
    "catalyst_update",
    "hedge_risk_update",
    "sa_exit_update",
    "sa_position_reduction_update",
    "market_data_gap",
    "filing_data_gap",
}


class DecisionEngineError(RuntimeError):
    """Base decision engine error."""


class MissingDecisionFile(DecisionEngineError):
    """Raised when a watchlist ticker has no decision file."""


@dataclass(frozen=True)
class DecisionResult:
    ticker: str
    name: str
    sleeve: str
    action: str
    urgency: str
    rationale: str
    next_trigger: str
    confidence: str
    hedge: str
    source_classification: str = ""
    instrument_role: str = ""
    trade_policy: str = ""
    broken_thesis: str = ""
    action_tier: str = ""
    bottleneck_upside_score: str = ""
    bottleneck_upside_case: str = ""
    promotion_trigger: str = ""
    max_add: str = ""


def load_watchlist(root: Path) -> list[dict[str, Any]]:
    data = load_yaml_file(root / "configs" / "watchlist.yaml")
    items = data.get("watchlist") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise DecisionEngineError("configs/watchlist.yaml must define a watchlist list")
    watchlist: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict) or not scalar_text(item.get("ticker")):
            raise DecisionEngineError("Every watchlist item must be a mapping with a ticker")
        copied = dict(item)
        copied["ticker"] = scalar_text(item["ticker"]).upper()
        watchlist.append(copied)
    return watchlist


def evaluate_all(root: Path) -> list[DecisionResult]:
    events = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    safe_bounded_dips = _safe_bounded_dip_tickers(root)
    decision_events = [
        event
        for event in events
        if not _is_safe_bounded_dip(event, safe_bounded_dips)
    ]
    return [evaluate_ticker(root, item, decision_events) for item in load_watchlist(root)]


def _safe_bounded_dip_tickers(root: Path) -> set[str]:
    from bottleneck_capital.dip_review import review_active_dips

    return {
        review.ticker
        for review in review_active_dips(root)
        if review.bounded
        and review.thesis_damage_risk in {"LOW", "LOW_MEDIUM"}
        and review.action_bias
        in {
            "ADD_ON_DIP_CANDIDATE_IF_VALUATION_CLEARS",
            "SLEEVE_RELATIVE_VALUE_REVIEW",
        }
    }


def _is_safe_bounded_dip(event: dict[str, Any], tickers: set[str]) -> bool:
    return (
        scalar_text(event.get("event_class")) == "dip_trigger"
        and scalar_text(event.get("ticker")).upper() in tickers
    )


def evaluate_ticker(
    root: Path,
    watchlist_item: dict[str, Any],
    signal_events: list[dict[str, Any]] | None = None,
) -> DecisionResult:
    ticker = scalar_text(watchlist_item.get("ticker")).upper()
    decision_path = root / "research" / "decisions" / f"{ticker}.md"
    if not decision_path.exists():
        raise MissingDecisionFile(f"Missing decision file for {ticker}: {decision_path}")

    asset_data, _ = read_markdown_frontmatter(root / "research" / "assets" / f"{ticker}.md")
    decision_data, _ = read_markdown_frontmatter(decision_path)
    ticker_events = [
        event
        for event in (signal_events or [])
        if scalar_text(event.get("ticker")).upper() == ticker
    ]
    unresolved_events = [event for event in ticker_events if _is_unresolved_material(event)]
    released_event_override = _is_released_material_event_override(
        asset_data,
        decision_data,
        unresolved_events,
    )
    asset_research_override = released_event_override or _asset_research_is_current(
        asset_data,
        decision_data,
    )
    data = (
        {**watchlist_item, **decision_data, **asset_data}
        if asset_research_override
        else {**watchlist_item, **asset_data, **decision_data}
    )

    name = scalar_text(data.get("name") or watchlist_item.get("name") or ticker)
    sleeve = scalar_text(data.get("sleeve") or watchlist_item.get("sleeve") or "unassigned")
    current = _normalize_decision(
        (
            asset_data.get("current_decision") or asset_data.get("decision")
            if asset_research_override
            else decision_data.get("current_decision")
            or decision_data.get("decision")
            or asset_data.get("current_decision")
            or asset_data.get("decision")
        )
    )
    thesis_damage = scalar_bool(asset_data.get("thesis_damage")) or scalar_bool(
        decision_data.get("thesis_damage")
    )
    broken_thesis = scalar_text(
        decision_data.get("broken_thesis") or asset_data.get("broken_thesis")
    )
    unacceptable_risk = scalar_text(
        decision_data.get("unacceptable_risk") or asset_data.get("unacceptable_risk")
    )
    thesis_damage_events = [
        event
        for event in unresolved_events
        if event.get("event_class") == "thesis_damage_candidate"
    ]
    sa_exit_events = [
        event
        for event in unresolved_events
        if event.get("event_class") == "sa_exit_update"
    ]
    sa_reduction_events = [
        event
        for event in unresolved_events
        if event.get("event_class") == "sa_position_reduction_update"
    ]
    trade_policy = scalar_text(data.get("trade_policy"))

    if current == "SELL":
        if not broken_thesis and not unacceptable_risk:
            return _research_required(
                ticker,
                name,
                sleeve,
                data,
                "SELL requires a named broken thesis or unacceptable risk.",
            )
        return _result(ticker, name, sleeve, "SELL", data, broken_thesis=broken_thesis)

    if thesis_damage_events:
        return _research_required(
            ticker,
            name,
            sleeve,
            data,
            "Unresolved thesis damage candidate must be researched before action.",
        )

    if sa_exit_events:
        return _research_required(
            ticker,
            name,
            sleeve,
            data,
            "Situational Awareness appears to have fully exited; review for exit, "
            "thesis correction, or changed source classification.",
        )

    if sa_reduction_events:
        return _research_required(
            ticker,
            name,
            sleeve,
            data,
            "Situational Awareness appears to have materially reduced exposure; "
            "review thesis weight and position discipline.",
        )

    unresolved_material_event = scalar_bool(data.get("unresolved_material_event"))
    if unresolved_events or unresolved_material_event:
        return _research_required(
            ticker,
            name,
            sleeve,
            data,
            "Unresolved material event requires research before changing capital.",
        )

    if thesis_damage:
        return _research_required(
            ticker,
            name,
            sleeve,
            data,
            "Thesis damage is flagged; ADD_ON_DIP and BUY_NOW are blocked.",
        )

    if trade_policy == "signal_only_no_puts_or_shorts" and current not in {"SELL", "TRIM"}:
        return _result(
            ticker,
            name,
            sleeve,
            "HOLD",
            {
                **data,
                "one_line_rationale": (
                    "Signal-only SA put/hedge exposure; no puts or shorts in the current mandate."
                ),
                "next_trigger": (
                    "Monitor as SA risk signal; act only if a separate long-only thesis emerges."
                ),
            },
        )

    if current == "BUY_NOW":
        missing = _missing_buy_requirements(data)
        if missing:
            return _research_required(
                ticker,
                name,
                sleeve,
                data,
                f"BUY_NOW missing required discipline fields: {', '.join(missing)}.",
            )
        return _result(ticker, name, sleeve, "BUY_NOW", data)

    if current == "ADD_ON_DIP":
        if not _dip_is_approved(data):
            return _research_required(
                ticker,
                name,
                sleeve,
                data,
                "ADD_ON_DIP requires an approved dip protocol with no thesis damage.",
            )
        if not _valuation_improved(data):
            return _research_required(
                ticker,
                name,
                sleeve,
                data,
                "ADD_ON_DIP requires improved valuation or entry-zone evidence.",
            )
        if not scalar_bool(data.get("portfolio_risk_allows_add", True)):
            return _research_required(
                ticker,
                name,
                sleeve,
                data,
                "ADD_ON_DIP blocked until portfolio risk allows adding.",
            )
        return _result(ticker, name, sleeve, "ADD_ON_DIP", data)

    return _result(ticker, name, sleeve, current, data)


def compile_decisions(root: Path) -> list[DecisionResult]:
    results = evaluate_all(root)
    now = _now()
    by_ticker = {item["ticker"]: item for item in load_watchlist(root)}
    ledger_path = root / "state" / "decision_ledger.jsonl"
    latest_ledger = _latest_ledger_by_ticker(read_jsonl(ledger_path))
    for result in results:
        path = root / "research" / "decisions" / f"{result.ticker}.md"
        existing, _ = read_markdown_frontmatter(path)
        asset_data, _ = read_markdown_frontmatter(
            root / "research" / "assets" / f"{result.ticker}.md"
        )
        source_data = (
            {**existing, **asset_data}
            if _asset_research_is_current(asset_data, existing)
            or _compiled_event_override_was_released(result, asset_data, existing)
            else existing
        )
        write_markdown_with_frontmatter(
            path,
            _decision_frontmatter(result, source_data, now),
            _decision_body(result, source_data),
        )
        ledger_record = _ledger_record(result, now)
        if _ledger_changed(latest_ledger.get(result.ticker), ledger_record):
            append_jsonl(ledger_path, ledger_record)
            latest_ledger[result.ticker] = ledger_record
    write_decision_index(root, results, now, by_ticker)
    return results


def write_daily_board(root: Path) -> Path:
    results = compile_decisions(root)
    now = _now()
    report_path = root / "reports" / "daily_decision_boards" / f"{now[:10]}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_daily_board(results, now), encoding="utf-8")
    return report_path


def write_action_board(root: Path) -> Path:
    from bottleneck_capital.dip_review import review_active_dips
    from bottleneck_capital.opportunity import (
        opportunity_board_limit,
        overdue_research_blocks,
        rank_opportunities,
    )

    results = evaluate_all(root)
    events = active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
    dip_reviews = review_active_dips(root)
    decisions = {result.ticker: result.action for result in results}
    opportunities = rank_opportunities(root, decision_overrides=decisions)[
        : opportunity_board_limit(root)
    ]
    overdue = overdue_research_blocks(root, decision_overrides=decisions)
    now = _now()
    report_path = root / "reports" / "action_boards" / f"{now[:10]}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_action_board(
            results,
            events,
            now,
            dip_reviews,
            opportunities=opportunities,
            overdue_research=overdue,
        ),
        encoding="utf-8",
    )
    return report_path


def write_decision_index(
    root: Path,
    results: list[DecisionResult],
    now: str | None = None,
    watchlist: dict[str, dict[str, Any]] | None = None,
) -> Path:
    del watchlist
    path = root / "research" / "decisions" / "index.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_decision_index(results, now or _now()), encoding="utf-8")
    return path


def render_daily_board(results: list[DecisionResult], now: str) -> str:
    lines = [
        "# Bottleneck Capital Daily Decision Board",
        "",
        f"Date: {now}",
        "",
        "## Immediate Actions",
        "",
        "| Ticker | Decision | Urgency | Why |",
        "|---|---|---:|---|",
    ]
    for result in results:
        lines.append(
            f"| {result.ticker} | {result.action} | {result.urgency} | {_table(result.rationale)} |"
        )
    lines.extend([""])
    lines.extend(_render_board_sections(results))
    return "\n".join(lines) + "\n"


def render_action_board(
    results: list[DecisionResult],
    signal_events: list[dict[str, Any]],
    now: str,
    dip_reviews: list[Any] | None = None,
    opportunities: list[Any] | None = None,
    overdue_research: list[Any] | None = None,
) -> str:
    from bottleneck_capital.dip_review import render_action_board_dip_reviews

    actionable = [
        result
        for result in results
        if result.action in {"BUY_NOW", "ADD_ON_DIP", "TRIM", "SELL", "RESEARCH_REQUIRED"}
    ]
    high_events = [
        event
        for event in signal_events
        if scalar_text(event.get("priority")) in {"high", "critical"}
        and scalar_text(event.get("event_class")) != "noise"
    ]
    source_gap_events = [
        event
        for event in high_events
        if scalar_text(event.get("event_class")) in {"market_data_gap", "filing_data_gap"}
    ]
    lines = [
        "# Bottleneck Capital Action Board",
        "",
        f"Date: {now}",
        "",
    ]
    if source_gap_events:
        lines.extend(
            [
                "## Operational Source Gaps",
                "",
                (
                    "Do not treat action rows as fully cleared while these source gaps are active; "
                    "recover the source or explicitly accept the blind spot for scheduled "
                    "monitoring."
                ),
                "",
                "| Event ID | Ticker | Class | Summary |",
                "|---|---|---|---|",
            ]
        )
        for event in source_gap_events:
            lines.append(
                f"| {event_id_for_record(event)} | "
                f"{_table(scalar_text(event.get('ticker')).upper())} | "
                f"{_table(scalar_text(event.get('event_class')))} | "
                f"{_table(scalar_text(event.get('summary')))} |"
            )
        lines.append("")
    lines.extend(_render_opportunity_ranking(opportunities or []))
    lines.append("")
    if overdue_research:
        lines.extend(_render_overdue_research(overdue_research))
        lines.append("")
    lines.extend(render_action_board_dip_reviews(dip_reviews or []))
    lines.append("")
    lines.extend(
        [
            "## Actions",
            "",
        ]
    )
    lines.extend([
        "| Ticker | Decision | Urgency | Max Add | Why |",
        "|---|---|---:|---:|---|",
    ])
    if actionable:
        for result in actionable:
            lines.append(
                f"| {result.ticker} | {result.action} | {result.urgency} | "
                f"{_table(result.max_add)} | {_table(result.rationale)} |"
            )
    else:
        lines.append("| - | - | - | - | No actionable decision changes. |")

    lines.extend(["", "## Active High-Priority Signals", ""])
    grouped_high_events = group_signal_events(high_events)
    lines.extend(
        [
            "| Latest Event ID | Ticker | Class | Count | Latest Summary |",
            "|---|---|---|---:|---|",
        ]
    )
    if grouped_high_events:
        for event in grouped_high_events:
            lines.append(
                f"| {event_id_for_record(event)} | "
                f"{_table(scalar_text(event.get('ticker')).upper())} | "
                f"{_table(scalar_text(event.get('event_class')))} | "
                f"{int(event.get('event_count', 1))} | "
                f"{_table(scalar_text(event.get('summary')))} |"
            )
    else:
        lines.append("| - | - | - | - | - |")
    return "\n".join(lines) + "\n"


def render_decision_index(results: list[DecisionResult], now: str) -> str:
    lines = ["# Bottleneck Capital Decision Index", "", f"Updated: {now}", ""]
    lines.extend(_render_board_sections(results))
    return "\n".join(lines) + "\n"


def _render_opportunity_ranking(opportunities: list[Any]) -> list[str]:
    lines = [
        "## Opportunity Ranking",
        "",
        (
            "Ranked by thesis health, valuation, bottleneck upside, confidence, "
            "portfolio capacity, and current decision."
        ),
        "",
        "| Rank | Ticker | Decision | Score | Price | Approved Entry | Why |",
        "|---:|---|---|---:|---:|---|---|",
    ]
    if not opportunities:
        lines.append("| - | - | - | - | - | - | - |")
        return lines
    for index, item in enumerate(opportunities, start=1):
        price = f"${item.current_price:,.2f}" if item.current_price > 0 else "Unknown"
        lines.append(
            f"| {index} | {_table(item.ticker)} | {_table(item.decision)} | "
            f"{item.score:.1f} | {price} | {_table(item.entry_zone)} | "
            f"{_table(item.rationale)} |"
        )
    return lines


def _render_overdue_research(items: list[Any]) -> list[str]:
    lines = [
        "## Overdue Research Blocks",
        "",
        (
            "These names have remained RESEARCH_REQUIRED beyond the configured review "
            "window. Refresh primary evidence and either resolve the block or explicitly "
            "reaffirm it."
        ),
        "",
        "| Ticker | Age | Max Age | Opportunity Score | Last Primary Check | Block |",
        "|---|---:|---:|---:|---|---|",
    ]
    for item in items:
        lines.append(
            f"| {_table(item.ticker)} | {item.age_days}d | {item.max_age_days}d | "
            f"{item.score:.1f} | {_table(item.last_primary_source_check)} | "
            f"{_table(item.rationale)} |"
        )
    return lines


def create_dip_investigation(root: Path, ticker: str) -> Path:
    ticker = ticker.upper()
    events = [
        event
        for event in active_signal_events(read_jsonl(root / "state" / "signal_events.jsonl"))
        if scalar_text(event.get("ticker")).upper() == ticker
    ]
    decision_data, _ = read_markdown_frontmatter(root / "research" / "decisions" / f"{ticker}.md")
    today = _now()[:10]
    path = root / "research" / "memos" / "dips" / f"{today}-{ticker}-dip.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    current_decision = _normalize_decision(decision_data.get("current_decision"))
    latest_event = events[-1] if events else {}
    path.write_text(
        "\n".join(
            [
                f"# Buyable Dip Investigation - {ticker}",
                "",
                f"Ticker: {ticker}",
                f"Move: {scalar_text(latest_event.get('summary')) or 'Unknown'}",
                f"Detected at: {scalar_text(latest_event.get('detected_at')) or 'Unknown'}",
                f"Known trigger: {scalar_text(latest_event.get('source')) or 'Unknown'}",
                f"Current decision: {current_decision}",
                f"Dip status: {scalar_text(decision_data.get('dip_status')) or 'UNKNOWN'}",
                "",
                "Goal: Decide whether this is a buyable dip, a dangerous dip, an unknown dip, "
                "or a thesis-break dip.",
                "",
                "Answer:",
                "1. What caused the move?",
                "2. Is the cause related to the core thesis?",
                "3. Did any primary evidence change?",
                "4. Did the long-term thesis improve, deteriorate, or stay the same?",
                "5. Did valuation become attractive enough to act?",
                "6. Does portfolio risk allow adding?",
                "7. Is this a better opportunity than other assets in the same sleeve?",
                "8. Should the decision change?",
                "",
                "Return one of:",
                "- BUY_DIP_NOW",
                "- ADD_SMALL_ON_DIP",
                "- HOLD",
                "- WAIT_FOR_RESEARCH",
                "- DO_NOT_BUY",
                "- SELL_THESIS_BROKEN",
                "",
                "Decision:",
                "",
                "Rationale:",
                "",
                "Evidence checked:",
                "",
                "Thesis damage:",
                "",
                "Valuation impact:",
                "",
                "Hedge impact:",
                "",
                "Invalidation trigger:",
                "",
                "Human action:",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _normalize_decision(value: Any) -> str:
    action = scalar_text(value).upper() or "RESEARCH_REQUIRED"
    if action not in ALLOWED_DECISIONS:
        return "RESEARCH_REQUIRED"
    return action


def _is_released_material_event_override(
    asset_data: dict[str, Any],
    decision_data: dict[str, Any],
    unresolved_events: list[dict[str, Any]],
) -> bool:
    if unresolved_events:
        return False
    asset_decision = _normalize_decision(
        asset_data.get("current_decision") or asset_data.get("decision")
    )
    decision = _normalize_decision(
        decision_data.get("current_decision") or decision_data.get("decision")
    )
    return (
        decision == "RESEARCH_REQUIRED"
        and asset_decision != "RESEARCH_REQUIRED"
        and scalar_text(decision_data.get("one_line_rationale"))
        == "Unresolved material event requires research before changing capital."
    )


def _asset_research_is_current(
    asset_data: dict[str, Any],
    decision_data: dict[str, Any],
) -> bool:
    asset_updated = scalar_text(asset_data.get("last_updated"))[:10]
    decision_updated = scalar_text(decision_data.get("last_updated"))[:10]
    return bool(asset_updated) and (
        not decision_updated or asset_updated >= decision_updated
    )


def _compiled_event_override_was_released(
    result: DecisionResult,
    asset_data: dict[str, Any],
    decision_data: dict[str, Any],
) -> bool:
    asset_decision = _normalize_decision(
        asset_data.get("current_decision") or asset_data.get("decision")
    )
    decision = _normalize_decision(
        decision_data.get("current_decision") or decision_data.get("decision")
    )
    return (
        result.action == asset_decision
        and result.action != "RESEARCH_REQUIRED"
        and decision == "RESEARCH_REQUIRED"
        and scalar_text(decision_data.get("one_line_rationale"))
        == "Unresolved material event requires research before changing capital."
    )


def _is_unresolved_material(event: dict[str, Any]) -> bool:
    if scalar_bool(event.get("resolved")):
        return False
    event_class = scalar_text(event.get("event_class"))
    if event_class not in MATERIAL_EVENT_CLASSES:
        return False
    return scalar_bool(event.get("requires_codex", True)) or scalar_text(event.get("priority")) in {
        "high",
        "critical",
    }


def _missing_buy_requirements(data: dict[str, Any]) -> list[str]:
    requirements = {
        "thesis": data.get("buy_thesis") or data.get("thesis_expressed"),
        "anti_thesis": data.get("anti_thesis"),
        "valuation": data.get("valuation_case") or data.get("approved_entry_zone"),
        "hedge": data.get("hedge_or_sizing") or data.get("main_hedge"),
        "invalidation": data.get("invalidation_trigger"),
        "evidence_quality": data.get("evidence_quality"),
    }
    return [key for key, value in requirements.items() if not scalar_text(value)]


def _dip_is_approved(data: dict[str, Any]) -> bool:
    dip_status = scalar_text(data.get("dip_status")).upper()
    return scalar_bool(data.get("dip_approved")) or dip_status in {"APPROVED", "BUYABLE"}


def _valuation_improved(data: dict[str, Any]) -> bool:
    if scalar_bool(data.get("valuation_improved")):
        return True
    status = scalar_text(data.get("valuation_status")).upper()
    if status in {"DEEP_DISCOUNT", "FAIR_ENTRY", "ATTRACTIVE"}:
        return True
    score = data.get("valuation_attractiveness_score")
    return isinstance(score, int | float) and score >= 70


def _research_required(
    ticker: str,
    name: str,
    sleeve: str,
    data: dict[str, Any],
    rationale: str,
) -> DecisionResult:
    return DecisionResult(
        ticker=ticker,
        name=name,
        sleeve=sleeve,
        action="RESEARCH_REQUIRED",
        urgency=(
            scalar_text(data.get("urgency"))
            or scalar_text(data.get("urgency_score"))
            or "HIGH"
        ),
        rationale=rationale,
        next_trigger=scalar_text(data.get("next_trigger")) or "Resolve material open question.",
        confidence=str(data.get("confidence_score") or "0"),
        hedge=scalar_text(data.get("main_hedge") or data.get("hedge_or_sizing") or "TBD"),
        source_classification=scalar_text(data.get("source_classification")),
        instrument_role=scalar_text(data.get("instrument_role")),
        trade_policy=scalar_text(data.get("trade_policy")),
        action_tier=scalar_text(data.get("action_tier")) or "RESEARCH_REQUIRED",
        bottleneck_upside_score=_score_text(data.get("bottleneck_upside_score")),
        bottleneck_upside_case=scalar_text(data.get("bottleneck_upside_case")),
        promotion_trigger=scalar_text(data.get("promotion_trigger")),
        max_add=_max_add_text(data),
    )


def _result(
    ticker: str,
    name: str,
    sleeve: str,
    action: str,
    data: dict[str, Any],
    broken_thesis: str = "",
) -> DecisionResult:
    return DecisionResult(
        ticker=ticker,
        name=name,
        sleeve=sleeve,
        action=action,
        urgency=(
            scalar_text(data.get("urgency"))
            or scalar_text(data.get("urgency_score"))
            or "MEDIUM"
        ),
        rationale=scalar_text(data.get("one_line_rationale"))
        or scalar_text(data.get("decision_sentence"))
        or "Maintain current decision until new primary evidence changes the thesis.",
        next_trigger=(
            scalar_text(data.get("next_trigger"))
            or "New filing, earnings, contract, or price dislocation."
        ),
        confidence=str(data.get("confidence_score", "")),
        hedge=scalar_text(data.get("main_hedge") or data.get("hedge_or_sizing") or "TBD"),
        source_classification=scalar_text(data.get("source_classification")),
        instrument_role=scalar_text(data.get("instrument_role")),
        trade_policy=scalar_text(data.get("trade_policy")),
        broken_thesis=broken_thesis,
        action_tier=scalar_text(data.get("action_tier")) or action,
        bottleneck_upside_score=_score_text(data.get("bottleneck_upside_score")),
        bottleneck_upside_case=scalar_text(data.get("bottleneck_upside_case")),
        promotion_trigger=scalar_text(data.get("promotion_trigger")),
        max_add=_max_add_text(data),
    )


def _decision_frontmatter(
    result: DecisionResult, existing: dict[str, Any], now: str
) -> dict[str, Any]:
    dip_decision = (
        "NOT_ARMED"
        if result.trade_policy == "signal_only_no_puts_or_shorts"
        else existing.get("dip_decision", "NOT_ARMED")
    )
    return {
        "ticker": result.ticker,
        "name": result.name,
        "sleeve": result.sleeve,
        "current_decision": result.action,
        "dip_decision": dip_decision,
        "sell_status": (
            "TRIGGERED"
            if result.action == "SELL"
            else existing.get("sell_status", "NOT_TRIGGERED")
        ),
        "confidence_score": existing.get("confidence_score", result.confidence or 0),
        "urgency": result.urgency,
        "last_updated": now[:10],
        "source_classification": result.source_classification
        or existing.get("source_classification", ""),
        "instrument_role": result.instrument_role or existing.get("instrument_role", ""),
        "trade_policy": result.trade_policy or existing.get("trade_policy", ""),
        "thesis_damage": existing.get("thesis_damage", False),
        "unresolved_material_event": existing.get("unresolved_material_event", False),
        "dip_approved": existing.get("dip_approved", False),
        "valuation_improved": existing.get("valuation_improved", False),
        "portfolio_risk_allows_add": existing.get("portfolio_risk_allows_add", True),
        "buy_thesis": existing.get("buy_thesis", ""),
        "thesis_expressed": existing.get(
            "thesis_expressed", existing.get("buy_thesis", "")
        ),
        "anti_thesis": existing.get("anti_thesis", ""),
        "evidence_quality": existing.get("evidence_quality", ""),
        "valuation_case": existing.get("valuation_case", ""),
        "hedge_or_sizing": existing.get("hedge_or_sizing", ""),
        "invalidation_trigger": existing.get("invalidation_trigger", ""),
        "broken_thesis": result.broken_thesis or existing.get("broken_thesis", ""),
        "next_trigger": result.next_trigger,
        "one_line_rationale": result.rationale,
        "action_tier": result.action_tier or existing.get("action_tier", result.action),
        "bottleneck_upside_score": result.bottleneck_upside_score
        or existing.get("bottleneck_upside_score", ""),
        "bottleneck_upside_case": result.bottleneck_upside_case
        or existing.get("bottleneck_upside_case", ""),
        "promotion_trigger": result.promotion_trigger or existing.get("promotion_trigger", ""),
    }


def _decision_body(result: DecisionResult, existing: dict[str, Any]) -> str:
    sell_answer = "YES" if result.action == "SELL" else "NO"
    buy_answer = "YES" if result.action == "BUY_NOW" else "NO"
    if result.trade_policy == "signal_only_no_puts_or_shorts":
        dip_answer = "NOT_ARMED"
        human_action = "No trade; monitor as signal."
    else:
        dip_answer = "YES" if result.action == "ADD_ON_DIP" else scalar_text(
            existing.get("dip_decision")
        ) or "NO"
        human_action = (
            "Research before acting."
            if result.action == "RESEARCH_REQUIRED"
            else "Follow sizing and hedge discipline before any trade."
        )
    return f"""# {result.ticker} Decision

Updated: {_now()[:10]}

Decision: {result.action}
Dip decision: {dip_answer}
Sell status: {"TRIGGERED" if result.action == "SELL" else "NOT_TRIGGERED"}
Confidence: {result.confidence or "TBD"} / 100
Urgency: {result.urgency}

One-line rationale:
{result.rationale}

Thesis expressed:
{scalar_text(existing.get("thesis_expressed") or existing.get("buy_thesis")) or "TBD"}

Anti-thesis:
{scalar_text(existing.get("anti_thesis")) or "TBD"}

Evidence quality:
{scalar_text(existing.get("evidence_quality")) or "TBD"}

Hedge or sizing:
{scalar_text(existing.get("hedge_or_sizing")) or result.hedge}

Invalidation trigger:
{scalar_text(existing.get("invalidation_trigger")) or "TBD"}

Buy now?
{buy_answer}

Buy on dip?
{dip_answer}

Sell?
{sell_answer}

Next trigger:
{result.next_trigger}

Human action:
{human_action}
"""


def _ledger_record(result: DecisionResult, now: str) -> dict[str, Any]:
    return {
        "recorded_at": now,
        "ticker": result.ticker,
        "decision": result.action,
        "urgency": result.urgency,
        "rationale": result.rationale,
    }


def _latest_ledger_by_ticker(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for record in records:
        ticker = scalar_text(record.get("ticker")).upper()
        if ticker:
            latest[ticker] = record
    return latest


def _ledger_changed(previous: dict[str, Any] | None, current: dict[str, Any]) -> bool:
    if previous is None:
        return True
    return any(
        scalar_text(previous.get(key)) != scalar_text(current.get(key))
        for key in ("decision", "urgency", "rationale")
    )


def _render_board_sections(results: list[DecisionResult]) -> list[str]:
    lines: list[str] = []
    for action, title in BOARD_SECTIONS:
        lines.extend([f"## {title}", ""])
        section = [result for result in results if result.action == action]
        if action == "BUY_NOW":
            lines.extend(["| Ticker | Reason | Max Add | Hedge? |", "|---|---|---:|---|"])
            if section:
                for result in section:
                    lines.append(
                        f"| {result.ticker} | {_table(result.rationale)} | "
                        f"{_table(result.max_add)} | {result.hedge} |"
                    )
            else:
                lines.append("| - | - | - | - |")
        elif action == "ADD_ON_DIP":
            lines.extend(
                [
                    "| Ticker | Dip Trigger | Why Thesis Intact | Urgency |",
                    "|---|---|---|---:|",
                ]
            )
            if section:
                for result in section:
                    lines.append(
                        f"| {result.ticker} | Approved dip protocol | "
                        f"{_table(result.rationale)} | {result.urgency} |"
                    )
            else:
                lines.append("| - | - | - | - |")
        elif action == "HOLD":
            lines.extend(
                [
                    "| Ticker | Tier | Why | Bottleneck Upside | Promotion Trigger |",
                    "|---|---|---|---|---|",
                ]
            )
            if section:
                for result in section:
                    upside = result.bottleneck_upside_case
                    if result.bottleneck_upside_score:
                        upside = (
                            f"{result.bottleneck_upside_score}: {upside}"
                            if upside
                            else result.bottleneck_upside_score
                        )
                    lines.append(
                        f"| {result.ticker} | {_table(result.action_tier or result.action)} | "
                        f"{_table(result.rationale)} | "
                        f"{_table(upside or 'Not scored')} | "
                        f"{_table(result.promotion_trigger or result.next_trigger)} |"
                    )
            else:
                lines.append("| - | - | - | - | - |")
        elif action == "TRIM":
            lines.extend(["| Ticker | Risk | Trigger |", "|---|---|---|"])
            if section:
                for result in section:
                    lines.append(
                        f"| {result.ticker} | {_table(result.rationale)} | "
                        f"{_table(result.next_trigger)} |"
                    )
            else:
                lines.append("| - | - | - |")
        elif action == "SELL":
            lines.extend(["| Ticker | Broken Thesis | Action |", "|---|---|---|"])
            if section:
                for result in section:
                    lines.append(
                        f"| {result.ticker} | "
                        f"{_table(result.broken_thesis or result.rationale)} | "
                        "Sell / exit review |"
                    )
            else:
                lines.append("| - | - | - |")
        else:
            lines.extend(["| Ticker | Question | Deadline |", "|---|---|---|"])
            if section:
                for result in section:
                    lines.append(
                        f"| {result.ticker} | {_table(result.rationale)} | Next review |"
                    )
            else:
                lines.append("| - | - | - |")
        lines.append("")
    return lines


def _table(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def _score_text(value: Any) -> str:
    if value is None or value == "":
        return ""
    return scalar_text(value)


def _max_add_text(data: dict[str, Any]) -> str:
    for key in ("max_add", "approved_entry_size", "starter_position_weight_pct", "starter_size"):
        value = scalar_text(data.get(key))
        if value:
            return _pct_text(value)
    entry_zone = scalar_text(data.get("approved_entry_zone"))
    match = re.search(r"(?:starter|up to|add)\D{0,24}(\d+(?:\.\d+)?\s*%)", entry_zone, re.I)
    if match:
        return match.group(1).replace(" ", "")
    max_position = scalar_text(data.get("max_position_weight_pct"))
    if max_position:
        return f"cap {_pct_text(max_position)}"
    return "TBD"


def _pct_text(value: str) -> str:
    text = value.strip()
    return text if text.endswith("%") else f"{text}%"


def _now() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="minutes")
