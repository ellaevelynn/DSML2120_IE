import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Simple Interactive Visualization")

st.markdown(
    """
    **Goal:** demonstrate a small interaction: pick a subset with a widget and update a chart.  
    Choose one dataset below and complete the TODOs.
    """
)

# ----------------- Dataset choice -----------------
dataset = st.radio(
    "Choose a dataset",
    options=["Tips (restaurant)", "Gapminder (world)"],
    horizontal=True
)

@st.cache_data
def load_tips():
    return px.data.tips()

@st.cache_data
def load_gapminder():
    return px.data.gapminder()

# ----------------- Tips Example -----------------
if dataset == "Tips (restaurant)":
    df = load_tips()
    st.write("**Columns:**", list(df.columns))

    # TODO 1: add one widget (e.g., filter by day)
    days = sorted(df["day"].unique())
    chosen_days = st.multiselect("Filter by day", options=days, default=days)

    # Optional second widget
    meal = st.radio("Meal time", options=sorted(df["time"].unique()), index=1)

    # Filter
    filtered = df.query("day in @chosen_days and time == @meal")

    # Chart
    st.markdown("#### Scatter: Total Bill vs Tip")
    if filtered.empty:
        st.warning("No rows match your filters.")
    else:
        fig = px.scatter(
            filtered,
            x="total_bill", y="tip",
            color="sex", size="size",
            hover_data=["day", "smoker"],
            labels={"total_bill": "Total Bill ($)", "tip": "Tip ($)"},
            title=f"Tips: {meal} · {', '.join(chosen_days)}"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Help text
    with st.expander("How to read this chart"):
        st.write(
            """
            - Each point is a party; bigger points mean larger party size.  
            - X: bill amount; Y: tip amount.  
            - Try selecting different days or meal times and watch the pattern shift.
            """
        )

# ----------------- Gapminder Example -----------------
else:
    df = load_gapminder()
    st.write("**Columns:**", list(df.columns))

    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    year = st.slider("Pick a year", min_value=year_min, max_value=year_max, value=2007, step=5)

    # TODO 2: choose continent or 'All'
    continents = ["All"] + sorted(df["continent"].unique())
    continent = st.selectbox("Continent", options=continents, index=0)

    view = df[df["year"] == year]
    if continent != "All":
        view = view[view["continent"] == continent]

    st.markdown("#### Bubble chart: GDP per capita vs Life Expectancy")
    if view.empty:
        st.warning("No data for this selection.")
    else:
        fig = px.scatter(
            view,
            x="gdpPercap", y="lifeExp",
            size="pop", color="continent", hover_name="country",
            size_max=50, log_x=True,
            labels={"gdpPercap": "GDP per Capita (USD)", "lifeExp": "Life Expectancy (years)"},
            title=f"{year} — {continent if continent!='All' else 'All continents'}"
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("How to read this chart"):
        st.write(
            """
            - X (log): income; Y: life expectancy; bubble size: population.  
            - Compare regions or switch the continent to narrow the view.
            """
        )

st.divider()
st.caption("Edit `pages/2_Visualization.py` to finish your interactive viz.")
