-- Q6. How do the three categories compare on traffic, conversion and revenue?
SELECT i.item_category,
       SUM(e.event_name = 'view_item')                                    AS views,
       ROUND(100.0 * SUM(e.event_name = 'view_item') / SUM(SUM(e.event_name = 'view_item')) OVER (), 1) AS share_of_views_pct,
       ROUND(100.0 * SUM(e.event_name = 'add_to_cart') / SUM(e.event_name = 'view_item'), 1)           AS view_to_cart_pct,
       SUM(CASE WHEN e.event_name = 'purchase' THEN i.quantity END)       AS units_sold,
       ROUND(SUM(CASE WHEN e.event_name = 'purchase' THEN i.price * i.quantity END)) AS revenue_inr,
       ROUND(100.0 * SUM(CASE WHEN e.event_name = 'purchase' THEN i.price * i.quantity END)
             / SUM(SUM(CASE WHEN e.event_name = 'purchase' THEN i.price * i.quantity END)) OVER (), 1) AS share_of_revenue_pct
FROM event_items i JOIN events e ON e.event_id = i.event_id
WHERE e.event_name IN ('view_item', 'add_to_cart', 'purchase')
GROUP BY i.item_category ORDER BY revenue_inr DESC;
