-- Q5. Which products get attention, and which ones actually sell?
SELECT i.item_name, i.item_category, i.price AS price_inr,
       SUM(e.event_name = 'view_item')                                AS views,
       SUM(e.event_name = 'add_to_cart')                              AS add_to_carts,
       SUM(CASE WHEN e.event_name = 'purchase' THEN i.quantity END)   AS units_sold,
       ROUND(SUM(CASE WHEN e.event_name = 'purchase' THEN i.price * i.quantity END)) AS revenue_inr,
       ROUND(100.0 * SUM(e.event_name = 'add_to_cart') / SUM(e.event_name = 'view_item'), 1) AS view_to_cart_pct,
       ROUND(100.0 * SUM(CASE WHEN e.event_name = 'purchase' THEN 1 END)
             / SUM(e.event_name = 'view_item'), 1)                    AS view_to_purchase_pct
FROM event_items i JOIN events e ON e.event_id = i.event_id
WHERE e.event_name IN ('view_item', 'add_to_cart', 'purchase')
GROUP BY i.item_id ORDER BY revenue_inr DESC;
