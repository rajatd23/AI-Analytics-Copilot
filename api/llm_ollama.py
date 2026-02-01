# import os
# import requests
# from schema import SCHEMA_TEXT

# OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
# MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# SYSTEM_PROMPT = f"""
# You are an expert data analyst. Convert user questions into SAFE PostgreSQL SQL queries.

# Rules:
# - Output ONLY SQL (no markdown, no explanations).
# - Use only SELECT queries.
# - Use only tables/columns from the schema.
# - Use GROUP BY for aggregates.
# - For revenue: SUM(quantity * price)
# - Always include LIMIT (top-N uses LIMIT N, otherwise LIMIT 200)

# Schema:
# {SCHEMA_TEXT}

# Example:
# Question: orders by status
# SQL:
# SELECT status, COUNT(*) AS cnt
# FROM orders
# GROUP BY status
# ORDER BY cnt DESC
# LIMIT 20;

# Question: top 5 products by revenue
# SQL:
# SELECT product, SUM(quantity * price) AS revenue
# FROM order_items
# GROUP BY product
# ORDER BY revenue DESC
# LIMIT 5;
# """.strip()

# def _clean_sql(text: str) -> str:
#     sql = (text or "").strip()
#     sql = sql.replace("```sql", "").replace("```", "").strip()
#     # If model returns extra text, keep from first SELECT
#     lower = sql.lower()
#     idx = lower.find("select")
#     if idx != -1:
#         sql = sql[idx:]
#     return sql.strip().rstrip(";") + ";"

# def generate_sql(question: str) -> str:
#     # 1) Try /api/chat (newer)
#     chat_payload = {
#         "model": MODEL,
#         "messages": [
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": f"{question}\nReturn ONLY SQL."}
#         ],
#         "stream": False
#     }
#     try:
#         r = requests.post(f"{OLLAMA_URL}/api/chat", json=chat_payload, timeout=120)
#         if r.status_code != 404:
#             r.raise_for_status()
#             data = r.json()
#             return _clean_sql(data["message"]["content"])
#     except requests.RequestException:
#         pass

#     # 2) Fallback to /api/generate (older)
#     gen_payload = {
#         "model": MODEL,
#         "prompt": f"{SYSTEM_PROMPT}\n\nUser question: {question}\nSQL:",
#         "stream": False
#     }
#     r = requests.post(f"{OLLAMA_URL}/api/generate", json=gen_payload, timeout=120)
#     r.raise_for_status()
#     data = r.json()
#     return _clean_sql(data.get("response", ""))


import os
import json
import re
import requests
from schema import SCHEMA_TEXT
from rag.retriever import retrieve_context

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

def _extract_json(text: str) -> dict:
    """
    Extract the first valid JSON object from model output.
    """
    if not text:
        raise ValueError("Empty LLM response")

    # Remove code fences if any
    cleaned = text.replace("```json", "").replace("```", "").strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Extract JSON object with regex (first {...})
    m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not m:
        raise ValueError(f"Could not find JSON in LLM output: {cleaned[:200]}")
    return json.loads(m.group(0))

def generate_plan(question: str) -> dict:
    rag_context = retrieve_context(question, k=5)

    prompt = f"""
You are an analytics copilot. Return ONLY strict JSON (no markdown, no explanation).

Rules:
- sql must be PostgreSQL SELECT only.
- Prefer LIMIT 200 unless top-N query.
- Use ONLY schema below.
- Use retrieved context as ground truth for metric definitions and joins.
- chart.type must be one of: bar, line, scatter, hist, none.
- chart.x and chart.y must be column names that exist in the query result.

Return JSON exactly with keys:
{{
  "sql": "...",
  "insights": ["...","..."],
  "chart": {{"type":"bar|line|scatter|hist|none","x":"col","y":"col","title":"..."}}
}}

Retrieved context:
{rag_context}

Schema:
{SCHEMA_TEXT}

User question: {question}
""".strip()

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=180)
    if not r.ok:
        raise RuntimeError(f"Ollama error {r.status_code}: {r.text}")

    data = r.json()
    plan = _extract_json(data.get("response", ""))

    return plan
