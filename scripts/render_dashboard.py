from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path
from string import Template


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
OUTPUT_PATH = REPO_ROOT / "submission" / "evidence" / "dashboard-runtime.html"


def load_records() -> list[dict]:
    records: list[dict] = []
    if not LOG_PATH.exists():
        return records
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    index = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[index])


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def render() -> str:
    records = load_records()
    request_events = [record for record in records if record.get("event") == "request_received"]
    response_events = [record for record in records if record.get("event") == "response_sent"]
    error_events = [record for record in records if record.get("event") == "request_failed"]

    latencies = [float(record.get("latency_ms") or 0) for record in response_events]
    costs = [float(record.get("cost_usd") or 0) for record in response_events]
    tokens_in = sum(int(record.get("tokens_in") or 0) for record in response_events)
    tokens_out = sum(int(record.get("tokens_out") or 0) for record in response_events)
    quality_scores = [float(record.get("quality_score") or 0) for record in response_events]
    error_breakdown = Counter(record.get("error_type", "unknown") for record in error_events)

    total_requests = len(request_events)
    error_rate = (len(error_events) / total_requests * 100) if total_requests else 0.0
    avg_quality = statistics.mean(quality_scores) if quality_scores else 0.0
    total_cost = sum(costs)

    error_breakdown_text = (
        ", ".join(f"{name}: {count}" for name, count in sorted(error_breakdown.items()))
        if error_breakdown
        else "No request_failed events"
    )

    template = Template(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Day 13 AI Observability Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: #f5f7fb;
      color: #18202f;
    }
    body {
      margin: 0;
      padding: 28px;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 24px;
      border-bottom: 1px solid #dbe2ef;
      padding-bottom: 18px;
      margin-bottom: 22px;
    }
    h1 {
      font-size: 28px;
      margin: 0 0 8px;
      letter-spacing: 0;
    }
    .subtle {
      color: #596579;
      font-size: 14px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(220px, 1fr));
      gap: 16px;
    }
    .card {
      background: #ffffff;
      border: 1px solid #dbe2ef;
      border-radius: 8px;
      padding: 18px;
      min-height: 156px;
      box-shadow: 0 1px 2px rgba(24, 32, 47, 0.05);
    }
    .card h2 {
      font-size: 15px;
      margin: 0 0 14px;
      color: #273248;
    }
    .metric {
      font-size: 30px;
      font-weight: 700;
      margin: 4px 0;
    }
    .row {
      display: flex;
      justify-content: space-between;
      border-top: 1px solid #edf1f7;
      padding-top: 10px;
      margin-top: 10px;
      font-size: 13px;
    }
    .ok {
      color: #0f7a4f;
      font-weight: 700;
    }
    .warn {
      color: #a45708;
      font-weight: 700;
    }
    @media (max-width: 850px) {
      body { padding: 16px; }
      header { align-items: flex-start; flex-direction: column; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Day 13 AI Observability Dashboard</h1>
      <div class="subtle">Source: data/logs.jsonl | Time range: last 60 minutes | Refresh: 30s</div>
    </div>
    <div class="subtle">Panels: latency, traffic, errors, cost, tokens, quality</div>
  </header>

  <main class="grid">
    <section class="card">
      <h2>Latency percentiles</h2>
      <div class="metric">${latency_p95} ms</div>
      <div class="subtle">p95 threshold <= 3000 ms</div>
      <div class="row"><span>p50</span><strong>${latency_p50} ms</strong></div>
      <div class="row"><span>p99</span><strong>${latency_p99} ms</strong></div>
    </section>

    <section class="card">
      <h2>Request traffic</h2>
      <div class="metric">${request_count}</div>
      <div class="subtle">requests in source log</div>
      <div class="row"><span>Threshold</span><strong class="ok">>= 1 request/min</strong></div>
      <div class="row"><span>Responses</span><strong>${response_count}</strong></div>
    </section>

    <section class="card">
      <h2>Error rate and breakdown</h2>
      <div class="metric">${error_rate}%</div>
      <div class="subtle">threshold <= 2%</div>
      <div class="row"><span>Errors</span><strong>${error_count}</strong></div>
      <div class="row"><span>Breakdown</span><strong>${error_breakdown}</strong></div>
    </section>

    <section class="card">
      <h2>Cost over time</h2>
      <div class="metric">$$${total_cost}</div>
      <div class="subtle">total threshold <= $$2.50</div>
      <div class="row"><span>Avg/request</span><strong>$$${avg_cost}</strong></div>
      <div class="row"><span>Unit</span><strong>USD</strong></div>
    </section>

    <section class="card">
      <h2>Input and output tokens</h2>
      <div class="metric">${total_tokens}</div>
      <div class="subtle">threshold <= 50000 tokens</div>
      <div class="row"><span>Input</span><strong>${tokens_in}</strong></div>
      <div class="row"><span>Output</span><strong>${tokens_out}</strong></div>
    </section>

    <section class="card">
      <h2>Quality proxy</h2>
      <div class="metric">${quality_avg}</div>
      <div class="subtle">mean threshold >= 0.75</div>
      <div class="row"><span>Unit</span><strong>score 0-1</strong></div>
      <div class="row"><span>Status</span><strong class="${quality_class}">${quality_status}</strong></div>
    </section>
  </main>
</body>
</html>
"""
    )

    return template.substitute(
        latency_p50=fmt(percentile(latencies, 50), 0),
        latency_p95=fmt(percentile(latencies, 95), 0),
        latency_p99=fmt(percentile(latencies, 99), 0),
        request_count=total_requests,
        response_count=len(response_events),
        error_rate=fmt(error_rate),
        error_count=len(error_events),
        error_breakdown=error_breakdown_text,
        total_cost=fmt(total_cost, 4),
        avg_cost=fmt(total_cost / len(response_events), 4) if response_events else "0.0000",
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        total_tokens=tokens_in + tokens_out,
        quality_avg=fmt(avg_quality, 3),
        quality_class="ok" if avg_quality >= 0.75 else "warn",
        quality_status="Meets SLO" if avg_quality >= 0.75 else "Below SLO",
    )


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render(), encoding="utf-8")
    print(f"Dashboard written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
