-- Q1. What are the headline KPIs for the 90-day period?
WITH purchases AS (
  SELECT transaction_id, value FROM events WHERE event_name = 'purchase'
)
SELECT
  COUNT(DISTINCT e.user_pseudo_id)                                   AS users,
  COUNT(DISTINCT e.ga_session_id)                                    AS sessions,
  (SELECT COUNT(*) FROM purchases)                                   AS orders,
  (SELECT ROUND(SUM(value)) FROM purchases)                          AS revenue_inr,
  (SELECT ROUND(AVG(value)) FROM purchases)                          AS avg_order_value_inr,
  ROUND(100.0 * (SELECT COUNT(*) FROM purchases)
        / COUNT(DISTINCT e.ga_session_id), 2)                        AS session_conversion_pct,
  ROUND((SELECT SUM(value) FROM purchases)
        / COUNT(DISTINCT e.ga_session_id), 1)                        AS revenue_per_session_inr
FROM events e;
