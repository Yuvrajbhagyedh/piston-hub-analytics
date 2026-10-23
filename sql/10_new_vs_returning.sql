-- Q10. Are returning visitors more valuable than first-time visitors?
WITH s AS (
  SELECT ga_session_id,
         CASE WHEN MIN(session_number) = 1 THEN 'new' ELSE 'returning' END AS visitor_type,
         MAX(event_name = 'purchase') AS purchased,
         SUM(CASE WHEN event_name = 'purchase' THEN value ELSE 0 END) AS revenue
  FROM events GROUP BY ga_session_id
)
SELECT visitor_type, COUNT(*) AS sessions, SUM(purchased) AS orders,
       ROUND(100.0 * SUM(purchased) / COUNT(*), 2) AS conversion_pct,
       ROUND(SUM(revenue)) AS revenue_inr,
       ROUND(SUM(revenue) / COUNT(*), 1) AS revenue_per_session_inr
FROM s GROUP BY visitor_type;
