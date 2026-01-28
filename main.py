import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 30-sec auto refresh
st_autorefresh(interval=30 * 1000, key="datarefresh")

st.set_page_config(page_title="AI Crypto Analyzer", layout="wide")
st.title("🤖 Akshay's AI Crypto Software")

# Sidebar - Yahoo symbols use 'BTC-USD' format
symbol = st.sidebar.selectbox("Select Coin", ['BTC-USD', 'ETH-USD', 'SOL-USD'])
timeframe = st.sidebar.selectbox("Timeframe", ['15m', '60m', '1d'])

def fetch_data():
    try:
        # Yahoo Finance block nahi hota
        df = yf.download(tickers=symbol, period='5d', interval=timeframe, progress=False)
        if df.empty: return None
        # Multi-index cleaning
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        st.error(f"Data Fetch Error: {e}")
        return None

df = fetch_data()

if df is not None:
    # Technical Analysis
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    last_price = round(float(df['Close'].iloc[-1]), 2)
    last_rsi = round(float(df['RSI'].iloc[-1]), 2)
    
    c1, c2 = st.columns(2)
    c1.metric("Live Price", f"${last_price}")
    c2.metric("RSI (14)", last_rsi)

    # AI Candlestick Patterns
    patterns = df.ta.cdl_pattern(name="all")
    last_row = patterns.iloc[-1]
    detected = last_row[last_row != 0]
    
    if not detected.empty:
        st.sidebar.success(f"Pattern: {detected.index[0]}")

    # Candlestick Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close']
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=600, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Yahoo Finance se connect ho raha hai... 30 seconds wait karein.")
