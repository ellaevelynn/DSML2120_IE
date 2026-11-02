"""
Spotify Analytics Dashboard — a page in a multipage Streamlit portfolio.
Lives in:  pages/1_Sales_Dashboard.py   (your existing app.py is the home page)
Run from the portfolio folder with:  streamlit run app.py
"""
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# 1. PAGE CONFIG (must be the first Streamlit command on this page)
st.set_page_config(
    page_title="Spotify Music Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. LOAD DATA (Requirement 6: Using Solomon Ameh Spotify Music Dataset)
@st.cache_data
def load_data():
    # Update path to your local copy of the Kaggle CSV file
    df = pd.read_csv("data/high_popularity_spotify_data.csv")
    
    # Parse release date and extract release month/year
    if "track_album_release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["track_album_release_date"], errors="coerce")
        df["month"] = df["release_date"].dt.to_period("M").dt.to_timestamp()
    else:
        # Fallback date creation if missing
        df["month"] = pd.date_range("2024-01-01", periods=len(df), freq="h")

    # Rename key columns to standardize dashboard processing
    df = df.rename(columns={
        "playlist_genre": "genre",
        "playlist_subgenre": "subgenre",
        "track_popularity": "popularity",
        "track_name": "track",
        "track_artist": "artist"
    })
    
    # Ensure numeric types
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
    
    return df

df = load_data()

# 3. SIDEBAR CONTROLS & FILTERS
st.sidebar.header("Filter Options")

# Genre Multi-select Filter
genres = df["genre"].dropna().unique()
selected_genres = st.sidebar.multiselect(
    "Select Genre(s)",
    options=genres,
    default=genres
)

# Requirement 2: Add Subgenre/Product st.multiselect to sidebar
subgenres = df[df["genre"].isin(selected_genres)]["subgenre"].dropna().unique() if "subgenre" in df.columns else []
selected_subgenres = st.sidebar.multiselect(
    "Select Subgenre(s)",
    options=subgenres,
    default=subgenres
)

# Filter dataframe using updated boolean mask
mask = (
    df["genre"].isin(selected_genres) & 
    (df["subgenre"].isin(selected_subgenres) if len(subgenres) > 0 else True)
)
filtered_df = df[mask]

# 4. MAIN DASHBOARD CONTENT
st.title("🎵 Spotify Music & Track Popularity Dashboard")
st.markdown("Explore track popularity, audio feature breakdowns, and genre insights from the Spotify Music Dataset.")

# Requirement 3: Four columns for KPIs (including Average Monthly Metrics)
total_tracks = len(filtered_df)
avg_popularity = filtered_df["popularity"].mean() if total_tracks > 0 else 0
avg_danceability = filtered_df["danceability"].mean() if "danceability" in filtered_df.columns else 0

# Calculate Average Monthly Popularity Index
monthly_grouped = filtered_df.groupby("month")["popularity"].mean()
avg_monthly_popularity = monthly_grouped.mean() if not monthly_grouped.empty else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Tracks", f"{total_tracks:,}")
kpi2.metric("Avg Popularity Score", f"{avg_popularity:.1f}/100")
kpi3.metric("Avg Danceability", f"{avg_danceability:.2f}")
kpi4.metric("Avg Monthly Popularity", f"{avg_monthly_popularity:.1f}")

st.markdown("---")

# Requirement 1: Column Ratio Adjustments (1.5, 4.5, 2 layout)
col1, col2, col3 = st.columns((1.5, 4.5, 2))

with col1:
    st.subheader("Filters")
    st.info(f"Showing **{len(selected_genres)}** Genres & **{len(selected_subgenres)}** Subgenres.")
    
with col2:
    st.subheader("Data Summary")
    st.write(f"Filtered Dataset: **{len(filtered_df):,}** tracks out of {len(df):,} total.")

with col3:
    st.subheader("Top Track")
    if not filtered_df.empty:
        top_row = filtered_df.loc[filtered_df["popularity"].idxmax()]
        st.success(f"**{top_row['track']}**\n\nArtist: *{top_row['artist']}*\n\nScore: {top_row['popularity']}/100")
    else:
        st.warning("No track data available for current selection.")

st.markdown("---")

# Requirement 4: Three Tabs (Overview, Trends, and Regional/Genre Breakdown Bar Chart)
tab1, tab2, tab3 = st.tabs(["📊 Track Data", "📈 Popularity Trends", "🎧 Genre Distribution"])

with tab1:
    st.subheader("Filtered Track Listing")
    display_cols = [c for c in ["track", "artist", "genre", "subgenre", "popularity", "danceability", "energy"] if c in filtered_df.columns]
    st.dataframe(filtered_df[display_cols], use_container_width=True)

with tab2:
    st.subheader("Average Monthly Track Popularity")
    if not filtered_df.empty:
        trend_df = filtered_df.groupby("month", as_index=False)["popularity"].mean()
        line_chart = alt.Chart(trend_df).mark_line(point=True, strokeWidth=3, color="#1DB954").encode(
            x=alt.X("month:T", title="Release Month"),
            y=alt.Y("popularity:Q", title="Avg Popularity Score"),
            tooltip=["month", "popularity"]
        ).properties(height=400)
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.write("No trend data to display.")

with tab3:
    st.subheader("Track Count by Genre")
    if not filtered_df.empty:
        genre_summary = filtered_df.groupby("genre", as_index=False)["popularity"].count().rename(columns={"popularity": "track_count"})
        
        # Requirement 4: Bar chart by category using mark_bar()
        bar_chart = alt.Chart(genre_summary).mark_bar(color="#1DB954").encode(
            x=alt.X("genre:N", title="Genre", sort="-y"),
            y=alt.Y("track_count:Q", title="Number of Tracks"),
            tooltip=["genre", "track_count"]
        ).properties(height=400)
        
        st.altair_chart(bar_chart, use_container_width=True)
    else:
        st.write("No genre data to display.")