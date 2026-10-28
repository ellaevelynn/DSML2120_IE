import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pie Chart Demo", page_icon="🥧", layout="wide")

st.title("🥧 CSV Data & Interactive Pie Chart Demo")
st.caption("Visualizing dataset proportions loaded directly from a local CSV file.")

# Cached function to load the CSV file
@st.cache_data
def load_pie_data():
    return pd.read_csv("data/pie_demo.csv")

try:
    df = load_pie_data()

    # Layout columns for data table and metrics
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📋 Raw Data")
        st.dataframe(df, use_container_width=True)
        st.metric("Total Count", df["count"].sum() if "count" in df.columns else len(df))

    with col2:
        st.subheader("📊 Proportion Breakdown")
        if "category" in df.columns and "count" in df.columns:
            # Create an interactive donut/pie chart
            fig = px.pie(
                df, 
                names="category", 
                values="count", 
                title="Category Distribution",
                hole=0.3 # Turns it into a sleek donut chart
            )
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("The CSV file must contain 'category' and 'count' columns.")

except FileNotFoundError:
    st.error("⚠️ Could not find `data/pie_demo.csv`. Please ensure the file is saved correctly in the `data/` folder.")