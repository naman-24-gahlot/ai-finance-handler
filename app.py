import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="AI Finance Handler", layout="wide")

st.title("💰 AI-Powered Finance Handler")
st.caption("Local Financial Intelligence • LLM-Augmented • Decision-Oriented")

st.sidebar.header("📂 Financial Directory Scanner")

directory = st.sidebar.text_input(
    "Enter directory path (cloud demo)",
    value="/mnt/data"
)

def scan_directory(path):
    files = []
    for root, _, filenames in os.walk(path):
        for f in filenames:
            if f.endswith((".xlsx", ".xls")):
                files.append(os.path.join(root, f))
    return files

def mock_llm_analysis():
    return {
        "profile": "Software company offering subscription-based cybersecurity solutions.",
        "insights": [
            "Revenue peaks during Q3",
            "R&D costs rising steadily",
            "Customer churn increasing slightly"
        ],
        "discrepancies": [
            "Duplicate invoice detected",
            "Marketing spend anomaly"
        ],
        "actions": [
            "Optimize pricing tiers",
            "Audit marketing expenses",
            "Improve retention strategy"
        ]
    }

if st.sidebar.button("Scan Files"):
    files = scan_directory(directory)

    if not files:
        st.warning("No Excel files found (cloud demo mode).")
    else:
        file = st.selectbox("Select a file", files)
        df = pd.read_excel(file)

        st.subheader("📊 Financial Data")
        st.dataframe(df)

        numeric_cols = df.select_dtypes("number").columns
        if len(numeric_cols):
            metric = st.selectbox("Metric", numeric_cols)
            fig = px.line(df, y=metric, title="Time-Based Simulation")
            st.plotly_chart(fig, use_container_width=True)

        if st.button("Run LLM Analysis"):
            res = mock_llm_analysis()

            st.subheader("🏢 Company Understanding")
            st.info(res["profile"])

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Insights")
                for i in res["insights"]:
                    st.write("•", i)

            with col2:
                st.subheader("⚠️ Discrepancies")
                for d in res["discrepancies"]:
                    st.write("•", d)

            st.subheader("✅ Recommended Actions")
            for a in res["actions"]:
                st.success(a)
