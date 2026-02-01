import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta

API_URL = st.secrets.get("API_URL", "http://localhost:8080")

st.set_page_config(layout="wide")
st.title("📊 Live Dashboard")

# -------- Sidebar Filters ----------
st.sidebar.header("Filters")

default_end = date.today()
default_start = default_end - timedelta(days=60)

date_range = st.sidebar.date_input(
    "Date range",
    value=(default_start, default_end),
)

start = None
end = None
if isinstance(date_range, tuple) and len(date_range) == 2:
    start = date_range[0].isoformat()
    end = date_range[1].isoformat()

status = st.sidebar.selectbox(
    "Order status",
    ["all", "completed", "pending", "cancelled", "shipped"],
    index=0
)

top_n = st.sidebar.slider("Top products", 5, 30, 10)

auto_refresh = st.sidebar.toggle("Auto refresh (every 10s)", value=False)

params = {"start": start, "end": end, "status": status}

# -------- Auto Refresh ----------
if auto_refresh:
    st.caption("🔄 Auto refresh enabled (10s)")
    st.experimental_set_query_params(_t=str(pd.Timestamp.utcnow().timestamp()))
    st.autorefresh(interval=10_000, key="dash_refresh")

# -------- Data Fetch ----------
@st.cache_data(ttl=10)
def fetch_kpis(params):
    return requests.get(f"{API_URL}/dashboard/kpis", params=params, timeout=30).json()

@st.cache_data(ttl=10)
def fetch_trend(params):
    return requests.get(f"{API_URL}/dashboard/revenue_trend", params=params, timeout=30).json()

@st.cache_data(ttl=10)
def fetch_top_products(params, limit):
    p = dict(params)
    p["limit"] = limit
    return requests.get(f"{API_URL}/dashboard/top_products", params=p, timeout=30).json()

k = fetch_kpis(params)
trend = fetch_trend(params)
top = fetch_top_products(params, top_n)

# -------- KPI Row ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", k.get("orders", 0))
c2.metric("Total Revenue", f"{k.get('revenue', 0):,.2f}")
c3.metric("AOV", f"{k.get('aov', 0):,.2f}")
c4.metric("Top Product", k.get("top_product", ""))

st.divider()

# -------- Charts + Tables ----------
left, right = st.columns([2, 1])

with left:
    st.subheader("Revenue Trend")
    df = pd.DataFrame(trend.get("data", []))
    if df.empty:
        st.info("No data for the selected filters.")
    else:
        df["day"] = pd.to_datetime(df["day"])
        df = df.sort_values("day")
        st.line_chart(df.set_index("day")["revenue"])

with right:
    st.subheader(f"Top {top_n} Products")
    tdf = pd.DataFrame(top.get("data", []))
    if tdf.empty:
        st.info("No product data for selected filters.")
    else:
        st.dataframe(tdf, use_container_width=True)

st.caption("Tip: Change filters from the left sidebar to update KPIs and charts instantly.")
