# import os
# import psycopg2
# from psycopg2.extras import RealDictCursor

# def get_conn():
#     return psycopg2.connect(
#         host=os.getenv("DB_HOST", "localhost"),
#         port=int(os.getenv("DB_PORT", "5432")),
#         dbname=os.getenv("DB_NAME", "copilot_db"),
#         user=os.getenv("DB_USER", "postgres"),
#         password=os.getenv("DB_PASSWORD", ""),
#     )

# def run_sql(sql: str, limit: int = 200):
#     # Safety: force LIMIT if not present
#     sql_clean = sql.strip().rstrip(";")
#     if "limit" not in sql_clean.lower():
#         sql_clean += f" LIMIT {limit}"

#     with get_conn() as conn:
#         with conn.cursor(cursor_factory=RealDictCursor) as cur:
#             cur.execute(sql_clean)
#             rows = cur.fetchall()
#             return rows


import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "copilot_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )

def init_history_table():
    sql = """
    CREATE TABLE IF NOT EXISTS query_history (
      id SERIAL PRIMARY KEY,
      created_at TIMESTAMP DEFAULT NOW(),
      question TEXT NOT NULL,
      sql TEXT NOT NULL
    );
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

def save_history(question: str, sql: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO query_history (question, sql) VALUES (%s, %s);",
                (question, sql)
            )
        conn.commit()

def list_history(limit: int = 50):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, created_at, question, sql FROM query_history ORDER BY id DESC LIMIT %s;",
                (limit,)
            )
            return cur.fetchall()

def run_sql(sql_text: str):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql_text)
            rows = cur.fetchall()
            return rows
