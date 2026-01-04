# AI Analytics Copilot (100% Free, Local)

An end-to-end **AI Analytics Copilot** that converts **natural language questions into SQL**, executes them on a relational database, and returns **insights with tables and charts**.

This project is built using a **completely free, local-first stack** — no paid cloud services required.

---

## 🚀 What This Project Does

- Ask questions in **plain English**
- Automatically converts questions to **PostgreSQL SQL**
- Executes queries safely (SELECT-only)
- Displays:
  - Generated SQL
  - Query results (tables)
  - Auto-generated charts
- Runs fully **locally** using a lightweight LLM

Example questions:
- `orders by status`
- `total sales`
- `top 5 products by revenue`
- `average order amount by status`

---

## 🧠 Architecture Overview

User (Browser)
│
▼
Streamlit Frontend
│ (HTTP)
▼
FastAPI Backend
│
├── Ollama (Local LLM) → Natural Language → SQL
│
└── PostgreSQL → Execute SQL → Results


---

## 🛠️ Tech Stack (Free)

- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **Database:** PostgreSQL (local)  
- **LLM:** Ollama (local, lightweight model)  
- **Language:** Python  

No OpenAI, no BigQuery, no paid cloud services.

---

## ⚙️ Prerequisites

Install the following on your machine:

- **Python 3.10+**
- **PostgreSQL 15**
- **Ollama** → https://ollama.com
- **Git**

---

## 🧪 Database Setup (One-Time)

### 1️⃣ Create Database
Create a PostgreSQL database named: copilot_db

### 2️⃣ Seed Tables & Sample Data
From the `api` folder:

```bash
python seed.py

How to Run the Project:

🔹 Step 1: Start Backend (FastAPI)
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8080

http://localhost:8080/health

🔹 Step 2: Start Frontend (Streamlit)
cd frontend
streamlit run app.py
