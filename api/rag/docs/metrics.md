# Metrics

Revenue:
SUM(order_items.quantity * order_items.price)

AOV (Average Order Value):
AVG(orders.amount)

Orders Count:
COUNT(*) FROM orders

Notes:
- Use orders.created_at for date filters.
- Join: orders.order_id = order_items.order_id