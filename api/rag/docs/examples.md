# Examples

Q: top 5 products by revenue
SQL:
SELECT product, SUM(quantity * price) AS revenue
FROM order_items
GROUP BY product
ORDER BY revenue DESC
LIMIT 5;

Q: orders by status
SQL:
SELECT status, COUNT(*) AS orders
FROM orders
GROUP BY status
ORDER BY orders DESC
LIMIT 20;

Q: revenue trend by day
SQL:
SELECT DATE(created_at) AS day, SUM(amount) AS revenue
FROM orders
GROUP BY day
ORDER BY day
LIMIT 200;