import streamlit as st
import requests
import pandas as pd

API_URL = st.secrets.get("API_URL", "http://localhost:8080")

st.title("Ask Copilot (NL → SQL → Insights)")

question = st.text_input("Ask a question", placeholder="e.g., top 5 products by revenue")

if st.button("Ask") and question.strip():
    with st.spinner("Thinking..."):
        r = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=180)

    if r.status_code != 200:
        st.error(f"Error: {r.status_code} - {r.text}")
    else:
        out = r.json()

        st.subheader("Generated SQL")
        st.code(out["sql"], language="sql")

        st.subheader("Insights")
        for i in out.get("insights", []):
            st.write(f"- {i}")

        df = pd.DataFrame(out.get("data", []))
        st.subheader("Results")
        st.dataframe(df, use_container_width=True)

        chart = out.get("chart", {"type": "none"})
        ctype = chart.get("type", "none")

        if not df.empty and ctype != "none":
            st.subheader("Chart")
            x = chart.get("x")
            y = chart.get("y")
            title = chart.get("title", "Chart")

            st.caption(title)

            if ctype == "bar":
                st.bar_chart(df.set_index(x)[y])
            elif ctype == "line":
                st.line_chart(df.set_index(x)[y])
            elif ctype == "scatter":
                st.scatter_chart(df, x=x, y=y)
            elif ctype == "hist":
                st.bar_chart(df[x].value_counts())
