# import streamlit as st
# import requests
# import pandas as pd

# st.set_page_config(page_title="AI Analytics Copilot", layout="wide")
# API_URL = st.secrets.get("API_URL", "http://localhost:8080")

# st.title("AI Analytics Copilot")
# q = st.text_input("Ask a question:", placeholder="e.g., orders by status, total sales last 30 days, top products")

# if st.button("Ask") and q:
#     with st.spinner("Generating SQL + running query..."):
#         r = requests.post(f"{API_URL}/ask", json={"question": q}, timeout=120)

#     if r.status_code != 200:
#         st.error(r.text)
#     else:
#         out = r.json()
#         st.subheader("Generated SQL")
#         st.code(out["sql"], language="sql")

#         df = pd.DataFrame(out["data"])
#         st.subheader("Results")
#         st.dataframe(df, use_container_width=True)

#         # Simple chart: if two cols and second numeric
#         if df.shape[1] >= 2:
#             cols = df.columns.tolist()
#             x, y = cols[0], cols[1]
#             if pd.api.types.is_numeric_dtype(df[y]):
#                 st.subheader("Chart")
#                 st.bar_chart(df.set_index(x)[y])


import streamlit as st

st.set_page_config(page_title="AI Analytics Copilot", layout="wide")

st.title("AI Analytics Copilot")
st.write("Use the pages on the left to explore the dashboard, ask questions, and view history.")
st.info("Go to **Dashboard** or **Ask Copilot** from the sidebar.")
