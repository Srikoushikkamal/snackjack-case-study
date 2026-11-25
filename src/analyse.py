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
            df["travels_well"] = df["travels_well"].map({True: 1, False: 0, "True": 1, "False": 0})
        df.to_sql(table, con, index=False)
    con.executescript((SQL / "00_views.sql").read_text())
    return con


def run_queries(con):
    return {p.stem: pd.read_sql_query(p.read_text(), con)
            for p in sorted(SQL.glob("*.sql")) if not p.stem.startswith("00_")}


def change_date(con, change_id):
    return con.execute("SELECT date FROM changes WHERE change_id = ?", (change_id,)).fetchone()[0]


def switching_streaks(con, threshold=0.85, lookback=10):
    """Find days when a spot's bills dropped well below normal, and how long each drop lasted.

    Only ordinary college weekdays without a power cut are used, so exams, holidays
    and weekends do not count as drops. "Normal" is the median of the spot's
    previous `lookback` such days. Drops that last several days in a row point
    to groups of students eating elsewhere together, not to chance.
    """
    df = pd.read_sql_query(
        """
        SELECT b.date, b.site_id, b.bills
        FROM billing_daily b JOIN calendar c ON c.date = b.date
        WHERE c.day_type = 'regular' AND c.weekday NOT IN ('Saturday', 'Sunday') AND c.power_cut = 0
        ORDER BY b.site_id, b.date
        """, con)
    c2 = change_date(con, "C2")
    runs, days = [], []
    for site, g in df.groupby("site_id"):
        normal = g["bills"].shift(1).rolling(lookback, min_periods=lookback).median()
        g = g.assign(dip=g["bills"] < threshold * normal)[normal.notna()]
        length, last_date = 0, None
        for r in g.itertuples():
            if r.dip:
                length, last_date = length + 1, r.date
            elif length:
                runs.append((site, last_date, length))
                length = 0
        if length:
            runs.append((site, last_date, length))
        for period, part in (("before", g[g["date"] < c2]), ("after", g[g["date"] >= c2])):
            days.append((period, len(part), int(part["dip"].sum())))

    runs = pd.DataFrame(runs, columns=["site_id", "end_date", "days"])
    runs["period"] = (runs["end_date"] >= c2).map({True: "after", False: "before"})
    summary = pd.DataFrame(days, columns=["period", "days", "dip_days"]).groupby("period").sum()
    summary["dip_days_per_100"] = (100 * summary["dip_days"] / summary["days"]).round(1)
    summary["drops"] = runs.groupby("period").size()
    summary["avg_drop_length_days"] = runs.groupby("period")["days"].mean().round(1)
    summary["share_of_drops_2_days_or_more"] = (
        100 * (runs["days"] >= 2).groupby(runs["period"]).mean()).round(0)
    return summary.reindex(["before", "after"]).reset_index()


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


def write_findings(r, streaks, path):
    summary = r["01_spot_summary"]
    star = r["02_star_dish"]
    launches = r["03_new_items"]
    upsell = r["04_upselling"].set_index(["brand", "period"])
    cal = r["05_waste_by_calendar"].set_index(["day_type", "period"])
    veg = r["06_veg_vs_chicken"].set_index(["diet", "period"])
    eng = r["07_engineering_transport"].set_index(["dish_type", "period"])
    st = streaks.set_index("period")

    tops = star[star["rank"] == 1].merge(summary[["site_id", "site_name"]], on="site_id")
    star_view = star.merge(summary[["site_id", "site_name"]], on="site_id")[
        ["site_name", "rank", "item_name", "share_pct"]]
    star_view.columns = ["Spot", "Rank", "Item", "Share of spot's sales %"]
    summary_view = summary[["site_name", "opened", "revenue", "bills", "avg_bill", "waste_pct_of_sales"]]
    summary_view.columns = ["Spot", "Opened", "Sales (₹)", "Bills", "Average bill (₹)", "Waste % of sales"]
    launch_view = launches[["item_name", "bills_per_day_before", "bills_per_day_after", "new_item_share_pct"]]
    launch_view.columns = ["Launch", "Bills per day, 4 weeks before", "Bills per day, 4 weeks after",
                           "New item's share of SnackJack sales after %"]
    cal_view = r["05_waste_by_calendar"].pivot(index="day_type", columns="period", values="waste_pct")
    cal_view = cal_view.reindex(["regular", "exam", "admissions", "holiday"]).reset_index()[
        ["day_type", "before", "after"]]
    cal_view["day_type"] = cal_view["day_type"].map(
        {"regular": "Ordinary day", "exam": "Exams", "admissions": "Admissions", "holiday": "Holidays"})
    cal_view.columns = ["Kind of day", "Binned % before", "Binned % after"]
    veg_view = r["06_veg_vs_chicken"][["period", "diet", "share_of_sold_pct", "share_of_binned_pct", "waste_pct"]]
    veg_view.columns = ["Period", "Dish type", "Share of food eaten %", "Share of food binned %", "Binned % of cooked"]
    eng_view = r["07_engineering_transport"][["dish_type", "period", "prepared", "wasted", "waste_pct"]]
    eng_view.columns = ["Dishes", "Period", "Portions sent", "Portions binned", "Binned %"]
    streak_view = streaks[["period", "dip_days_per_100", "drops", "avg_drop_length_days",
                           "share_of_drops_2_days_or_more"]]
    streak_view.columns = ["Period", "Drop days per 100 days", "Drops", "Average length (days)",
                           "Drops lasting 2+ days %"]

    def star_of(site):
        return tops.set_index("site_id").loc[site, "item_name"]

    text = f"""# Findings

Generated by `src/analyse.py`. Every number below comes from the query results.
The records are rebuilt sample data (see the README): the problems and what I changed are real,
the sizes of the effects are illustrative.

## The spots

{md_table(summary_view)}

## 1. A star dish for each spot

`sql/02_star_dish.sql`, last six months of sales:

{md_table(star_view)}

FoodJack Arts College is led by **{star_of('FJ-ARTS')}**. Every SnackJack spot is led by **{star_of('SJ-LIB')}**. At the
Engineering College the leader is **{star_of('FJ-ENG')}**, because Kothu Parotta does not survive the trip from the hub
kitchen (see section 7).

## 2. New items brought students to the counter

`sql/03_new_items.sql`, SnackJack spots open for the full 8 weeks around each launch:

{md_table(launch_view)}

Each launch was backed by Canva posters and posts in the student WhatsApp community. Bills per day rose after each one.
Part of each rise comes from other things: the juice jars launched as summer started, when cold drinks sell more
anyway, and the spots were still growing. So the new item's own share of sales is the cleaner measure.

![SnackJack Library Block bills per day](library_bills.png)

## 3. Students move in groups

`switching_streaks` in `src/analyse.py` marks a drop when a spot's bills on an ordinary weekday fall below 85% of its
recent normal, and measures how many days each drop lasts.

{md_table(streak_view)}

Before the WhatsApp community and the posters, drops came **{st.loc['before', 'dip_days_per_100']:.1f} days in every 100**
(only {st.loc['before', 'days']:.0f} ordinary weekdays, so a small sample),
and {st.loc['before', 'share_of_drops_2_days_or_more']:.0f}% of them lasted two days or more. Random bad days rarely
come in runs; a group of friends deciding to eat somewhere else for a while does. After, drops came
{st.loc['after', 'dip_days_per_100']:.1f} days in every 100. The data shows the pattern; talking to the students is
what explained it.

## 4. Upselling in the students' own language

`sql/04_upselling.sql`, ordinary college days, 8 weeks either side:

| Brand | Items per bill before | after | Average bill before | after |
|---|---|---|---|---|
| FoodJack | {upsell.loc[('FoodJack', 'before'), 'items_per_bill']:.2f} | {upsell.loc[('FoodJack', 'after'), 'items_per_bill']:.2f} | {rupees(upsell.loc[('FoodJack', 'before'), 'avg_bill'])} | {rupees(upsell.loc[('FoodJack', 'after'), 'avg_bill'])} |
| SnackJack | {upsell.loc[('SnackJack', 'before'), 'items_per_bill']:.2f} | {upsell.loc[('SnackJack', 'after'), 'items_per_bill']:.2f} | {rupees(upsell.loc[('SnackJack', 'before'), 'avg_bill'])} | {rupees(upsell.loc[('SnackJack', 'after'), 'avg_bill'])} |

## 5. Waste and the college calendar

`sql/05_waste_by_calendar.sql`, all spots, share of prepared food that was binned:

{md_table(cal_view)}

Before, every open day was prepped like an ordinary day. Exams ({cal.loc[('exam', 'before'), 'waste_pct']:.0f}% binned)
and hostel holidays ({cal.loc[('holiday', 'before'), 'waste_pct']:.0f}%) were the worst. Planning prep from the exam
timetable, holidays, admissions, the monthly power cut and the season brought exam days to
**{cal.loc[('exam', 'after'), 'waste_pct']:.0f}%** and holidays to **{cal.loc[('holiday', 'after'), 'waste_pct']:.0f}%**.

![Food binned by kind of day](waste_by_calendar.png)

## 6. What the bin said: veg against chicken

FoodJack weighed what was cooked and weighed it again at the bin. `sql/06_veg_vs_chicken.sql`, ordinary college days:

{md_table(veg_view)}

Before the change, veg dishes were **{veg.loc[('veg', 'before'), 'share_of_sold_pct']:.0f}%** of what students ate but
**{veg.loc[('veg', 'before'), 'share_of_binned_pct']:.0f}%** of what was binned. The menu was rebuilt around chicken:
the veg versions of kothu parotta, fried rice and noodles came off, and the chicken versions were made in larger batches.

## 7. Food that does not travel

FoodJack Engineering College gets its food from the hub kitchen at the arts college. `sql/07_engineering_transport.sql`:

{md_table(eng_view)}

Dishes that do not hold up on the trip were binned at **{eng.loc[('does not travel well', 'before'), 'waste_pct']:.0f}%**,
against {eng.loc[('travels well', 'before'), 'waste_pct']:.0f}% for dishes that do. The Engineering College menu was
redesigned around the dishes that travel well.
"""
    path.write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)
    con = load_database()
    results = run_queries(con)
    streaks = switching_streaks(con)
    for name, df in results.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
    streaks.to_csv(OUT / "08_switching_streaks.csv", index=False)
    chart_waste_by_calendar(results["05_waste_by_calendar"], REPORTS / "waste_by_calendar.png")
    chart_library_bills(con, REPORTS / "library_bills.png")
    write_findings(results, streaks, REPORTS / "findings.md")
    print("Wrote outputs/, reports/findings.md and charts")


if __name__ == "__main__":
    main()
