-- Items per bill and average bill on ordinary college days, 8 weeks before and
-- after we started suggesting add-ons in the students' own slang (C1).
WITH c1 AS (SELECT date AS d FROM changes WHERE change_id = 'C1'),
daily AS (
    SELECT s.date, s.site_id, SUM(s.qty) AS units, SUM(s.revenue) AS revenue
    FROM sales s GROUP BY s.date, s.site_id
)
SELECT st.brand,
       CASE WHEN d.date < c1.d THEN 'before' ELSE 'after' END AS period,
       ROUND(1.0 * SUM(d.units) / SUM(b.bills), 2) AS items_per_bill,
       ROUND(1.0 * SUM(d.revenue) / SUM(b.bills), 1) AS avg_bill
FROM daily d
JOIN billing_daily b ON b.date = d.date AND b.site_id = d.site_id
JOIN calendar cal ON cal.date = d.date
JOIN sites st ON st.site_id = d.site_id
CROSS JOIN c1
WHERE cal.day_type = 'regular'
  AND d.date >= date(c1.d, '-56 days') AND d.date < date(c1.d, '+56 days')
GROUP BY st.brand, period
ORDER BY st.brand, period DESC;
