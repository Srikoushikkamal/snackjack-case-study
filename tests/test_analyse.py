from pathlib import Path

import pandas as pd
import pytest

import analyse
import generate_data

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="module")
def con():
    return analyse.load_database()


@pytest.fixture(scope="module")
def results(con):
    return analyse.run_queries(con)


def test_committed_data_matches_the_generator():
    sales, bills, fj, sj = generate_data.generate()
    assert pd.read_csv(DATA / "billing_item_sales.csv")["qty"].tolist() == sales["qty"].tolist()
    assert pd.read_csv(DATA / "billing_daily.csv")["bills"].tolist() == bills["bills"].tolist()
    assert pd.read_csv(DATA / "foodjack_waste_log.csv")["binned_kg"].tolist() == fj["binned_kg"].tolist()
    assert pd.read_csv(DATA / "snackjack_waste_log.csv")["wasted_units"].tolist() == sj["wasted_units"].tolist()


def test_sql_sales_match_a_separate_pandas_calculation(results):
    sales = pd.read_csv(DATA / "billing_item_sales.csv").merge(pd.read_csv(DATA / "items.csv"), on="item_id")
    revenue = (sales["qty"] * sales["price"]).groupby(sales["site_id"]).sum()
    bills = pd.read_csv(DATA / "billing_daily.csv").groupby("site_id")["bills"].sum()
    summary = results["01_spot_summary"].set_index("site_id")
    assert summary["revenue"].to_dict() == revenue.to_dict()
    assert summary["bills"].to_dict() == bills.to_dict()


def test_foodjack_kg_converts_to_portions(con):
    row = con.execute(
        "SELECT f.cooked_kg, i.portion_kg FROM foodjack_waste_log f JOIN items i USING (item_id) LIMIT 1").fetchone()
    view = con.execute("SELECT prepared_portions FROM waste_log LIMIT 1").fetchone()[0]
    assert view == pytest.approx(row[0] / row[1])


def test_star_dishes(results):
    top = results["02_star_dish"].query("rank == 1").set_index("site_id")["item_name"]
    assert top["FJ-ARTS"] == "Chicken Kothu Parotta"
    assert {top[s] for s in ("SJ-LIB", "SJ-BH", "SJ-GH")} == {"Boba Tea"}


def test_calendar_planning_cut_waste_on_exam_and_holiday_days(results):
    w = results["05_waste_by_calendar"].set_index(["day_type", "period"])["waste_pct"]
    assert w["exam", "after"] < w["exam", "before"] / 2
    assert w["holiday", "after"] < w["holiday", "before"] / 2


def test_veg_was_binned_out_of_proportion_before_the_chicken_menu(results):
    v = results["06_veg_vs_chicken"].set_index(["diet", "period"])
    assert v.loc[("veg", "before"), "share_of_binned_pct"] > v.loc[("veg", "before"), "share_of_sold_pct"] + 10


def test_ready_made_dishes_held_up_at_the_engineering_spot(results):
    e = results["07_engineering_menu"].set_index("site_name")["waste_pct"]
    assert abs(e["FoodJack, Engineering College"] - e["FoodJack, Arts College"]) < 3


def test_upselling_raised_items_per_bill(results):
    u = results["04_upselling"].set_index(["brand", "period"])["items_per_bill"]
    for brand in ("FoodJack", "SnackJack"):
        assert u[brand, "after"] > u[brand, "before"]


def test_quiet_days_fell_after_the_community(results):
    q = results["08_quiet_days"].set_index("period")["quiet_days_per_100"]
    assert q["after"] < q["before"] / 2
