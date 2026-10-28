import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.set_page_config(page_title="Live Crypto Demo (CoinGecko)", page_icon="📡", layout="wide")

# Disable transitions/fade so charts don't blink between reruns
st.markdown("""
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

st.title("📡 Live Crypto Data Demo (CoinGecko)")
st.caption("Friendly demo with manual refresh + fallback data so it never crashes.")

# --- Config ---
COINS = ["bitcoin", "ethereum"]
VS = "usd"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

def build_url(ids):
    return f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies={VS}"

API_URL = build_url(COINS)

# Tiny sample to keep the demo working even if the API is rate-limiting
SAMPLE_DF = pd.DataFrame(
    [{"coin": "bitcoin", VS: 68000}, {"coin": "ethereum", VS: 3500}]
)

# --- Fetch (Cached) ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_prices(url: str):
    """Return (df, error_message). Never raise. Safe for beginners."""
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "a bit")
            return None, f"429 Too Many Requests — try again after {retry_after}s"
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data).T.reset_index().rename(columns={"index": "coin"})
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"

# --- Auto Refresh Controls ---
st.subheader("🔁 Auto Refresh Settings")
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)
auto_refresh = st.toggle("Enable auto-refresh", value=False)
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# --- Main View ---
st.subheader("Prices")
df, err = fetch_prices(API_URL)

if err:
    st.warning(f"{err}\nShowing sample data so the demo continues.")
    df = SAMPLE_DF.copy()

st.dataframe(df, use_container_width=True)

fig = px.bar(df, x="coin", y=VS, title=f"Current Price ({VS.upper()})")
st.plotly_chart(fig, use_container_width=True)

# If auto-refresh is ON, wait and rerun the app
if auto_refresh:
    time.sleep(refresh_sec)
    fetch_prices.clear()
    st.rerun()