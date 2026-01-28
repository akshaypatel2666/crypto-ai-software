import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1-second refresh for live feel, 30-sec for data fetch
st_autorefresh(interval=1000, key="pricerefresh")

st.set_page_config(page_title="Pro AI Crypto Analyzer", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4256; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Akshay's Pro AI Trading Suite")

# Sidebar settings
symbol = st.sidebar.selectbox("Select Coin", ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD'])
# Yahoo Finance supports these specific intervals
timeframe = st.sidebar.selectbox("Select Timeframe", ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1d'])

def fetch_data():
    try:
        # Fetching data for the selected timeframe
        df = yf.download(tickers=symbol, period='1d', interval=timeframe, progress=False)
        if df.empty:
            return None
        # Clean multi-index columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        return None

# --- UI Execution ---
df = fetch_data()

if df is not None:
    # Get the very latest price for the "Live Seconds" display
    last_price = float(df['Close'].iloc[-1])
    
    # 1. LIVE SECONDS RATE DASHBOARD
    st.markdown(f"""
        <div style="background-color:#1e2130; padding:20px; border-radius:10px; border-left: 8px solid #00ff00; margin-bottom: 20px;">
            <p style="color:gray; margin:0; font-size:18px;">Live {symbol} Rate (Seconds Update)</p>
            <h1 style="color:#00ff00; font-family:monospace; font-size:45px; margin:0;">${last_price:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    # 2. TECHNICAL ANALYSIS
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current RSI", round(float(df['RSI'].iloc[-1]), 2))
    col2.metric("High", f"${df['High'].max():,.2f}")
    col3.metric("Low", f"${df['Low'].min():,.2f}")
    col4.metric("Change", f"{((last_price/df['Open'].iloc[0])-1)*100:.2f}%")

    # 3. ADVANCED CHART
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="Market Data"
        ),
        go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='orange', width=1.5), name="EMA 20")
    ])
    
    fig.update_layout(
        title=f"{symbol} {timeframe} Analysis",
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_dark",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. PATTERN DETECTION
    patterns = df.ta.cdl_pattern(name="all")
    last_row = patterns.iloc[-1]
    detected = last_row[last_row != 0]
    
    if not detected.empty:
        st.sidebar.success(f"Pattern Detected: {detected.index[0]}")
    else:
        st.sidebar.info("No major pattern in current candle")

else:
    st.error("Data Load Error: Please check your internet or try a different timeframe.")
    st.info("Note: 1m data is only available for the last 7-30 days.")
