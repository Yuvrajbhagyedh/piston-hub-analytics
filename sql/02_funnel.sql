-- Q2. Where in the shopping journey do we lose people? (session-level funnel)
WITH s AS (
  SELECT ga_session_id,
         MAX(event_name = 'view_item_list') AS listed,
         MAX(event_name = 'view_item')      AS viewed,
         MAX(event_name = 'add_to_cart')    AS carted,
         MAX(event_name = 'begin_checkout') AS checkout,
         MAX(event_name = 'purchase')       AS purchased
  FROM events GROUP BY ga_session_id
), f AS (
  SELECT 1 AS step, 'session_start' AS stage, COUNT(*) AS sessions FROM s
  UNION ALL SELECT 2, 'view_item_list', SUM(listed)    FROM s
  UNION ALL SELECT 3, 'view_item',      SUM(viewed)    FROM s
  UNION ALL SELECT 4, 'add_to_cart',    SUM(carted)    FROM s
  UNION ALL SELECT 5, 'begin_checkout', SUM(checkout)  FROM s
  UNION ALL SELECT 6, 'purchase',       SUM(purchased) FROM s
)
SELECT step, stage, sessions,
       ROUND(100.0 * sessions / FIRST_VALUE(sessions) OVER (ORDER BY step), 2) AS pct_of_all_sessions,
       ROUND(100.0 * sessions / LAG(sessions) OVER (ORDER BY step), 1)         AS step_conversion_pct,
       LAG(sessions) OVER (ORDER BY step) - sessions                            AS sessions_lost
FROM f ORDER BY step;
