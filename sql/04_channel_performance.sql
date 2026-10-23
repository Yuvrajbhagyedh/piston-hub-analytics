-- Q4. Which marketing channels bring buyers, not just visitors?
WITH s AS (
  SELECT ga_session_id, source || ' / ' || medium AS channel,
         MAX(event_name = 'purchase') AS purchased,
         SUM(CASE WHEN event_name = 'purchase' THEN value ELSE 0 END) AS revenue
  FROM events GROUP BY ga_session_id, channel
)
SELECT channel,
       COUNT(*)                                        AS sessions,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_of_sessions_pct,
       SUM(purchased)                                  AS orders,
       ROUND(100.0 * SUM(purchased) / COUNT(*), 2)     AS conversion_pct,
       ROUND(SUM(revenue))                             AS revenue_inr,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS share_of_revenue_pct,
       ROUND(SUM(revenue) / COUNT(*), 1)               AS revenue_per_session_inr
FROM s GROUP BY channel ORDER BY revenue_inr DESC;
