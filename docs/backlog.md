# Backlog

The six problems written as user stories and tasks, with acceptance criteria. The same list is in
`backlog.csv`, ready to import into Jira.

I have this backlog on a Jira Kanban board (FOOD-1 to FOOD-11). The things we actually changed at Snackjack are in
Done, the weekly check of three numbers is In Progress, and spotting quiet days early is still To Do.

## Students did not know us

**Find the star dish for each spot** (story, high priority)

As the owner, I want to know which item sells best at each spot, so that we push one item students will come back for.

Acceptance criteria:
- Given a month of billing machine totals, when I rank items by sales at each spot, then the top item for each spot is listed.
- The top item is shown on that spot's posters and counter.

**Check if a new item brings students in** (story, high priority)

As the operations manager, I want to compare bills per day four weeks before and after a launch, so that I know if boba tea, waffles or juice jars actually worked.

Acceptance criteria:
- Given a launch date, when I compare bills per day before and after, then I can see the change.
- The new item's share of sales is shown, so a busy exam week is not mistaken for a hit.

## A spot would go quiet for a few days

**Spot quiet days early** (story, medium priority)

As the operations manager, I want to know when a spot's bills drop below normal for two days in a row, so that I can go and talk to the regulars.

Acceptance criteria:
- Given two ordinary weekdays below 85% of the spot's usual bills, then the spot is flagged.
- Exam days, holidays and power cuts are not flagged.

**Keep regulars close** (task, medium priority)

Set up a student WhatsApp community for each spot and post new items and offers there.

Done when:
- Each spot has a group.
- New items are posted in the group on launch day.

## Students bought one thing and left

**Suggest one add-on at the counter** (story, medium priority)

As counter staff, I want one simple add-on to suggest with each main item, said the way students talk, so that each bill has more than one item.

Acceptance criteria:
- Each main item has one suggested add-on.
- Items per bill is checked weekly and goes up.

## Food binned on some days

**Plan prep from the college calendar** (story, high priority)

As a spot manager, I want tomorrow's prep based on the college calendar and recent days of the same kind, so that we stop cooking for students who are not on campus.

Acceptance criteria:
- Given tomorrow is an exam day, the prep amount is based on recent exam days.
- Given a power cut is announced, blender drinks are cut.
- Holidays and admissions days are marked in advance.

**Log waste the same way at every spot** (story, high priority)

As the operations manager, I want FoodJack to weigh food before serving and before binning, and SnackJack to count leftover cups and pieces, so that waste can be compared across spots.

Acceptance criteria:
- Every spot logs waste daily in the same Excel sheet.
- A missing log shows as missing, not as zero.

## Some dishes kept ending up in the bin

**Find dishes binned more than they are eaten** (story, high priority)

As the owner, I want each dish's share of food eaten next to its share of food binned, so that I know which dishes to change or drop.

Acceptance criteria:
- Given a month of waste logs, dishes binned well above their share of sales are highlighted.
- Veg and chicken dishes can be compared side by side.

**Rebuild the FoodJack menu around chicken** (task, high priority)

Cut the veg versions that were binned most and make the chicken versions in larger batches.

Done when:
- The new menu is up at both FoodJack spots.
- Binned % is checked again after four weeks.

## The Engineering College spot could not cook

**Set the Engineering College menu** (task, high priority)

The Engineering College spot has no exhaust, so no wok stove. Sell only dishes made earlier at the hub kitchen, plus snacks from vendors.

Done when:
- The menu lists only ready-made dishes and vendor snacks.
- Daily transport from the hub kitchen is fixed.
- Binned % there is checked against the Arts College.

## Keeping it working

**Weekly check of three numbers** (task, medium priority)

Every week, check bills per day, items per bill and % of food binned for each spot. If one moves the wrong way, ask staff and students why and change one thing.

Done when:
- The three numbers are in one weekly sheet for all five spots.
