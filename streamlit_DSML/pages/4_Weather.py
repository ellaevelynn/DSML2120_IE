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
st.caption("Tracking real-time temperature in Mountain Time (MDT/MST) with session state history and auto-refresh.")

# --- City Coordinates Dictionary ---
CITIES = {
    "Denver": (39.7392, -104.9903),
    "Boulder": (40.0150, -105.2705),
    "Aurora": (39.7294, -104.8319),
    "Colorado Springs": (38.8339, -104.8214)
}

# --- Controls Layout ---
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])

with col_ctrl1:
    selected_city = st.selectbox("Select City", list(CITIES.keys()))

lat, lon = CITIES[selected_city]
wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

with col_ctrl2:
    refresh_sec = st.slider("Refresh every (sec)", 10, 120, 10)

with col_ctrl3:
    auto_refresh = st.toggle("Enable auto-refresh", value=True)

# Accurate Mountain Time display
current_mountain_time = pd.Timestamp.now(tz="America/Denver")
st.caption(f"Viewing weather for **{selected_city}** | Current Mountain Time: {current_mountain_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

# --- Cached Fetch Function ---
@st.cache_data(ttl=60, show_spinner=False)
def get_weather(url: str):
    """Fetch current weather safely from Open-Meteo."""
    try:
        r = requests.get(url, timeout=10, headers=HEADERS)
        r.raise_for_status()
        j = r.json().get("current", {})
        return {
            "temperature": j.get("temperature_2m"),
            "wind": j.get("wind_speed_10m")
        }, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"

# --- Initialize Session State History per City ---
if "city_histories" not in st.session_state:
    st.session_state.city_histories = {}

if selected_city not in st.session_state.city_histories:
    st.session_state.city_histories[selected_city] = pd.DataFrame(columns=["time", "temperature", "wind"])

# --- Fetch Data and Log with Live Local Timestamp ---
weather_data, err = get_weather(wurl)

if err:
    st.warning(f"{err}\nUsing fallback sample data.")
    weather_data = {"temperature": 20.0, "wind": 5.0}

if weather_data:
    # Use exact local fetch time so every 10-second refresh logs a new distinct point on the chart
    fetch_time = pd.Timestamp.now(tz="America/Denver").strftime("%Y-%m-%d %H:%M:%S")
    
    new_row = pd.DataFrame([{
        "time": fetch_time,
        "temperature": weather_data["temperature"],
        "wind": weather_data["wind"]
    }])
    
    history = st.session_state.city_histories[selected_city]
    
    # Append new data point to session history
    st.session_state.city_histories[selected_city] = pd.concat([history, new_row], ignore_index=True)
    
    # Keep last 50 points to prevent memory bloat
    if len(st.session_state.city_histories[selected_city]) > 50:
        st.session_state.city_histories[selected_city] = st.session_state.city_histories[selected_city].iloc[-50:]

# --- Display Metrics & Line Plot ---
current_history = st.session_state.city_histories[selected_city]
if not current_history.empty:
    latest = current_history.iloc[-1]
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Current Temp ({selected_city})", f"{latest['temperature']} °C")
    m2.metric("Wind Speed", f"{latest['wind']} km/h")
    m3.metric("Logged Points", len(current_history))

    # Tidy line plot for temperature over time
    fig = px.line(
        current_history, 
        x="time", 
        y="temperature", 
        markers=True, 
        title=f"Live Temperature History — {selected_city} (Mountain Time)",
        labels={"time": "Local Timestamp", "temperature": "Temperature (°C)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"View Raw Weather History Table ({selected_city})"):
        st.dataframe(current_history, use_container_width=True)

# --- Auto-refresh Execution ---
if auto_refresh:
    time.sleep(refresh_sec)
    get_weather.clear()
    st.rerun()