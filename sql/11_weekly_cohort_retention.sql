-- Q11. Of users who first visited in week N, what share came back in later weeks?
WITH first_seen AS (
  SELECT user_pseudo_id, MIN(event_date) AS first_date FROM events GROUP BY user_pseudo_id
), activity AS (
  SELECT DISTINCT e.user_pseudo_id,
         CAST((julianday(f.first_date) - julianday('2026-07-25')) / 7 AS INTEGER) AS cohort_week,
         CAST((julianday(e.event_date) - julianday(f.first_date)) / 7 AS INTEGER) AS weeks_since_first
  FROM events e JOIN first_seen f USING (user_pseudo_id)
), cohort_size AS (
  SELECT cohort_week, COUNT(DISTINCT user_pseudo_id) AS users FROM activity WHERE weeks_since_first = 0 GROUP BY cohort_week
)
SELECT a.cohort_week, c.users AS cohort_users, a.weeks_since_first,
       COUNT(DISTINCT a.user_pseudo_id) AS active_users,
       ROUND(100.0 * COUNT(DISTINCT a.user_pseudo_id) / c.users, 1) AS retention_pct
FROM activity a JOIN cohort_size c USING (cohort_week)
WHERE a.weeks_since_first BETWEEN 0 AND 6 AND a.cohort_week <= 6
GROUP BY a.cohort_week, a.weeks_since_first ORDER BY a.cohort_week, a.weeks_since_first;
