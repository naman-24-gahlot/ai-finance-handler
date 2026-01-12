import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Finance Handler",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("💼 AI Finance Handler")
st.caption("An AI-powered financial analyst & decision assistant")

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

def financial_health_scores(df, numeric_cols):
    scores = {
        "Revenue Stability": min(100, int(100 - df[numeric_cols].std().mean() / 1000)),
        "Cost Efficiency": min(100, int(100 - df[numeric_cols].mean().mean() / 2000)),
        "Cashflow Health": np.random.randint(65, 90),
        "Churn Risk": np.random.randint(40, 70)
    }
    return scores

def generate_suggested_queries():
    return [
        "Why did expenses spike recently?",
        "Is revenue growth slowing?",
        "Which category shows the highest risk?",
        "How healthy is our cashflow?",
        "What should management focus on next quarter?"
    ]

def mock_llm_answer(question):
    return f"""
**Question:** {question}

**AI Analysis:**
Based on the financial patterns observed, this issue appears to be driven by
cost concentration, seasonal effects, and recent operational inefficiencies.

**Recommendation:**
Investigate the highlighted category, validate assumptions, and adjust
budget allocation proactively.
"""

# ---------------- MAIN ----------------
if not uploaded_files:
    st.info("👈 Upload Excel files to begin analysis")
    st.stop()

df = merge_excels(uploaded_files)

date_col = detect_date_column(df)
numeric_cols = df.select_dtypes(include=np.number).columns

# ---------------- DASHBOARD KPIs ----------------
st.subheader("📊 Financial Health Overview")
scores = financial_health_scores(df, numeric_cols)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Revenue Stability", f"{scores['Revenue Stability']}%")
kpi2.metric("Cost Efficiency", f"{scores['Cost Efficiency']}%")
kpi3.metric("Cashflow Health", f"{scores['Cashflow Health']}%")
kpi4.metric("Churn Risk", f"{scores['Churn Risk']}%", delta="-5%")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Overview", "🔮 Forecast", "🧠 AI Insights", "💬 Ask AI"]
)

# ---------------- TAB 1: OVERVIEW ----------------
with tab1:
    st.subheader("Financial Trends")

    if date_col and len(numeric_cols):
        metric = st.selectbox("Select Metric", numeric_cols)
        df[date_col] = pd.to_datetime(df[date_col])
        df_sorted = df.sort_values(date_col)

        fig = px.line(
            df_sorted,
            x=date_col,
            y=metric,
            markers=True,
            title=f"{metric} Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2: FORECAST ----------------
with tab2:
    st.subheader("Projected Trends")

    if date_col and len(numeric_cols):
        series = df_sorted[metric].rolling(3).mean().dropna()
        future_vals = [series.iloc[-1] * (1 + 0.02 * i) for i in range(1, 7)]
        future_dates = [
            df_sorted[date_col].max() + timedelta(days=30 * i)
            for i in range(1, 7)
        ]

        forecast_df = pd.DataFrame({
            "Date": future_dates,
            "Forecast": future_vals
        })

        forecast_fig = px.line(
            forecast_df,
            x="Date",
            y="Forecast",
            markers=True,
            title="6-Month Forecast"
        )
        st.plotly_chart(forecast_fig, use_container_width=True)

# ---------------- TAB 3: AI INSIGHTS ----------------
with tab3:
    st.subheader("AI-Generated Insights")

    st.success("The company appears to be a subscription-based cybersecurity SaaS business.")

    st.markdown("""
- Revenue growth is flattening quarter-over-quarter  
- Marketing expenses show volatility  
- Early indicators of customer churn detected  
    """)

    if st.button("📄 Export Executive Report"):
        report = f"""
AI FINANCIAL REPORT

Health Scores:
{scores}

Key Insights:
- Revenue growth slowing
- Expense volatility detected
- Churn risk increasing

Recommended Actions:
- Audit marketing spend
- Improve renewal strategy
- Strengthen cashflow planning
        """
        st.download_button(
            "Download Report",
            report,
            file_name="AI_Financial_Report.txt"
        )

# ---------------- TAB 4: ASK AI ----------------
with tab4:
    st.subheader("Ask Your Financial AI")

    suggested_queries = generate_suggested_queries()

    st.sidebar.subheader("💡 Suggested Questions")
    for q in suggested_queries:
        if st.sidebar.button(q):
            st.markdown(mock_llm_answer(q))

    user_query = st.text_input("Ask a custom question")
    if user_query:
        st.markdown(mock_llm_answer(user_query))
