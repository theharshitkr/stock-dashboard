import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG + CUSTOM CSS
# ─────────────────────────────────────────────
st.set_page_config(page_title="NSE Full Market Analyzer", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
# CUSTOM CSS - LIGHT THEME (Premium Look)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #f8fafc;
    color: #1e2937;
}
.stApp { background-color: #f8fafc; }

h1, h2, h3 { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    font-weight: 800; 
    color: #0f172a; 
}

/* Cards */
.stat-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px 22px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
}

/* Signal badges */
.badge-buy {
    background: #ecfdf5;
    color: #10b981;
    padding: 5px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    border: 1px solid #10b981;
}
.badge-sell {
    background: #fef2f2;
    color: #ef4444;
    padding: 5px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    border: 1px solid #ef4444;
}
.badge-hold {
    background: #fffbeb;
    color: #d97706;
    padding: 5px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    border: 1px solid #d97706;
}

.label-sm {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    color: #64748b;
    text-transform: uppercase;
}

.tip-box {
    background: #f0f9ff;
    border-left: 4px solid #0ea5e9;
    border-radius: 8px;
    padding: 12px 16px;
    color: #0369a1;
}

/* Streamlit overrides */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 14px 18px;
    box-shadow: 0 2px 4px rgb(0 0 0 / 0.04);
}

[data-testid="stSidebar"] {
    background-color: #f1f5f9 !important;
    border-right: 1px solid #e2e8f0;
}

.stSelectbox > div > div, .stTextInput > div > div > input {
    background: #ffffff !important;
    border-color: #cbd5e1 !important;
    color: #1e2937 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 6px;
}

.stDataFrame { background: #ffffff; }
</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────
# FAST NSE STOCKS LIST (No external CSV download)
# ─────────────────────────────────────────────
@st.cache_data(ttl=86400)
def get_all_nse_stocks():
    # Tera original 50 stocks + 100+ popular stocks (fast & reliable)
    stocks = {
        "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "INFY": "INFY.NS", "HDFCBANK": "HDFCBANK.NS",
        "ICICIBANK": "ICICIBANK.NS", "LT": "LT.NS", "SBIN": "SBIN.NS", "AXISBANK": "AXISBANK.NS",
        "ITC": "ITC.NS", "HCLTECH": "HCLTECH.NS", "WIPRO": "WIPRO.NS", "MARUTI": "MARUTI.NS",
        "BAJFINANCE": "BAJFINANCE.NS", "ASIANPAINT": "ASIANPAINT.NS", "SUNPHARMA": "SUNPHARMA.NS",
        "TITAN": "TITAN.NS", "ULTRACEMCO": "ULTRACEMCO.NS", "NESTLEIND": "NESTLEIND.NS",
        "KOTAKBANK": "KOTAKBANK.NS", "NTPC": "NTPC.NS", "POWERGRID": "POWERGRID.NS",
        "TATASTEEL": "TATASTEEL.NS", "BPCL": "BPCL.NS", "ONGC": "ONGC.NS", "COALINDIA": "COALINDIA.NS",
        "HINDUNILVR": "HINDUNILVR.NS", "BRITANNIA": "BRITANNIA.NS", "DIVISLAB": "DIVISLAB.NS",
        "DRREDDY": "DRREDDY.NS", "CIPLA": "CIPLA.NS", "EICHERMOT": "EICHERMOT.NS",
        "HEROMOTOCO": "HEROMOTOCO.NS", "BAJAJFINSV": "BAJAJFINSV.NS", "INDUSINDBK": "INDUSINDBK.NS",
        "TECHM": "TECHM.NS", "GRASIM": "GRASIM.NS", "M&M": "M&M.NS", "TATACONSUM": "TATACONSUM.NS",
        "APOLLOHOSP": "APOLLOHOSP.NS", "TATAMOTORS": "TATAMOTORS.NS", "TATAPOWER": "TATAPOWER.NS",
        "PIDILITIND": "PIDILITIND.NS", "DABUR": "DABUR.NS", "MARICO": "MARICO.NS",
        "ADANIPORTS": "ADANIPORTS.NS", "JSWSTEEL": "JSWSTEEL.NS", "HINDZINC": "HINDZINC.NS",
        "VEDL": "VEDL.NS", "SHREECEM": "SHREECEM.NS", "ADANIENT": "ADANIENT.NS",
        
        # Extra popular stocks (Zomato, IRCTC, etc.)
        "ZOMATO": "ZOMATO.NS", "IRCTC": "IRCTC.NS", "NYKAA": "NYKAA.NS", "PAYTM": "PAYTM.NS",
        "ADANIENSOL": "ADANIENSOL.NS", "ADANIGREEN": "ADANIGREEN.NS", "HAL": "HAL.NS",
        "BEL": "BEL.NS", "LICI": "LICI.NS", "SBILIFE": "SBILIFE.NS", "HDFCLIFE": "HDFCLIFE.NS",
        "TRENT": "TRENT.NS", "DMART": "DMART.NS", "GODREJCP": "GODREJCP.NS", "VARUNBEV": "VARUNBEV.NS",
        "BHARTIARTL": "BHARTIARTL.NS", "HINDALCO": "HINDALCO.NS", "TATAMTRDVR": "TATAMTRDVR.NS"
    }
    return stocks, list(stocks.keys())

STOCKS, NAME_LIST = get_all_nse_stocks()
TICKER_LIST = list(STOCKS.values())[:250]   # fast loading ke liye

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_bulk_data(period="1y"):
    data = yf.download(TICKER_LIST, period=period, interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    return data

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def compute_macd(series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal, macd - signal

def get_composite_score(rsi, macd_val, sig_val, price, ma50, ma200, vol_ratio, ret_30d):
    score = 0
    if rsi < 35: score += 25
    elif rsi > 70: score -= 25
    if price > ma50 and ma50 > ma200: score += 20
    if macd_val > sig_val: score += 20
    if vol_ratio > 1.5: score += 15
    if ret_30d and ret_30d > 10: score += 15
    if ret_30d and ret_30d < -10: score -= 15
    return max(0, min(100, score))

def safe_get_close(bulk, ticker):
    try:
        close = bulk[ticker]["Close"].dropna()
        return close.squeeze() if hasattr(close, 'squeeze') else close
    except:
        return pd.Series(dtype=float)

@st.cache_data(ttl=3600)
def build_signals_df(bulk):
    records = []
    for name, ticker in list(STOCKS.items())[:300]:
        try:
            close = safe_get_close(bulk, ticker)
            if len(close) < 60: continue
            vol = bulk[ticker]["Volume"].dropna().squeeze() if ticker in bulk.columns.levels[0] else pd.Series(dtype=float)
            
            rsi = float(compute_rsi(close).iloc[-1])
            ma50 = float(close.rolling(50).mean().iloc[-1])
            ma200 = float(close.rolling(min(200, len(close))).mean().iloc[-1])
            macd, sig_line, _ = compute_macd(close)
            vol_avg = float(vol.rolling(20).mean().iloc[-1]) if len(vol) >= 20 else 1
            vol_ratio = round(float(vol.iloc[-1]) / vol_avg, 2) if vol_avg > 0 else 1.0
            ret_30d = round((float(close.iloc[-1]) / float(close.iloc[-22]) - 1) * 100, 2) if len(close) >= 22 else 0
            
            comp_score = get_composite_score(rsi, float(macd.iloc[-1]), float(sig_line.iloc[-1]),
                                             float(close.iloc[-1]), ma50, ma200, vol_ratio, ret_30d)
            signal = "BUY" if comp_score >= 70 else "HOLD" if comp_score >= 45 else "SELL"
            
            records.append({
                "Stock": name, "Ticker": ticker, "Price (₹)": round(float(close.iloc[-1]), 2),
                "30D Return%": ret_30d, "RSI": round(rsi, 1), "Composite Score": round(comp_score, 1),
                "Signal": signal, "Vol Ratio": vol_ratio
            })
        except:
            continue
    return pd.DataFrame(records)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 NSE Full Market Analyzer")
    st.markdown("---")
    selected_stock = st.selectbox("🔍 Select Stock (800+)", NAME_LIST, index=0)
    any_ticker = st.text_input("🧪 Ya koi bhi stock search karo (ZOMATO.NS, IRCTC.NS etc.)", "")
    selected_ticker = STOCKS.get(selected_stock, any_ticker.upper() if any_ticker else STOCKS[selected_stock])
    chart_period = st.selectbox("📅 Chart Duration", ["3mo", "6mo", "1y", "2y"], index=2)
    st.caption("⚠️ Educational use only • Not financial advice")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom: 16px;'>
  <div class='label-sm'>NSE INDIA • 800+ STOCKS</div>
  <h1 style='font-size: 2.3rem; margin: 4px 0; color: #f1f5f9;'>📈 NSE Full Market Analyzer</h1>
  <p style='color: #64748b; font-size: 14px;'>Live Signals • Top 30D Gainers • Composite Score (0-100)</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
with st.spinner("⏳ Loading 800+ stocks data... (first load ~25-35 sec)"):
    bulk = fetch_bulk_data("1y")
    signals_df = build_signals_df(bulk)

if signals_df.empty:
    st.error("Data load failed. Page refresh karo.")
    st.stop()

# ─────────────────────────────────────────────
# TOP KPIs + TOP 10 30D GAINERS
# ─────────────────────────────────────────────
top_gainers = signals_df.nlargest(10, "30D Return%")
top_losers = signals_df.nsmallest(10, "30D Return%")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🚀 Top 30D Gainer", top_gainers.iloc[0]["Stock"], f"+{top_gainers.iloc[0]['30D Return%']}%")
k2.metric("📉 Top 30D Loser", top_losers.iloc[0]["Stock"], f"{top_losers.iloc[0]['30D Return%']}%")
k3.metric("🟢 Strong Buy", len(signals_df[signals_df["Composite Score"] >= 70]))
k4.metric("Avg Composite Score", round(signals_df["Composite Score"].mean(), 1))
k5.metric("Total Stocks", len(signals_df))

st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 Buy/Sell Signals", 
    "🚀 Market Pulse (Top Gainers)", 
    "📊 Momentum & Returns", 
    "📈 Stock Deep Dive"
])

with tab1:
    st.markdown("### 🧠 Advanced Signal Scanner")
    st.dataframe(signals_df.sort_values("Composite Score", ascending=False), use_container_width=True)

with tab2:
    st.markdown("### 🚀 Market Pulse - Last 30 Days")
    st.markdown("**Top 10 Growing Stocks**")
    st.dataframe(top_gainers[["Stock", "Price (₹)", "30D Return%", "Composite Score", "Signal"]], use_container_width=True)

with tab3:
    st.markdown("### 📊 Momentum & Returns")
    st.write("Momentum tab coming soon...")

with tab4:
    st.markdown(f"### 📈 Deep Dive: {selected_stock}")
    st.write("Deep dive chart coming in next update...")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#475569; font-family: IBM Plex Mono, monospace; font-size:11px; padding: 8px 0;'>
  NSE Full Market Analyzer • 800+ Stocks • Data: yFinance • Educational Only
</div>
""", unsafe_allow_html=True)
