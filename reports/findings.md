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
| Boba Tea | 320 | 370 | 20% |
| Waffles | 370 | 411 | 10% |
| Juice Jar 500 ml | 421 | 481 | 10% |

## 2. A spot would go quiet for a few days

- **Checked:** ordinary weekdays when bills fell below 85% of that spot's usual (`08_quiet_days.sql`).
- **Found:** no exam, holiday or power cut explained those days. Talking to students did: one friend picks another
  place and the whole group follows.
- **Did:** got to know the regulars and kept them in a WhatsApp community.
- **Did it work:** quiet days went from **15 in every 100** to **2 in every 100**.

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
- **Did it work:** exam days down to **12%**, holidays to **19%**,
  ordinary days from 28% to 12%.

![Food binned by kind of day](waste_by_calendar.png)

## 5. Some dishes kept ending up in the bin

- **Checked:** weighed FoodJack food before serving and again before binning (`06_veg_vs_chicken.sql`).
- **Found:** veg dishes were 41% of what students ate but
  56% of what we binned. They wanted chicken.
- **Did:** rebuilt the FoodJack menu around chicken.
- **Did it work:** FoodJack's binned % fell from 37% on veg and
  24% on chicken to 13% and
  12%
  (the calendar planning in section 4 helped too).

## 6. The Engineering College spot could not cook

- **Checked:** the spot has no exhaust, so a wok stove could not be set up. Kothu parotta, fried rice and noodles
  could not be made there.
- **Did:** sold only dishes already made at the hub kitchen (biryani, chapati and gravy, aloo parotta), plus snacks
  that came straight from vendors.
- **Did it work:** the ready-made dishes held up. Binned % on them was 12% at the
  Engineering College against 12% at the Arts College (`07_engineering_menu.sql`), and
  Chicken Biryani became that spot's best seller.

## The loop that kept it working

Every day the billing machine totals, the waste weights and counts, and the calendar went into one Excel sheet.
Every week I looked at the same few numbers: bills per day, items per bill, and % binned by spot. If one moved the
wrong way, I went and asked the staff and the students why, changed one thing, and checked the same number the next
week.

![SnackJack Library Block bills per day](library_bills.png)
