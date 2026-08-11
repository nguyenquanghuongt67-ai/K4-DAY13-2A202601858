import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="Day 13 AI Observability", layout="wide")
st.title("Day 13 AI Observability Dashboard")

# Read data
@st.cache_data(ttl=10)
def load_data():
    try:
        with open("data/logs.jsonl", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        data = []
        for line in lines:
            if not line.strip(): continue
            try:
                record = json.loads(line)
                flat_record = {**record, **record.get("payload", {})}
                data.append(flat_record)
            except:
                pass
        df = pd.DataFrame(data)
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"])
            df = df.set_index("ts").sort_index()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data found in data/logs.jsonl")
    st.stop()

# Helper filters
response_sent = df[df["event"] == "response_sent"]
request_received = df[df["event"] == "request_received"]
request_failed = df[df["event"] == "request_failed"]

col1, col2, col3 = st.columns(3)

# 1. Latency
with col1:
    st.subheader("Latency percentiles (ms)")
    if not response_sent.empty and "latency_ms" in response_sent.columns:
        latency = pd.to_numeric(response_sent["latency_ms"], errors="coerce").dropna()
        p50, p95, p99 = latency.quantile([0.5, 0.95, 0.99])
        st.metric("P95 Latency (Threshold: <= 3000ms)", f"{p95:.1f} ms", 
                 delta="High" if p95 > 3000 else "Normal", delta_color="inverse")
        st.write(f"**P50**: {p50:.1f} ms | **P99**: {p99:.1f} ms")
        fig_lat = px.box(response_sent, y="latency_ms", title="Latency Distribution")
        fig_lat.add_hline(y=3000, line_dash="dash", line_color="red", annotation_text="SLO")
        st.plotly_chart(fig_lat, use_container_width=True)

# 2. Traffic
with col2:
    st.subheader("Request traffic")
    if not request_received.empty:
        traffic_per_min = request_received.resample("1Min").size()
        current_rate = traffic_per_min.iloc[-1] if not traffic_per_min.empty else 0
        st.metric("Requests/minute (Threshold: >= 1)", f"{current_rate}", 
                  delta="Low" if current_rate < 1 else "Normal", delta_color="normal")
        traffic_df = traffic_per_min.reset_index()
        traffic_df.columns = ["ts", "count"]
        fig_traffic = px.line(traffic_df, x="ts", y="count", title="Requests per minute")
        st.plotly_chart(fig_traffic, use_container_width=True)

# 3. Errors
with col3:
    st.subheader("Error rate and breakdown")
    total_reqs = len(request_received)
    total_errs = len(request_failed)
    error_rate = (total_errs / total_reqs * 100) if total_reqs > 0 else 0
    st.metric("Error Rate (Threshold: <= 2%)", f"{error_rate:.2f}%", 
              delta="High" if error_rate > 2 else "Normal", delta_color="inverse")
    
    if not request_failed.empty and "error_type" in request_failed.columns:
        error_counts = request_failed["error_type"].value_counts().reset_index()
        # the column name after value_counts().reset_index() could be 'count' or similar
        count_col = 'count' if 'count' in error_counts.columns else error_counts.columns[1]
        fig_err = px.pie(error_counts, values=count_col, names="error_type", title="Error Breakdown")
        st.plotly_chart(fig_err, use_container_width=True)

st.divider()
col4, col5, col6 = st.columns(3)

# 4. Cost
with col4:
    st.subheader("Cost over time (USD)")
    if not response_sent.empty and "cost_usd" in response_sent.columns:
        cost = pd.to_numeric(response_sent["cost_usd"], errors="coerce").dropna()
        total_cost = cost.sum()
        cost_per_min = cost.resample("1Min").sum().reset_index()
        st.metric("Total Cost (Threshold: <= 2.5)", f"${total_cost:.4f}", 
                  delta="High" if total_cost > 2.5 else "Normal", delta_color="inverse")
        fig_cost = px.bar(cost_per_min, x="ts", y="cost_usd", title="Cost per Minute")
        st.plotly_chart(fig_cost, use_container_width=True)

# 5. Tokens
with col5:
    st.subheader("Input and output tokens")
    if not response_sent.empty and "tokens_in" in response_sent.columns and "tokens_out" in response_sent.columns:
        total_tokens_in = pd.to_numeric(response_sent["tokens_in"], errors="coerce").sum()
        total_tokens_out = pd.to_numeric(response_sent["tokens_out"], errors="coerce").sum()
        total_tokens = total_tokens_in + total_tokens_out
        st.metric("Total Tokens (Threshold: <= 50,000)", f"{total_tokens:,.0f}", 
                  delta="High" if total_tokens > 50000 else "Normal", delta_color="inverse")
        token_data = pd.DataFrame({"Type": ["Input", "Output"], "Count": [total_tokens_in, total_tokens_out]})
        fig_tok = px.bar(token_data, x="Type", y="Count", title="Token Usage")
        st.plotly_chart(fig_tok, use_container_width=True)

# 6. Quality
with col6:
    st.subheader("Quality proxy")
    if not response_sent.empty and "quality_score" in response_sent.columns:
        quality = pd.to_numeric(response_sent["quality_score"], errors="coerce").dropna()
        mean_quality = quality.mean()
        st.metric("Mean Quality Score (Threshold: >= 0.75)", f"{mean_quality:.2f}", 
                  delta="Low" if mean_quality < 0.75 else "Normal", delta_color="normal")
        fig_qual = px.histogram(response_sent, x="quality_score", nbins=10, title="Quality Score Distribution")
        fig_qual.add_vline(x=0.75, line_dash="dash", line_color="red", annotation_text="SLO")
        st.plotly_chart(fig_qual, use_container_width=True)
