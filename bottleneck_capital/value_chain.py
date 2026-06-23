from __future__ import annotations

# ruff: noqa: E501
import json
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bottleneck_capital.decision_engine import load_watchlist
from bottleneck_capital.io import read_markdown_frontmatter, scalar_text

JENSEN_STACK_SOURCE = {
    "framework": "Jensen Huang five-layer AI stack",
    "layers": "Energy -> chips -> infrastructure -> models -> applications",
    "primary_source_note": (
        "The public summary used here describes Huang's five-layer stack as energy, "
        "chips, infrastructure, models, and applications."
    ),
    "source_urls": [
        "https://www.axios.com/2026/03/10/jensen-huang-ais-biggest-buildout-is-still-ahead",
        "https://www.techradar.com/pro/nvidia-wants-to-have-your-cake-and-eat-it-jensen-described-the-ai-layered-stack-and-hints-at-what-worlds-most-valuable-firm-will-do-next",
    ],
}


@dataclass(frozen=True)
class LayerDefinition:
    id: str
    order: int
    name: str
    headline: str
    description: str
    watch_question: str
    color: str
    empty_note: str = ""


LAYERS = [
    LayerDefinition(
        id="applications",
        order=5,
        name="Applications",
        headline="Where intelligence becomes products, labor, autonomy, and services",
        description=(
            "End-market expressions that pull demand through the whole stack and reveal "
            "whether AI capex is turning into economic value."
        ),
        watch_question="Is the application layer creating durable demand or just narrative pull?",
        color="#9a6a2d",
    ),
    LayerDefinition(
        id="models",
        order=4,
        name="Models",
        headline="The capability layer that consumes compute and creates frontier pressure",
        description=(
            "Model labs and platform signals. This system currently tracks this layer mostly "
            "through demand pull and hedge pressure rather than pure-play model equities."
        ),
        watch_question="Does model progress justify the next unit of infrastructure spend?",
        color="#6f5f91",
        empty_note="No pure-play model lab ticker is currently tracked; model risk is inferred.",
    ),
    LayerDefinition(
        id="infrastructure",
        order=3,
        name="Infrastructure",
        headline="AI factories: sites, clusters, networking, clouds, and conversion assets",
        description=(
            "The built layer that turns power and silicon into contracted compute capacity."
        ),
        watch_question="Is capacity scarce, contracted, financed, and deliverable?",
        color="#3f725f",
    ),
    LayerDefinition(
        id="chips",
        order=2,
        name="Chips",
        headline="Accelerators, memory, foundry, tooling, packaging, and chip beta",
        description=(
            "The semiconductor bottleneck layer, including scarce compute silicon and the "
            "equipment or foundry capacity needed to make it."
        ),
        watch_question="Is the scarcity structural enough to beat valuation and cycle risk?",
        color="#2f6c9e",
    ),
    LayerDefinition(
        id="energy",
        order=1,
        name="Energy",
        headline="Power, interconnection, onsite generation, thermal, and water constraints",
        description=(
            "The physical foundation. AI factories only scale when power and cooling arrive "
            "on useful timelines."
        ),
        watch_question="Who controls scarce power, interconnection, or equipment leverage?",
        color="#b65b38",
    ),
]


SLEEVE_LAYER_MAP: dict[str, dict[str, Any]] = {
    "power_bottleneck": {
        "layer_id": "energy",
        "role": "Power bottleneck",
        "bridge_to": ["infrastructure"],
    },
    "ai_power_equipment": {
        "layer_id": "energy",
        "role": "Power, thermal, and water equipment",
        "bridge_to": ["infrastructure"],
    },
    "semicap_equipment": {
        "layer_id": "chips",
        "role": "Semicap, lithography, foundry enablement",
        "bridge_to": ["infrastructure"],
    },
    "memory_storage_networking": {
        "layer_id": "chips",
        "role": "HBM, storage, foundry, and advanced packaging",
        "bridge_to": ["infrastructure"],
    },
    "crowded_ai_beta_hedge": {
        "layer_id": "chips",
        "role": "Crowded AI chip beta and hedge signal",
        "bridge_to": ["models", "infrastructure"],
    },
    "compute_infra": {
        "layer_id": "infrastructure",
        "role": "Contracted compute and AI cloud capacity",
        "bridge_to": ["models"],
    },
    "miner_to_datacenter": {
        "layer_id": "infrastructure",
        "role": "Power/site conversion into AI or HPC datacenters",
        "bridge_to": ["energy"],
    },
    "enterprise_ai_infra": {
        "layer_id": "infrastructure",
        "role": "Enterprise AI cloud/capex duration signal",
        "bridge_to": ["models", "applications"],
    },
    "ai_networking_optical": {
        "layer_id": "infrastructure",
        "role": "Cluster fabric, optical, and data movement",
        "bridge_to": ["chips"],
    },
    "space_infra": {
        "layer_id": "infrastructure",
        "role": "Strategic connectivity and defense infrastructure proxy",
        "bridge_to": ["applications"],
    },
    "ai_services_put_signal": {
        "layer_id": "applications",
        "role": "AI disruption signal in services/application labor",
        "bridge_to": ["models"],
    },
    "autonomy_energy": {
        "layer_id": "applications",
        "role": "Autonomy, robotics, embodied AI, and energy adjacency",
        "bridge_to": ["energy", "models"],
    },
}


FLOW_LINKS = [
    {
        "from": "energy",
        "to": "chips",
        "label": "Power and cooling enable fabs, packaging, and AI factories.",
    },
    {
        "from": "chips",
        "to": "infrastructure",
        "label": "Silicon becomes deployed clusters, clouds, and interconnect fabric.",
    },
    {
        "from": "infrastructure",
        "to": "models",
        "label": "Clusters train and serve models; model demand feeds back into capex.",
    },
    {
        "from": "models",
        "to": "applications",
        "label": "Models become workflows, autonomy, robotics, and enterprise disruption.",
    },
]


def build_value_chain_data(root: Path) -> dict[str, Any]:
    watchlist = load_watchlist(root)
    tickers = [_build_ticker(root, item) for item in watchlist]
    by_layer = {layer.id: [] for layer in LAYERS}
    for ticker in tickers:
        by_layer[ticker["layer_id"]].append(ticker)

    layer_payload = []
    for layer in LAYERS:
        layer_tickers = sorted(
            by_layer[layer.id],
            key=lambda item: (
                _priority_rank(item.get("priority")),
                item.get("sleeve", ""),
                item.get("ticker", ""),
            ),
        )
        layer_payload.append(
            {
                "id": layer.id,
                "order": layer.order,
                "name": layer.name,
                "headline": layer.headline,
                "description": layer.description,
                "watch_question": layer.watch_question,
                "color": layer.color,
                "empty_note": layer.empty_note,
                "tickers": layer_tickers,
                "sleeves": sorted({ticker["sleeve"] for ticker in layer_tickers}),
            }
        )

    return {
        "generated_at": datetime.now(ZoneInfo("America/Toronto")).isoformat(timespec="seconds"),
        "source": JENSEN_STACK_SOURCE,
        "layers": layer_payload,
        "flow_links": FLOW_LINKS,
        "tickers": tickers,
        "sleeve_layer_map": SLEEVE_LAYER_MAP,
        "summary": _build_summary(tickers),
    }


def write_value_chain_visualizer(root: Path, output_path: Path | None = None) -> Path:
    root = root.resolve()
    if output_path is None:
        output_path = root / "reports" / "value_chain_visualizer.html"
    elif not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = build_value_chain_data(root)
    json_payload = json.dumps(data, indent=2, sort_keys=True).replace("</", "<\\/")
    output_path.write_text(HTML_TEMPLATE.replace("__DATA_JSON__", json_payload), encoding="utf-8")
    return output_path


def serve_value_chain_visualizer(root: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    root = root.resolve()
    write_value_chain_visualizer(root)
    handler = partial(_ValueChainRequestHandler, root=root, directory=str(root))
    server = _ReusableThreadingHTTPServer((host, port), handler)
    url = f"http://{host}:{port}/reports/value_chain_visualizer.html"
    print(url, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _build_ticker(root: Path, watchlist_item: dict[str, Any]) -> dict[str, Any]:
    ticker = scalar_text(watchlist_item["ticker"]).upper()
    asset_data, _ = read_markdown_frontmatter(root / "research" / "assets" / f"{ticker}.md")
    decision_data, _ = read_markdown_frontmatter(root / "research" / "decisions" / f"{ticker}.md")
    data = {**watchlist_item, **asset_data, **decision_data}
    sleeve = scalar_text(data.get("sleeve") or "unassigned")
    layer_info = SLEEVE_LAYER_MAP.get(
        sleeve,
        {
            "layer_id": "applications",
            "role": "Unmapped application or thesis signal",
            "bridge_to": [],
        },
    )
    return {
        "ticker": ticker,
        "name": scalar_text(data.get("name") or ticker),
        "sleeve": sleeve,
        "layer_id": layer_info["layer_id"],
        "layer_role": layer_info["role"],
        "bridge_to": layer_info.get("bridge_to", []),
        "current_decision": scalar_text(data.get("current_decision") or "RESEARCH_REQUIRED"),
        "dip_decision": scalar_text(data.get("dip_decision") or ""),
        "sell_status": scalar_text(data.get("sell_status") or ""),
        "confidence_score": scalar_text(data.get("confidence_score") or ""),
        "urgency": scalar_text(data.get("urgency") or ""),
        "source_classification": scalar_text(data.get("source_classification") or ""),
        "instrument_role": scalar_text(data.get("instrument_role") or ""),
        "trade_policy": scalar_text(data.get("trade_policy") or ""),
        "priority": scalar_text(data.get("priority") or ""),
        "thesis_expressed": scalar_text(data.get("thesis_expressed") or data.get("buy_thesis") or ""),
        "anti_thesis": scalar_text(data.get("anti_thesis") or ""),
        "hedge_or_sizing": scalar_text(data.get("hedge_or_sizing") or ""),
        "invalidation_trigger": scalar_text(data.get("invalidation_trigger") or ""),
        "evidence_quality": scalar_text(data.get("evidence_quality") or ""),
        "one_line_rationale": scalar_text(data.get("one_line_rationale") or ""),
        "next_trigger": scalar_text(data.get("next_trigger") or ""),
    }


def _priority_rank(priority: str | None) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(scalar_text(priority).lower(), 3)


class _ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class _ValueChainRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, root: Path, **kwargs: Any) -> None:
        self._root = root
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if self.path in {"", "/"}:
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/reports/value_chain_visualizer.html")
            self.end_headers()
            return
        if self.path.split("?", 1)[0] == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] != "/__bcap_update":
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")
            return
        try:
            output_path = write_value_chain_visualizer(self._root)
        except Exception as exc:  # pragma: no cover - exercised manually through local server.
            payload = json.dumps({"ok": False, "error": str(exc)}).encode("utf-8")
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        payload = json.dumps({"ok": True, "path": str(output_path)}).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: Any) -> None:
        return


def _build_summary(tickers: list[dict[str, Any]]) -> dict[str, Any]:
    decisions: dict[str, int] = {}
    source_classes: dict[str, int] = {}
    signal_only = 0
    for ticker in tickers:
        decisions[ticker["current_decision"]] = decisions.get(ticker["current_decision"], 0) + 1
        source = ticker["source_classification"] or "unclassified"
        source_classes[source] = source_classes.get(source, 0) + 1
        if ticker["trade_policy"] == "signal_only_no_puts_or_shorts":
            signal_only += 1
    return {
        "ticker_count": len(tickers),
        "decision_counts": dict(sorted(decisions.items())),
        "source_classification_counts": dict(sorted(source_classes.items())),
        "signal_only_count": signal_only,
    }


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bottleneck Capital Visualizer</title>
  <style>
    :root {
      --bg: #f6f8fb;
      --panel: #ffffff;
      --panel-soft: #eef3f7;
      --text: #17202a;
      --muted: #5d6875;
      --border: #d7e0e8;
      --strong-border: #9fb0bf;
      --shadow: 0 18px 46px rgba(39, 54, 71, 0.10);
      --buy: #0f7a55;
      --hold: #586575;
      --research: #a2641d;
      --sell: #a23b3b;
      --signal: #4d5d8c;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      color: var(--text);
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(246, 248, 251, 0.98)),
        repeating-linear-gradient(90deg, transparent 0, transparent 31px, rgba(130, 151, 171, 0.08) 32px),
        repeating-linear-gradient(0deg, transparent 0, transparent 31px, rgba(130, 151, 171, 0.08) 32px);
    }

    button,
    input,
    select {
      font: inherit;
    }

    .app {
      min-height: 100vh;
      padding: 20px;
    }

    .shell {
      max-width: 1680px;
      margin: 0 auto;
    }

    .topbar {
      display: grid;
      grid-template-columns: minmax(280px, 1fr) minmax(320px, 680px);
      gap: 16px;
      align-items: end;
      padding: 18px 0 16px;
      border-bottom: 1px solid var(--border);
    }

    .title h1 {
      margin: 0;
      font-size: 28px;
      line-height: 1.1;
      font-weight: 760;
      letter-spacing: 0;
    }

    .title p {
      max-width: 940px;
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }

    .controls {
      display: grid;
      grid-template-columns: 1.4fr 1fr 1fr 0.8fr auto auto;
      gap: 8px;
      align-items: center;
    }

    .control {
      width: 100%;
      height: 38px;
      padding: 0 11px;
      color: var(--text);
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      outline: none;
    }

    .control:focus {
      border-color: #6686a5;
      box-shadow: 0 0 0 3px rgba(47, 108, 158, 0.13);
    }

    .icon-button {
      width: 38px;
      height: 38px;
      display: inline-grid;
      place-items: center;
      color: var(--text);
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      cursor: pointer;
    }

    .icon-button:hover {
      border-color: var(--strong-border);
      background: #f9fbfd;
    }

    .update-button {
      height: 38px;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 0 12px;
      color: #ffffff;
      background: #244c6d;
      border: 1px solid #244c6d;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 740;
      cursor: pointer;
      white-space: nowrap;
    }

    .update-button:hover {
      background: #1d405d;
      border-color: #1d405d;
    }

    .update-button:disabled {
      cursor: wait;
      opacity: 0.72;
    }

    .update-button svg {
      flex: 0 0 auto;
    }

    .status-line {
      min-height: 18px;
      grid-column: 1 / -1;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }

    .status-line.error {
      color: #8f3f1c;
    }

    .summary-strip {
      display: grid;
      grid-template-columns: repeat(5, minmax(120px, 1fr));
      gap: 10px;
      margin: 16px 0;
    }

    .metric {
      min-height: 74px;
      padding: 13px 14px;
      background: rgba(255, 255, 255, 0.76);
      border: 1px solid var(--border);
      border-radius: 8px;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 720;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .metric strong {
      display: block;
      margin-top: 7px;
      font-size: 25px;
      line-height: 1;
      letter-spacing: 0;
    }

    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 16px;
      align-items: start;
    }

    .workspace > *,
    .cake,
    .layer,
    .ticker-zone,
    .inspector {
      min-width: 0;
    }

    .cake {
      display: grid;
      gap: 10px;
    }

    .layer {
      --layer-color: #3f725f;
      position: relative;
      display: grid;
      grid-template-columns: 260px minmax(0, 1fr);
      gap: 12px;
      min-height: 156px;
      padding: 14px;
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid var(--border);
      border-left: 7px solid var(--layer-color);
      border-radius: 8px;
      box-shadow: 0 1px 0 rgba(255,255,255,0.9) inset;
    }

    .layer::before {
      content: "";
      position: absolute;
      left: 18px;
      top: -10px;
      bottom: -10px;
      width: 1px;
      background: linear-gradient(180deg, transparent, rgba(95, 114, 132, 0.38), transparent);
      pointer-events: none;
    }

    .layer:first-child::before { top: 18px; }
    .layer:last-child::before { bottom: 18px; }

    .layer-meta {
      padding-left: 18px;
    }

    .layer-kicker {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: var(--layer-color);
      font-size: 11px;
      font-weight: 760;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .layer-dot {
      width: 8px;
      height: 8px;
      border-radius: 99px;
      background: var(--layer-color);
      box-shadow: 0 0 0 4px rgba(255,255,255,0.9);
    }

    .layer h2 {
      margin: 9px 0 0;
      font-size: 21px;
      line-height: 1.12;
      font-weight: 740;
      letter-spacing: 0;
    }

    .layer p {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.42;
    }

    .layer-question {
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid rgba(110, 128, 145, 0.22);
      color: #374454;
      font-size: 12px;
      line-height: 1.35;
    }

    .ticker-zone {
      display: grid;
      gap: 10px;
      align-content: start;
    }

    .sleeve-group {
      display: grid;
      gap: 8px;
    }

    .sleeve-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      color: #324051;
      font-size: 12px;
      font-weight: 720;
      line-height: 1.2;
    }

    .sleeve-title code {
      color: var(--muted);
      font-size: 11px;
      font-weight: 620;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(138px, 1fr));
      gap: 8px;
    }

    .ticker-card {
      min-width: 0;
      min-height: 82px;
      padding: 10px;
      text-align: left;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      cursor: pointer;
      transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
    }

    .ticker-card:hover,
    .ticker-card.selected {
      transform: translateY(-1px);
      border-color: var(--layer-color);
      box-shadow: 0 8px 24px rgba(39, 54, 71, 0.12);
    }

    .ticker-card.hidden {
      display: none;
    }

    .ticker-top {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: start;
    }

    .ticker-symbol {
      font-size: 16px;
      line-height: 1;
      font-weight: 780;
      letter-spacing: 0;
    }

    .ticker-name {
      margin-top: 5px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.25;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }

    .ticker-tags {
      display: flex;
      gap: 5px;
      flex-wrap: wrap;
      margin-top: 9px;
    }

    .tag {
      display: inline-flex;
      max-width: 100%;
      align-items: center;
      height: 20px;
      padding: 0 7px;
      border-radius: 999px;
      border: 1px solid rgba(102, 118, 135, 0.22);
      background: #f7fafc;
      color: #425064;
      font-size: 10px;
      font-weight: 720;
      white-space: nowrap;
    }

    .tag.decision-HOLD { color: var(--hold); }
    .tag.decision-BUY_NOW,
    .tag.decision-ADD_ON_DIP { color: var(--buy); }
    .tag.decision-RESEARCH_REQUIRED { color: var(--research); }
    .tag.decision-SELL,
    .tag.decision-TRIM { color: var(--sell); }
    .tag.signal { color: var(--signal); }

    .empty-layer {
      display: grid;
      min-height: 76px;
      place-items: center;
      padding: 14px;
      color: var(--muted);
      background: rgba(246, 248, 251, 0.84);
      border: 1px dashed var(--strong-border);
      border-radius: 8px;
      font-size: 13px;
      text-align: center;
    }

    .inspector {
      position: sticky;
      top: 16px;
      display: grid;
      gap: 12px;
      padding: 16px;
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }

    .inspector-header {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }

    .inspector h2 {
      margin: 0;
      font-size: 24px;
      line-height: 1;
      letter-spacing: 0;
    }

    .inspector .name {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }

    .decision-pill {
      display: inline-flex;
      align-items: center;
      height: 28px;
      padding: 0 10px;
      border-radius: 999px;
      background: #f2f5f8;
      color: var(--hold);
      font-size: 11px;
      font-weight: 780;
      white-space: nowrap;
    }

    .decision-pill.BUY_NOW,
    .decision-pill.ADD_ON_DIP { color: var(--buy); }
    .decision-pill.RESEARCH_REQUIRED { color: var(--research); }
    .decision-pill.SELL,
    .decision-pill.TRIM { color: var(--sell); }

    .detail-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .detail {
      padding: 10px;
      background: var(--panel-soft);
      border-radius: 8px;
      min-width: 0;
    }

    .detail span {
      display: block;
      color: var(--muted);
      font-size: 10px;
      font-weight: 760;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .detail strong {
      display: block;
      margin-top: 5px;
      font-size: 12px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .narrative {
      display: grid;
      gap: 10px;
    }

    .narrative section {
      display: grid;
      gap: 4px;
    }

    .narrative h3 {
      margin: 0;
      color: #334255;
      font-size: 12px;
      line-height: 1.2;
      font-weight: 760;
    }

    .narrative p {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.42;
    }

    .table-wrap {
      width: 100%;
      max-width: 100%;
      margin-top: 16px;
      background: rgba(255, 255, 255, 0.82);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 920px;
    }

    th,
    td {
      padding: 9px 10px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      font-size: 12px;
      line-height: 1.3;
      vertical-align: top;
    }

    th {
      position: sticky;
      top: 0;
      z-index: 1;
      background: #f7fafc;
      color: #38475a;
      font-size: 11px;
      font-weight: 780;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    tbody tr {
      cursor: pointer;
    }

    tbody tr:hover {
      background: #f8fbfd;
    }

    .footer {
      margin: 18px 0 10px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.45;
    }

    .footer a {
      color: #285f90;
      text-decoration: none;
    }

    .footer a:hover {
      text-decoration: underline;
    }

    @media (max-width: 1180px) {
      .topbar,
      .workspace {
        grid-template-columns: 1fr;
      }

      .inspector {
        position: static;
      }
    }

    @media (max-width: 760px) {
      .app {
        padding: 12px;
      }

      .topbar {
        padding-top: 10px;
      }

      .controls,
      .summary-strip,
      .layer,
      .detail-grid {
        grid-template-columns: 1fr;
      }

      .layer-meta {
        padding-left: 14px;
      }

      .title h1 {
        font-size: 24px;
      }
    }
  </style>
</head>
<body>
  <main class="app">
    <div class="shell">
      <header class="topbar">
        <div class="title">
          <h1>Bottleneck Capital Visualizer</h1>
          <p id="frameworkSummary"></p>
        </div>
        <div class="controls" aria-label="Visualizer filters">
          <input id="searchInput" class="control" type="search" placeholder="Search ticker, company, sleeve">
          <select id="decisionFilter" class="control" aria-label="Decision filter"></select>
          <select id="sourceFilter" class="control" aria-label="Source filter"></select>
          <select id="layerFilter" class="control" aria-label="Layer filter"></select>
          <button id="updateButton" class="update-button" type="button">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M20 6v5h-5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 18v-5h5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M17.8 9a6.8 6.8 0 0 0-11-2M6.2 15a6.8 6.8 0 0 0 11 2" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>
            </svg>
            Update
          </button>
          <button id="resetButton" class="icon-button" type="button" title="Reset filters" aria-label="Reset filters">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M4 6v5h5M20 18v-5h-5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7.2 9.1a6.8 6.8 0 0 1 11 2M16.8 14.9a6.8 6.8 0 0 1-11-2" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>
            </svg>
          </button>
          <div id="updateStatus" class="status-line" role="status" aria-live="polite"></div>
        </div>
      </header>

      <section id="summaryStrip" class="summary-strip" aria-label="Portfolio summary"></section>

      <section class="workspace">
        <div>
          <div id="cake" class="cake" aria-label="Five-layer value chain"></div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Company</th>
                  <th>Layer</th>
                  <th>Sleeve</th>
                  <th>Decision</th>
                  <th>Source</th>
                  <th>Role</th>
                </tr>
              </thead>
              <tbody id="tickerRows"></tbody>
            </table>
          </div>
        </div>
        <aside id="inspector" class="inspector" aria-live="polite"></aside>
      </section>

      <footer class="footer">
        Generated from <code>configs/watchlist.yaml</code> and <code>research/decisions/*.md</code>.
        Five-layer source framing: <a href="https://www.axios.com/2026/03/10/jensen-huang-ais-biggest-buildout-is-still-ahead">Axios</a>
        and <a href="https://www.techradar.com/pro/nvidia-wants-to-have-your-cake-and-eat-it-jensen-described-the-ai-layered-stack-and-hints-at-what-worlds-most-valuable-firm-will-do-next">TechRadar</a>.
      </footer>
    </div>
  </main>

  <script id="valueChainData" type="application/json">__DATA_JSON__</script>
  <script>
    const data = JSON.parse(document.getElementById("valueChainData").textContent);
    const state = {
      selectedTicker: data.tickers[0]?.ticker || "",
      search: "",
      decision: "all",
      source: "all",
      layer: "all",
    };

    const layerById = Object.fromEntries(data.layers.map((layer) => [layer.id, layer]));
    const tickerBySymbol = Object.fromEntries(data.tickers.map((ticker) => [ticker.ticker, ticker]));

    const el = {
      frameworkSummary: document.getElementById("frameworkSummary"),
      summaryStrip: document.getElementById("summaryStrip"),
      cake: document.getElementById("cake"),
      inspector: document.getElementById("inspector"),
      rows: document.getElementById("tickerRows"),
      search: document.getElementById("searchInput"),
      decision: document.getElementById("decisionFilter"),
      source: document.getElementById("sourceFilter"),
      layer: document.getElementById("layerFilter"),
      update: document.getElementById("updateButton"),
      updateStatus: document.getElementById("updateStatus"),
      reset: document.getElementById("resetButton"),
    };

    function cleanLabel(value) {
      return (value || "unclassified").replaceAll("_", " ");
    }

    function shortSource(value) {
      if (value === "sa_reported_current_13f") return "SA 13F";
      if (value === "sa_post_quarter_13g") return "SA 13G";
      if (value === "sa_adjacent_historical_or_thesis_proxy") return "Adjacent historical";
      if (value === "sa_adjacent_thesis_proxy") return "Adjacent proxy";
      return cleanLabel(value);
    }

    function matchesFilters(ticker) {
      const haystack = [
        ticker.ticker,
        ticker.name,
        ticker.sleeve,
        ticker.layer_role,
        ticker.current_decision,
        ticker.source_classification,
      ].join(" ").toLowerCase();
      return (
        (!state.search || haystack.includes(state.search.toLowerCase())) &&
        (state.decision === "all" || ticker.current_decision === state.decision) &&
        (state.source === "all" || ticker.source_classification === state.source) &&
        (state.layer === "all" || ticker.layer_id === state.layer)
      );
    }

    function visibleTickers() {
      return data.tickers.filter(matchesFilters);
    }

    function setOptions(select, values, label) {
      select.innerHTML = "";
      select.append(new Option(label, "all"));
      values.forEach((value) => select.append(new Option(cleanLabel(value), value)));
    }

    function initControls() {
      const decisions = [...new Set(data.tickers.map((ticker) => ticker.current_decision))].sort();
      const sources = [...new Set(data.tickers.map((ticker) => ticker.source_classification))].sort();
      setOptions(el.decision, decisions, "All decisions");
      setOptions(el.source, sources, "All sources");
      el.layer.innerHTML = "";
      el.layer.append(new Option("All layers", "all"));
      data.layers.forEach((layer) => el.layer.append(new Option(layer.name, layer.id)));
      el.search.addEventListener("input", (event) => {
        state.search = event.target.value.trim();
        render();
      });
      el.decision.addEventListener("change", (event) => {
        state.decision = event.target.value;
        render();
      });
      el.source.addEventListener("change", (event) => {
        state.source = event.target.value;
        render();
      });
      el.layer.addEventListener("change", (event) => {
        state.layer = event.target.value;
        render();
      });
      el.reset.addEventListener("click", () => {
        state.search = "";
        state.decision = "all";
        state.source = "all";
        state.layer = "all";
        el.search.value = "";
        el.decision.value = "all";
        el.source.value = "all";
        el.layer.value = "all";
        render();
      });
      el.update.addEventListener("click", updateVisualizer);
    }

    function renderSummary() {
      const visible = visibleTickers();
      const current13f = visible.filter((ticker) => ticker.source_classification === "sa_reported_current_13f").length;
      const signalOnly = visible.filter((ticker) => ticker.trade_policy === "signal_only_no_puts_or_shorts").length;
      const researchFirst = visible.filter((ticker) => ticker.dip_decision === "RESEARCH_FIRST").length;
      const layerCount = new Set(visible.map((ticker) => ticker.layer_id)).size;
      const metrics = [
        ["Visible tickers", visible.length],
        ["Layers occupied", `${layerCount} / 5`],
        ["Current SA 13F", current13f],
        ["Signal-only", signalOnly],
        ["Research-first dips", researchFirst],
      ];
      el.summaryStrip.innerHTML = metrics.map(([label, value]) => `
        <article class="metric"><span>${label}</span><strong>${value}</strong></article>
      `).join("");
    }

    function renderCake() {
      const visible = new Set(visibleTickers().map((ticker) => ticker.ticker));
      el.cake.innerHTML = data.layers.map((layer) => {
        const layerTickers = layer.tickers.filter((ticker) => visible.has(ticker.ticker));
        const bySleeve = Object.groupBy ? Object.groupBy(layerTickers, (ticker) => ticker.sleeve) : groupBy(layerTickers, (ticker) => ticker.sleeve);
        const sleeveMarkup = Object.entries(bySleeve).sort(([a], [b]) => a.localeCompare(b)).map(([sleeve, tickers]) => `
          <section class="sleeve-group">
            <div class="sleeve-title">
              <span>${cleanLabel(sleeve)}</span>
              <code>${tickers.length} ${tickers.length === 1 ? "ticker" : "tickers"}</code>
            </div>
            <div class="cards">
              ${tickers.map((ticker) => tickerCard(ticker, layer)).join("")}
            </div>
          </section>
        `).join("");
        const emptyMarkup = layerTickers.length
          ? ""
          : `<div class="empty-layer">${layer.empty_note || "No tracked ticker matches the active filters in this layer."}</div>`;
        const display = state.layer !== "all" && state.layer !== layer.id ? "display:none" : "";
        return `
          <article class="layer" style="--layer-color: ${layer.color}; ${display}" data-layer="${layer.id}">
            <div class="layer-meta">
              <div class="layer-kicker"><span class="layer-dot"></span>Layer ${layer.order}</div>
              <h2>${layer.name}</h2>
              <p>${layer.headline}</p>
              <p>${layer.description}</p>
              <div class="layer-question">${layer.watch_question}</div>
            </div>
            <div class="ticker-zone">${sleeveMarkup}${emptyMarkup}</div>
          </article>
        `;
      }).join("");
      el.cake.querySelectorAll("[data-ticker]").forEach((button) => {
        button.addEventListener("click", () => {
          state.selectedTicker = button.dataset.ticker;
          render();
        });
      });
    }

    function tickerCard(ticker, layer) {
      const selected = ticker.ticker === state.selectedTicker ? " selected" : "";
      const signal = ticker.trade_policy === "signal_only_no_puts_or_shorts" ? `<span class="tag signal">signal</span>` : "";
      const confidence = ticker.confidence_score ? `<span class="tag">${ticker.confidence_score}</span>` : "";
      return `
        <button class="ticker-card${selected}" type="button" data-ticker="${ticker.ticker}" style="--layer-color: ${layer.color}">
          <span class="ticker-top">
            <span class="ticker-symbol">${ticker.ticker}</span>
            <span class="tag decision-${ticker.current_decision}">${ticker.current_decision}</span>
          </span>
          <span class="ticker-name">${ticker.name}</span>
          <span class="ticker-tags">
            <span class="tag">${shortSource(ticker.source_classification)}</span>
            ${signal}
            ${confidence}
          </span>
        </button>
      `;
    }

    function renderRows() {
      const visible = visibleTickers().sort((a, b) => a.layer_id.localeCompare(b.layer_id) || a.sleeve.localeCompare(b.sleeve) || a.ticker.localeCompare(b.ticker));
      el.rows.innerHTML = visible.map((ticker) => {
        const layer = layerById[ticker.layer_id];
        return `
          <tr data-ticker="${ticker.ticker}">
            <td><strong>${ticker.ticker}</strong></td>
            <td>${ticker.name}</td>
            <td>${layer.name}</td>
            <td><code>${ticker.sleeve}</code></td>
            <td>${ticker.current_decision}</td>
            <td>${shortSource(ticker.source_classification)}</td>
            <td>${ticker.layer_role}</td>
          </tr>
        `;
      }).join("");
      el.rows.querySelectorAll("[data-ticker]").forEach((row) => {
        row.addEventListener("click", () => {
          state.selectedTicker = row.dataset.ticker;
          render();
          window.scrollTo({ top: 0, behavior: "smooth" });
        });
      });
    }

    function renderInspector() {
      const selected = tickerBySymbol[state.selectedTicker] || visibleTickers()[0] || data.tickers[0];
      if (!selected) {
        el.inspector.innerHTML = "<p>No ticker selected.</p>";
        return;
      }
      state.selectedTicker = selected.ticker;
      const layer = layerById[selected.layer_id];
      const bridges = selected.bridge_to.length
        ? selected.bridge_to.map((id) => layerById[id]?.name || id).join(", ")
        : "None";
      el.inspector.innerHTML = `
        <div class="inspector-header">
          <div>
            <h2>${selected.ticker}</h2>
            <p class="name">${selected.name}</p>
          </div>
          <span class="decision-pill ${selected.current_decision}">${selected.current_decision}</span>
        </div>
        <div class="detail-grid">
          ${detail("Layer", layer.name)}
          ${detail("Sleeve", selected.sleeve)}
          ${detail("Source", shortSource(selected.source_classification))}
          ${detail("Policy", selected.trade_policy || "unclassified")}
          ${detail("Dip", selected.dip_decision || "unclassified")}
          ${detail("Confidence", selected.confidence_score || "unscored")}
          ${detail("Role", selected.layer_role)}
          ${detail("Bridge", bridges)}
        </div>
        <div class="narrative">
          ${copySection("Rationale", selected.one_line_rationale)}
          ${copySection("Thesis Expressed", selected.thesis_expressed)}
          ${copySection("Anti-thesis", selected.anti_thesis)}
          ${copySection("Sizing / Hedge Response", selected.hedge_or_sizing)}
          ${copySection("Invalidation Trigger", selected.invalidation_trigger)}
          ${copySection("Next Trigger", selected.next_trigger)}
        </div>
      `;
    }

    function detail(label, value) {
      return `<div class="detail"><span>${label}</span><strong>${value || "n/a"}</strong></div>`;
    }

    function copySection(label, value) {
      return `<section><h3>${label}</h3><p>${value || "Not specified."}</p></section>`;
    }

    function groupBy(items, getKey) {
      return items.reduce((acc, item) => {
        const key = getKey(item);
        acc[key] = acc[key] || [];
        acc[key].push(item);
        return acc;
      }, {});
    }

    function setUpdateStatus(message, isError = false) {
      el.updateStatus.textContent = message;
      el.updateStatus.classList.toggle("error", isError);
    }

    async function updateVisualizer() {
      el.update.disabled = true;
      setUpdateStatus("Updating visualizer...");
      try {
        if (window.location.protocol === "file:") {
          throw new Error("file_mode");
        }
        const response = await fetch("/__bcap_update", {
          method: "POST",
          headers: { "Accept": "application/json" },
        });
        if (!response.ok) {
          const text = await response.text();
          throw new Error(text || `HTTP ${response.status}`);
        }
        setUpdateStatus("Updated. Reloading...");
        window.location.reload();
      } catch (error) {
        const fileMode = error && error.message === "file_mode";
        setUpdateStatus(
          fileMode
            ? "One-click update needs local server mode: ./bcap value-chain --serve. For this file, run ./bcap value-chain, then refresh."
            : "Update failed. Run ./bcap value-chain in the terminal, then refresh.",
          true,
        );
        el.update.disabled = false;
      }
    }

    function render() {
      el.frameworkSummary.textContent = `${data.source.framework}: ${data.source.layers}. Generated ${new Date(data.generated_at).toLocaleString()}.`;
      renderSummary();
      renderCake();
      renderRows();
      renderInspector();
    }

    initControls();
    render();
  </script>
</body>
</html>
"""
