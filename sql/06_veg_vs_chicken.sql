-- FoodJack on ordinary college days: what students ate and what was binned,
-- by veg, egg and chicken, before and after the menu was rebuilt around chicken (C3).
-- Shares are used rather than totals, because the "after" period is longer.
WITH c3 AS (SELECT date AS d FROM changes WHERE change_id = 'C3'),
base AS (
    SELECT i.diet,
           CASE WHEN w.date < c3.d THEN 'before' ELSE 'after' END AS period,
           SUM(w.prepared_portions - w.wasted_portions) AS sold,
           SUM(w.wasted_portions) AS wasted,
           SUM(w.prepared_portions) AS prepared
    FROM waste_log w
    JOIN items i      ON i.item_id = w.item_id
    JOIN calendar cal ON cal.date = w.date
    CROSS JOIN c3
    WHERE i.brand = 'FoodJack' AND i.prep_type = 'batch' AND cal.day_type = 'regular'
    GROUP BY i.diet, period
)
SELECT diet, period,
       ROUND(100.0 * sold / SUM(sold) OVER (PARTITION BY period), 1) AS share_of_sold_pct,
       ROUND(100.0 * wasted / SUM(wasted) OVER (PARTITION BY period), 1) AS share_of_binned_pct,
       ROUND(100.0 * wasted / prepared, 1) AS waste_pct
FROM base
ORDER BY period DESC, diet;
