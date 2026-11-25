from datetime import date

import pandas as pd

from generate_data import CHANGE_DATE, ITEMS, SITES, calendar, generate, on_menu


def test_same_seed_gives_same_data():
    for a, b in zip(generate(), generate()):
        pd.testing.assert_frame_equal(a, b)


def test_no_sales_before_a_spot_opened_or_an_item_launched():
    sales, bills, _, _ = generate()
    opened = SITES.set_index("site_id")["opened"]
    assert (sales["date"] >= sales["site_id"].map(opened)).all()
    assert (bills["date"] >= bills["site_id"].map(opened)).all()

    launched = ITEMS.dropna(subset=["launched_by"]).set_index("item_id")["launched_by"]
    for item_id, change in launched.items():
        first = sales.loc[sales["item_id"] == item_id, "date"].min()
        assert first >= CHANGE_DATE[change].isoformat()


def test_waste_logs_are_consistent():
    _, _, fj, sj = generate()
    assert (fj["binned_kg"] <= fj["cooked_kg"]).all()
    assert (fj["binned_kg"] >= 0).all()
    assert (sj["wasted_units"] <= sj["prepared_units"]).all()


def test_veg_dishes_come_off_foodjack_after_the_chicken_menu():
    assert on_menu("FJ-ARTS", "F04", date(2023, 5, 31))
    assert not on_menu("FJ-ARTS", "F04", date(2023, 6, 1))
    assert on_menu("FJ-ARTS", "F02", date(2024, 1, 1))  # plain biryani stays


def test_engineering_menu_drops_dishes_that_travel_badly():
    assert on_menu("FJ-ENG", "F03", date(2023, 10, 15))
    assert not on_menu("FJ-ENG", "F03", date(2023, 10, 16))
    assert on_menu("FJ-ARTS", "F03", date(2024, 1, 1))  # still the star at the arts college


def test_college_spots_closed_on_sundays_and_holidays():
    sales, *_ = generate()
    cal = calendar().set_index("date")
    college = sales[sales["site_id"].isin(["FJ-ARTS", "FJ-ENG", "SJ-LIB"])]
    days = college["date"].map(cal["weekday"])
    kinds = college["date"].map(cal["day_type"])
    assert not (days == "Sunday").any()
    assert not (kinds == "holiday").any()
