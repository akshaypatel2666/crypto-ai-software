import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 30-second auto refresh
st_autorefresh(interval=30 * 1000, key="datarefresh")

st.set_page_config(page_title="AI Crypto Analyzer", layout="wide")
st.title("🤖 Akshay's AI Crypto Software")

# Sidebar Settings
symbol = st.sidebar.selectbox("Select Coin", ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
timeframe = st.sidebar.selectbox("Timeframe", ['15m', '1h', '4h'])

# Setup Exchange with retry logic
exchange = ccxt.binance({'enableRateLimit': True})

def fetch_data():
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
        df = pd.DataFrame(bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        return df
    except Exception as e:
        st.warning(f"Connection issue: {e}. Retrying...")
        return None

# Execution logic
df = fetch_data()

if df is not None:
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    
    last_price = df['Close'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # Display Stats
    c1, c2 = st.columns(2)
    c1.metric("Live Price", f"${last_price}")
    c2.metric("RSI", round(last_rsi, 2))

    # Pattern Detection
    patterns = df.ta.cdl_pattern(name="all")
    last_pattern = patterns.iloc[-1]
    detected = last_pattern[last_pattern != 0]
    
    if not detected.empty:
        st.sidebar.success(f"Pattern Detected: {detected.index[0]}")

    # Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['Timestamp'],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close']
    )])
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Waiting for data from Binance... Please wait 30 seconds.")

