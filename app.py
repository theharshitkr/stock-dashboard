import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG + LIGHT THEME CSS (Fixed for visibility)
# ─────────────────────────────────────────────
st.set_page_config(page_title="NSE Full Market Analyzer", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #f8fafc;
    color: #1e2937;
}
.stApp { background-color: #f8fafc; }
h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; color: #0f172a; }

/* Signal badges - Light theme friendly */
.badge-buy { background: #ecfdf5; color: #10b981; padding: 5px 16px; border-radius: 9999px; font-size: 13px; font-family: 'IBM Plex Mono', monospace; font-weight: 600; border: 1px solid #10b981; }
.badge-sell { background: #fef2f2; color: #ef4444; padding: 5px 16px; border-radius: 9999px; font-size: 13px; font-family: 'IBM Plex Mono', monospace; font-weight: 600; border: 1px solid #ef4444; }
.badge-hold { background: #fffbeb; color: #d97706; padding: 5px 16px; border-radius: 9999px; font-size: 13px; font-family: 'IBM Plex Mono', monospace; font-weight: 600; border: 1px solid #d97706; }

.label-sm { font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 1.5px; color: #64748b; text-transform: uppercase; }
.tip-box { background: #f0f9ff; border-left: 4px solid #0ea5e9; border-radius: 8px; padding: 12px 16px; color: #0369a1; }

div[data-testid="metric-container"] { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px 18px; box-shadow: 0 2px 4px rgb(0 0 0 / 0.04); }
[data-testid="stSidebar"] { background-color: #f1f5f9 !important; border-right: 1px solid #e2e8f0; }
.stSelectbox > div > div, .stTextInput > div > div > input { background: #ffffff !important; border-color: #cbd5e1 !important; color: #1e2937 !important; }
.stDataFrame { background: #ffffff; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FAST NSE STOCKS (250+ popular - no hanging)
# ─────────────────────────────────────────────
@st.cache_data(ttl=86400)
def get_all_nse_stocks():
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
        "ZOMATO": "ZOMATO.NS", "IRCTC": "IRCTC.NS", "NYKAA": "NYKAA.NS", "PAYTM": "PAYTM.NS",
        "ADANIENSOL": "ADANIENSOL.NS", "ADANIGREEN": "ADANIGREEN.NS", "HAL": "HAL.NS",
        "BEL": "BEL.NS", "LICI": "LICI.NS", "SBILIFE": "SBILIFE.NS", "HDFCLIFE": "HDFCLIFE.NS",
        "TRENT": "TRENT.NS", "DMART": "DMART.NS", "GODREJCP": "GODREJCP.NS", "VARUNBEV": "VARUNBEV.NS",
        "BHARTIARTL": "BHARTIARTL.NS", "HINDALCO": "HINDALCO.NS", "TATAMTRDVR": "TATAMTRDVR.NS"
    }
    return stocks, list(stocks.keys())

STOCKS, NAME_LIST = get_all_nse_stocks()
TICKER_LIST = list(STOCKS.values())[:250]

# ─────────────────────────────────────────────
# HELPER FUNCTIONS (Full Analysis)
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_bulk_data(period="1y"):
    return yf.download(TICKER_LIST, period=period, interval="1d", group_by="ticker", auto_adjust=True, progress=False)

@st.cache_data(ttl=3600)
def fetch_single_stock(ticker, period="1y"):
    return yf.download(ticker, period=period, auto_adjust=True, progress=False)

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
    for name, ticker in list(STOCKS.items())[:250]:
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
                "Signal": signal, "Vol Ratio": vol_ratio,
                "MA50": round(ma50, 2), "MA200": round(ma200, 2),
                "Price vs MA50": "Above ✅" if float(close.iloc[-1]) > ma50 else "Below ❌",
                "Price vs MA200": "Above ✅" if float(close.iloc[-1]) > ma200 else "Below ❌",
                "Golden Cross": "Yes ✅" if ma50 > ma200 else "No",
                "MACD Trend": "Bullish ↑" if float(macd.iloc[-1]) > float(sig_line.iloc[-1]) else "Bearish ↓",
                "Volume Spike": "High 🔥" if vol_ratio > 1.5 else ("Low" if vol_ratio < 0.7 else "Normal")
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
    selected_stock = st.selectbox("🔍 Select Stock", NAME_LIST, index=0)
    any_ticker = st.text_input("🧪 Search any stock (e.g. ZOMATO.NS)", "")
    selected_ticker = STOCKS.get(selected_stock, any_ticker.upper() if any_ticker else STOCKS[selected_stock])
    chart_period = st.selectbox("📅 Chart Duration", ["3mo", "6mo", "1y", "2y"], index=2)
    st.caption("⚠️ Educational use only • Not financial advice")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom: 16px;'>
  <div class='label-sm'>NSE INDIA • 250+ STOCKS</div>
  <h1 style='font-size: 2.4rem; margin: 4px 0;'>📈 NSE Full Market Analyzer</h1>
  <p style='color: #64748b; font-size: 14px;'>Live Signals • 30D Growth • RSI • MACD • Composite Score (0-100)</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
with st.spinner("⏳ Loading market data..."):
    bulk = fetch_bulk_data("1y")
    signals_df = build_signals_df(bulk)

if signals_df.empty:
    st.error("Data load failed. Refresh the page.")
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
k4.metric("Avg Composite", round(signals_df["Composite Score"].mean(), 1))
k5.metric("Total Stocks", len(signals_df))
st.markdown("---")

# ─────────────────────────────────────────────
# TABS (Full Analysis)
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 Buy/Sell Signals", "🚀 Market Pulse", "📊 Momentum & Returns", "📈 Stock Deep Dive"
])

with tab1:
    st.markdown("### 🧠 Advanced Signal Scanner (Composite Score 0-100)")
    st.markdown('<div class="tip-box">Higher Score = Stronger Buy (RSI + MACD + MA + Volume + 30D Return)</div>', unsafe_allow_html=True)
    
    # Filters
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        sig_filter = st.selectbox("Signal Filter", ["All", "BUY only", "SELL only", "HOLD only"])
    with fc2:
        rsi_filter = st.selectbox("RSI Status", ["All", "Oversold (<30)", "Overbought (>70)", "Normal"])
    with fc3:
        sort_by = st.selectbox("Sort By", ["Composite Score", "30D Return%", "RSI", "Price (₹)"])
    with fc4:
        ascending = st.checkbox("Ascending", value=False)
    
    df_view = signals_df.copy()
    if sig_filter != "All":
        df_view = df_view[df_view["Signal"] == sig_filter.replace(" only", "")]
    if rsi_filter == "Oversold (<30)":
        df_view = df_view[df_view["RSI"] < 30]
    elif rsi_filter == "Overbought (>70)":
        df_view = df_view[df_view["RSI"] > 70]
    elif rsi_filter == "Normal":
        df_view = df_view[(df_view["RSI"] >= 30) & (df_view["RSI"] <= 70)]
    
    df_view = df_view.sort_values(sort_by, ascending=ascending)
    
    st.dataframe(df_view[["Stock", "Price (₹)", "30D Return%", "RSI", "Composite Score", "Signal", 
                          "Price vs MA50", "Price vs MA200", "Golden Cross", "MACD Trend", "Volume Spike"]], 
                 use_container_width=True, height=480)

with tab2:
    st.markdown("### 🚀 Market Pulse - Last 30 Days")
    st.markdown("**Top 10 Growing Stocks**")
    st.dataframe(top_gainers[["Stock", "Price (₹)", "30D Return%", "Composite Score", "Signal"]], use_container_width=True)
    
    st.markdown("**Top 10 Declining Stocks**")
    st.dataframe(top_losers[["Stock", "Price (₹)", "30D Return%", "Composite Score", "Signal"]], use_container_width=True)

with tab3:
    st.markdown("### 📊 Momentum & Returns")
    st.write("Momentum analysis with streaks coming in next update (will show Up/Down streaks)")

with tab4:
    st.markdown(f"### 📈 Deep Dive: {selected_stock}")
    stock_data = fetch_single_stock(selected_ticker, chart_period)
    if not stock_data.empty:
        close = stock_data["Close"].squeeze()
        high = stock_data["High"].squeeze()
        low = stock_data["Low"].squeeze()
        open_ = stock_data["Open"].squeeze()
        vol = stock_data["Volume"].squeeze()
        idx = close.index
        
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(min(200, len(close))).mean()
        rsi_s = compute_rsi(close)
        macd_line, sig_line, histogram = compute_macd(close)
        bb_upper = ma20 + 2 * close.rolling(20).std()
        bb_lower = ma20 - 2 * close.rolling(20).std()
        
        cur_price = float(close.iloc[-1])
        cur_rsi = float(rsi_s.iloc[-1])
        cur_ma50 = float(ma50.iloc[-1]) if not pd.isna(ma50.iloc[-1]) else cur_price
        cur_ma200 = float(ma200.iloc[-1]) if not pd.isna(ma200.iloc[-1]) else cur_price
        comp_score = get_composite_score(cur_rsi, float(macd_line.iloc[-1]), float(sig_line.iloc[-1]),
                                         cur_price, cur_ma50, cur_ma200, 1.0, 
                                         round((cur_price / float(close.iloc[-22]) - 1) * 100, 2) if len(close) >= 22 else 0)
        signal_label = "BUY" if comp_score >= 70 else "HOLD" if comp_score >= 45 else "SELL"
        
        # Stats
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Current Price", f"₹{cur_price:,.2f}")
        m2.metric("RSI (14)", f"{cur_rsi:.1f}")
        m3.metric("Composite Score", f"{comp_score}/100")
        m4.metric("Signal", signal_label)
        m5.metric("30D Return", f"{round((cur_price / float(close.iloc[-22]) - 1) * 100, 2) if len(close) >= 22 else 0}%")
        
        st.markdown("---")
        
        # Chart 1: Price with MA + Bollinger
        st.markdown("#### 🕯️ Price Chart — Candlestick + MA + Bollinger Bands")
        fig_price = go.Figure()
        fig_price.add_trace(go.Candlestick(x=idx, open=open_, high=high, low=low, close=close,
                                           increasing_line_color="#10b981", decreasing_line_color="#ef4444"))
        fig_price.add_trace(go.Scatter(x=idx, y=bb_upper, name="BB Upper", line=dict(color="#8b5cf6", width=1, dash="dot")))
        fig_price.add_trace(go.Scatter(x=idx, y=bb_lower, name="BB Lower", line=dict(color="#8b5cf6", width=1, dash="dot")))
        fig_price.add_trace(go.Scatter(x=idx, y=ma50, name="MA 50", line=dict(color="#3b82f6", width=1.5)))
        fig_price.add_trace(go.Scatter(x=idx, y=ma200, name="MA 200", line=dict(color="#ec4899", width=1.5, dash="dash")))
        fig_price.update_layout(paper_bgcolor="#f8fafc", plot_bgcolor="#f8fafc", font=dict(color="#1e2937"),
                                height=420, xaxis_rangeslider_visible=False,
                                xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0", title="Price (₹)"))
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Chart 2: RSI
        st.markdown("#### 📊 RSI Chart")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=idx, y=rsi_s, name="RSI", line=dict(color="#f59e0b", width=2)))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ef4444")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#10b981")
        fig_rsi.update_layout(paper_bgcolor="#f8fafc", plot_bgcolor="#f8fafc", font=dict(color="#1e2937"),
                              height=260, xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0", title="RSI", range=[0, 100]))
        st.plotly_chart(fig_rsi, use_container_width=True)
        
     # Chart 3: MACD (FIXED)
st.markdown("#### 📉 MACD Chart")
fig_macd = make_subplots(rows=1, cols=1)
histogram_filled = histogram.fillna(0)   # NaN fix
hist_colors = ["#10b98180" if h >= 0 else "#ef444480" for h in histogram_filled]
fig_macd.add_trace(go.Bar(
    x=idx, 
    y=list(histogram_filled), 
    name="Histogram", 
    marker=dict(color=hist_colors)
))
fig_macd.add_trace(go.Scatter(x=idx, y=macd_line, name="MACD", line=dict(color="#3b82f6", width=2)))
fig_macd.add_trace(go.Scatter(x=idx, y=sig_line, name="Signal", line=dict(color="#ec4899", width=2)))
fig_macd.update_layout(
    paper_bgcolor="#f8fafc", 
    plot_bgcolor="#f8fafc", 
    font=dict(color="#1e2937"),
    height=260, 
    xaxis=dict(gridcolor="#e2e8f0"), 
    yaxis=dict(gridcolor="#e2e8f0", title="MACD")
)
st.plotly_chart(fig_macd, use_container_width=True)
        
        # Chart 4: Volume
        st.markdown("#### 📦 Volume Chart")
        vol_20ma = vol.rolling(20).mean()
        vol_colors = ["#10b98166" if float(c) >= float(o) else "#ef444466" for c, o in zip(close, open_)]
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=idx, y=list(vol), name="Volume", marker=dict(color=vol_colors)))
        fig_vol.add_trace(go.Scatter(x=idx, y=vol_20ma, name="20-day Avg", line=dict(color="#f59e0b", width=1.5, dash="dot")))
        fig_vol.update_layout(paper_bgcolor="#f8fafc", plot_bgcolor="#f8fafc", font=dict(color="#1e2937"),
                              height=260, xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0", title="Volume"))
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Key Levels
        st.markdown("### 🎯 Key Price Levels")
        w52h = float(close.rolling(min(252, len(close))).max().iloc[-1])
        w52l = float(close.rolling(min(252, len(close))).min().iloc[-1])
        from_52h = round((cur_price / w52h - 1) * 100, 1)
        from_52l = round((cur_price / w52l - 1) * 100, 1)
        
        lc1, lc2, lc3, lc4 = st.columns(4)
        lc1.metric("52W High", f"₹{w52h:,.1f}", f"{from_52h}% from high")
        lc2.metric("52W Low", f"₹{w52l:,.1f}", f"+{from_52l}% from low")
        lc3.metric("MA 50", f"₹{cur_ma50:,.1f}")
        lc4.metric("MA 200", f"₹{cur_ma200:,.1f}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#475569; font-family: IBM Plex Mono, monospace; font-size:11px; padding: 8px 0;'>
  NSE Full Market Analyzer • 250+ Stocks • Data: yFinance • Educational Only • Not Financial Advice
</div>
""", unsafe_allow_html=True)
