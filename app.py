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
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="NSE Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #0f172a;
    color: #e2e8f0;
}

.stApp { background-color: #0f172a; }

h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; color: #f1f5f9; }

/* Cards */
.stat-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 10px;
}

/* Signal badges */
.badge-buy {
    background: #052e16;
    color: #4ade80;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    border: 1px solid #166534;
    display: inline-block;
}
.badge-sell {
    background: #2d0a0a;
    color: #f87171;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    border: 1px solid #991b1b;
    display: inline-block;
}
.badge-hold {
    background: #1c1408;
    color: #fbbf24;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    border: 1px solid #92400e;
    display: inline-block;
}

.label-sm {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    color: #64748b;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.tip-box {
    background: #0f2444;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 13px;
    color: #93c5fd;
    margin: 8px 0 16px 0;
}

/* Streamlit overrides */
div[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 12px 16px;
}
div[data-testid="metric-container"] label {
    color: #94a3b8 !important;
    font-size: 12px !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-size: 22px !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] {
    background-color: #0b1120 !important;
    border-right: 1px solid #1e293b;
}

.stSelectbox > div > div, .stTextInput > div > div > input {
    background: #1e293b !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #1e293b;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    color: #94a3b8;
    border-radius: 8px;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #3b82f6 !important;
    color: #ffffff !important;
}

.stRadio > div { gap: 8px; }
.stRadio label { color: #e2e8f0 !important; }

hr { border-color: #1e293b; margin: 12px 0; }

/* DataFrame */
.stDataFrame { font-family: 'IBM Plex Mono', monospace; font-size: 12px; }
[data-testid="stDataFrameResizable"] { background: #1e293b !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NIFTY 50 + POPULAR STOCKS (manageable list)
# ─────────────────────────────────────────────
STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "LT": "LT.NS",
    "SBIN": "SBIN.NS",
    "AXISBANK": "AXISBANK.NS",
    "ITC": "ITC.NS",
    "HCLTECH": "HCLTECH.NS",
    "WIPRO": "WIPRO.NS",
    "MARUTI": "MARUTI.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TITAN": "TITAN.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "NTPC": "NTPC.NS",
    "POWERGRID": "POWERGRID.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "BPCL": "BPCL.NS",
    "ONGC": "ONGC.NS",
    "COALINDIA": "COALINDIA.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "DRREDDY": "DRREDDY.NS",
    "CIPLA": "CIPLA.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "TECHM": "TECHM.NS",
    "GRASIM": "GRASIM.NS",
    "M&M": "M&M.NS",
    "TATACONSUM": "TATACONSUM.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "TATAPOWER": "TATAPOWER.NS",
    "PIDILITIND": "PIDILITIND.NS",
    "DABUR": "DABUR.NS",
    "MARICO": "MARICO.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "HINDZINC": "HINDZINC.NS",
    "VEDL": "VEDL.NS",
    "SHREECEM": "SHREECEM.NS",
    "ADANIENT": "ADANIENT.NS",
}

TICKER_LIST = list(STOCKS.values())
NAME_LIST = list(STOCKS.keys())

SECTORS = {
    "RELIANCE": "Energy", "TCS": "IT", "INFY": "IT", "HDFCBANK": "Banking",
    "ICICIBANK": "Banking", "LT": "Infrastructure", "SBIN": "Banking",
    "AXISBANK": "Banking", "ITC": "FMCG", "HCLTECH": "IT", "WIPRO": "IT",
    "MARUTI": "Auto", "BAJFINANCE": "NBFC", "ASIANPAINT": "Paints",
    "SUNPHARMA": "Pharma", "TITAN": "Consumer", "ULTRACEMCO": "Cement",
    "NESTLEIND": "FMCG", "KOTAKBANK": "Banking", "NTPC": "Power",
    "POWERGRID": "Power", "TATASTEEL": "Metal", "BPCL": "Energy",
    "ONGC": "Energy", "COALINDIA": "Mining", "HINDUNILVR": "FMCG",
    "BRITANNIA": "FMCG", "DIVISLAB": "Pharma", "DRREDDY": "Pharma",
    "CIPLA": "Pharma", "EICHERMOT": "Auto", "HEROMOTOCO": "Auto",
    "BAJAJFINSV": "NBFC", "INDUSINDBK": "Banking", "TECHM": "IT",
    "GRASIM": "Diversified", "M&M": "Auto", "TATACONSUM": "FMCG",
    "APOLLOHOSP": "Healthcare", "TATAMOTORS": "Auto", "TATAPOWER": "Power",
    "PIDILITIND": "Chemicals", "DABUR": "FMCG", "MARICO": "FMCG",
    "ADANIPORTS": "Infrastructure", "JSWSTEEL": "Metal", "HINDZINC": "Metal",
    "VEDL": "Metal", "SHREECEM": "Cement", "ADANIENT": "Diversified",
}


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_bulk_data(period="1y"):
    data = yf.download(TICKER_LIST, period=period, interval="1d",
                       group_by="ticker", auto_adjust=True, progress=False)
    return data

@st.cache_data(ttl=3600)
def fetch_single_stock(ticker, period="1y"):
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    return df

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
    histogram = macd - signal
    return macd, signal, histogram

def rsi_label(rsi):
    if rsi < 30: return "Oversold 🟢"
    elif rsi < 50: return "Neutral-Low"
    elif rsi < 70: return "Neutral-High"
    else: return "Overbought 🔴"

def get_signal(rsi, price, ma50, ma200, macd_val, signal_val):
    score = 0
    if rsi < 35: score += 2
    elif rsi < 50: score += 1
    elif rsi > 70: score -= 2
    elif rsi > 60: score -= 1
    if price > ma50: score += 1
    if price > ma200: score += 1
    if ma50 > ma200: score += 1  # golden cross
    if macd_val > signal_val: score += 1
    else: score -= 1
    if score >= 3: return "BUY", score
    elif score <= 0: return "SELL", score
    else: return "HOLD", score

def get_rsi_status(rsi):
    if rsi < 30: return "Oversold"
    elif rsi > 70: return "Overbought"
    else: return "Normal"

def safe_get_close(bulk, ticker):
    try:
        close = bulk[ticker]["Close"].dropna()
        if hasattr(close, 'squeeze'):
            close = close.squeeze()
        return close
    except Exception:
        return pd.Series(dtype=float)

def safe_get_vol(bulk, ticker):
    try:
        vol = bulk[ticker]["Volume"].dropna()
        if hasattr(vol, 'squeeze'):
            vol = vol.squeeze()
        return vol
    except Exception:
        return pd.Series(dtype=float)

def build_signals_df(bulk):
    records = []
    for name, ticker in STOCKS.items():
        try:
            close = safe_get_close(bulk, ticker)
            vol = safe_get_vol(bulk, ticker)
            if len(close) < 60:
                continue
            rsi = float(compute_rsi(close).iloc[-1])
            ma50 = float(close.rolling(50).mean().iloc[-1])
            ma200 = float(close.rolling(min(200, len(close))).mean().iloc[-1])
            macd, sig_line, _ = compute_macd(close)
            signal, score = get_signal(rsi, float(close.iloc[-1]), ma50, ma200,
                                        float(macd.iloc[-1]), float(sig_line.iloc[-1]))
            vol_avg = float(vol.rolling(20).mean().iloc[-1]) if len(vol) >= 20 else float(vol.mean())
            vol_ratio = round(float(vol.iloc[-1]) / vol_avg, 2) if vol_avg > 0 else 1.0

            ret_1m = round((float(close.iloc[-1]) / float(close.iloc[-22]) - 1) * 100, 2) if len(close) >= 22 else None
            ret_3m = round((float(close.iloc[-1]) / float(close.iloc[-66]) - 1) * 100, 2) if len(close) >= 66 else None

            records.append({
                "Stock": name,
                "Ticker": ticker,
                "Sector": SECTORS.get(name, "Other"),
                "Price (₹)": round(float(close.iloc[-1]), 2),
                "RSI": round(rsi, 1),
                "RSI Status": get_rsi_status(rsi),
                "MA50": round(ma50, 2),
                "MA200": round(ma200, 2),
                "Price vs MA50": "Above ✅" if float(close.iloc[-1]) > ma50 else "Below ❌",
                "Price vs MA200": "Above ✅" if float(close.iloc[-1]) > ma200 else "Below ❌",
                "Golden Cross": "Yes ✅" if ma50 > ma200 else "No",
                "MACD Trend": "Bullish ↑" if float(macd.iloc[-1]) > float(sig_line.iloc[-1]) else "Bearish ↓",
                "Volume Spike": "High 🔥" if vol_ratio > 1.5 else ("Low" if vol_ratio < 0.7 else "Normal"),
                "Vol Ratio": vol_ratio,
                "1M Return%": ret_1m,
                "3M Return%": ret_3m,
                "Score": score,
                "Signal": signal,
            })
        except Exception:
            continue
    return pd.DataFrame(records)

def build_momentum_df(bulk):
    records = []
    for name, ticker in STOCKS.items():
        try:
            close = safe_get_close(bulk, ticker)
            if len(close) < 30:
                continue
            monthly = close.resample("ME").last()
            monthly_ret = monthly.pct_change().dropna()
            if len(monthly_ret) < 2:
                continue
            latest = monthly_ret.iloc[::-1]
            up_streak = 0
            down_streak = 0
            for r in latest:
                if r > 0:
                    if down_streak == 0:
                        up_streak += 1
                    else:
                        break
                else:
                    if up_streak == 0:
                        down_streak += 1
                    else:
                        break

            p = float(close.iloc[-1])
            ret_1m = round((p / float(close.iloc[-22]) - 1) * 100, 2) if len(close) >= 22 else None
            ret_3m = round((p / float(close.iloc[-66]) - 1) * 100, 2) if len(close) >= 66 else None
            ret_6m = round((p / float(close.iloc[-126]) - 1) * 100, 2) if len(close) >= 126 else None
            ret_1y = round((p / float(close.iloc[-252]) - 1) * 100, 2) if len(close) >= 252 else None

            records.append({
                "Stock": name,
                "Ticker": ticker,
                "Sector": SECTORS.get(name, "Other"),
                "Price (₹)": round(p, 2),
                "1M%": ret_1m,
                "3M%": ret_3m,
                "6M%": ret_6m,
                "1Y%": ret_1y,
                "Up Streak": up_streak,
                "Down Streak": down_streak,
                "Trend": "🟢 Rising" if up_streak >= 2 else ("🔴 Falling" if down_streak >= 2 else "➡ Mixed"),
            })
        except Exception:
            continue
    return pd.DataFrame(records)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 NSE Analyzer")
    st.markdown("---")

    selected_stock = st.selectbox("🔍 Select Stock for Analysis", NAME_LIST, index=0)
    selected_ticker = STOCKS[selected_stock]

    chart_period = st.selectbox("📅 Chart Duration", ["3mo", "6mo", "1y", "2y"], index=2)

    st.markdown("---")
    st.markdown("### 🧭 How to Read Signals?")
    st.markdown("""
    **Score System (max 6):**
    - ≥ 3 → 🟢 **BUY** (Strong upside signals)
    - 1–2 → 🟡 **HOLD** (Mixed signals)
    - ≤ 0 → 🔴 **SELL** (Weak/overbought)

    **Key Terms:**
    - **RSI < 30** → Stock oversold, may bounce
    - **RSI > 70** → Stock overbought, may fall
    - **Golden Cross** → Short-term MA crossed above long-term MA (bullish)
    - **Vol Spike** → Unusual volume = big move coming
    - **MACD Bullish** → Momentum turning positive
    """)
    st.markdown("---")
    st.caption("⚠️ For educational use only · Not financial advice · Data: yFinance")


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom: 16px;'>
  <div class='label-sm'>NSE INDIA · NIFTY 50 ANALYSIS DASHBOARD</div>
  <h1 style='font-size: 2rem; margin: 4px 0; color: #f1f5f9;'>
    📈 NSE Stock Analyzer
  </h1>
  <p style='color: #64748b; font-size: 13px; margin: 0;'>
    Live Buy/Sell Signals · RSI · MACD · Momentum Streaks · Sector View
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
with st.spinner("⏳ Loading market data... (first load takes ~30 sec)"):
    bulk = fetch_bulk_data(period="1y")
    signals_df = build_signals_df(bulk)
    momentum_df = build_momentum_df(bulk)

if signals_df.empty:
    st.error("❌ Could not load market data. Please refresh the page.")
    st.stop()

# ─────────────────────────────────────────────
# TOP KPIs
# ─────────────────────────────────────────────
buy_c = len(signals_df[signals_df["Signal"] == "BUY"])
sell_c = len(signals_df[signals_df["Signal"] == "SELL"])
hold_c = len(signals_df[signals_df["Signal"] == "HOLD"])
avg_rsi = round(signals_df["RSI"].mean(), 1)

valid_mom = momentum_df.dropna(subset=["1M%"])
top_g = valid_mom.sort_values("1M%", ascending=False).iloc[0] if not valid_mom.empty else None
top_l = valid_mom.sort_values("1M%").iloc[0] if not valid_mom.empty else None

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("🟢 BUY Signals", buy_c, help="Stocks with strong bullish indicators")
k2.metric("🔴 SELL Signals", sell_c, help="Stocks that are overbought or weakening")
k3.metric("🟡 HOLD Signals", hold_c, help="Mixed signals — wait and watch")
k4.metric("📊 Avg Market RSI", avg_rsi, help="Below 40 = market oversold, Above 60 = overbought")
if top_g is not None:
    k5.metric("🚀 Best (1 Month)", top_g["Stock"], f"+{top_g['1M%']}%")
if top_l is not None:
    k6.metric("📉 Worst (1 Month)", top_l["Stock"], f"{top_l['1M%']}%")

st.markdown("---")


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 Buy/Sell Signals",
    "📊 Momentum & Returns",
    "📈 Stock Deep Dive",
    "🏭 Sector Overview",
])


# ═══════════════════════════════════════════
# TAB 1: BUY/SELL SIGNALS
# ═══════════════════════════════════════════
with tab1:
    st.markdown("### 🧠 Technical Signal Scanner")
    st.markdown('<div class="tip-box">💡 <strong>How it works:</strong> Each stock gets a score from 0–6 based on RSI, Moving Averages, MACD, and Volume. Score ≥ 3 = BUY, Score 1-2 = HOLD, Score ≤ 0 = SELL.</div>', unsafe_allow_html=True)

    # Filters row
    fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 1])
    with fc1:
        sig_filter = st.selectbox("🎯 Signal Filter", ["All Signals", "BUY only", "SELL only", "HOLD only"])
    with fc2:
        sector_opts = ["All Sectors"] + sorted(set(SECTORS.values()))
        sec_filter = st.selectbox("🏭 Sector", sector_opts)
    with fc3:
        rsi_filter = st.selectbox("📊 RSI Status", ["All", "Oversold (<30)", "Overbought (>70)", "Normal (30-70)"])
    with fc4:
        sort_col = st.selectbox("↕️ Sort By", ["Score", "RSI", "Price (₹)", "1M Return%", "Vol Ratio"])

    # Apply filters
    df_view = signals_df.copy()
    if sig_filter != "All Signals":
        sig_map = {"BUY only": "BUY", "SELL only": "SELL", "HOLD only": "HOLD"}
        df_view = df_view[df_view["Signal"] == sig_map[sig_filter]]
    if sec_filter != "All Sectors":
        df_view = df_view[df_view["Sector"] == sec_filter]
    if rsi_filter == "Oversold (<30)":
        df_view = df_view[df_view["RSI"] < 30]
    elif rsi_filter == "Overbought (>70)":
        df_view = df_view[df_view["RSI"] > 70]
    elif rsi_filter == "Normal (30-70)":
        df_view = df_view[(df_view["RSI"] >= 30) & (df_view["RSI"] <= 70)]

    ascending = sig_filter == "SELL only"
    df_view = df_view.sort_values(sort_col, ascending=ascending)

    st.markdown(f"**{len(df_view)} stocks found**")

    display_cols = ["Stock", "Sector", "Price (₹)", "RSI", "RSI Status",
                    "Price vs MA50", "Price vs MA200", "Golden Cross",
                    "MACD Trend", "Volume Spike", "1M Return%", "Score", "Signal"]

    def style_signals(val):
        if val == "BUY": return "background-color: #052e16; color: #4ade80; font-weight: bold"
        elif val == "SELL": return "background-color: #2d0a0a; color: #f87171; font-weight: bold"
        elif val == "HOLD": return "background-color: #1c1408; color: #fbbf24; font-weight: bold"
        return ""

    def style_rsi(val):
        if isinstance(val, (int, float)):
            if val < 30: return "color: #4ade80; font-weight: bold"
            elif val > 70: return "color: #f87171; font-weight: bold"
        return ""

    def style_ret(val):
        if isinstance(val, (int, float)):
            if val is not None:
                if val > 5: return "color: #4ade80"
                elif val > 0: return "color: #86efac"
                elif val < -5: return "color: #f87171"
                elif val < 0: return "color: #fca5a5"
        return ""

    styled = df_view[display_cols].reset_index(drop=True).style \
        .map(style_signals, subset=["Signal"]) \
        .map(style_rsi, subset=["RSI"]) \
        .map(style_ret, subset=["1M Return%"])

    st.dataframe(styled, use_container_width=True, height=480)

    # Charts
    st.markdown("---")
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("#### 📊 Signal Distribution")
        sig_counts = signals_df["Signal"].value_counts()
        fig_pie = go.Figure(go.Pie(
            labels=sig_counts.index,
            values=sig_counts.values,
            hole=0.55,
            marker_colors=["#4ade80", "#fbbf24", "#f87171"],
            textinfo="label+percent",
            textfont_size=13,
        ))
        fig_pie.update_layout(
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font_color="#e2e8f0", height=280, margin=dict(t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with ch2:
        st.markdown("#### 📊 RSI Distribution (All Stocks)")
        fig_rsi = go.Figure(go.Histogram(
            x=signals_df["RSI"], nbinsx=20,
            marker_color="#3b82f6", opacity=0.8
        ))
        fig_rsi.add_vline(x=30, line_dash="dash", line_color="#4ade80",
                          annotation_text="30 — Oversold", annotation_font_color="#4ade80")
        fig_rsi.add_vline(x=70, line_dash="dash", line_color="#f87171",
                          annotation_text="70 — Overbought", annotation_font_color="#f87171")
        fig_rsi.update_layout(
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font_color="#e2e8f0", height=280,
            xaxis=dict(gridcolor="#334155", title="RSI Value"),
            yaxis=dict(gridcolor="#334155", title="No. of Stocks"),
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_rsi, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 2: MOMENTUM & RETURNS
# ═══════════════════════════════════════════
with tab2:
    st.markdown("### 📊 Momentum & Multi-Period Returns")
    st.markdown('<div class="tip-box">💡 <strong>Up Streak</strong> = Number of consecutive months the stock went UP. <strong>Down Streak</strong> = Consecutive months it fell. Higher streak = stronger momentum.</div>', unsafe_allow_html=True)

    m_fc1, m_fc2 = st.columns(2)
    with m_fc1:
        trend_filter = st.selectbox("🎯 Trend Filter", ["All", "🟢 Rising (2+ months up)", "🔴 Falling (2+ months down)"])
    with m_fc2:
        m_sector = st.selectbox("🏭 Sector Filter", ["All Sectors"] + sorted(set(SECTORS.values())), key="mom_sec")

    mom_view = momentum_df.copy()
    if trend_filter == "🟢 Rising (2+ months up)":
        mom_view = mom_view[mom_view["Up Streak"] >= 2]
    elif trend_filter == "🔴 Falling (2+ months down)":
        mom_view = mom_view[mom_view["Down Streak"] >= 2]
    if m_sector != "All Sectors":
        mom_view = mom_view[mom_view["Sector"] == m_sector]

    mom_view = mom_view.sort_values("1M%", ascending=False)

    def ret_style(val):
        if isinstance(val, (int, float)) and val is not None:
            if val > 10: return "color: #4ade80; font-weight:bold"
            elif val > 0: return "color: #86efac"
            elif val < -10: return "color: #f87171; font-weight:bold"
            elif val < 0: return "color: #fca5a5"
        return ""

    display_m = ["Stock", "Sector", "Price (₹)", "1M%", "3M%", "6M%", "1Y%",
                 "Up Streak", "Down Streak", "Trend"]
    st.dataframe(
        mom_view[display_m].reset_index(drop=True).style.map(
            ret_style, subset=["1M%", "3M%", "6M%", "1Y%"]
        ),
        use_container_width=True, height=400
    )

    st.markdown("---")

    # Top 15 stocks bar chart
    st.markdown("#### 🚀 Top 15 Gainers vs Losers (1 Month)")
    sorted_1m = momentum_df.dropna(subset=["1M%"]).sort_values("1M%", ascending=False)
    top15 = pd.concat([sorted_1m.head(8), sorted_1m.tail(7)])
    colors = ["#4ade80" if v > 0 else "#f87171" for v in top15["1M%"]]

    fig_bar = go.Figure(go.Bar(
        x=top15["Stock"], y=top15["1M%"],
        marker_color=colors,
        text=[f"{v:.1f}%" for v in top15["1M%"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
    ))
    fig_bar.add_hline(y=0, line_color="#475569", line_width=1)
    fig_bar.update_layout(
        paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
        font_color="#e2e8f0", height=360,
        xaxis=dict(gridcolor="#334155"),
        yaxis=dict(gridcolor="#334155", title="1-Month Return %"),
        margin=dict(t=10),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Multi-period return chart for top 10 by 1Y
    st.markdown("#### 📈 Multi-Period Returns — Top 10 Stocks (1Y)")
    top10_1y = momentum_df.dropna(subset=["1Y%"]).sort_values("1Y%", ascending=False).head(10)
    fig_multi = go.Figure()
    for period_col, color in [("1M%", "#3b82f6"), ("3M%", "#10b981"), ("6M%", "#f59e0b"), ("1Y%", "#8b5cf6")]:
        fig_multi.add_trace(go.Bar(
            name=period_col, x=top10_1y["Stock"], y=top10_1y[period_col],
            marker_color=color, opacity=0.85
        ))
    fig_multi.update_layout(
        barmode="group",
        paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
        font_color="#e2e8f0", height=380,
        xaxis=dict(gridcolor="#334155"),
        yaxis=dict(gridcolor="#334155", title="Return %"),
        legend=dict(bgcolor="#1e293b", bordercolor="#334155"),
        margin=dict(t=10),
    )
    st.plotly_chart(fig_multi, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 3: DEEP DIVE CHART
# ═══════════════════════════════════════════
with tab3:
    st.markdown(f"### 📈 Deep Dive: {selected_stock}")

    stock_data = fetch_single_stock(selected_ticker, period=chart_period)

    if stock_data.empty:
        st.error("❌ No data available for this stock.")
    else:
        # Squeeze to 1D series safely
        close = stock_data["Close"].squeeze()
        vol   = stock_data["Volume"].squeeze()
        high  = stock_data["High"].squeeze()
        low   = stock_data["Low"].squeeze()
        open_ = stock_data["Open"].squeeze()

        # Align all to close index to avoid length mismatch
        idx = close.index
        vol   = vol.reindex(idx).fillna(0)
        high  = high.reindex(idx)
        low   = low.reindex(idx)
        open_ = open_.reindex(idx)

        ma20  = close.rolling(20).mean()
        ma50  = close.rolling(50).mean()
        ma200 = close.rolling(min(200, len(close))).mean()
        rsi_s = compute_rsi(close)
        macd_line, sig_line, histogram = compute_macd(close)
        bb_upper = ma20 + 2 * close.rolling(20).std()
        bb_lower = ma20 - 2 * close.rolling(20).std()

        cur_price = float(close.iloc[-1])
        cur_rsi   = float(rsi_s.iloc[-1])
        cur_ma50  = float(ma50.iloc[-1]) if not pd.isna(ma50.iloc[-1]) else cur_price
        cur_ma200 = float(ma200.iloc[-1]) if not pd.isna(ma200.iloc[-1]) else cur_price
        signal_label, score_val = get_signal(
            cur_rsi, cur_price, cur_ma50, cur_ma200,
            float(macd_line.iloc[-1]), float(sig_line.iloc[-1])
        )

        ret_1m = round((cur_price / float(close.iloc[-22]) - 1) * 100, 2) if len(close) >= 22 else 0
        ret_3m = round((cur_price / float(close.iloc[-66]) - 1) * 100, 2) if len(close) >= 66 else 0

        badge_map = {"BUY": "badge-buy", "SELL": "badge-sell", "HOLD": "badge-hold"}
        badge = badge_map[signal_label]

        # Stats row
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Current Price", f"₹{cur_price:,.2f}")
        m2.metric("1M Return", f"{ret_1m:+.2f}%")
        m3.metric("3M Return", f"{ret_3m:+.2f}%")
        m4.metric("RSI (14)", f"{cur_rsi:.1f}", help="<30 = Oversold, >70 = Overbought")
        m5.metric("Signal Score", f"{score_val}/6")
        m6.markdown(f'<div style="margin-top:22px; text-align:center;"><span class="{badge}">{signal_label}</span></div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── CHART 1: Price with MA + Bollinger Bands
        st.markdown("#### 🕯️ Price Chart — Candlestick + Moving Averages + Bollinger Bands")
        st.markdown('<div class="tip-box">💡 <strong>Bollinger Bands</strong> (purple): When price touches lower band = oversold signal. Upper band = overbought. <strong>MA50</strong> (orange) and <strong>MA200</strong> (pink) = trend direction lines.</div>', unsafe_allow_html=True)

        fig_price = go.Figure()
        fig_price.add_trace(go.Candlestick(
            x=idx, open=open_, high=high, low=low, close=close,
            name="OHLC",
            increasing_line_color="#4ade80",
            decreasing_line_color="#f87171",
        ))
        fig_price.add_trace(go.Scatter(
            x=idx, y=bb_upper, name="BB Upper",
            line=dict(color="#8b5cf6", width=1, dash="dot"), opacity=0.6
        ))
        fig_price.add_trace(go.Scatter(
            x=idx, y=bb_lower, name="BB Lower",
            line=dict(color="#8b5cf6", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(139,92,246,0.06)", opacity=0.6
        ))
        fig_price.add_trace(go.Scatter(x=idx, y=ma20, name="MA 20 (short)",
            line=dict(color="#fbbf24", width=1.5)))
        fig_price.add_trace(go.Scatter(x=idx, y=ma50, name="MA 50 (medium)",
            line=dict(color="#3b82f6", width=1.5)))
        fig_price.add_trace(go.Scatter(x=idx, y=ma200, name="MA 200 (long)",
            line=dict(color="#ec4899", width=1.5, dash="dash")))
        fig_price.update_layout(
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0"), height=480,
            xaxis_rangeslider_visible=False,
            xaxis=dict(gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155", title="Price (₹)"),
            legend=dict(bgcolor="#0f172a", bordercolor="#334155"),
            margin=dict(t=10),
        )
        st.plotly_chart(fig_price, use_container_width=True)

        # ── CHART 2: RSI
        st.markdown("#### 📊 RSI — Relative Strength Index")
        st.markdown('<div class="tip-box">💡 RSI measures how fast the stock is moving. <strong>Below 30</strong> = stock is very oversold (possible buy opportunity). <strong>Above 70</strong> = stock is overbought (possible fall ahead).</div>', unsafe_allow_html=True)

        fig_rsi = go.Figure()
        rsi_colors = ["#4ade80" if v < 30 else ("#f87171" if v > 70 else "#f59e0b") for v in rsi_s]
        fig_rsi.add_trace(go.Scatter(
            x=idx, y=rsi_s, name="RSI",
            line=dict(color="#f59e0b", width=2),
        ))
        fig_rsi.add_hrect(y0=70, y1=100, fillcolor="#f87171", opacity=0.07, line_width=0,
                          annotation_text="Overbought Zone", annotation_font_color="#f87171",
                          annotation_position="top left")
        fig_rsi.add_hrect(y0=0, y1=30, fillcolor="#4ade80", opacity=0.07, line_width=0,
                          annotation_text="Oversold Zone", annotation_font_color="#4ade80",
                          annotation_position="bottom left")
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#f87171", line_width=1)
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#4ade80", line_width=1)
        fig_rsi.update_layout(
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0"), height=260,
            xaxis=dict(gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155", title="RSI", range=[0, 100]),
            margin=dict(t=10),
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

        # ── CHART 3: MACD
        st.markdown("#### 📉 MACD — Momentum Indicator")
        st.markdown('<div class="tip-box">💡 When <strong>MACD line (blue)</strong> crosses above <strong>Signal line (pink)</strong> = bullish signal (possible buy). Below = bearish signal. <strong>Green bars</strong> = positive momentum, <strong>red bars</strong> = negative.</div>', unsafe_allow_html=True)

        fig_macd = make_subplots(rows=1, cols=1)
        hist_colors_list = ["#4ade8880" if h >= 0 else "#f8717180" for h in histogram]
        fig_macd.add_trace(go.Bar(
            x=idx,
            y=list(histogram),
            name="Histogram",
            marker=dict(color=hist_colors_list),
        ))
        fig_macd.add_trace(go.Scatter(x=idx, y=macd_line, name="MACD",
            line=dict(color="#3b82f6", width=2)))
        fig_macd.add_trace(go.Scatter(x=idx, y=sig_line, name="Signal",
            line=dict(color="#ec4899", width=2)))
        fig_macd.update_layout(
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0"), height=260,
            xaxis=dict(gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155", title="MACD"),
            legend=dict(bgcolor="#0f172a", bordercolor="#334155"),
            margin=dict(t=10),
        )
        st.plotly_chart(fig_macd, use_container_width=True)

        # ── CHART 4: Volume
        st.markdown("#### 📦 Volume Analysis")
        st.markdown('<div class="tip-box">💡 High volume on an up day = strong buying. High volume on a down day = heavy selling. Red line shows 20-day average volume.</div>', unsafe_allow_html=True)

        vol_20ma = vol.rolling(20).mean()
        vol_colors_list = ["#4ade8866" if float(c) >= float(o) else "#f8717166"
                           for c, o in zip(close, open_)]
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=idx,
            y=list(vol),
            name="Volume",
            marker=dict(color=vol_colors_list),
        ))
        fig_vol.add_trace(go.Scatter(
            x=idx, y=vol_20ma, name="20-day Avg",
            line=dict(color="#f59e0b", width=1.5, dash="dot")
        ))
        fig_vol.update_layout(
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0"), height=260,
            xaxis=dict(gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155", title="Volume"),
            legend=dict(bgcolor="#0f172a"),
            margin=dict(t=10),
        )
        st.plotly_chart(fig_vol, use_container_width=True)

        # Key levels
        st.markdown("---")
        st.markdown("### 🎯 Key Price Levels")
        lc1, lc2, lc3, lc4, lc5 = st.columns(5)
        w52h = float(close.rolling(min(252, len(close))).max().iloc[-1])
        w52l = float(close.rolling(min(252, len(close))).min().iloc[-1])
        from_52h = round((cur_price / w52h - 1) * 100, 1)
        from_52l = round((cur_price / w52l - 1) * 100, 1)
        lc1.metric("52W High", f"₹{w52h:,.1f}", f"{from_52h}% from high")
        lc2.metric("52W Low", f"₹{w52l:,.1f}", f"+{from_52l}% from low")
        lc3.metric("MA 50", f"₹{cur_ma50:,.1f}")
        lc4.metric("MA 200", f"₹{cur_ma200:,.1f}")
        lc5.metric("BB Upper", f"₹{float(bb_upper.iloc[-1]):,.1f}")


# ═══════════════════════════════════════════
# TAB 4: SECTOR OVERVIEW
# ═══════════════════════════════════════════
with tab4:
    st.markdown("### 🏭 Sector-wise Performance")
    st.markdown('<div class="tip-box">💡 Compare how different sectors (Banking, IT, FMCG, etc.) are performing. Helps you find which sectors are strong or weak right now.</div>', unsafe_allow_html=True)

    merged = signals_df.merge(momentum_df[["Stock", "1M%", "3M%", "6M%", "1Y%"]], on="Stock", how="left")

    # Sector summary
    sector_summary = merged.groupby("Sector").agg(
        Stocks=("Stock", "count"),
        Avg_RSI=("RSI", lambda x: round(x.mean(), 1)),
        BUY_Count=("Signal", lambda x: (x == "BUY").sum()),
        SELL_Count=("Signal", lambda x: (x == "SELL").sum()),
        Avg_1M=("1M%", lambda x: round(x.mean(), 2)),
        Avg_3M=("3M%", lambda x: round(x.mean(), 2)),
        Avg_1Y=("1Y%", lambda x: round(x.mean(), 2)),
    ).reset_index()
    sector_summary.columns = ["Sector", "No. of Stocks", "Avg RSI",
                               "BUY Signals", "SELL Signals",
                               "Avg 1M%", "Avg 3M%", "Avg 1Y%"]
    sector_summary = sector_summary.sort_values("Avg 1M%", ascending=False)

    st.dataframe(
        sector_summary.reset_index(drop=True).style.map(
            ret_style, subset=["Avg 1M%", "Avg 3M%", "Avg 1Y%"]
        ),
        use_container_width=True, height=380
    )

    # Sector return chart
    st.markdown("---")
    sc1, sc2 = st.columns(2)

    with sc1:
        st.markdown("#### 📊 Sector 1-Month Return")
        fig_sec_bar = go.Figure(go.Bar(
            x=sector_summary["Sector"],
            y=sector_summary["Avg 1M%"],
            marker_color=["#4ade80" if v > 0 else "#f87171" for v in sector_summary["Avg 1M%"]],
            text=[f"{v:.1f}%" for v in sector_summary["Avg 1M%"]],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=11),
        ))
        fig_sec_bar.update_layout(
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font_color="#e2e8f0", height=340,
            xaxis=dict(gridcolor="#334155", tickangle=-30),
            yaxis=dict(gridcolor="#334155", title="Avg 1M Return %"),
            margin=dict(t=30, b=80),
        )
        st.plotly_chart(fig_sec_bar, use_container_width=True)

    with sc2:
        st.markdown("#### 🧠 Buy vs Sell Signals by Sector")
        fig_sec_sig = go.Figure()
        fig_sec_sig.add_trace(go.Bar(
            name="BUY", x=sector_summary["Sector"], y=sector_summary["BUY Signals"],
            marker_color="#4ade80", opacity=0.85
        ))
        fig_sec_sig.add_trace(go.Bar(
            name="SELL", x=sector_summary["Sector"], y=sector_summary["SELL Signals"],
            marker_color="#f87171", opacity=0.85
        ))
        fig_sec_sig.update_layout(
            barmode="group",
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font_color="#e2e8f0", height=340,
            xaxis=dict(gridcolor="#334155", tickangle=-30),
            yaxis=dict(gridcolor="#334155", title="No. of Stocks"),
            legend=dict(bgcolor="#0f172a"),
            margin=dict(t=30, b=80),
        )
        st.plotly_chart(fig_sec_sig, use_container_width=True)

    # Stock breakdown by sector
    st.markdown("---")
    st.markdown("#### 🔍 All Stocks by Sector")
    sec_choose = st.selectbox("Select Sector to Explore", sorted(set(SECTORS.values())))
    sec_stocks = merged[merged["Sector"] == sec_choose].sort_values("Score", ascending=False)
    show_cols = ["Stock", "Price (₹)", "RSI", "RSI Status", "MACD Trend", "1M%", "3M%", "Score", "Signal"]
    st.dataframe(
        sec_stocks[show_cols].reset_index(drop=True).style
            .map(style_signals, subset=["Signal"])
            .map(style_rsi, subset=["RSI"])
            .map(ret_style, subset=["1M%", "3M%"]),
        use_container_width=True, height=300
    )


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#475569; font-family: IBM Plex Mono, monospace; font-size:11px; padding: 8px 0;'>
  NSE Stock Analyzer · Data via yFinance · Refreshes every hour · ⚠️ Not financial advice — for educational use only
</div>
""", unsafe_allow_html=True)
