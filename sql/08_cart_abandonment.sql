-- Q8. How much money is left in abandoned carts, and where?
WITH cart_sessions AS (
  SELECT ga_session_id, device_category,
         MAX(event_name = 'begin_checkout') AS checkout,
         MAX(event_name = 'purchase')       AS purchased,
         MAX(CASE WHEN event_name IN ('view_cart', 'add_to_cart', 'begin_checkout') THEN value END) AS cart_value
  FROM events
  GROUP BY ga_session_id, device_category
  HAVING MAX(event_name = 'add_to_cart') = 1
)
SELECT device_category,
       COUNT(*)                                                     AS sessions_with_cart,
       SUM(1 - purchased)                                           AS abandoned_carts,
       ROUND(100.0 * SUM(1 - purchased) / COUNT(*), 1)              AS abandonment_pct,
       SUM(checkout * (1 - purchased))                              AS abandoned_at_checkout,
       ROUND(SUM(CASE WHEN purchased = 0 THEN cart_value END))      AS abandoned_value_inr,
       ROUND(SUM(CASE WHEN checkout = 1 AND purchased = 0 THEN cart_value END)) AS abandoned_at_checkout_value_inr
FROM cart_sessions GROUP BY device_category ORDER BY abandoned_value_inr DESC;
