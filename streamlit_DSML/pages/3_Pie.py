import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pie Chart Demo", page_icon="🥧", layout="wide")

st.title("🥧 CSV Data & Interactive Pie Chart Demo")
st.caption("Visualizing dataset proportions loaded directly from a local CSV file.")

# Robust cached function that checks multiple paths to prevent FileNotFoundError
@st.cache_data
def load_pie_data():
    possible_paths = [
        "data/pie_demo.csv",
        "../data/pie_demo.csv",
        os.path.join(os.path.dirname(__file__), "..", "data", "pie_demo.csv")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    raise FileNotFoundError("Could not locate pie_demo.csv")

try:
    df = load_pie_data()
    data_source_msg = "Loaded successfully from `data/pie_demo.csv`"
except FileNotFoundError:
    st.warning("⚠️ Could not find `data/pie_demo.csv` on the server. Using fallback sample data.")
    df = pd.DataFrame({
        "category": ["Python", "R", "SQL", "Git/GitHub", "Flask"],
        "count": [45, 25, 15, 10, 5]
    })
    data_source_msg = "Using fallback sample data"

st.info(f"**Status:** {data_source_msg}")

# Layout columns for data table and metrics
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Raw Data")
    st.dataframe(df, use_container_width=True)
    st.metric("Total Count", df["count"].sum() if "count" in df.columns else len(df))

with col2:
    st.subheader("📊 Proportion Breakdown")
    if "category" in df.columns and "count" in df.columns:
        fig = px.pie(
            df, 
            names="category", 
            values="count", 
            title="Category Distribution",
            hole=0.3
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("The dataset must contain 'category' and 'count' columns.")