"""
Sales Dashboard — a page in a multipage Streamlit portfolio.
Lives in:  pages/1_Sales_Dashboard.py   (your existing app.py is the home page)
Run from the portfolio folder with:  streamlit run app.py
"""
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# 1. PAGE CONFIG (must be the first Streamlit command on this page)
st.set_page_config(
    page_title="Coffee Sales Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. LOAD DATA (cached so it runs once, not on every rerun)
@st.cache_data
def load_data():
    rng = np.random.default_rng(42)
    regions = ["North", "South", "East", "West"]
    products = ["Latte", "Espresso", "Cold Brew", "Mocha", "Tea"]
    months = pd.date_range("2025-01-01", periods=12, freq="MS")
    rows = []
    for m in months:
        for r in regions:
            for p in products:
                rows.append({
                    "month": m,
                    "region": r,
                    "product": p,
                    "sales": int(rng.integers(200, 1200)),
                })
    return pd.DataFrame(rows)

df = load_data()

# 3. SIDEBAR (all the user controls live here)
with st.sidebar:
    st.title("☕ Coffee Dashboard")
    region_choice = st.multiselect(
        "Region", options=sorted(df["region"].unique()),
        default=sorted(df["region"].unique()),
    )
    month_range = st.slider("Months", min_value=1, max_value=12, value=(1, 12))
    theme = st.selectbox("Color theme", ["blues", "greens", "oranges", "purples"])

mask = (
    df["region"].isin(region_choice)
    & df["month"].dt.month.between(month_range[0], month_range[1])
)
filtered = df[mask]

if filtered.empty:
    st.warning("No data for these filters. Pick at least one region.")
    st.stop()

# 4. KPI ROW (three equal columns)
st.header("Sales Overview")

monthly = filtered.groupby("month", as_index=False)["sales"].sum()
last = monthly["sales"].iloc[-1]
prev = monthly["sales"].iloc[-2] if len(monthly) > 1 else last

k1, k2, k3 = st.columns(3)
k1.metric("Total sales", f"{filtered['sales'].sum():,}")
k2.metric("Latest month", f"{last:,}", delta=f"{last - prev:,}")
k3.metric("Top product", filtered.groupby("product")["sales"].sum().idxmax())

# 5. MAIN ROW (unequal columns: 2 parts chart, 1 part table)
left, right = st.columns((2, 1), gap="medium")

with left:
    st.subheader("Monthly trend by region")
    trend = filtered.groupby(["month", "region"], as_index=False)["sales"].sum()
    line = (
        alt.Chart(trend)
        .mark_line(point=True)
        .encode(
            x=alt.X("month:T", title="Month"),
            y=alt.Y("sales:Q", title="Sales"),
            color=alt.Color("region:N", scale=alt.Scale(scheme=theme)),
            tooltip=["month:T", "region:N", "sales:Q"],
        )
    )
    st.altair_chart(line, width="stretch")

with right:
    st.subheader("Top products")
    top = (
        filtered.groupby("product", as_index=False)["sales"].sum()
        .sort_values("sales", ascending=False)
    )
    st.dataframe(
        top,
        hide_index=True,
        width="stretch",
        column_config={
            "product": st.column_config.TextColumn("Product"),
            "sales": st.column_config.ProgressColumn(
                "Sales", format="%d", min_value=0,
                max_value=int(top["sales"].max()),
            ),
        },
    )

# 6. TABS (switch between views in the same space)
tab_heat, tab_data = st.tabs(["🔥 Heatmap", "📄 Raw data"])

with tab_heat:
    heat_df = filtered.groupby(["region", "product"], as_index=False)["sales"].sum()
    heat = (
        alt.Chart(heat_df)
        .mark_rect()
        .encode(
            x=alt.X("product:N", title="Product"),
            y=alt.Y("region:N", title="Region"),
            color=alt.Color("sales:Q", scale=alt.Scale(scheme=theme)),
            tooltip=["region", "product", "sales"],
        )
        .properties(height=250)
    )
    st.altair_chart(heat, width="stretch")

with tab_data:
    st.dataframe(filtered, hide_index=True, width="stretch")

# 7. EXPANDER (extra info hidden until clicked)
with st.expander("About this dashboard"):
    st.write(
        "Synthetic data for teaching. Change the sidebar filters and "
        "watch every chart rerun automatically."
    )