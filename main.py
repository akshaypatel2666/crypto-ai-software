import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 30-second auto refresh
st_autorefresh(interval=30 * 1000, key="datarefresh")

st.set_page_config(page_title="AI Crypto Analyzer", layout="wide")
st.title("🤖 Akshay's AI Crypto Software")

# Sidebar Settings
# Note: Yahoo Finance ke liye symbols 'BTC-USD' format mein hote hain
symbol = st.sidebar.selectbox("Select Coin", ['BTC-USD', 'ETH-USD', 'SOL-USD'])
timeframe = st.sidebar.selectbox("Timeframe (Interval)", ['15m', '60m', '1d'])

def fetch_data():
    try:
        # Yahoo Finance se data lena (Ye block nahi hota)
        data = yf.download(tickers=symbol, period='5d', interval=timeframe, progress=False)
        if data.empty:
            return None
        df = data.copy()
        # Data clean up for technical analysis
        df.columns = df.columns.get_level_values(0) 
        return df
    except Exception as e:
        st.warning(f"Data issue: {e}. Retrying...")
        return None

# Execution logic
df = fetch_data()

if df is not None:
    # Indicators (RSI aur Patterns)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    last_price = round(float(df['Close'].iloc[-1]), 2)
    last_rsi = round(float(df['RSI'].iloc[-1]), 2)
    
    # Display Stats
    c1, c2 = st.columns(2)
    c1.metric("Live Price (Y! Finance)", f"${last_price}")
    c2.metric("RSI (14)", last_rsi)

    # AI Pattern Detection logic
    patterns = df.ta.cdl_pattern(name="all")
    last_pattern = patterns.iloc[-1]
    detected = last_pattern[last_pattern != 0]
    
    if not detected.empty:
        st.sidebar.success(f"Pattern Detected: {detected.index[0]}")
    else:
        st.sidebar.info("Scanning for Patterns...")

    # Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="Market Data"
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=600, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Yahoo Finance se data connect ho raha hai... Please wait.")
