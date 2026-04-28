import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📊 Live Stock Dashboard")

stocks = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"]

data = yf.download(stocks, period="5d")["Close"]

returns = (data.iloc[-1] / data.iloc[0] - 1) * 100

df = pd.DataFrame({
    "Stock": returns.index,
    "Return %": returns.values
}).sort_values(by="Return %", ascending=False)

st.subheader("Top Gainers")
st.dataframe(df.head(5))

st.subheader("Top Losers")
st.dataframe(df.tail(5))
