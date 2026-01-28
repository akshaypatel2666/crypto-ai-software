import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Real-time feel ke liye 1 second refresh
st_autorefresh(interval=1000, key="vantage_match")

st.set_page_config(page_title="Vantage Price Matcher", layout="wide")

st.title("📊 Akshay's AI Analyzer (Vantage Sync)")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Vantage Settings")
symbol = st.sidebar.selectbox("Select Asset", ['BTC-USD', 'ETH-USD', 'GOLD', 'EURUSD=X'])

# Price Offset: Agar Vantage ka rate $5 upar hai, toh aap yahan +5 set kar sakte hain
offset = st.sidebar.number_input("Price Adjustment (Offset)", value=0.0, step=0.1)

timeframe = st.sidebar.selectbox("Timeframe", ['1m', '5m', '15m', '30m', '1h'])

def get_vantage_style_data():
    try:
        # Yahoo Finance se data lena
        df = yf.download(tickers=symbol, period='1d', interval=timeframe, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Apply Offset to match Vantage
        df['Open'] += offset
        df['High'] += offset
        df['Low'] += offset
        df['Close'] += offset
        return df
    except:
        return None

df = get_vantage_style_data()

if df is not None:
    # Latest Price with Offset
    current_price = float(df['Close'].iloc[-1])
    
    # --- VANTAGE STYLE DASHBOARD ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
            <div style="background-color:#111; padding:20px; border-radius:10px; border: 2px solid #555;">
                <p style="color:#aaa; margin:0;">VANTAGE LIVE RATE SYNC</p>
                <h1 style="color:#f0b90b; font-size:60px; margin:0;">${current_price:,.2f}</h1>
                <p style="color:gray;">Offset Applied: {offset}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # Mini Stats
        st.metric("Vantage High", f"${df['High'].max():,.2f}")
        st.metric("Vantage Low", f"${df['Low'].min():,.2f}")

    st.divider()

    # Chart Analysis
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="Vantage Style"
    )])
    
    fig.update_layout(
        template="plotly_dark", 
        xaxis_rangeslider_visible=False, 
        height=500,
        margin=dict(l=0,r=0,t=0,b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # AI Pattern Detection (Sidebar)
    patterns = df.ta.cdl_pattern(name="all")
    last_row = patterns.iloc[-1]
    detected = last_row[last_row != 0]
    if not detected.empty:
        st.sidebar.success(f"Signal for Vantage: {detected.index[0]}")

else:
    st.info("Connecting to Vantage Data Feed...")
