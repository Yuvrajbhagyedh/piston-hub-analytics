-- Q9. Which cities buy the most, and is there demand outside Bengaluru?
WITH s AS (
  SELECT ga_session_id, city,
         MAX(event_name = 'purchase') AS purchased,
         SUM(CASE WHEN event_name = 'purchase' THEN value ELSE 0 END) AS revenue
  FROM events GROUP BY ga_session_id, city
)
SELECT city, COUNT(*) AS sessions, SUM(purchased) AS orders,
       ROUND(100.0 * SUM(purchased) / COUNT(*), 2) AS conversion_pct,
       ROUND(SUM(revenue)) AS revenue_inr,
       ROUND(SUM(revenue) / NULLIF(SUM(purchased), 0)) AS avg_order_value_inr,
       RANK() OVER (ORDER BY SUM(revenue) DESC) AS revenue_rank
FROM s GROUP BY city ORDER BY revenue_rank;
