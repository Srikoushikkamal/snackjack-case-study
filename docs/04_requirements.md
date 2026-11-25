# 4. Requirements

At Snackjack all of this ran on an Excel sheet and my own memory. These are the requirements I would write if the
same business asked for a proper tool today. Priorities use MoSCoW: **Must**, **Should**, **Could**, **Won't**.

## Business requirements

| ID | Requirement | Priority |
|---|---|---|
| BR1 | Plan each day's prep per spot from the college calendar and recent sales | Must |
| BR2 | Record waste the same way at every spot, in a form that can be compared | Must |
| BR3 | Show which dishes are binned out of proportion to what students eat | Must |
| BR4 | Show whether a new item or promotion actually brought more students in | Should |
| BR5 | Warn when a spot's bills drop for more than a day, so someone can find out why | Should |
| BR6 | Keep working with the billing machine and Excel; no new till | Must |

## User stories

**US1. Prep plan from the calendar** (BR1, BR6)
> As a spot manager, I want tomorrow's prep amount for each item worked out from the college calendar and what sold on
> recent days of the same kind, so I stop cooking for students who are not on campus.

- Given tomorrow is an exam day, when I open the prep sheet, then each item's amount is based on recent exam days, not
  ordinary days.
- Given the electricity board has announced a power cut, when I open the prep sheet, then blender drinks are cut.
- Given there is no recent day of the same kind, then the sheet uses the last ordinary day and says so.

**US2. One waste log** (BR2)
> As the operations manager, I want FoodJack to log kg cooked and kg binned, and SnackJack to log cups and pieces, in
> one sheet per day, so waste can be compared across spots.

- Given a FoodJack dish is weighed at close, when the weight is entered, then the sheet converts it to portions and cost.
- Given a spot has not entered its waste by 9 pm, then it shows as missing, not as zero.

**US3. Dishes binned out of proportion** (BR3)
> As the owner, I want to see each dish's share of what was eaten next to its share of what was binned, so I know
> which dishes to change or drop.

- Given a month of logs, when I open the report, then dishes whose share of binned food is more than 10 points above
  their share of eaten food are highlighted.

**US4. Did the launch work?** (BR4)
> As the operations manager, I want bills per day for four weeks before and after a launch, and the new item's share of
> sales, so I can tell a real hit from a busy week.

- Given a launch date, when I open the report, then it shows both numbers and marks exam or holiday weeks in either
  window.

**US5. Quiet spot warning** (BR5)
> As the operations manager, I want to be told when a spot's bills are more than 15% below normal for two ordinary
> days in a row, so I can go and talk to the regulars.

- Given two ordinary weekdays in a row below 85% of the spot's recent normal, then the spot is flagged.
- Given the low days are exams, holidays or a power cut, then no flag is raised.

## Won't do this time

- Forecasting with weather or events outside the college.
- Vendor ordering and payments (kept on WhatsApp and paid at the weekend).
