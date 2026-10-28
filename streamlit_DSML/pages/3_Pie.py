import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pie Chart Demo", page_icon="🥧", layout="wide")

st.title("🥧 CSV Data & Interactive Pie Chart Demo")
st.caption("Visualizing dataset proportions loaded directly from `data/pie_demo.csv`.")

@st.cache_data
def load_pie_data():
    csv_path = "data/pie_demo.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    # Fallback if file isn't found
    return pd.DataFrame({
        "Category": ["Python", "R", "SQL", "Git", "Streamlit"],
        "Value": [45, 20, 15, 10, 10]
    })

try:
    df = load_pie_data()
    st.success("Successfully loaded `data/pie_demo.csv`!")
except Exception as e:
    st.warning(f"⚠️ Error loading file: {e}. Using fallback data.")
    df = pd.DataFrame({
        "Category": ["Python", "R", "SQL", "Git", "Streamlit"],
        "Value": [45, 20, 15, 10, 10]
    })

# Normalize column names (strip spaces, lowercase) for robust matching
df.columns = [col.strip().lower() for col in df.columns]

# Automatically detect label and value columns
label_col = next((c for c in df.columns if c in ["category", "name", "item"]), df.columns[0])
value_col = next((c for c in df.columns if c in ["value", "count", "amount", "total"]), df.columns[1])

# Layout columns for data table and metrics
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Raw Data")
    st.dataframe(df, use_container_width=True)
    if pd.api.types.is_numeric_dtype(df[value_col]):
        st.metric("Total Value", int(df[value_col].sum()))

with col2:
    st.subheader("📊 Proportion Breakdown")
    if label_col and value_col:
        fig = px.pie(
            df, 
            names=label_col, 
            values=value_col, 
            title="Category Distribution",
            hole=0.3
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not find appropriate category and value columns in the CSV.")