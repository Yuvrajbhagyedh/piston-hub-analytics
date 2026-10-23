-- Q3. Does the funnel behave differently on mobile vs desktop?
WITH s AS (
  SELECT ga_session_id, device_category,
         MAX(event_name = 'view_item')      AS viewed,
         MAX(event_name = 'add_to_cart')    AS carted,
         MAX(event_name = 'begin_checkout') AS checkout,
         MAX(event_name = 'purchase')       AS purchased
  FROM events GROUP BY ga_session_id, device_category
)
SELECT device_category,
       COUNT(*)                                              AS sessions,
       ROUND(100.0 * SUM(carted)    / SUM(viewed), 1)        AS view_to_cart_pct,
       ROUND(100.0 * SUM(checkout)  / SUM(carted), 1)        AS cart_to_checkout_pct,
       ROUND(100.0 * SUM(purchased) / SUM(checkout), 1)      AS checkout_to_purchase_pct,
       ROUND(100.0 * SUM(purchased) / COUNT(*), 2)           AS session_conversion_pct
FROM s GROUP BY device_category ORDER BY sessions DESC;
