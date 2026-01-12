import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Finance Handler", layout="wide")

st.title("💼 AI Finance Handler")
st.caption("AI-powered financial analyst & decision assistant")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📂 Data Upload")
uploaded_files = st.sidebar.file_uploader(
    "Upload Excel files",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

st.sidebar.divider()
st.sidebar.header("🧠 AI Command Center")

# ---------------- HELPERS ----------------
def merge_excels(files):
    dfs = []
    for f in files:
        df = pd.read_excel(f)
        df["source"] = f.name
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def detect_date_column(df):
    for c in df.columns:
        if "date" in c.lower():
            return c
    return None

def detect_category_column(df):
    for c in df.columns:
        if c.lower() in ["category", "type", "expense_category"]:
            return c
    return None

def financial_health_scores(df, numeric_cols):
    return {
        "Revenue Stability": min(100, int(100 - df[numeric_cols].std().mean() / 1000)),
        "Cost Efficiency": min(100, int(100 - df[numeric_cols].mean().mean() / 2000)),
        "Cashflow Health": np.random.randint(65, 90),
        "Churn Risk": np.random.randint(40, 70)
    }

def generate_suggested_queries(anomalies_found):
    base = [
        "Is revenue growth slowing?",
        "How healthy is our cashflow?",
        "What should management focus on next quarter?"
    ]
    if anomalies_found:
        base.insert(0, "Why were unusual expense spikes detected?")
    return base

def mock_llm_answer(question, anomalies_summary):
    response = f"""
**Question:** {question}

**AI Analysis:**
Based on detected financial trends and anomalies, this issue is driven by
cost volatility, seasonal effects, and operational inefficiencies.
"""
    if anomalies_summary:
        response += f"\n**Detected Anomalies:**\n{anomalies_summary}\n"

    response += "\n**Recommendation:** Review flagged categories and rebalance spending."
    return response

def detect_anomalies(df, category_col, value_col):
    anomalies = []
    grouped = df.groupby(category_col)[value_col]

    stats = grouped.agg(["mean", "std"]).reset_index()

    merged = df.merge(stats, on=category_col)

    for _, row in merged.iterrows():
        if row["std"] > 0 and abs(row[value_col] - row["mean"]) > 2 * row["std"]:
            anomalies.append({
                "Category": row[category_col],
                "Value": row[value_col],
                "Mean": round(row["mean"], 2),
                "Deviation": round(row[value_col] / row["mean"], 2)
            })

    return pd.DataFrame(anomalies)

# ---------------- MAIN ----------------
if not uploaded_files:
    st.info("👈 Upload Excel files to begin analysis")
    st.stop()

df = merge_excels(uploaded_files)
numeric_cols = df.select_dtypes(include=np.number).columns
date_col = detect_date_column(df)
category_col = detect_category_column(df)

# ---------------- DASHBOARD KPIs ----------------
st.subheader("📊 Financial Health Overview")
scores = financial_health_scores(df, numeric_cols)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue Stability", f"{scores['Revenue Stability']}%")
c2.metric("Cost Efficiency", f"{scores['Cost Efficiency']}%")
c3.metric("Cashflow Health", f"{scores['Cashflow Health']}%")
c4.metric("Churn Risk", f"{scores['Churn Risk']}%", delta="-5%")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Overview", "🔮 Forecast", "🧠 AI Insights", "💬 Ask AI"]
)

# ---------------- TAB 1: OVERVIEW ----------------
with tab1:
    if date_col and len(numeric_cols):
        metric = st.selectbox("Select Metric", numeric_cols)
        df[date_col] = pd.to_datetime(df[date_col])
        df_sorted = df.sort_values(date_col)

        fig = px.line(df_sorted, x=date_col, y=metric, markers=True)
        st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2: FORECAST (BUG FIXED) ----------------
with tab2:
    if date_col and len(numeric_cols):
        series = df_sorted[metric].rolling(3).mean().dropna()

        if len(series) < 1:
            st.warning("Not enough data to generate forecast.")
        else:
            last_val = series.iloc[-1]
            future_vals = [last_val * (1 + 0.02 * i) for i in range(1, 7)]
            future_dates = [
                df_sorted[date_col].max() + timedelta(days=30 * i)
                for i in range(1, 7)
            ]

            forecast_df = pd.DataFrame({
                "Date": future_dates,
                "Forecast": future_vals
            })

            fig = px.line(forecast_df, x="Date", y="Forecast", markers=True)
            st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 3: AI INSIGHTS (ANOMALY DETECTION) ----------------
with tab3:
    st.subheader("🔍 Detected Anomalies")

    anomalies_df = pd.DataFrame()
    if category_col and len(numeric_cols):
        anomalies_df = detect_anomalies(df, category_col, numeric_cols[0])

        if not anomalies_df.empty:
            st.error("⚠️ Financial anomalies detected")
            st.dataframe(anomalies_df, use_container_width=True)
        else:
            st.success("No significant anomalies detected")

# ---------------- TAB 4: ASK AI ----------------
with tab4:
    anomalies_summary = ""
    if not anomalies_df.empty:
        anomalies_summary = anomalies_df.head(3).to_string(index=False)

    suggested_queries = generate_suggested_queries(not anomalies_df.empty)

    st.sidebar.subheader("💡 Suggested Questions")
    for q in suggested_queries:
        if st.sidebar.button(q):
            st.markdown(mock_llm_answer(q, anomalies_summary))

    user_query = st.text_input("Ask a custom financial question")
    if user_query:
        st.markdown(mock_llm_answer(user_query, anomalies_summary))
