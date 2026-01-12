import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import json
from datetime import timedelta

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Finance Handler",
    layout="wide"
)

st.title("💰 AI Finance Handler")
st.caption("Upload • Analyze • Forecast • Decide")

# ---------------- FILE UPLOAD ----------------
st.sidebar.header("📂 Upload Financial Files")

uploaded_files = st.sidebar.file_uploader(
    "Upload Excel files",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

# ---------------- HELPERS ----------------
def merge_excels(files):
    dfs = []
    for f in files:
        df = pd.read_excel(f)
        df["source_file"] = f.name
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def detect_date_column(df):
    for col in df.columns:
        if "date" in col.lower():
            return col
    return None

def chunk_dataframe(df, chunk_size=200):
    return [df.iloc[i:i+chunk_size] for i in range(0, len(df), chunk_size)]

def mock_llm(summary):
    return {
        "company_profile": "The data suggests a subscription-based cybersecurity software company.",
        "insights": [
            "Revenue growth slowing quarter-over-quarter",
            "Operating expenses increasing faster than revenue",
            "Customer churn risk emerging"
        ],
        "discrepancies": [
            "Irregular expense spikes detected",
            "Duplicate invoice identifiers found"
        ],
        "actions": [
            "Rebalance operational spending",
            "Investigate churn causes",
            "Improve renewal pricing strategy"
        ]
    }

def simple_forecast(series, periods=6):
    trend = series.rolling(3).mean()
    last_val = trend.dropna().iloc[-1]
    return [last_val + i*(last_val*0.02) for i in range(1, periods+1)]

# ---------------- MAIN ----------------
if uploaded_files:
    df = merge_excels(uploaded_files)

    st.subheader("📊 Consolidated Financial Data")
    st.dataframe(df, use_container_width=True)

    date_col = detect_date_column(df)
    numeric_cols = df.select_dtypes(include=np.number).columns

    # ---------------- VISUALIZATION ----------------
    st.subheader("📈 Financial Simulation")

    if date_col and len(numeric_cols):
        metric = st.selectbox("Select Metric", numeric_cols)
        df[date_col] = pd.to_datetime(df[date_col])
        df_sorted = df.sort_values(date_col)

        fig = px.line(
            df_sorted,
            x=date_col,
            y=metric,
            title=f"{metric} Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---------------- FORECAST ----------------
        st.subheader("🔮 Forecast (Next Periods)")

        forecast_vals = simple_forecast(df_sorted[metric])
        future_dates = [
            df_sorted[date_col].max() + timedelta(days=30*i)
            for i in range(1, len(forecast_vals)+1)
        ]

        forecast_df = pd.DataFrame({
            "Date": future_dates,
            "Forecast": forecast_vals
        })

        forecast_fig = px.line(
            forecast_df,
            x="Date",
            y="Forecast",
            title="Projected Trend"
        )
        st.plotly_chart(forecast_fig, use_container_width=True)

    # ---------------- LLM ANALYSIS ----------------
    st.subheader("🧠 AI Financial Intelligence")

    if st.button("Run LLM Analysis"):
        with st.spinner("Analyzing financial structure & patterns..."):
            summary = {
                "rows": len(df),
                "columns": list(df.columns),
                "stats": df[numeric_cols].describe().to_dict()
            }

            chunks = chunk_dataframe(df)
            llm_response = mock_llm(summary)

        st.subheader("🏢 Company Understanding")
        st.info(llm_response["company_profile"])

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Insights")
            for i in llm_response["insights"]:
                st.write("•", i)

        with col2:
            st.subheader("⚠️ Discrepancies")
            for d in llm_response["discrepancies"]:
                st.write("•", d)

        st.subheader("✅ Recommended Actions")
        for a in llm_response["actions"]:
            st.success(a)

else:
    st.info("👈 Upload Excel files to begin analysis")
