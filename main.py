import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import requests # Direct API call ke liye

# --- 1 SECOND REFRESH ---
st_autorefresh(interval=1000, key="vantage_sync")

st.set_page_config(page_title="Vantage Real-Time Sync", layout="wide")

# Custom UI for Price
st.markdown("""
    <style>
    .vantage-price {
        background-color: #000000;
        padding: 30px;
        border-radius: 10px;
        border: 2px solid #ffcc00;
        text-align: center;
    }
    .big-font { font-size: 70px !important; color: #ffcc00; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Vantage Sync Settings")
coin = st.sidebar.selectbox("Select Coin", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
# Vantage price match karne ke liye manual adjustment
offset = st.sidebar.number_input("Price Adjustment (Manual Sync)", value=0.0)

def get_crypto_price_direct(symbol):
    try:
        # Hum Binance ki aisi API use karenge jo location block nahi karti
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=2)
        data = response.json()
        return float(data['price'])
    except:
        return None

def get_klines_direct(symbol):
    try:
        # Candlestick data fetch karne ke liye
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=50"
        res = requests.get(url, timeout=2)
        data = res.json()
        df = pd.DataFrame(data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVol', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore'])
        df['Close'] = df['Close'].astype(float)
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        return df
    except:
        return None

# Execution
live_rate = get_crypto_price_direct(coin)
df = get_klines_direct(coin)

if live_rate:
    adjusted_price = live_rate + offset
    
    # --- VANTAGE LIVE DASHBOARD ---
    st.markdown(f'''
        <div class="vantage-price">
            <p style="color:white; font-size:20px;">VANTAGE LIVE RATE (SECONDS)</p>
            <p class="big-font">${adjusted_price:,.2f}</p>
        </div>
    ''', unsafe_allow_html=True)

    if df is not None:
        # Indicators
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # Chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'], open=df['Open']+offset, high=df['High']+offset,
            low=df['Low']+offset, close=df['Close']+offset
        )])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Sidebar RSI
        st.sidebar.metric("Live RSI", round(df['RSI'].iloc[-1], 2))
else:
    st.error("Connecting to Global Price Server...")
