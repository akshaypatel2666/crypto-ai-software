import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import requests

# --- SPEED FIX: Refresh every 5 seconds instead of 1 ---
st_autorefresh(interval=5000, key="vantage_sync_fast")

st.set_page_config(page_title="Vantage Fast Sync", layout="wide")

# Sidebar
coin = st.sidebar.selectbox("Select Coin", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
offset = st.sidebar.number_input("Price Adjustment", value=0.0)

# --- SPEED FIX: Data caching ---
@st.cache_data(ttl=5) # 5 second tak data save rahega
def get_crypto_data(symbol):
    try:
        # Ticker price
        p_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        # Klines (Chart) - Limit kam rakhi hai speed ke liye
        k_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=30"
        
        price_res = requests.get(p_url, timeout=1).json()
        klines_res = requests.get(k_url, timeout=1).json()
        
        return float(price_res['price']), klines_res
    except:
        return None, None

live_rate, klines = get_crypto_data(coin)

if live_rate:
    # Dashboard Display
    st.subheader(f"⚡ Live {coin} Rate")
    st.title(f"${live_rate + offset:,.2f}")
    
    if klines:
        df = pd.DataFrame(klines, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Vol', 'CT', 'QAV', 'T', 'TBB', 'TBQ', 'I'])
        df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')

        # Chart optimized (Simplified layout)
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'], open=df['Open']+offset, high=df['High']+offset,
            low=df['Low']+offset, close=df['Close']+offset
        )])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning("Speeding up connection... Please wait.")
