import streamlit as st
import requests
import pandas as pd

API_URL = st.secrets.get("API_URL", "http://localhost:8080")

st.title("Query History")

limit = st.slider("Rows", 10, 200, 50)
resp = requests.get(f"{API_URL}/history?limit={limit}", timeout=30).json()

items = resp.get("items", [])
df = pd.DataFrame(items)

if df.empty:
    st.info("No history yet. Ask some questions first.")
else:
    st.dataframe(df, use_container_width=True)
