import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 1 SECOND REFRESH TRIGGER ---
# Ye line har 1000 milliseconds (1 second) mein app ko refresh karegi
st_autorefresh(interval=1000, key="pricerefresh")

st.set_page_config(page_title="Live AI Crypto Tracker", layout="wide")

st.markdown("""
    <style>
    .live-box {
        background-color: #161a25;
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #00ff00;
        box-shadow: 2px 2px 15px rgba(0,255,0,0.1);
    }
    .price-text {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-size: 55px;
        font-weight: bold;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Akshay's Real-Time AI Analyzer")

# Sidebar
symbol = st.sidebar.selectbox("Select Coin", ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD'])
timeframe = st.sidebar.selectbox("Analysis Timeframe", ['1m', '2m', '5m', '15m', '30m', '1h'])

def get_data():
    try:
        # 1-minute data fetch kar rahe hain sabse latest rate ke liye
        data = yf.download(tickers=symbol, period='1d', interval='1m', progress=False)
        if data.empty: return None
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except:
        return None

df = get_data()

if df is not None:
    # Sabse aakhri (Latest) price nikalna
    current_price = float(df['Close'].iloc[-1])
    price_change = current_price - float(df['Open'].iloc[-1])
    color = "#00ff00" if price_change >= 0 else "#ff4b4b"

    # --- LIVE SECONDS RATE DISPLAY ---
    st.markdown(f"""
        <div class="live-box">
            <p style="color:gray; font-size:20px; margin-bottom:5px;">{symbol} LIVE RATE (UPDATES EVERY SECOND)</p>
            <p class="price-text">${current_price:,.2f}</p>
            <p style="color:{color}; font-size:20px;">{'▲' if price_change >= 0 else '▼'} {price_change:,.2f} (Today)</p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Chart Analysis Section
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="Market"
        )])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("Current RSI", round(float(df['RSI'].iloc[-1]), 2))
        # Pattern Alert
        patterns = df.ta.cdl_pattern(name="all")
        last_p = patterns.iloc[-1]
        det = last_p[last_p != 0]
        if not det.empty:
            st.success(f"AI Signal: {det.index[0]}")
        else:
            st.info("Searching for AI Patterns...")

else:
    st.warning("Connecting to Live Feed... Please wait.")
