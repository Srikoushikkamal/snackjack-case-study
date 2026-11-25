-- One waste log for both brands, in portions.
-- FoodJack weighs food (kg cooked, kg binned); SnackJack counts cups and pieces.
CREATE VIEW waste_log AS
SELECT f.date, f.site_id, f.item_id,
       f.cooked_kg / i.portion_kg AS prepared_portions,
       f.binned_kg / i.portion_kg AS wasted_portions
FROM foodjack_waste_log f
JOIN items i ON i.item_id = f.item_id
UNION ALL
SELECT date, site_id, item_id, prepared_units, wasted_units
FROM snackjack_waste_log;

-- Sales from the billing machine, with price.
CREATE VIEW sales AS
SELECT b.date, b.site_id, b.item_id, b.qty, b.qty * i.price AS revenue
FROM billing_item_sales b
JOIN items i ON i.item_id = b.item_id;
