-- Each spot over the whole period: sales, bills, average bill and waste.
WITH s AS (
    SELECT site_id, SUM(revenue) AS revenue, SUM(qty) AS units
    FROM sales GROUP BY site_id
),
b AS (
    SELECT site_id, COUNT(*) AS days_open, SUM(bills) AS bills
    FROM billing_daily GROUP BY site_id
),
w AS (
    SELECT w.site_id, SUM(w.wasted_portions * i.unit_cost) AS waste_cost
    FROM waste_log w JOIN items i ON i.item_id = w.item_id
    GROUP BY w.site_id
)
SELECT st.site_id, st.site_name, st.opened, b.days_open,
       s.revenue, b.bills,
       ROUND(1.0 * s.revenue / b.bills, 1) AS avg_bill,
       ROUND(w.waste_cost, 0) AS waste_cost,
       ROUND(100.0 * w.waste_cost / s.revenue, 1) AS waste_pct_of_sales
FROM sites st
JOIN s ON s.site_id = st.site_id
JOIN b ON b.site_id = st.site_id
JOIN w ON w.site_id = st.site_id
ORDER BY s.revenue DESC;
