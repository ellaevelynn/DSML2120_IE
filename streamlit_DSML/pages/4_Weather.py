import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.set_page_config(page_title="Live Weather Demo (Open-Meteo)", page_icon="🌤️", layout="wide")

# Disable transitions/fade so charts don't blink between reruns
st.markdown("""
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

st.title("🌤️ Live Colorado Weather Demo (Open-Meteo)")
st.caption("Track live temperature over time across multiple cities with caching (`ttl=600`), session state history, and auto-refresh.")

# --- City Coordinates Dictionary ---
CITIES = {
    "Denver": (39.7392, -104.9903),
    "Boulder": (40.0150, -105.2705),
    "Aurora": (39.7294, -104.8319),
    "Colorado Springs": (38.8339, -104.8214)
}

# --- Sidebar / Top Controls for City & Refresh ---
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])

with col_ctrl1:
    selected_city = st.selectbox("Select City", list(CITIES.keys()))

lat, lon = CITIES[selected_city]
wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

with col_ctrl2:
    refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)

with col_ctrl3:
    auto_refresh = st.toggle("Enable auto-refresh", value=False)

st.caption(f"Viewing weather for **{selected_city}** | Last refreshed at: {time.strftime('%H:%M:%S')}")

# Fallback sample data in case of network issues
SAMPLE_WEATHER_DF = pd.DataFrame([{
    "time": pd.Timestamp.now(),
    "temperature": 20.0,
    "wind": 5.0
}])

# --- Cached Fetch Function ---
@st.cache_data(ttl=600, show_spinner=False)
def get_weather(url: str):
    """Fetch current weather safely from Open-Meteo with caching (10-minute TTL)."""
    try:
        r = requests.get(url, timeout=10, headers=HEADERS)
        r.raise_for_status()
        j = r.json().get("current", {})
        df = pd.DataFrame([{
            "time": pd.to_datetime(j.get("time")),
            "temperature": j.get("temperature_2m"),
            "wind": j.get("wind_speed_10m")
        }])
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"

# --- Initialize Session State History per City ---
if "city_histories" not in st.session_state:
    st.session_state.city_histories = {}

if selected_city not in st.session_state.city_histories:
    st.session_state.city_histories[selected_city] = pd.DataFrame(columns=["time", "temperature", "wind"])

# --- Fetch and Append Data ---
new_df, err = get_weather(wurl)

if err:
    st.warning(f"{err}\nShowing fallback sample data so the demo continues.")
    new_df = SAMPLE_WEATHER_DF.copy()

if new_df is not None and not new_df.empty:
    latest_time = new_df["time"].iloc[0]
    history = st.session_state.city_histories[selected_city]
    
    # Append to session state history if it's a new timestamp
    if history.empty or latest_time not in history["time"].values:
        st.session_state.city_histories[selected_city] = pd.concat([history, new_df], ignore_index=True)
        # Keep the last 50 data points per city to prevent memory bloat
        if len(st.session_state.city_histories[selected_city]) > 50:
            st.session_state.city_histories[selected_city] = st.session_state.city_histories[selected_city].iloc[-50:]

# --- Display Metrics & Line Plot ---
current_history = st.session_state.city_histories[selected_city]
if not current_history.empty:
    latest = current_history.iloc[-1]
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Current Temp ({selected_city})", f"{latest['temperature']} °C")
    m2.metric("Wind Speed", f"{latest['wind']} km/h")
    m3.metric("Data Points Logged", len(current_history))

    # Tidy line plot for temperature over time
    fig = px.line(
        current_history, 
        x="time", 
        y="temperature", 
        markers=True, 
        title=f"Temperature History — {selected_city}",
        labels={"time": "Timestamp", "temperature": "Temperature (°C)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"View Raw Weather History ({selected_city})"):
        st.dataframe(current_history, use_container_width=True)

# --- Auto-refresh Execution ---
if auto_refresh:
    time.sleep(refresh_sec)
    get_weather.clear()
    st.rerun()