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
    page_title="Smart Stock Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS — White/Light Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #f8fafc;
    color: #1e293b;
}

.stApp { background-color: #f8fafc; }

h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }

.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.buy-badge {
    background: linear-gradient(90deg, #dcfce7, #bbf7d0);
    color: #166534;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    border: 1px solid #86efac;
}

.sell-badge {
    background: linear-gradient(90deg, #fee2e2, #fecaca);
    color: #991b1b;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    border: 1px solid #fca5a5;
}

.neutral-badge {
    background: linear-gradient(90deg, #fef3c7, #fde68a);
    color: #854d0e;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    border: 1px solid #fcd34d;
}

.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    color: #3b82f6;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.stDataFrame { font-family: 'JetBrains Mono', monospace; font-size: 13px; }

div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.stSelectbox > div > div { background: #ffffff; border-color: #e2e8f0; }
.stTabs [data-baseweb="tab"] { font-family: 'Syne', sans-serif; font-size: 14px; }
.stTabs [data-baseweb="tab-list"] { background: #f1f5f9; }
.stTabs [aria-selected="true"] { color: #3b82f6 !important; border-color: #3b82f6 !important; }

hr { border-color: #e2e8f0; }

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

[data-testid="stSidebar"] .css-1d391kg {
    background-color: #ffffff;
}

/* DataFrame styling */
.stDataFrame {
    background-color: #ffffff;
}

/* Input fields */
.stTextInput > div > div > input {
    background-color: #ffffff;
    color: #1e293b;
}

/* Selectbox */
.stSelectbox label {
    color: #1e293b !important;
}

/* Radio buttons */
.stRadio label {
    color: #1e293b !important;
}

/* Caption text */
.caption {
    color: #64748b;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STOCK LIST — NIFTY 200 (Extended)
# ─────────────────────────────────────────────
STOCKS = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","SBIN.NS","AXISBANK.NS","ITC.NS","HCLTECH.NS",
    "WIPRO.NS","MARUTI.NS","BAJFINANCE.NS","ASIANPAINT.NS","SUNPHARMA.NS",
    "TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS","KOTAKBANK.NS","NTPC.NS",
    "POWERGRID.NS","ADANIENT.NS","ADANIPORTS.NS","JSWSTEEL.NS","TATASTEEL.NS",
    "BPCL.NS","ONGC.NS","COALINDIA.NS","HINDUNILVR.NS","BRITANNIA.NS",
    "DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","EICHERMOT.NS","HEROMOTOCO.NS",
    "BAJAJFINSV.NS","INDUSINDBK.NS","TECHM.NS","GRASIM.NS","SHREECEM.NS",
    "M&M.NS","TATACONSUM.NS","APOLLOHOSP.NS","HINDZINC.NS","VEDL.NS",
    "TATAMOTORS.NS","TATAPOWER.NS","PIDILITIND.NS","DABUR.NS","MARICO.NS"
]


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_bulk_data(period="1y"):
    """Fetch bulk Close/Volume data for all stocks"""
    data = yf.download(STOCKS, period=period, interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    return data

@st.cache_data(ttl=3600)
def fetch_single_stock(ticker, period="2y"):
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram

def get_signal(rsi, price, ma50, ma200, macd_val, signal_val):
    score = 0
    if rsi < 35: score += 2
    elif rsi < 50: score += 1
    elif rsi > 70: score -= 2
    elif rsi > 60: score -= 1
    if price > ma50: score += 1
    if price > ma200: score += 1
    if price > ma50 and ma50 > ma200: score += 1  # golden cross zone
    if macd_val > signal_val: score += 1
    else: score -= 1
    if score >= 3: return "BUY", score
    elif score <= 0: return "SELL", score
    else: return "HOLD", score

def get_momentum_streaks(bulk_data):
    """Compute how many consecutive months a stock has been up/down"""
    records = []
    for ticker in STOCKS:
        try:
            close = bulk_data[ticker]["Close"].dropna()
            if len(close) < 30:
                continue
            # Resample to monthly
            monthly = close.resample("ME").last()
            monthly_ret = monthly.pct_change().dropna()
            if len(monthly_ret) < 3:
                continue
            # Count consecutive up/down from latest
            latest = monthly_ret.iloc[::-1]  # reverse
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

            last_price = close.iloc[-1]
            ret_1m = (close.iloc[-1] / close.iloc[-22] - 1) * 100 if len(close) >= 22 else None
            ret_3m = (close.iloc[-1] / close.iloc[-66] - 1) * 100 if len(close) >= 66 else None
            ret_6m = (close.iloc[-1] / close.iloc[-126] - 1) * 100 if len(close) >= 126 else None
            ret_1y = (close.iloc[-1] / close.iloc[-252] - 1) * 100 if len(close) >= 252 else None

            records.append({
                "Stock": ticker.replace(".NS", ""),
                "Ticker": ticker,
                "Price (₹)": round(last_price, 2),
                "1M Ret%": round(ret_1m, 2) if ret_1m else None,
                "3M Ret%": round(ret_3m, 2) if ret_3m else None,
                "6M Ret%": round(ret_6m, 2) if ret_6m else None,
                "1Y Ret%": round(ret_1y, 2) if ret_1y else None,
                "Up Streak (mo)": up_streak,
                "Down Streak (mo)": down_streak,
            })
        except Exception:
            continue
    return pd.DataFrame(records)

def get_signals_table(bulk_data):
    records = []
    for ticker in STOCKS:
        try:
            close = bulk_data[ticker]["Close"].dropna()
            vol = bulk_data[ticker]["Volume"].dropna()
            if len(close) < 60:
                continue
            rsi = compute_rsi(close).iloc[-1]
            ma50 = close.rolling(50).mean().iloc[-1]
            ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else close.rolling(len(close)).mean().iloc[-1]
            macd, signal_line, _ = compute_macd(close)
            signal, score = get_signal(rsi, close.iloc[-1], ma50, ma200, macd.iloc[-1], signal_line.iloc[-1])
            vol_avg = vol.rolling(20).mean().iloc[-1]
            vol_ratio = round(vol.iloc[-1] / vol_avg, 2) if vol_avg > 0 else 1.0
            records.append({
                "Stock": ticker.replace(".NS", ""),
                "Ticker": ticker,
                "Price (₹)": round(close.iloc[-1], 2),
                "RSI": round(rsi, 1),
                "MA50": round(ma50, 2),
                "MA200": round(ma200, 2),
                "MACD Signal": "↑ Bullish" if macd.iloc[-1] > signal_line.iloc[-1] else "↓ Bearish",
                "Vol Ratio": vol_ratio,
                "Score": score,
                "Signal": signal,
            })
        except Exception:
            continue
    return pd.DataFrame(records)

def monthly_heatmap_data(bulk_data):
    rows = {}
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for ticker in STOCKS:
        try:
            close = bulk_data[ticker]["Close"].dropna()
            monthly = close.resample("ME").last()
            monthly_ret = monthly.pct_change().dropna() * 100
            name = ticker.replace(".NS","")
            row = {}
            for idx, val in monthly_ret.items():
                m = months[idx.month - 1]
                y = str(idx.year)
                row[f"{y}-{m}"] = round(val, 2)
            rows[name] = row
        except Exception:
            continue
    return pd.DataFrame(rows).T


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">⚙ Dashboard Controls</div>', unsafe_allow_html=True)
    st.markdown("## 📊 Smart Stock Dashboard")
    st.markdown("---")

    selected_stock = st.selectbox(
        "🔍 Deep Dive Stock",
        [s.replace(".NS","") for s in STOCKS],
        index=0
    )
    selected_ticker = selected_stock + ".NS"

    chart_period = st.selectbox(
        "📅 Chart Period",
        ["3mo", "6mo", "1y", "2y", "5y"],
        index=2
    )

    st.markdown("---")
    st.markdown('<div class="section-header">📌 Legend</div>', unsafe_allow_html=True)
    st.markdown("""
    - 🟢 **BUY** — Strong fundamentals + momentum  
    - 🔴 **SELL** — Weak/overbought signals  
    - 🟡 **HOLD** — Mixed signals  
    - **RSI < 35** → Oversold (potential buy)  
    - **RSI > 70** → Overbought (caution)  
    - **Golden Cross** → MA50 > MA200 ✅  
    """)
    st.markdown("---")
    st.caption("Data via yFinance · Refreshes hourly")


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom: 8px;'>
  <div class='section-header'>NIFTY 200 ANALYSIS ENGINE</div>
  <h1 style='font-size: 2.2rem; margin: 0; background: linear-gradient(90deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
    📊 Smart Stock Dashboard
  </h1>
  <p style='color: #64748b; font-family: JetBrains Mono, monospace; font-size: 13px; margin-top: 6px;'>
    Real-time · RSI · MACD · Momentum Streaks · Buy/Sell Signals · Monthly Returns
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
with st.spinner("🔄 Fetching market data... (can take 30-60 sec first time)"):
    bulk = fetch_bulk_data(period="1y")

momentum_df = get_momentum_streaks(bulk)
signals_df = get_signals_table(bulk)


# ─────────────────────────────────────────────
# TOP KPIs
# ─────────────────────────────────────────────
buy_count = len(signals_df[signals_df["Signal"] == "BUY"])
sell_count = len(signals_df[signals_df["Signal"] == "SELL"])
hold_count = len(signals_df[signals_df["Signal"] == "HOLD"])
avg_rsi = round(signals_df["RSI"].mean(), 1)
top_gainer = momentum_df.sort_values("1M Ret%", ascending=False).iloc[0]
top_loser = momentum_df.sort_values("1M Ret%").iloc[0]

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("🟢 BUY Signals", buy_count)
k2.metric("🔴 SELL Signals", sell_count)
k3.metric("🟡 HOLD Signals", hold_count)
k4.metric("📊 Avg RSI", avg_rsi)
k5.metric("🚀 Top Gainer (1M)", top_gainer["Stock"], f"{top_gainer['1M Ret%']}%")
k6.metric("📉 Top Loser (1M)", top_loser["Stock"], f"{top_loser['1M Ret%']}%")

st.markdown("---")


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Momentum Trends",
    "🧠 Buy/Sell Signals",
    "📅 Monthly Returns",
    "📈 Deep Dive Chart",
    "🏆 All Stocks Ranking"
])


# ═══════════════════════════════════════════
# TAB 1: MOMENTUM TRENDS
# ═══════════════════════════════════════════
with tab1:
    st.markdown("### 📈 Stocks Consistently Going UP (Consecutive Monthly Gains)")
    st.caption("Stocks with the highest streak of month-on-month positive returns")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🚀 TOP 20 — RISING STREAK</div>', unsafe_allow_html=True)
        top_up = momentum_df[momentum_df["Up Streak (mo)"] > 0].sort_values(
            ["Up Streak (mo)", "1M Ret%"], ascending=False
        ).head(20)

        # Color styling
        def color_up(val):
            if isinstance(val, float) and val > 0:
                return "background-color: #dcfce7; color: #166534"
            elif isinstance(val, float) and val < 0:
                return "color: #dc2626"
            return ""

        display_up = top_up[["Stock", "Price (₹)", "Up Streak (mo)", "1M Ret%", "3M Ret%", "6M Ret%", "1Y Ret%"]].reset_index(drop=True)
        st.dataframe(
            display_up.style.map(color_up, subset=["1M Ret%","3M Ret%","6M Ret%","1Y Ret%"]),
            use_container_width=True,
            height=550
        )

    with col2:
        st.markdown('<div class="section-header">📉 TOP 20 — FALLING STREAK</div>', unsafe_allow_html=True)
        top_down = momentum_df[momentum_df["Down Streak (mo)"] > 0].sort_values(
            ["Down Streak (mo)", "1M Ret%"], ascending=True
        ).head(20)

        def color_down(val):
            if isinstance(val, float) and val < 0:
                return "background-color: #fee2e2; color: #991b1b"
            elif isinstance(val, float) and val > 0:
                return "color: #16a34a"
            return ""

        display_down = top_down[["Stock", "Price (₹)", "Down Streak (mo)", "1M Ret%", "3M Ret%", "6M Ret%", "1Y Ret%"]].reset_index(drop=True)
        st.dataframe(
            display_down.style.map(color_down, subset=["1M Ret%","3M Ret%","6M Ret%","1Y Ret%"]),
            use_container_width=True,
            height=550
        )

    st.markdown("---")
    st.markdown("### 📊 Multi-Period Return Comparison — Top 20 Gainers (1Y)")
    top20_1y = momentum_df.dropna(subset=["1Y Ret%"]).sort_values("1Y Ret%", ascending=False).head(20)
    fig_bar = go.Figure()
    periods = ["1M Ret%","3M Ret%","6M Ret%","1Y Ret%"]
    colors = ["#3b82f6","#10b981","#f59e0b","#8b5cf6"]
    for p, c in zip(periods, colors):
        fig_bar.add_trace(go.Bar(
            name=p.replace(" Ret%",""),
            x=top20_1y["Stock"],
            y=top20_1y[p],
            marker_color=c,
            opacity=0.85
        ))
    fig_bar.update_layout(
        barmode="group",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font_color="#1e293b",
        legend_bgcolor="#f8fafc",
        height=420,
        xaxis=dict(gridcolor="#e2e8f0"),
        yaxis=dict(gridcolor="#e2e8f0", title="Return %"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 2: BUY/SELL SIGNALS
# ═══════════════════════════════════════════
with tab2:
    st.markdown("### 🧠 Technical Signal Analysis")
    st.caption("Based on RSI, Moving Averages (MA50/MA200), MACD, and Volume — composite score")

    sig_col1, sig_col2 = st.columns([1.2, 1])

    with sig_col1:
        filter_sig = st.radio("Filter by Signal", ["ALL", "BUY", "HOLD", "SELL"], horizontal=True)

    with sig_col2:
        sort_by = st.selectbox("Sort by", ["Score", "RSI", "Price (₹)", "Vol Ratio"], index=0)

    filtered = signals_df if filter_sig == "ALL" else signals_df[signals_df["Signal"] == filter_sig]
    filtered = filtered.sort_values(sort_by, ascending=(filter_sig == "SELL"))

    def signal_color(val):
        if val == "BUY": return "background-color: #dcfce7; color: #166534; font-weight:bold"
        elif val == "SELL": return "background-color: #fee2e2; color: #991b1b; font-weight:bold"
        else: return "background-color: #fef3c7; color: #854d0e; font-weight:bold"

    def rsi_color(val):
        if isinstance(val, float):
            if val < 35: return "color: #16a34a"
            elif val > 70: return "color: #dc2626"
        return ""

    display_cols = ["Stock","Price (₹)","RSI","MA50","MA200","MACD Signal","Vol Ratio","Score","Signal"]
    styled = filtered[display_cols].reset_index(drop=True).style\
        .map(signal_color, subset=["Signal"])\
        .map(rsi_color, subset=["RSI"])

    st.dataframe(styled, use_container_width=True, height=500)

    st.markdown("---")
    st.markdown("### 📊 RSI Distribution")
    fig_rsi = px.histogram(
        signals_df, x="RSI", nbins=20,
        color_discrete_sequence=["#3b82f6"],
        title="RSI Distribution Across All Stocks"
    )
    fig_rsi.add_vline(x=30, line_dash="dash", line_color="#10b981", annotation_text="Oversold (30)", annotation_font_color="#10b981")
    fig_rsi.add_vline(x=70, line_dash="dash", line_color="#ef4444", annotation_text="Overbought (70)", annotation_font_color="#ef4444")
    fig_rsi.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font_color="#1e293b", height=320,
        xaxis=dict(gridcolor="#e2e8f0"),
        yaxis=dict(gridcolor="#e2e8f0")
    )
    st.plotly_chart(fig_rsi, use_container_width=True)

    st.markdown("### 🗺 Score vs RSI Bubble Chart")
    merged = signals_df.merge(momentum_df[["Ticker","1M Ret%"]], on="Ticker", how="left")
    fig_bubble = px.scatter(
        merged,
        x="RSI", y="Score",
        color="Signal",
        size="Vol Ratio",
        hover_data=["Stock","Price (₹)","1M Ret%"],
        color_discrete_map={"BUY":"#10b981","HOLD":"#f59e0b","SELL":"#ef4444"},
        title="Score vs RSI (bubble size = Volume Ratio)"
    )
    fig_bubble.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font_color="#1e293b", height=380,
        xaxis=dict(gridcolor="#e2e8f0"),
        yaxis=dict(gridcolor="#e2e8f0")
    )
    st.plotly_chart(fig_bubble, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 3: MONTHLY RETURNS HEATMAP
# ═══════════════════════════════════════════
with tab3:
    st.markdown("### 📅 Month-on-Month Return Heatmap")
    st.caption("Green = Positive month · Red = Negative month · Intensity = Magnitude")

    year_filter = st.selectbox("Select Year", ["2025","2024","2023","2022"], index=0)
    months_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    hmap_df = monthly_heatmap_data(bulk)
    year_cols = [c for c in hmap_df.columns if c.startswith(year_filter + "-")]

    if not year_cols:
        st.warning(f"No data for {year_filter} yet. Try 2024.")
    else:
        hmap_year = hmap_df[year_cols].copy()
        hmap_year.columns = [c.split("-")[1] for c in hmap_year.columns]
        existing = [m for m in months_order if m in hmap_year.columns]
        hmap_year = hmap_year[existing]

        fig_heat = go.Figure(data=go.Heatmap(
            z=hmap_year.values,
            x=hmap_year.columns.tolist(),
            y=hmap_year.index.tolist(),
            colorscale=[
                [0.0, "#dc2626"],
                [0.35, "#ef4444"],
                [0.5, "#f8fafc"],
                [0.65, "#10b981"],
                [1.0, "#059669"]
            ],
            zmid=0,
            text=hmap_year.round(1).values,
            texttemplate="%{text}%",
            textfont={"size": 10, "family": "JetBrains Mono", "color": "#1e293b"},
            colorbar=dict(
                tickfont=dict(color="#1e293b"),
                title=dict(text="Ret%", font=dict(color="#1e293b"))
            )
        ))
        fig_heat.update_layout(
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font_color="#1e293b",
            height=max(400, len(hmap_year) * 22),
            xaxis=dict(side="top"),
            margin=dict(l=120)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 Year-on-Year Performance")
    yoy_records = []
    for ticker in STOCKS:
        try:
            close = bulk[ticker]["Close"].dropna()
            yearly = close.resample("YE").last()
            yr_ret = yearly.pct_change().dropna() * 100
            for yr, val in yr_ret.items():
                yoy_records.append({"Stock": ticker.replace(".NS",""), "Year": str(yr.year), "Return %": round(val, 2)})
        except Exception:
            continue
    yoy_df = pd.DataFrame(yoy_records)

    if not yoy_df.empty:
        top_yoy_stocks = momentum_df.dropna(subset=["1Y Ret%"]).sort_values("1Y Ret%", ascending=False).head(15)["Stock"].tolist()
        yoy_filtered = yoy_df[yoy_df["Stock"].isin(top_yoy_stocks)]
        fig_yoy = px.bar(
            yoy_filtered, x="Year", y="Return %", color="Stock",
            barmode="group", title="Year-on-Year Returns — Top 15 Stocks",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_yoy.update_layout(
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font_color="#1e293b", height=420,
            xaxis=dict(gridcolor="#e2e8f0"),
            yaxis=dict(gridcolor="#e2e8f0")
        )
        st.plotly_chart(fig_yoy, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 4: DEEP DIVE CHART
# ═══════════════════════════════════════════
with tab4:
    st.markdown(f"### 📈 Deep Dive: {selected_stock}")

    stock_data = fetch_single_stock(selected_ticker, period=chart_period)

    if stock_data.empty:
        st.error("No data found for this stock.")
    else:
        close = stock_data["Close"].squeeze()
        vol = stock_data["Volume"].squeeze()
        high = stock_data["High"].squeeze()
        low = stock_data["Low"].squeeze()
        open_ = stock_data["Open"].squeeze()

        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()
        rsi_series = compute_rsi(close)
        macd_line, signal_line, histogram = compute_macd(close)
        upper_bb = ma20 + 2 * close.rolling(20).std()
        lower_bb = ma20 - 2 * close.rolling(20).std()

        # Quick stats
        cur_price = close.iloc[-1]
        ret_1m = (cur_price / close.iloc[-22] - 1) * 100 if len(close) >= 22 else 0
        ret_3m = (cur_price / close.iloc[-66] - 1) * 100 if len(close) >= 66 else 0
        cur_rsi = rsi_series.iloc[-1]
        signal_label, score_val = get_signal(
            cur_rsi, cur_price,
            ma50.iloc[-1] if not pd.isna(ma50.iloc[-1]) else cur_price,
            ma200.iloc[-1] if not pd.isna(ma200.iloc[-1]) else cur_price,
            macd_line.iloc[-1], signal_line.iloc[-1]
        )
        badge = {"BUY": "buy-badge", "SELL": "sell-badge", "HOLD": "neutral-badge"}[signal_label]

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Current Price", f"₹{cur_price:,.2f}")
        m2.metric("1M Return", f"{ret_1m:.2f}%")
        m3.metric("3M Return", f"{ret_3m:.2f}%")
        m4.metric("RSI (14)", f"{cur_rsi:.1f}")
        m5.metric("Signal Score", score_val)
        m6.markdown(f'<div class="{badge}" style="text-align: center; margin-top: 25px;">{signal_label}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # MAIN CHART — Candlestick + MAs + BB + Volume + RSI + MACD
        fig = make_subplots(
            rows=4, cols=1, shared_xaxes=True,
            row_heights=[0.55, 0.15, 0.15, 0.15],
            vertical_spacing=0.02,
            subplot_titles=["Price + MAs + Bollinger Bands", "Volume", "RSI (14)", "MACD"]
        )

        # Candlestick (removed invalid fillcolor parameters)
        fig.add_trace(go.Candlestick(
            x=stock_data.index, 
            open=open_, 
            high=high, 
            low=low, 
            close=close,
            name="OHLC",
            increasing_line_color="#10b981", 
            decreasing_line_color="#ef4444"
        ), row=1, col=1)

        # Bollinger Bands
        fig.add_trace(go.Scatter(x=stock_data.index, y=upper_bb, name="BB Upper",
            line=dict(color="#8b5cf6", width=1, dash="dot"), opacity=0.7), row=1, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=lower_bb, name="BB Lower",
            line=dict(color="#8b5cf6", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(139,92,246,0.05)", opacity=0.7), row=1, col=1)

        # Moving Averages
        fig.add_trace(go.Scatter(x=stock_data.index, y=ma20, name="MA20",
            line=dict(color="#f59e0b", width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=ma50, name="MA50",
            line=dict(color="#3b82f6", width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=ma200, name="MA200",
            line=dict(color="#ec4899", width=1.5, dash="dash")), row=1, col=1)

        # Volume
        vol_colors = ["#10b98166" if c >= o else "#ef444466"
                      for c, o in zip(close, open_)]
        fig.add_trace(go.Bar(x=stock_data.index, y=vol, name="Volume",
            marker_color=vol_colors), row=2, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=stock_data.index, y=rsi_series, name="RSI",
            line=dict(color="#f59e0b", width=2)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#10b981", row=3, col=1)

        # MACD
        fig.add_trace(go.Scatter(x=stock_data.index, y=macd_line, name="MACD",
            line=dict(color="#3b82f6", width=1.5)), row=4, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=signal_line, name="Signal",
            line=dict(color="#ec4899", width=1.5)), row=4, col=1)
        hist_colors = ["#10b98188" if h >= 0 else "#ef444488" for h in histogram]
        fig.add_trace(go.Bar(x=stock_data.index, y=histogram, name="Histogram",
            marker_color=hist_colors), row=4, col=1)

        fig.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(color="#1e293b", family="JetBrains Mono"),
            height=900,
            xaxis_rangeslider_visible=False,
            legend=dict(bgcolor="#f8fafc", bordercolor="#e2e8f0"),
        )
        for i in range(1, 5):
            fig.update_xaxes(gridcolor="#e2e8f0", row=i, col=1)
            fig.update_yaxes(gridcolor="#e2e8f0", row=i, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # Support / Resistance
        st.markdown("### 🎯 Key Levels")
        lc1, lc2, lc3, lc4 = st.columns(4)
        lc1.metric("52W High", f"₹{close.rolling(252).max().iloc[-1]:,.2f}" if len(close) >= 252 else "N/A")
        lc2.metric("52W Low", f"₹{close.rolling(252).min().iloc[-1]:,.2f}" if len(close) >= 252 else "N/A")
        lc3.metric("BB Upper", f"₹{upper_bb.iloc[-1]:,.2f}")
        lc4.metric("BB Lower", f"₹{lower_bb.iloc[-1]:,.2f}")


# ═══════════════════════════════════════════
# TAB 5: ALL STOCKS RANKING
# ═══════════════════════════════════════════
with tab5:
    st.markdown("### 🏆 Full Stock Ranking — Composite View")
    st.caption("All signals + returns in one table. Sort any column.")

    full = momentum_df.merge(
        signals_df[["Ticker","RSI","MACD Signal","Score","Signal","Vol Ratio"]],
        on="Ticker", how="left"
    ).drop(columns=["Ticker"]).sort_values("Score", ascending=False).reset_index(drop=True)
    full.index += 1

    def full_color(val):
        if val == "BUY": return "background-color: #dcfce7; color: #166534; font-weight:bold"
        elif val == "SELL": return "background-color: #fee2e2; color: #991b1b; font-weight:bold"
        elif val == "HOLD": return "background-color: #fef3c7; color: #854d0e; font-weight:bold"
        return ""

    def ret_color(val):
        if isinstance(val, float):
            if val > 5: return "color: #059669"
            elif val > 0: return "color: #10b981"
            elif val < -5: return "color: #dc2626"
            elif val < 0: return "color: #ef4444"
        return ""

    styled_full = full.style\
        .map(full_color, subset=["Signal"])\
        .map(ret_color, subset=["1M Ret%","3M Ret%","6M Ret%","1Y Ret%"])

    st.dataframe(styled_full, use_container_width=True, height=650)

    st.markdown("---")
    st.markdown("### 📊 1Y Return — Full Market Snapshot")
    full_sorted = full.dropna(subset=["1Y Ret%"]).sort_values("1Y Ret%", ascending=True)
    bar_colors = ["#10b981" if v > 0 else "#ef4444" for v in full_sorted["1Y Ret%"]]
    fig_all = go.Figure(go.Bar(
        x=full_sorted["1Y Ret%"],
        y=full_sorted["Stock"],
        orientation="h",
        marker_color=bar_colors,
        text=full_sorted["1Y Ret%"].round(1).astype(str) + "%",
        textposition="outside",
        textfont=dict(size=10, family="JetBrains Mono", color="#1e293b")
    ))
    fig_all.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font_color="#1e293b", height=max(500, len(full_sorted)*18),
        xaxis=dict(gridcolor="#e2e8f0", title="1Y Return %"),
        yaxis=dict(gridcolor="#e2e8f0", tickfont=dict(size=10)),
        margin=dict(l=120, r=80)
    )
    st.plotly_chart(fig_all, use_container_width=True)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#94a3b8; font-family: JetBrains Mono, monospace; font-size:11px; padding: 8px 0;'>
  Smart Stock Dashboard · Data: yFinance · Not financial advice · For educational use only
</div>
""", unsafe_allow_html=True)
