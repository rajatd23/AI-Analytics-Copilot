import streamlit as st
import requests
import pandas as pd

API_URL = st.secrets.get("API_URL", "http://localhost:8080")

st.title("Dashboard")

k = requests.get(f"{API_URL}/dashboard/kpis", timeout=30).json()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", k.get("orders", 0))
c2.metric("Total Revenue", round(float(k.get("revenue", 0)), 2))
c3.metric("AOV", round(float(k.get("aov", 0)), 2))
c4.metric("Top Product", k.get("top_product", ""))

st.subheader("Revenue Trend (Daily)")
trend = requests.get(f"{API_URL}/dashboard/revenue_trend", timeout=30).json()
df = pd.DataFrame(trend.get("data", []))

if df.empty:
    st.info("No trend data available.")
else:
    df["day"] = pd.to_datetime(df["day"])
    df = df.sort_values("day")
    st.line_chart(df.set_index("day")["revenue"])
