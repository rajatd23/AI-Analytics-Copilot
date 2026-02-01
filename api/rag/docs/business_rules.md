# Business Rules

- Only use SELECT queries.
- Prefer LIMIT 200 for non-top queries.
- If "revenue" is requested, compute using quantity * price.
- For "top" questions, ORDER BY metric DESC and LIMIT N.