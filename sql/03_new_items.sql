-- Each SnackJack launch: bills per day in the 4 weeks before and after, at spots
-- open for the whole 8 weeks, and the new item's share of sales after launch.
WITH launches AS (
    SELECT c.change_id, c.date AS launch_date, i.item_id, i.item_name
    FROM changes c JOIN items i ON i.launched_by = c.change_id
    WHERE i.brand = 'SnackJack'
),
windows AS (
    SELECT l.change_id, l.item_name, l.item_id, b.site_id, b.date, b.bills,
           CASE WHEN b.date < l.launch_date THEN 'before' ELSE 'after' END AS period
    FROM launches l
    JOIN billing_daily b
      ON b.date >= date(l.launch_date, '-28 days') AND b.date < date(l.launch_date, '+28 days')
    JOIN sites st ON st.site_id = b.site_id
    WHERE st.brand = 'SnackJack' AND st.opened <= date(l.launch_date, '-28 days')
),
new_item AS (
    SELECT l.change_id,
           ROUND(100.0 * SUM(CASE WHEN s.item_id = l.item_id THEN s.revenue ELSE 0 END) / SUM(s.revenue), 1)
               AS new_item_share_pct
    FROM launches l
    JOIN sales s ON s.date >= l.launch_date AND s.date < date(l.launch_date, '+28 days')
    JOIN sites st ON st.site_id = s.site_id AND st.brand = 'SnackJack'
    GROUP BY l.change_id
)
SELECT w.change_id, w.item_name,
       ROUND(AVG(CASE WHEN period = 'before' THEN bills END), 0) AS bills_per_day_before,
       ROUND(AVG(CASE WHEN period = 'after' THEN bills END), 0) AS bills_per_day_after,
       n.new_item_share_pct
FROM windows w JOIN new_item n ON n.change_id = w.change_id
GROUP BY w.change_id, w.item_name
ORDER BY w.change_id;
