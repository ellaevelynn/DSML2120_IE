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

st.title("🌤️ Live Weather Demo (Open-Meteo)")
st.caption("Tracking Denver temperature over time with caching (`ttl=600`), session state history, and auto-refresh.")

# --- Config ---
LAT, LON = 39.7392, -104.9903
WURL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,wind_speed_10m"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

# Fallback sample data in case of network issues
SAMPLE_WEATHER_DF = pd.DataFrame([{
    "time": pd.Timestamp.now(),
    "temperature": 22.5,
    "wind": 4.2
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

# --- Initialize Session State for History ---
if "weather_history" not in st.session_state:
    st.session_state.weather_history = pd.DataFrame(columns=["time", "temperature", "wind"])

# --- Auto Refresh Controls ---
st.subheader("🔁 Auto Refresh Settings")
col1, col2 = st.columns(2)
with col1:
    refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)
with col2:
    auto_refresh = st.toggle("Enable auto-refresh", value=False)

st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# --- Fetch and Append Data ---
st.subheader("📊 Denver Weather Time Series")
new_df, err = get_weather(WURL)

if err:
    st.warning(f"{err}\nShowing fallback sample data so the demo continues.")
    new_df = SAMPLE_WEATHER_DF.copy()

if new_df is not None and not new_df.empty:
    latest_time = new_df["time"].iloc[0]
    history = st.session_state.weather_history
    # Append to session state history if it's a new timestamp
    if history.empty or latest_time not in history["time"].values:
        st.session_state.weather_history = pd.concat([history, new_df], ignore_index=True)
        # Keep the last 50 data points to prevent memory bloat
        if len(st.session_state.weather_history) > 50:
            st.session_state.weather_history = st.session_state.weather_history.iloc[-50:]

# --- Display Metrics & Line Plot ---
current_history = st.session_state.weather_history
if not current_history.empty:
    latest = current_history.iloc[-1]
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Temperature", f"{latest['temperature']} °C")
    m2.metric("Wind Speed", f"{latest['wind']} km/h")
    m3.metric("Data Points Logged", len(current_history))

    # Tidy line plot for temperature over time
    fig = px.line(
        current_history, 
        x="time", 
        y="temperature", 
        markers=True, 
        title="Denver Temperature Over Time",
        labels={"time": "Timestamp", "temperature": "Temperature (°C)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Raw Weather History Table"):
        st.dataframe(current_history, use_container_width=True)

# --- Auto-refresh Execution ---
if auto_refresh:
    time.sleep(refresh_sec)
    get_weather.clear()
    st.rerun()