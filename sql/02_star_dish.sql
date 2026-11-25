-- The top three items at each spot by share of its sales, over the last six months.
WITH recent AS (
    SELECT site_id, item_id, SUM(revenue) AS revenue
    FROM sales
    WHERE date >= '2024-04-01'
    GROUP BY site_id, item_id
),
ranked AS (
    SELECT r.site_id, i.item_name, r.revenue,
           ROUND(100.0 * r.revenue / SUM(r.revenue) OVER (PARTITION BY r.site_id), 1) AS share_pct,
           ROW_NUMBER() OVER (PARTITION BY r.site_id ORDER BY r.revenue DESC) AS rank
    FROM recent r JOIN items i ON i.item_id = r.item_id
)
SELECT site_id, rank, item_name, share_pct
FROM ranked
WHERE rank <= 3
ORDER BY site_id, rank;
