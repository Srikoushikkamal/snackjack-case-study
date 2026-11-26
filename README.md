# Snackjack: five campus food spots

From February 2023 to October 2024 I ran operations at Snackjack Foods in Coimbatore. We sold food inside college
campuses as FoodJack (meals) and SnackJack (snacks and drinks), and grew from one shop to five spots.

This repo goes back over the problems we had, and for each one shows the same simple loop:
**what was wrong, what the numbers said, what I changed, and whether it worked.**

## The problems and what I did

| Problem | What the numbers said | What I did | Did it work |
|---|---|---|---|
| Students did not know us; two competitors already had the campus | Each spot had one item that outsold the rest | Pushed a star item per spot (chicken kothu parotta, boba tea, juice jars), launched trending items, Canva posters, WhatsApp community | Bills per day rose after each launch |
| A spot would go quiet for a few days | No exam or holiday explained it; students said they follow their friends | Got to know the regulars, kept them in the WhatsApp community | Far fewer quiet days |
| Students bought one thing and left | About 1.35 items per bill | Suggested one add-on at the counter, in their slang | About 1.6 items per bill |
| Food binned on some days | We cooked the same every day; exams and holidays were the worst | Planned prep from the college calendar and the season | Waste on exam days fell from 44% to 12% |
| Some dishes kept ending up in the bin | Weighing before serving and before binning: veg binned far more than it was eaten | Rebuilt the FoodJack menu around chicken | Veg and chicken now binned at the same low rate |
| The Engineering College spot could not cook | No exhaust there, so no wok stove for kothu parotta, fried rice or noodles | Sold only dishes ready-made at the hub kitchen, plus snacks straight from vendors | Ready-made dishes binned no more than at the Arts College; biryani became its best seller |

The details, with every number: [Findings](reports/findings.md).
How a day ran and the weekly loop: [How we ran it](docs/how_we_ran_it.md).
The changes as user stories with acceptance criteria, ready for Jira: [Backlog](docs/backlog.md).

![Food binned before and after planning from the college calendar](reports/waste_by_calendar.png)

## About the data

The problems and what I did are real. **The data is rebuilt.** I no longer have the original records, so
`src/generate_data.py` rebuilds them in the same shape we kept them: item sales from each spot's billing machine,
FoodJack food weighed before serving and before binning, SnackJack leftovers counted, and the college calendar.
Prices, quantities, the months of each change and the size of each effect are illustrative.

## How I built this

The problems, the decisions and what we changed all come from my time running Snackjack. I used Claude, an AI
assistant, to help me write the code and put the documents together. I set up the Jira board and the Confluence
pages myself, and I can walk through any part of this.

## Running it

```bash
pip install -r requirements-dev.txt
python src/generate_data.py   # rebuilds data/
python src/analyse.py         # runs the SQL in sql/, writes outputs/ and reports/
python -m pytest              # checks the numbers
```
