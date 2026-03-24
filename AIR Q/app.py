import os
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db_handler import get_history

st.set_page_config(
    page_title="IoT Air Quality Monitor",
    page_icon="🌬️",
    layout="wide"
)

# ── Load ML model (cached) ────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        model_path = os.path.join(os.path.dirname(__file__), "air_quality_model.pkl")
        with open(model_path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None

ml_model = load_model()

# ── AQI formula (mirrors api_server.py) ──────────────────────────────────────
def compute_aqi(gas_raw, humidity, temperature):
    gas_norm = (gas_raw / 1023.0) * 100.0
    return round((0.6 * gas_norm) + (0.25 * humidity) + (0.15 * temperature), 2)

def aqi_to_category(aqi):
    if aqi <= 50:    return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Poor"
    elif aqi <= 200: return "Very Poor"
    else:            return "Hazardous"

def category_style(cat):
    return {
        "Good":      ("🟢", "#2ecc71"),
        "Moderate":  ("🟡", "#f1c40f"),
        "Poor":      ("🟠", "#e67e22"),
        "Very Poor": ("🔴", "#e74c3c"),
        "Hazardous": ("⚫", "#8e44ad"),
    }.get(cat, ("⚪", "#95a5a6"))

# ── Chart ─────────────────────────────────────────────────────────────────────
def build_chart(df):
    fig = go.Figure()
    if "aqi_score" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["aqi_score"],
            mode="lines+markers", name="AQI Score",
            line=dict(color="#FFE66D", width=3),
            fill="tozeroy", fillcolor="rgba(255,230,109,0.1)"
        ))
    if "temperature" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["temperature"],
            mode="lines+markers", name="Temp (°C)",
            line=dict(color="#FF6B6B", width=2)
        ))
    if "humidity" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["humidity"],
            mode="lines+markers", name="Humidity (%)",
            line=dict(color="#4ECDC4", width=2)
        ))
    if "gas_raw" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["gas_raw"],
            mode="lines+markers", name="MQ-2 Raw",
            line=dict(color="#A8E6CF", width=2),
            yaxis="y2"
        ))
    fig.update_layout(
        title="Sensor Readings & AQI Over Time",
        xaxis_title="Timestamp",
        yaxis=dict(title="AQI / Temp (°C) / Humidity (%)", side="left", rangemode="tozero"),
        yaxis2=dict(title="MQ-2 Raw (0–1023)", side="right",
                    overlaying="y", showgrid=False, range=[0, 1023]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        hovermode="x unified",
        height=420
    )
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
refresh_rate  = 5   # auto-refresh every 5 seconds
history_limit = 30  # show last 30 readings

st.sidebar.header("📊 AQI Categories")
st.sidebar.markdown(
    "| AQI Range | Category |\n"
    "|---|---|\n"
    "| 0 – 50 | 🟢 Good |\n"
    "| 51 – 100 | 🟡 Moderate |\n"
    "| 101 – 150 | 🟠 Poor |\n"
    "| 151 – 200 | 🔴 Very Poor |\n"
    "| 200+ | ⚫ Hazardous |"
)
# ── Page header ───────────────────────────────────────────────────────────────
st.title("🌬️ IoT Air Quality Monitor")
st.markdown("---")

# ── Real-time fragment ────────────────────────────────────────────────────────
@st.fragment(run_every=refresh_rate)
def live_stream():
    history = get_history(history_limit)

    if not history:
        st.warning(
            "⚠️ No data in MongoDB yet.\n\n"
            "Make sure:\n"
            "1. `api_server.py` is running\n"
            "2. The ESP32 is powered and connected to Wi-Fi\n"
            "3. The ESP32 firmware is POSTing to `http://10.245.201.34:5000/api/data`"
        )
        return

    df = pd.DataFrame(history)
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

    # Compute AQI score for every row (frontend formula matches backend)
    if "gas_raw" in df.columns:
        df["aqi_score"] = df.apply(
            lambda r: compute_aqi(r["gas_raw"],
                                  r.get("humidity", 0),
                                  r.get("temperature", 0)),
            axis=1
        )
        df["rule_category"] = df["aqi_score"].apply(aqi_to_category)

    latest   = df.iloc[-1]
    aqi_val  = compute_aqi(
                    latest.get("gas_raw", 0),
                    latest.get("humidity", 0),
                    latest.get("temperature", 0))
    rule_cat = aqi_to_category(aqi_val)
    rule_icon, rule_color = category_style(rule_cat)

    # ── AQI banner ────────────────────────────────────────────────────────────
    st.subheader("📡 Latest Reading")
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {rule_color}33, {rule_color}11);
                    border-left: 5px solid {rule_color};
                    border-radius: 8px; padding: 16px 20px; margin-bottom: 12px;">
            <span style="font-size: 2rem; font-weight: bold; color: {rule_color};">
                {rule_icon} AQI: {aqi_val:.1f}
            </span>
            &nbsp;&nbsp;
            <span style="font-size: 1.3rem; color: white;">— {rule_cat}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Metric cards ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ Temperature",  f"{latest.get('temperature', '?')} °C")
    c2.metric("💧 Humidity",     f"{latest.get('humidity', '?')} %")
    c3.metric("🔥 MQ-2 Raw",     str(latest.get("gas_raw", "?")))
    c4.metric("📐 AQI Score",    f"{aqi_val:.1f}")


    st.markdown("---")

    # ── Chart ─────────────────────────────────────────────────────────────────
    st.subheader("📈 Trend Chart")
    st.plotly_chart(build_chart(df), width="stretch", key="rt_chart")

    # ── Table ─────────────────────────────────────────────────────────────────
    st.subheader("📋 Recent Readings")
    disp_cols = [c for c in
        ["timestamp", "temperature", "humidity", "gas_raw", "aqi_score",
         "rule_category"]
        if c in df.columns]
    st.dataframe(
        df.tail(10)[disp_cols].rename(columns={
            "temperature":   "Temp (°C)",
            "humidity":      "Hum (%)",
            "gas_raw":       "MQ-2 Raw",
            "aqi_score":     "AQI",
            "rule_category": "AQI Category",
        }),
        width="stretch"
    )

    # ── Summary stats ─────────────────────────────────────────────────────────
    st.subheader("📊 Summary Statistics")
    stats_cols = [c for c in ["temperature", "humidity", "gas_raw", "aqi_score"]
                  if c in df.columns]
    if stats_cols:
        st.dataframe(df[stats_cols].describe().round(2), width="stretch")

live_stream()

# ── 10-Step ML Forecast ───────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🔮 ML Forecast — Next 10 Time Periods")
st.caption("Projected using linear trend on MQ-2 gas_raw from recent readings. "
           "Predictions are computed in memory — **not stored in the database**.")

history_for_forecast = get_history(30)   # fetch last 30 for trend fitting

if not history_for_forecast or len(history_for_forecast) < 3:
    st.info("Need at least 3 readings in MongoDB to generate a forecast.")
else:
    fdf = pd.DataFrame(history_for_forecast)
    if "_id"       in fdf.columns: fdf = fdf.drop(columns=["_id"])
    if "timestamp" in fdf.columns:
        fdf["timestamp"] = pd.to_datetime(fdf["timestamp"])
        fdf = fdf.sort_values("timestamp").reset_index(drop=True)

    # Infer average sampling interval
    if len(fdf) >= 2:
        deltas   = fdf["timestamp"].diff().dropna()
        avg_interval = deltas.median()
    else:
        avg_interval = timedelta(seconds=5)

    # Linear trend on gas_raw
    x = np.arange(len(fdf))
    y = fdf["gas_raw"].values.astype(float)
    coeffs = np.polyfit(x, y, 1)        # slope, intercept
    slope, intercept = coeffs

    # Recent averages for temp & humidity (assumed stable)
    avg_temp = float(fdf["temperature"].mean()) if "temperature" in fdf.columns else 30.0
    avg_hum  = float(fdf["humidity"].mean())    if "humidity"    in fdf.columns else 50.0

    last_ts  = fdf["timestamp"].iloc[-1]
    last_idx = len(fdf) - 1

    forecast_rows = []
    for i in range(1, 11):
        future_idx  = last_idx + i
        future_gas  = float(np.clip(slope * future_idx + intercept, 0, 1023))
        future_ts   = last_ts + avg_interval * i
        future_aqi  = compute_aqi(future_gas, avg_hum, avg_temp)
        future_cat  = aqi_to_category(future_aqi)
        icon, _     = category_style(future_cat)

        forecast_rows.append({
            "Forecast Time":  future_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Projected MQ-2": int(round(future_gas)),
            "Projected AQI":  round(future_aqi, 1),
            "Prediction":     f"{icon} {future_cat}",
        })

    forecast_df = pd.DataFrame(forecast_rows)
    st.dataframe(forecast_df, width="stretch", hide_index=True)

    # ── Forecast chart ────────────────────────────────────────────────────────
    fig_fc = go.Figure()

    # Historical AQI (actual)
    hist_aqi = [compute_aqi(g, avg_hum, avg_temp) for g in fdf["gas_raw"]]
    fig_fc.add_trace(go.Scatter(
        x=fdf["timestamp"], y=hist_aqi,
        mode="lines+markers", name="Historical AQI",
        line=dict(color="#4ECDC4", width=2)
    ))

    # Forecasted AQI
    fig_fc.add_trace(go.Scatter(
        x=pd.to_datetime(forecast_df["Forecast Time"]),
        y=forecast_df["Projected AQI"],
        mode="lines+markers", name="Forecasted AQI",
        line=dict(color="#FFE66D", width=2, dash="dash"),
        marker=dict(symbol="diamond", size=9)
    ))

    # AQI tier reference lines
    for level, label, color in [
        (50,  "Good / Moderate",   "#2ecc71"),
        (100, "Moderate / Poor",   "#f1c40f"),
        (150, "Poor / Very Poor",  "#e67e22"),
        (200, "Very Poor / Hazardous", "#e74c3c"),
    ]:
        fig_fc.add_hline(y=level, line_dash="dot", line_color=color,
                         annotation_text=label, annotation_position="right")

    fig_fc.update_layout(
        title="AQI — Historical vs Forecast (next 10 periods)",
        xaxis_title="Time",
        yaxis=dict(title="AQI Score", rangemode="tozero"),
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        hovermode="x unified",
        height=380
    )
    st.plotly_chart(fig_fc, width="stretch")
