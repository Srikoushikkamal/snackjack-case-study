# Findings

Every number here comes from the SQL in `sql/`, run on the rebuilt records. The problems and the changes are real;
the sizes are illustrative (see the README).

## 1. Students did not know us

- **Checked:** which item sells most at each spot (`02_star_dish.sql`).
- **Found:** Chicken Kothu Parotta leads FoodJack. Boba Tea leads every SnackJack spot.
- **Did:** pushed one star item per spot, and launched new trending items with Canva posters and WhatsApp posts.
- **Did it work:** bills per day, 4 weeks before and after each launch (`03_new_items.sql`):

| Launch | Bills per day before | After | New item's share of sales |
|---|---|---|---|
| Boba Tea | 321 | 364 | 20% |
| Waffles | 373 | 417 | 10% |
| Juice Jar 500 ml | 421 | 482 | 10% |

## 2. A spot would go quiet for a few days

- **Checked:** ordinary weekdays when bills fell below 85% of that spot's usual (`08_quiet_days.sql`).
- **Found:** no exam, holiday or power cut explained those days. Talking to students did: one friend picks another
  place and the whole group follows.
- **Did:** got to know the regulars and kept them in a WhatsApp community.
- **Did it work:** quiet days went from **15 in every 100** to **1 in every 100**.

## 3. Students bought one thing and left

- **Checked:** items per bill and average bill (`04_upselling.sql`).
- **Did:** suggested one add-on at the counter, in the students' own slang.
- **Did it work:** items per bill went from 1.35 to
  1.61 at SnackJack and 1.35
  to 1.59 at FoodJack.

## 4. Too much food binned on some days

- **Checked:** % of prepared food binned, by kind of day (`05_waste_by_calendar.sql`).
- **Found:** we cooked the same every day. Exams (44% binned) and holidays
  (88%) were the worst.
- **Did:** planned each day's prep from the college calendar: exams, holidays, admissions, power cuts and the season.
- **Did it work:** exam days down to **12%**, holidays to **21%**,
  ordinary days from 28% to 12%.

![Food binned by kind of day](waste_by_calendar.png)

## 5. Some dishes kept ending up in the bin

- **Checked:** weighed FoodJack food before serving and again before binning (`06_veg_vs_chicken.sql`).
- **Found:** veg dishes were 41% of what students ate but
  56% of what we binned. They wanted chicken.
- **Did:** rebuilt the FoodJack menu around chicken.
- **Did it work:** FoodJack's binned % fell from 37% on veg and
  24% on chicken to 12% and
  11%
  (the calendar planning in section 4 helped too).

## 6. Food sent to the Engineering College was binned more

- **Checked:** waste at that spot, for dishes that travel well against those that do not (`07_engineering_transport.sql`).
- **Found:** food comes from the hub kitchen. Dishes that do not hold up on the trip were binned at
  22%, against 12% for the rest.
- **Did:** changed that spot's menu to dishes that travel well.
- **Did it work:** the badly travelling dishes are gone, and the rest stayed at about 11%.

## The loop that kept it working

Every day the billing machine totals, the waste weights and counts, and the calendar went into one Excel sheet.
Every week I looked at the same few numbers: bills per day, items per bill, and % binned by spot. If one moved the
wrong way, I went and asked the staff and the students why, changed one thing, and checked the same number the next
week.

![SnackJack Library Block bills per day](library_bills.png)
