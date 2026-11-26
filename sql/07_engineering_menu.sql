-- The Engineering College spot has no exhaust, so no wok stove: it only sells
-- dishes made earlier at the hub kitchen, plus snacks from vendors. Did those
-- ready-made dishes hold up? Compare how much was binned at each FoodJack spot,
-- on the same dishes, once prep was planned from the calendar (C4).
WITH c4 AS (SELECT date AS d FROM changes WHERE change_id = 'C4')
SELECT st.site_name,
       ROUND(SUM(w.prepared_portions), 0) AS prepared,
       ROUND(SUM(w.wasted_portions), 0) AS wasted,
       ROUND(100.0 * SUM(w.wasted_portions) / SUM(w.prepared_portions), 1) AS waste_pct
FROM waste_log w
JOIN items i  ON i.item_id = w.item_id
JOIN sites st ON st.site_id = w.site_id
CROSS JOIN c4
WHERE st.brand = 'FoodJack' AND i.needs_wok = 0 AND i.prep_type = 'batch' AND w.date >= c4.d
GROUP BY st.site_name
ORDER BY st.site_name;
