import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# 1-second refresh for live price, 30-sec for graph
st_autorefresh(interval=1000, key="pricerefresh")

st.set_page_config(page_title="Pro AI Crypto Analyzer", layout="wide")
st.title("🚀 Akshay's Pro AI Trading Suite")

# Sidebar - Saare Timeframes jo aapne maange
symbol = st.sidebar.selectbox("Select Coin", ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD'])
timeframe = st.sidebar.selectbox("Select Timeframe", ['1m', '2m', '5m', '15m', '30m', '60m', '90m'])

def fetch_live_price():
    # Last price fetch karne ke liye fast method
    ticker = yf.Ticker(symbol)
    data = ticker.fast_info
    return data['last_price']

def fetch_chart_data():
    try:
        # 1m, 2m, 5m ke liye Yahoo 'last 1 day' ka data deta hai
        df = yf.download(tickers=symbol, period='1d', interval=timeframe, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        return None

# --- UI Layout ---
live_price = fetch_live_price()
df = fetch_chart_data()

# 1. LIVE SECONDS RATE DISPLAY
st.markdown(f"""
    <div style="background-color:#1e1e1e; padding:20px; border-radius:10px; border-left: 5px solid #00ff00;">
        <h2 style="color:white; margin:0;">Live {symbol} Price</h2>
        <h1 style="color:#00ff00; font-family:monospace;">${live_price:,.2f} <span style="font-size:15px; color:gray;">(Live Seconds Update)</span></h1>
    </div>
""", unsafe_allow_html=True)

st.divider()

if df is not None:
    # 2. GRAPH ANALYSIS
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Current RSI", round(float(df['RSI'].iloc[-1]), 2))
    col2.metric("24h High", f"${df['High'].max():,.2f}")
    col3.metric("24h Low",
