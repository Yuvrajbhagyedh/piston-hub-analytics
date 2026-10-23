-- Q12. Which shop entry points (all products vs. bike / brand pages) lead to carts?
WITH s AS (
  SELECT ga_session_id,
         MAX(CASE WHEN event_name = 'view_item_list' THEN item_list_name END) AS list_name,
         MAX(event_name = 'add_to_cart') AS carted,
         MAX(event_name = 'purchase')    AS purchased
  FROM events GROUP BY ga_session_id
)
SELECT list_name, COUNT(*) AS sessions,
       ROUND(100.0 * SUM(carted) / COUNT(*), 1)    AS cart_rate_pct,
       ROUND(100.0 * SUM(purchased) / COUNT(*), 2) AS conversion_pct
FROM s WHERE list_name IS NOT NULL
GROUP BY list_name ORDER BY sessions DESC;
