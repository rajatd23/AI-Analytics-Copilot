from dotenv import load_dotenv
load_dotenv()
import re
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import run_sql, init_history_table, save_history, list_history
from llm_ollama import generate_plan
from dotenv import load_dotenv
load_dotenv()
app = FastAPI(title="AI Analytics Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str

def _is_safe_select(sql: str) -> bool:
    s = sql.strip().lower()
    if not s.startswith("select"):
        return False
    # Block common dangerous keywords
    blocked = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke"]
    if any(b in s for b in blocked):
        return False
    # Only allow single statement
    if ";" in s[:-1]:
        return False
    return True

def _ensure_limit(sql: str, default_limit: int = 200) -> str:
    s = sql.strip().rstrip(";")
    if re.search(r"\blimit\b", s, re.IGNORECASE):
        return s + ";"
    return f"{s} LIMIT {default_limit};"

def _validate_chart(chart: Dict[str, Any], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {"type": "none", "x": "", "y": "", "title": "No data"}
    cols = set(rows[0].keys())
    ctype = (chart.get("type") or "none").lower()
    if ctype not in {"bar", "line", "scatter", "hist", "none"}:
        ctype = "none"
    x = chart.get("x", "")
    y = chart.get("y", "")
    title = chart.get("title", "Chart")

    # For hist, y can be empty (we just need x numeric)
    if ctype == "hist":
        if x not in cols:
            ctype = "none"
        return {"type": ctype, "x": x, "y": "", "title": title}

    if ctype != "none":
        if x not in cols or y not in cols:
            ctype = "none"

    return {"type": ctype, "x": x if ctype != "none" else "", "y": y if ctype != "none" else "", "title": title}

@app.on_event("startup")
def startup():
    init_history_table()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: AskRequest):
    q = req.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question is empty")

    plan = generate_plan(q)

    sql = (plan.get("sql") or "").strip()
    if not _is_safe_select(sql):
        raise HTTPException(status_code=400, detail=f"Unsafe SQL generated: {sql[:200]}")

    sql = _ensure_limit(sql)
    rows = run_sql(sql)

    # Save history
    save_history(q, sql)

    # Validate chart spec against actual result columns
    chart = _validate_chart(plan.get("chart", {}), rows)

    # Insights can be LLM suggestions; keep them, but ensure list
    insights = plan.get("insights") or []
    if not isinstance(insights, list):
        insights = [str(insights)]

    return {"question": q, "sql": sql, "data": rows, "insights": insights, "chart": chart}

@app.get("/history")
def history(limit: int = 50):
    return {"items": list_history(limit=limit)}

# ---- Dashboard endpoints (simple, extend later) ----

@app.get("/dashboard/kpis")
def dashboard_kpis():
    kpi = {}
    # total orders
    kpi["orders"] = run_sql("SELECT COUNT(*)::int AS value FROM orders;")[0]["value"]
    # total revenue (from orders.amount)
    kpi["revenue"] = float(run_sql("SELECT COALESCE(SUM(amount),0) AS value FROM orders;")[0]["value"])
    # aov
    kpi["aov"] = float(run_sql("SELECT COALESCE(AVG(amount),0) AS value FROM orders;")[0]["value"])
    # top product by revenue (from order_items)
    top = run_sql("""
        SELECT product, SUM(quantity*price) AS revenue
        FROM order_items
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 1;
    """)
    kpi["top_product"] = top[0]["product"] if top else ""
    return kpi

@app.get("/dashboard/revenue_trend")
def revenue_trend():
    rows = run_sql("""
      SELECT DATE(created_at) AS day, SUM(amount) AS revenue
      FROM orders
      GROUP BY day
      ORDER BY day
      LIMIT 200;
    """)
    return {"data": rows}
