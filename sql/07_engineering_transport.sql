-- FoodJack Engineering College gets its food from the hub kitchen. Waste by
-- whether a dish travels well, before and after the menu redesign (C8).
WITH c8 AS (SELECT date AS d FROM changes WHERE change_id = 'C8')
SELECT CASE WHEN i.travels_well = 1 THEN 'travels well' ELSE 'does not travel well' END AS dish_type,
       CASE WHEN w.date < c8.d THEN 'before' ELSE 'after' END AS period,
       ROUND(SUM(w.prepared_portions), 0) AS prepared,
       ROUND(SUM(w.wasted_portions), 0) AS wasted,
       ROUND(100.0 * SUM(w.wasted_portions) / SUM(w.prepared_portions), 1) AS waste_pct
FROM waste_log w
JOIN items i ON i.item_id = w.item_id
CROSS JOIN c8
WHERE w.site_id = 'FJ-ENG'
GROUP BY dish_type, period
ORDER BY dish_type DESC, period DESC;
