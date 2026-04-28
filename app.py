import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Smart Stock Analysis Dashboard")

# 🔹 NIFTY 200 (sample ~50, aap baad me 200 full add kar sakte ho)
stocks = [
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
"LT.NS","SBIN.NS","AXISBANK.NS","ITC.NS","HCLTECH.NS",
"WIPRO.NS","MARUTI.NS","BAJFINANCE.NS","ASIANPAINT.NS","SUNPHARMA.NS",
"TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS","KOTAKBANK.NS","NTPC.NS",
"POWERGRID.NS","ADANIENT.NS","ADANIPORTS.NS","JSWSTEEL.NS","TATASTEEL.NS",
"BPCL.NS","ONGC.NS","COALINDIA.NS","HINDUNILVR.NS","BRITANNIA.NS",
"DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","EICHERMOT.NS","HEROMOTOCO.NS",
"BAJAJFINSV.NS","INDUSINDBK.NS","TECHM.NS","GRASIM.NS","SHREECEM.NS"
]

# 🔹 Sidebar Filters
st.sidebar.header("🔍 Filters")

selected_stock = st.sidebar.selectbox("Select Stock for Chart", stocks)

# 🔹 Data Fetch
data = yf.download(stocks, period="5d", interval="1d")["Close"]

# 🔹 Returns Calculation
returns = (data.iloc[-1] / data.iloc[0] - 1) * 100

df = pd.DataFrame({
    "Stock": returns.index,
    "Return %": returns.values
})

# 🔹 Scoring Logic (simple)
df["Score"] = df["Return %"]

df = df.sort_values(by="Score", ascending=False)

# 🔹 Layout Columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Top 10 Gainers")
    st.dataframe(df.head(10), use_container_width=True)

with col2:
    st.subheader("📉 Top 10 Losers")
    st.dataframe(df.tail(10), use_container_width=True)

# 🔹 Full Table
st.subheader("📋 All Stocks Ranking")
st.dataframe(df, use_container_width=True)

# 🔹 Chart Section
st.subheader(f"📈 Chart: {selected_stock}")

chart_data = yf.download(selected_stock, period="1mo")
st.line_chart(chart_data["Close"])
