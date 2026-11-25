-- Quiet days: an ordinary weekday when a spot's bills fell below 85% of its
-- average for ordinary weekdays that month. Before and after the WhatsApp
-- community and getting to know the regulars (C2).
WITH c2 AS (SELECT date AS d FROM changes WHERE change_id = 'C2'),
days AS (
    SELECT b.site_id, b.date, b.bills, substr(b.date, 1, 7) AS month
    FROM billing_daily b JOIN calendar c ON c.date = b.date
    WHERE c.day_type = 'regular' AND c.weekday NOT IN ('Saturday', 'Sunday') AND c.power_cut = 0
),
marked AS (
    SELECT d.*, d.bills < 0.85 * AVG(d.bills) OVER (PARTITION BY d.site_id, d.month) AS quiet
    FROM days d
)
SELECT CASE WHEN m.date < c2.d THEN 'before' ELSE 'after' END AS period,
       COUNT(*) AS ordinary_days,
       SUM(m.quiet) AS quiet_days,
       ROUND(100.0 * SUM(m.quiet) / COUNT(*), 1) AS quiet_days_per_100
FROM marked m CROSS JOIN c2
GROUP BY period
ORDER BY period DESC;
