-- Q7. How did traffic and sales move day by day? (7-day rolling averages, festive flag)
WITH d AS (
  SELECT event_date,
         COUNT(DISTINCT ga_session_id)                                  AS sessions,
         SUM(event_name = 'purchase')                                   AS orders,
         SUM(CASE WHEN event_name = 'purchase' THEN value ELSE 0 END)   AS revenue
  FROM events GROUP BY event_date
)
SELECT event_date, sessions, orders, ROUND(revenue) AS revenue_inr,
       ROUND(AVG(sessions) OVER w, 1) AS sessions_7d_avg,
       ROUND(AVG(revenue)  OVER w)    AS revenue_7d_avg,
       CASE WHEN event_date BETWEEN '2026-10-10' AND '2026-10-20' THEN 'festive_sale' ELSE 'regular' END AS period
FROM d
WINDOW w AS (ORDER BY event_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
ORDER BY event_date;
