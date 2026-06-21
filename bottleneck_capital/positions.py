from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import evaluate_all, load_watchlist
from bottleneck_capital.io import ConfigError, dump_yaml_mapping, load_yaml_file, scalar_text

LOCAL_POSITIONS_PATH = Path("state/local_positions.yaml")


@dataclass(frozen=True)
class Position:
    ticker: str
    quantity: float
    average_cost: float
    current_price: float
    currency: str
    account: str
    notes: str

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.quantity * self.average_cost

    @property
    def unrealized_pl(self) -> float:
        return self.market_value - self.cost_basis


def initialize_local_positions(root: Path, overwrite: bool = False) -> Path:
    path = root / LOCAL_POSITIONS_PATH
    if path.exists() and not overwrite:
        return path
    watchlist = load_watchlist(root)
    data = {
        "as_of": _today(),
        "base_currency": "CAD",
        "cash": {
            "CAD": 0,
            "USD": 0,
        },
        "positions": [
            {
                "ticker": item["ticker"],
                "quantity": 0,
                "average_cost": 0,
                "current_price": 0,
                "currency": "USD",
                "account": "",
                "notes": "",
            }
            for item in watchlist
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml_mapping(data), encoding="utf-8")
    return path


def render_exposure(root: Path, positions_path: Path | None = None) -> str:
    path = positions_path or root / LOCAL_POSITIONS_PATH
    positions_data = _load_positions_data(path)
    positions = _load_positions(positions_data)
    decisions = {result.ticker: result for result in evaluate_all(root)}
    watchlist = {item["ticker"]: item for item in load_watchlist(root)}
    total_value = sum(position.market_value for position in positions)
    as_of = scalar_text(positions_data.get("as_of")) or _today()
    base_currency = scalar_text(positions_data.get("base_currency")) or "CAD"
    cash = _cash_total(positions_data.get("cash"))

    lines = [
        "# Bottleneck Capital Local Exposure",
        "",
        f"As of: {as_of}",
        f"Base currency: {base_currency}",
        "",
        "Privacy: generated from local gitignored position data.",
        "",
        "## Summary",
        "",
        f"- Positions market value: {_money(total_value)}",
        f"- Cash entered: {_money(cash)}",
        f"- Total entered exposure: {_money(total_value + cash)}",
        "",
        "## By Ticker",
        "",
        "| Ticker | Sleeve | Decision | Qty | Price | Value | Weight | P/L | Account | Notes |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for position in sorted(positions, key=lambda item: item.ticker):
        decision = decisions.get(position.ticker)
        watch = watchlist.get(position.ticker, {})
        sleeve = scalar_text(watch.get("sleeve")) or "UNTRACKED"
        action = decision.action if decision else "UNTRACKED"
        weight = position.market_value / total_value if total_value else 0
        lines.append(
            f"| {position.ticker} | {sleeve} | {action} | {_number(position.quantity)} | "
            f"{_money(position.current_price)} | {_money(position.market_value)} | "
            f"{weight:.1%} | {_money(position.unrealized_pl)} | "
            f"{_table(position.account)} | {_table(position.notes)} |"
        )

    lines.extend(["", "## By Sleeve", ""])
    lines.extend(_render_group_table(_group_by_sleeve(positions, watchlist), total_value))
    lines.extend(["", "## By Decision", ""])
    lines.extend(_render_group_table(_group_by_decision(positions, decisions), total_value))
    unknown = [position.ticker for position in positions if position.ticker not in watchlist]
    if unknown:
        lines.extend(["", "## Untracked Tickers", ""])
        lines.extend(f"- `{ticker}` is not in configs/watchlist.yaml" for ticker in unknown)
    return "\n".join(lines) + "\n"


def write_exposure_report(root: Path, positions_path: Path | None = None) -> Path:
    report_path = root / "reports" / "local_exposure.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_exposure(root, positions_path), encoding="utf-8")
    return report_path


def _load_positions_data(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(
            f"Missing local positions file: {path}. Run `bcap positions-init` first."
        )
    data = load_yaml_file(path)
    if not isinstance(data, dict):
        raise ConfigError(f"Local positions file must be a mapping: {path}")
    return data


def _load_positions(data: dict[str, Any]) -> list[Position]:
    raw_positions = data.get("positions", [])
    if not isinstance(raw_positions, list):
        raise ConfigError("positions must be a list")
    positions: list[Position] = []
    for index, item in enumerate(raw_positions, start=1):
        if not isinstance(item, dict):
            raise ConfigError(f"Position {index} must be a mapping")
        ticker = scalar_text(item.get("ticker")).upper()
        if not ticker:
            raise ConfigError(f"Position {index} is missing ticker")
        quantity = _float(item.get("quantity"))
        average_cost = _float(item.get("average_cost"))
        current_price = _float(item.get("current_price"))
        if quantity == 0 and average_cost == 0 and current_price == 0:
            continue
        positions.append(
            Position(
                ticker=ticker,
                quantity=quantity,
                average_cost=average_cost,
                current_price=current_price,
                currency=scalar_text(item.get("currency")) or "USD",
                account=scalar_text(item.get("account")),
                notes=scalar_text(item.get("notes")),
            )
        )
    return positions


def _cash_total(value: Any) -> float:
    if not isinstance(value, dict):
        return 0.0
    return sum(_float(amount) for amount in value.values())


def _group_by_sleeve(
    positions: list[Position], watchlist: dict[str, dict[str, Any]]
) -> dict[str, float]:
    grouped: dict[str, float] = {}
    for position in positions:
        sleeve = scalar_text(watchlist.get(position.ticker, {}).get("sleeve")) or "UNTRACKED"
        grouped[sleeve] = grouped.get(sleeve, 0.0) + position.market_value
    return grouped


def _group_by_decision(positions: list[Position], decisions: dict[str, Any]) -> dict[str, float]:
    grouped: dict[str, float] = {}
    for position in positions:
        decision = decisions.get(position.ticker)
        action = decision.action if decision else "UNTRACKED"
        grouped[action] = grouped.get(action, 0.0) + position.market_value
    return grouped


def _render_group_table(grouped: dict[str, float], total_value: float) -> list[str]:
    lines = ["| Group | Value | Weight |", "|---|---:|---:|"]
    if not grouped:
        lines.append("| - | - | - |")
        return lines
    for group, value in sorted(grouped.items(), key=lambda item: (-item[1], item[0])):
        weight = value / total_value if total_value else 0
        lines.append(f"| {group} | {_money(value)} | {weight:.1%} |")
    return lines


def _float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Expected numeric position value, got {value!r}") from exc


def _money(value: float) -> str:
    return f"{value:,.2f}"


def _number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:,.4f}".rstrip("0").rstrip(".")


def _table(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def _today() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).date().isoformat()
