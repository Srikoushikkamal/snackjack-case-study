# 5. Weekly spot report: dashboard requirements

A Power BI report built on the files in `data/`, covering user stories US2 to US5.

## Who uses it

| User | Question | How often |
|---|---|---|
| Owner | Which spot is doing well, which is slipping? | Weekly |
| Operations manager | Is waste under control? Did the latest launch work? | Weekly |
| Spot manager | How did my spot do against the others? | Weekly |

## Data model

| Table | One row per | Key |
|---|---|---|
| `billing_item_sales` | Spot, day, item | `date`, `site_id`, `item_id` |
| `billing_daily` | Spot, day | `date`, `site_id` |
| `foodjack_waste_log` | FoodJack spot, day, dish | `date`, `site_id`, `item_id` |
| `snackjack_waste_log` | SnackJack spot, day, item | `date`, `site_id`, `item_id` |
| `sites`, `items`, `calendar`, `changes` | Lookup tables | `site_id`, `item_id`, `date`, `change_id` |

## Measures

| Measure | Definition |
|---|---|
| Sales | qty × price |
| Bills | Sum of bills |
| Average bill | Sales ÷ bills |
| Items per bill | Sum of qty ÷ bills |
| Portions binned | FoodJack: binned_kg ÷ portion_kg. SnackJack: wasted_units |
| Binned % | Portions binned ÷ portions prepared |
| Waste cost | Portions binned × unit_cost |

## Pages

1. **Spots.** Sales, bills, average bill and binned % for each spot, this week against the last four.
2. **Waste.** Binned % by spot and kind of day; share eaten against share binned by dish.
3. **Launches.** Bills per day around each launch in `changes`, with the new item's share.
4. **Quiet days.** Bills against each spot's recent normal, with flags from US5.

Filters in one row at the top: date range, brand, spot, kind of day.

## Acceptance

- Sales and bills per spot match `outputs/01_spot_summary.csv` for the full period.
- Binned % by kind of day matches `outputs/05_waste_by_calendar.csv`.
