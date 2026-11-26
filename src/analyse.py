"""Load the records into SQLite, run the SQL, and write the findings.

Outputs:
  outputs/*.csv          query results, ready for Power BI or Excel
  reports/findings.md    the findings, with every number taken from the results
  reports/*.png          charts used in the findings
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, SQL, OUT, REPORTS = ROOT / "data", ROOT / "sql", ROOT / "outputs", ROOT / "reports"
TABLES = ["sites", "items", "changes", "calendar", "billing_item_sales", "billing_daily",
          "foodjack_waste_log", "snackjack_waste_log"]

BLUE, ORANGE, GREY, INK, MUTED = "#257de0", "#f47230", "#b8b8b8", "#1a1a1a", "#6b6b6b"


def load_database(data_dir=DATA):
    con = sqlite3.connect(":memory:")
    for table in TABLES:
        df = pd.read_csv(data_dir / f"{table}.csv")
        if table == "items":
            df["needs_wok"] = df["needs_wok"].map({True: 1, False: 0, "True": 1, "False": 0})
        df.to_sql(table, con, index=False)
    con.executescript((SQL / "00_views.sql").read_text())
    return con


def run_queries(con):
    return {p.stem: pd.read_sql_query(p.read_text(), con)
            for p in sorted(SQL.glob("*.sql")) if not p.stem.startswith("00_")}


def change_date(con, change_id):
    return con.execute("SELECT date FROM changes WHERE change_id = ?", (change_id,)).fetchone()[0]


def md_table(df):
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    rule = "|" + "|".join("---" for _ in df.columns) + "|"
    body = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([head, rule, *body])


def fmt(value):
    if isinstance(value, float):
        return f"{value:,.0f}" if value.is_integer() and abs(value) >= 1000 else f"{value:,.1f}"
    if hasattr(value, "dtype") or isinstance(value, int):
        return f"{int(value):,}"
    return str(value)


def rupees(value):
    return f"₹{value:,.0f}"


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GREY)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.6)
    ax.set_axisbelow(True)


def chart_waste_by_calendar(df, path):
    order = ["regular", "exam", "admissions", "holiday"]
    labels = {"regular": "Ordinary day", "exam": "Exams", "admissions": "Admissions", "holiday": "Holidays"}
    pivot = df.pivot(index="day_type", columns="period", values="waste_pct").reindex(order)
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150)
    x = range(len(order))
    w = 0.38
    for offset, period, colour, name in ((-w / 2, "before", GREY, "Before"), (w / 2, "after", BLUE, "After")):
        bars = ax.bar([i + offset for i in x], pivot[period], width=w - 0.03, color=colour, label=name)
        for bar, v in zip(bars, pivot[period]):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 1, f"{v:.0f}%", ha="center", fontsize=8, color=INK)
    ax.set_xticks(list(x), [labels[k] for k in order])
    ax.set_ylim(0, pivot.max().max() * 1.15)
    ax.set_ylabel("% of prepared food binned", color=MUTED, fontsize=9)
    ax.set_title("Food binned, before and after planning prep from the college calendar", loc="left",
                 fontsize=11, color=INK)
    ax.legend(frameon=False, fontsize=9)
    style(ax)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def chart_library_bills(con, path):
    df = pd.read_sql_query(
        "SELECT date, bills FROM billing_daily WHERE site_id = 'SJ-LIB' ORDER BY date", con)
    df["date"] = pd.to_datetime(df["date"])
    weekly = df.set_index("date")["bills"].resample("W").mean()
    launches = pd.read_sql_query(
        """SELECT c.date, i.item_name FROM changes c JOIN items i ON i.launched_by = c.change_id
           WHERE i.brand = 'SnackJack' ORDER BY c.date""", con)
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150)
    ax.plot(weekly.index, weekly.values, color=BLUE, linewidth=2)
    top = weekly.max()
    for n, (d, name) in enumerate(zip(pd.to_datetime(launches["date"]), launches["item_name"])):
        ax.axvline(d, color=ORANGE, linewidth=1, linestyle="--")
        ax.text(d, top * (1.12 if n % 2 else 1.03), f" {name}", color=INK, fontsize=8, va="bottom")
    ax.set_ylim(0, top * 1.24)
    ax.text(0.01, 0.02, "Gaps are holidays, when the library spot is closed.", transform=ax.transAxes,
            fontsize=8, color=MUTED)
    ax.set_ylabel("Bills per day (weekly average)", color=MUTED, fontsize=9)
    ax.set_title("SnackJack Library Block: bills per day, with new item launches", loc="left",
                 fontsize=11, color=INK)
    style(ax)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_findings(r, path):
    star = r["02_star_dish"].query("rank == 1").set_index("site_id")["item_name"]
    launches = r["03_new_items"]
    up = r["04_upselling"].set_index(["brand", "period"])
    cal = r["05_waste_by_calendar"].set_index(["day_type", "period"])["waste_pct"]
    veg = r["06_veg_vs_chicken"].set_index(["diet", "period"])
    eng = r["07_engineering_menu"].set_index("site_name")["waste_pct"]
    quiet = r["08_quiet_days"].set_index("period")["quiet_days_per_100"]

    launch_rows = "\n".join(
        f"| {row.item_name} | {row.bills_per_day_before:.0f} | {row.bills_per_day_after:.0f} | "
        f"{row.new_item_share_pct:.0f}% |" for row in launches.itertuples())

    text = f"""# Findings

Every number here comes from the SQL in `sql/`, run on the rebuilt records. The problems and the changes are real;
the sizes are illustrative (see the README).

## 1. Students did not know us

- **Checked:** which item sells most at each spot (`02_star_dish.sql`).
- **Found:** {star['FJ-ARTS']} leads FoodJack. {star['SJ-LIB']} leads every SnackJack spot.
- **Did:** pushed one star item per spot, and launched new trending items with Canva posters and WhatsApp posts.
- **Did it work:** bills per day, 4 weeks before and after each launch (`03_new_items.sql`):

| Launch | Bills per day before | After | New item's share of sales |
|---|---|---|---|
{launch_rows}

## 2. A spot would go quiet for a few days

- **Checked:** ordinary weekdays when bills fell below 85% of that spot's usual (`08_quiet_days.sql`).
- **Found:** no exam, holiday or power cut explained those days. Talking to students did: one friend picks another
  place and the whole group follows.
- **Did:** got to know the regulars and kept them in a WhatsApp community.
- **Did it work:** quiet days went from **{quiet['before']:.0f} in every 100** to **{quiet['after']:.0f} in every 100**.

## 3. Students bought one thing and left

- **Checked:** items per bill and average bill (`04_upselling.sql`).
- **Did:** suggested one add-on at the counter, in the students' own slang.
- **Did it work:** items per bill went from {up.loc[('SnackJack', 'before'), 'items_per_bill']:.2f} to
  {up.loc[('SnackJack', 'after'), 'items_per_bill']:.2f} at SnackJack and {up.loc[('FoodJack', 'before'), 'items_per_bill']:.2f}
  to {up.loc[('FoodJack', 'after'), 'items_per_bill']:.2f} at FoodJack.

## 4. Too much food binned on some days

- **Checked:** % of prepared food binned, by kind of day (`05_waste_by_calendar.sql`).
- **Found:** we cooked the same every day. Exams ({cal['exam', 'before']:.0f}% binned) and holidays
  ({cal['holiday', 'before']:.0f}%) were the worst.
- **Did:** planned each day's prep from the college calendar: exams, holidays, admissions, power cuts and the season.
- **Did it work:** exam days down to **{cal['exam', 'after']:.0f}%**, holidays to **{cal['holiday', 'after']:.0f}%**,
  ordinary days from {cal['regular', 'before']:.0f}% to {cal['regular', 'after']:.0f}%.

![Food binned by kind of day](waste_by_calendar.png)

## 5. Some dishes kept ending up in the bin

- **Checked:** weighed FoodJack food before serving and again before binning (`06_veg_vs_chicken.sql`).
- **Found:** veg dishes were {veg.loc[('veg', 'before'), 'share_of_sold_pct']:.0f}% of what students ate but
  {veg.loc[('veg', 'before'), 'share_of_binned_pct']:.0f}% of what we binned. They wanted chicken.
- **Did:** rebuilt the FoodJack menu around chicken.
- **Did it work:** FoodJack's binned % fell from {veg.loc[('veg', 'before'), 'waste_pct']:.0f}% on veg and
  {veg.loc[('chicken', 'before'), 'waste_pct']:.0f}% on chicken to {veg.loc[('veg', 'after'), 'waste_pct']:.0f}% and
  {veg.loc[('chicken', 'after'), 'waste_pct']:.0f}%
  (the calendar planning in section 4 helped too).

## 6. The Engineering College spot could not cook

- **Checked:** the spot has no exhaust, so a wok stove could not be set up. Kothu parotta, fried rice and noodles
  could not be made there.
- **Did:** sold only dishes already made at the hub kitchen (biryani, chapati and gravy, aloo parotta), plus snacks
  that came straight from vendors.
- **Did it work:** the ready-made dishes held up. Binned % on them was {eng['FoodJack, Engineering College']:.0f}% at the
  Engineering College against {eng['FoodJack, Arts College']:.0f}% at the Arts College (`07_engineering_menu.sql`), and
  {star['FJ-ENG']} became that spot's best seller.

## The loop that kept it working

Every day the billing machine totals, the waste weights and counts, and the calendar went into one Excel sheet.
Every week I looked at the same few numbers: bills per day, items per bill, and % binned by spot. If one moved the
wrong way, I went and asked the staff and the students why, changed one thing, and checked the same number the next
week.

![SnackJack Library Block bills per day](library_bills.png)
"""
    path.write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)
    con = load_database()
    results = run_queries(con)
    for name, df in results.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
    chart_waste_by_calendar(results["05_waste_by_calendar"], REPORTS / "waste_by_calendar.png")
    chart_library_bills(con, REPORTS / "library_bills.png")
    write_findings(results, REPORTS / "findings.md")
    print("Wrote outputs/, reports/findings.md and charts")


if __name__ == "__main__":
    main()
