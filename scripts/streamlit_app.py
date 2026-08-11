"""Runtime dashboard for the Day 13 observability lab."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml


ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "data" / "logs.jsonl"
DASHBOARD_FILE = ROOT / "config" / "dashboard.yaml"
SLO_FILE = ROOT / "config" / "slo.yaml"

st.set_page_config(page_title="Day 13 AI Observability", page_icon="🔭", layout="wide")


@st.cache_data(ttl=30)
def load_logs() -> pd.DataFrame:
    if not LOG_FILE.exists():
        return pd.DataFrame()
    records = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(records)


@st.cache_data(ttl=30)
def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def metric_status(value: float, operator: str, threshold: float) -> str:
    passed = value <= threshold if operator == "lte" else value >= threshold
    return "PASS" if passed else "BREACH"


def status_delta(status: str) -> tuple[str, str]:
    return ("✅ PASS", "normal") if status == "PASS" else ("🚨 BREACH", "inverse")


def detect_pii(frame: pd.DataFrame) -> int:
    detectors = [
        r"[\w.-]+@[\w.-]+\.\w+",
        r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
        r"\b\d{12}\b",
        r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    ]
    hits = 0
    for record in frame.to_dict(orient="records"):
        # ``ts`` is a pandas.Timestamp after dataframe normalization.
        # ``default=str`` keeps the independent PII scan read-only and
        # supports pandas/numpy scalar values without changing the log data.
        raw = json.dumps(record, ensure_ascii=False, default=str)
        if any(re.search(pattern, raw) for pattern in detectors):
            hits += 1
    return hits


def number(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(frame.get(column, pd.Series(dtype=float)), errors="coerce")


df = load_logs()
st.title("🔭 Day 13 — AI Observability")
st.caption("Metrics → Traces → Logs → Root cause | Nguồn chuẩn: data/logs.jsonl")

if df.empty:
    st.error("Không tìm thấy log hợp lệ. Hãy chạy API và scripts/load_test.py trước.")
    st.stop()

df["ts"] = pd.to_datetime(df["ts"], errors="coerce", utc=True)
df = df.dropna(subset=["ts"]).sort_values("ts")

with st.sidebar:
    st.header("Bộ lọc")
    window = st.slider("Khoảng thời gian (phút)", 15, 60, 60, step=15)
    features = sorted(str(value) for value in df.get("feature", pd.Series()).dropna().unique())
    selected_features = st.multiselect("Feature", features, default=features)
    if st.button("🔄 Làm mới dữ liệu"):
        load_logs.clear()
        st.rerun()
    st.divider()
    st.caption(f"Refresh dữ liệu: 30 giây")
    st.caption(f"File: {LOG_FILE.relative_to(ROOT)}")

latest = df["ts"].max()
filtered = df[df["ts"] >= latest - pd.Timedelta(minutes=window)].copy()
if selected_features and "feature" in filtered:
    filtered = filtered[filtered["feature"].astype(str).isin(selected_features)]

responses = filtered[filtered["event"] == "response_sent"].copy()
requests = filtered[filtered["event"] == "request_received"].copy()
failures = filtered[filtered["event"] == "request_failed"].copy()
latency = number(responses, "latency_ms").dropna()
quality = number(responses, "quality_score").dropna()
cost = number(responses, "cost_usd").dropna()

dashboard = load_config(DASHBOARD_FILE).get("dashboard", {})
panels = {panel["id"]: panel for panel in dashboard.get("panels", [])}

st.subheader("Tổng quan hệ thống")
total_requests = len(requests)
success_rate = ((total_requests - len(failures)) / total_requests * 100) if total_requests else 0
unique_cids = filtered.get("correlation_id", pd.Series()).dropna().nunique()
unique_sessions = filtered.get("session_id", pd.Series()).dropna().nunique()
overview = st.columns(5)
overview[0].metric("Requests", f"{total_requests:,}")
overview[1].metric("Success rate", f"{success_rate:.1f}%")
overview[2].metric("Correlation IDs", f"{unique_cids:,}")
overview[3].metric("Sessions", f"{unique_sessions:,}")
overview[4].metric("PII leaks", f"{detect_pii(filtered)}", help="Independent regex scan of visible log records")

st.subheader("SLO và trạng thái cảnh báo")
if latency.size:
    p95 = float(latency.quantile(0.95))
else:
    p95 = 0.0
error_rate = len(failures) / total_requests * 100 if total_requests else 0.0
total_cost = float(cost.sum()) if cost.size else 0.0
quality_avg = float(quality.mean()) if quality.size else 0.0
slo_rows = [
    {"SLI": "Latency p95", "Current": f"{p95:.1f} ms", "Objective": "≤ 3000 ms", "Status": metric_status(p95, "lte", 3000)},
    {"SLI": "Error rate", "Current": f"{error_rate:.2f}%", "Objective": "≤ 2%", "Status": metric_status(error_rate, "lte", 2)},
    {"SLI": "Daily cost", "Current": f"${total_cost:.4f}", "Objective": "≤ $2.50", "Status": metric_status(total_cost, "lte", 2.5)},
    {"SLI": "Quality proxy", "Current": f"{quality_avg:.2f}", "Objective": "≥ 0.75", "Status": metric_status(quality_avg, "gte", 0.75)},
]
st.dataframe(pd.DataFrame(slo_rows), use_container_width=True, hide_index=True)

incident_events = filtered[filtered["event"].isin(["incident_enabled", "incident_disabled"])]
challenge_rows = filtered[filtered.get("session_id", pd.Series(dtype=str)).astype(str).str.startswith("k4-challenge-")]
col_incident, col_prompt, col_challenge = st.columns(3)
with col_incident:
    st.markdown("**Incident state**")
    if incident_events.empty:
        st.success("Không có incident control event trong cửa sổ này")
    else:
        st.warning(incident_events.iloc[-1].get("event", "unknown"))
        st.caption(str(incident_events.iloc[-1].get("payload", {})))
with col_prompt:
    st.markdown("**Prompt / tracing**")
    prompt_rows = responses[[column for column in ["prompt_name", "prompt_label", "prompt_version", "prompt_source"] if column in responses]].drop_duplicates()
    if prompt_rows.empty:
        st.info("Chưa có prompt metadata")
    else:
        st.dataframe(prompt_rows, use_container_width=True, hide_index=True)
with col_challenge:
    st.markdown("**Official challenge**")
    st.metric("Challenge requests", len(challenge_rows))
    if not challenge_rows.empty:
        st.caption("Feature: monitoring | Incident: rag_slow")

st.subheader("6 panel chỉ số chính")
col1, col2, col3 = st.columns(3)
with col1:
    panel = panels.get("latency", {})
    st.markdown(f"**1. Latency percentiles** · threshold p95 ≤ {panel.get('threshold', {}).get('value', 3000)}ms")
    if latency.size:
        st.metric("P95", f"{p95:.1f} ms", delta=status_delta(metric_status(p95, "lte", 3000))[0], delta_color=status_delta(metric_status(p95, "lte", 3000))[1])
        st.write(f"P50: {latency.quantile(.50):.1f}ms · P99: {latency.quantile(.99):.1f}ms")
        st.line_chart(responses.set_index("ts")["latency_ms"])
with col2:
    st.markdown("**2. Request traffic** · threshold ≥ 1 req/min")
    span = (requests["ts"].max() - requests["ts"].min()).total_seconds() / 60 if len(requests) > 1 else 0
    rpm = len(requests) / max(span, 1)
    st.metric("Rate", f"{rpm:.2f} req/min", delta="✅ PASS" if rpm >= 1 else "🚨 BREACH", delta_color="normal" if rpm >= 1 else "inverse")
    if not requests.empty:
        st.line_chart(requests.set_index("ts").resample("1min").size())
with col3:
    st.markdown("**3. Error rate & breakdown** · threshold ≤ 2%")
    st.metric("Error rate", f"{error_rate:.2f}%", delta="✅ PASS" if error_rate <= 2 else "🚨 BREACH", delta_color="normal" if error_rate <= 2 else "inverse")
    if not failures.empty and "error_type" in failures:
        st.bar_chart(failures["error_type"].value_counts())
    else:
        st.caption("Không có request_failed")

col4, col5, col6 = st.columns(3)
with col4:
    st.markdown("**4. Cost over time** · threshold ≤ $2.50")
    st.metric("Total cost", f"${total_cost:.4f}", delta="✅ PASS" if total_cost <= 2.5 else "🚨 BREACH", delta_color="normal" if total_cost <= 2.5 else "inverse")
    if not cost.empty:
        st.line_chart(responses.set_index("ts")["cost_usd"].resample("1min").sum())
with col5:
    st.markdown("**5. Input/output tokens** · threshold ≤ 50,000")
    tokens_in = number(responses, "tokens_in").sum()
    tokens_out = number(responses, "tokens_out").sum()
    st.metric("Total tokens", f"{tokens_in + tokens_out:,.0f}", delta="✅ PASS" if tokens_in + tokens_out <= 50000 else "🚨 BREACH", delta_color="normal" if tokens_in + tokens_out <= 50000 else "inverse")
    st.write(f"Input: {tokens_in:,.0f} · Output: {tokens_out:,.0f}")
    if not responses.empty:
        st.bar_chart(responses.set_index("ts")[["tokens_in", "tokens_out"]].resample("1min").sum())
with col6:
    st.markdown("**6. Quality proxy** · threshold ≥ 0.75")
    st.metric("Mean quality", f"{quality_avg:.2f}", delta="✅ PASS" if quality_avg >= .75 else "🚨 BREACH", delta_color="normal" if quality_avg >= .75 else "inverse")
    if not quality.empty:
        st.line_chart(responses.set_index("ts")["quality_score"].resample("1min").mean())

st.subheader("Recent requests — mở trace rồi đối chiếu log")
recent_columns = [
    "ts", "event", "correlation_id", "session_id", "feature", "latency_ms",
    "quality_score", "prompt_version", "prompt_source", "error_type",
]
available = [column for column in recent_columns if column in filtered.columns]
recent = filtered.sort_values("ts", ascending=False)[available].head(25).copy()
if "ts" in recent:
    recent["ts"] = recent["ts"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
st.dataframe(recent, use_container_width=True, hide_index=True)

with st.expander("Hướng dẫn điều tra nhanh", expanded=False):
    st.markdown(
        "1. Chọn khoảng thời gian có SLO **BREACH**.  \n"
        "2. Lọc feature hoặc session liên quan.  \n"
        "3. Lấy `correlation_id` từ bảng Recent requests.  \n"
        "4. Mở trace tương ứng trên Langfuse, kiểm tra prompt version, generation latency và token/cost.  \n"
        "5. Đối chiếu lại `data/logs.jsonl` để kết luận root cause."
    )
