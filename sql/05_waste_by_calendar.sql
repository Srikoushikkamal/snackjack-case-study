-- Share of prepared food thrown away, by kind of day, before and after prep was
-- planned from the college calendar (C4).
WITH c4 AS (SELECT date AS d FROM changes WHERE change_id = 'C4')
SELECT cal.day_type,
       CASE WHEN w.date < c4.d THEN 'before' ELSE 'after' END AS period,
       ROUND(SUM(w.prepared_portions), 0) AS prepared,
       ROUND(SUM(w.wasted_portions), 0) AS wasted,
       ROUND(100.0 * SUM(w.wasted_portions) / SUM(w.prepared_portions), 1) AS waste_pct
FROM waste_log w
JOIN calendar cal ON cal.date = w.date
CROSS JOIN c4
GROUP BY cal.day_type, period
ORDER BY cal.day_type, period DESC;
