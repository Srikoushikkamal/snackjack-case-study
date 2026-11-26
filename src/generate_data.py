"""Rebuild Snackjack's daily records as sample data.

The spots, the menu, the problems and the changes are real. The numbers are not:
I no longer have the original billing and waste records, so this script rebuilds
data with the same shape as what we kept every day. Change dates and the size of
each effect are illustrative. The generator is deterministic (fixed seed).

What we recorded, and the file each becomes in data/:
  billing machine, item totals per spot per day   billing_item_sales.csv
  billing machine, number of bills per day        billing_daily.csv
  FoodJack: kg cooked, and kg binned at close     foodjack_waste_log.csv
  SnackJack: portions prepped and thrown away     snackjack_waste_log.csv
  college calendar                                calendar.csv
Reference tables: sites.csv, items.csv, changes.csv
"""
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 7
START, END = date(2023, 2, 1), date(2024, 9, 30)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

SITES = pd.DataFrame([
    ("FJ-ARTS", "FoodJack, Arts College", "FoodJack", "college", "2023-02-01", "Main kitchen (hub)"),
    ("SJ-LIB", "SnackJack, Arts Library Block", "SnackJack", "college", "2023-02-01", "Own counter"),
    ("SJ-BH", "SnackJack, Boys Hostel", "SnackJack", "hostel", "2023-06-15", "Own counter"),
    ("FJ-ENG", "FoodJack, Engineering College", "FoodJack", "college", "2023-08-01", "Ready-made food from the hub; no exhaust for a wok stove"),
    ("SJ-GH", "SnackJack, Girls Hostel", "SnackJack", "hostel", "2024-01-08", "Own counter"),
], columns=["site_id", "site_name", "brand", "location", "opened", "kitchen"])

# The changes I made, in order. Dates are illustrative.
CHANGES = pd.DataFrame([
    ("C1", "2023-04-03", "Talk to students in their own slang and suggest an add-on at the counter", "All"),
    ("C2", "2023-04-17", "Canva posters and a student WhatsApp community; friends with regulars", "All"),
    ("C3", "2023-06-01", "FoodJack menu rebuilt around chicken after weighing what was binned", "FoodJack"),
    ("C4", "2023-07-03", "Prep planned ahead from the college calendar and the season", "All"),
    ("C5", "2023-08-21", "Boba tea launched", "SnackJack"),
    ("C6", "2023-09-04", "Dosa varieties (podi, masala, potato, hot chutney, ghee podi masala, special spice)", "FJ-ARTS"),
    ("C7", "2023-10-09", "Waffles launched", "SnackJack"),
    ("C8", "2024-03-04", "500 ml juice jars launched for summer", "SnackJack"),
], columns=["change_id", "date", "change", "applies_to"])
CHANGE_DATE = {c: date.fromisoformat(d) for c, d in zip(CHANGES["change_id"], CHANGES["date"])}

# measured_by: kg = FoodJack, cooked in bulk and weighed; units = SnackJack, counted
# prep_type:   batch = made ahead, leftovers binned; to_order = made when ordered;
#              vendor = bought in from vendors, not logged as waste
# needs_wok:  cooked on the Chinese (wok) stove. The engineering college spot has no
#             exhaust for one, so it only sells food already made at the hub kitchen.
ITEMS = pd.DataFrame([
    ("F01", "Chicken Biryani", "FoodJack", "Main course", "chicken", "batch", "kg", 0.40, 130, 55, False, None),
    ("F02", "Plain Biryani", "FoodJack", "Main course", "veg", "batch", "kg", 0.35, 90, 32, False, None),
    ("F03", "Chicken Kothu Parotta", "FoodJack", "Main course", "chicken", "batch", "kg", 0.35, 120, 48, True, None),
    ("F04", "Veg Kothu Parotta", "FoodJack", "Main course", "veg", "batch", "kg", 0.35, 90, 32, True, None),
    ("F05", "Chicken Fried Rice", "FoodJack", "Main course", "chicken", "batch", "kg", 0.35, 110, 42, True, None),
    ("F06", "Veg Fried Rice", "FoodJack", "Main course", "veg", "batch", "kg", 0.35, 80, 28, True, None),
    ("F07", "Chicken Noodles", "FoodJack", "Main course", "chicken", "batch", "kg", 0.35, 110, 42, True, None),
    ("F08", "Veg Noodles", "FoodJack", "Main course", "veg", "batch", "kg", 0.35, 80, 28, True, None),
    ("F09", "Egg Fried Rice", "FoodJack", "Main course", "egg", "batch", "kg", 0.35, 90, 34, True, None),
    ("F10", "Chapati and Gravy", "FoodJack", "Main course", "veg", "batch", "kg", 0.30, 60, 22, False, None),
    ("F11", "Aloo Parotta", "FoodJack", "Main course", "veg", "batch", "kg", 0.30, 70, 25, False, None),
    ("F12", "Ghee Podi Roast", "FoodJack", "Dosa", "veg", "to_order", "kg", 0.25, 60, 20, False, "C6"),
    ("F13", "Masala Dosa", "FoodJack", "Dosa", "veg", "to_order", "kg", 0.25, 60, 22, False, "C6"),
    ("F14", "Chicken Special Spice Dosa", "FoodJack", "Dosa", "chicken", "to_order", "kg", 0.25, 90, 38, False, "C6"),
    ("S01", "Filter Coffee", "SnackJack", "Hot drink", None, "to_order", "units", None, 20, 7, None, None),
    ("S02", "Masala Tea", "SnackJack", "Hot drink", None, "to_order", "units", None, 15, 5, None, None),
    ("S03", "Fresh Juice", "SnackJack", "Cold drink", None, "batch", "units", None, 50, 20, None, None),
    ("S04", "Rose Milk", "SnackJack", "Cold drink", None, "to_order", "units", None, 40, 15, None, None),
    ("S05", "Milkshake", "SnackJack", "Cold drink", None, "to_order", "units", None, 90, 35, None, None),
    ("S06", "Veg Sandwich", "SnackJack", "Snack", None, "batch", "units", None, 60, 25, None, None),
    ("S07", "Chicken Roll", "SnackJack", "Snack", None, "batch", "units", None, 90, 40, None, None),
    ("S08", "Veg Momos", "SnackJack", "Snack", None, "batch", "units", None, 80, 30, None, None),
    ("S09", "Chicken Momos", "SnackJack", "Snack", None, "batch", "units", None, 100, 40, None, None),
    ("S10", "Cheese Fries", "SnackJack", "Snack", None, "to_order", "units", None, 80, 30, None, None),
    ("S11", "Boba Tea", "SnackJack", "Cold drink", None, "batch", "units", None, 120, 45, None, "C5"),
    ("S12", "Waffles", "SnackJack", "Snack", None, "batch", "units", None, 100, 35, None, "C7"),
    ("S13", "Juice Jar 500 ml", "SnackJack", "Cold drink", None, "batch", "units", None, 90, 35, None, "C8"),
    ("V01", "Vendor Snacks (puffs, samosa)", "FoodJack", "Snack", None, "vendor", "units", None, 20, 14, False, None),
], columns=["item_id", "item_name", "brand", "category", "diet", "prep_type", "measured_by", "portion_kg",
            "price", "unit_cost", "needs_wok", "launched_by"])

# Portions sold on an ordinary college day, before any of the changes.
BASE = {
    "FJ-ARTS": {"F01": 60, "F02": 35, "F03": 70, "F04": 30, "F05": 40, "F06": 25, "F07": 35, "F08": 20,
                "F09": 25, "F10": 30, "F11": 20, "F12": 30, "F13": 30, "F14": 20},
    # No exhaust, so no wok stove: ready-made dishes from the hub, snacks straight from vendors.
    "FJ-ENG": {"F01": 90, "F02": 45, "F10": 50, "F11": 30, "V01": 120},
    "SJ-LIB": {"S01": 120, "S02": 150, "S03": 40, "S04": 30, "S05": 30, "S06": 40, "S07": 25, "S08": 30,
               "S09": 30, "S10": 30, "S11": 60, "S12": 40, "S13": 35},
    "SJ-BH": {"S01": 100, "S02": 120, "S03": 30, "S04": 20, "S05": 40, "S06": 30, "S07": 40, "S08": 30,
              "S09": 45, "S10": 45, "S11": 50, "S12": 30, "S13": 30},
    "SJ-GH": {"S01": 90, "S02": 110, "S03": 45, "S04": 40, "S05": 45, "S06": 35, "S07": 25, "S08": 40,
              "S09": 30, "S10": 35, "S11": 80, "S12": 50, "S13": 45},
}
# Where demand goes when a veg dish comes off the FoodJack menu (C3).
VEG_TO_CHICKEN = {"F04": "F03", "F06": "F05", "F08": "F07"}

# Illustrative college calendar (Tamil Nadu arts and engineering colleges).
PERIODS = [
    ("exam", "2023-04-17", "2023-05-06"), ("holiday", "2023-05-08", "2023-06-18"),
    ("admissions", "2023-06-19", "2023-07-08"), ("holiday", "2023-11-11", "2023-11-14"),
    ("exam", "2023-11-20", "2023-12-15"), ("holiday", "2023-12-23", "2024-01-01"),
    ("holiday", "2024-01-13", "2024-01-17"), ("exam", "2024-04-15", "2024-05-04"),
    ("holiday", "2024-05-06", "2024-06-16"), ("admissions", "2024-06-17", "2024-07-06"),
]

# How busy each kind of day is compared with an ordinary college day.
DAY_FACTOR = {
    ("FoodJack", "college"): {"regular": 1.0, "exam": 0.55, "holiday": 0.0, "admissions": 1.3},
    ("SnackJack", "college"): {"regular": 1.0, "exam": 1.35, "holiday": 0.0, "admissions": 1.1},
    ("SnackJack", "hostel"): {"regular": 1.0, "exam": 1.25, "holiday": 0.15, "admissions": 0.9},
}
COLD = {"S03", "S04", "S05", "S11", "S13"}
BLENDER = {"S03", "S05", "S13"}
HOT = {"S01", "S02"}
ADD_ONS = {"S01", "S02", "S04", "S10", "F10"}


def calendar():
    rows = []
    day = START
    while day <= END:
        kind = "regular"
        for name, a, b in PERIODS:
            if date.fromisoformat(a) <= day <= date.fromisoformat(b):
                kind = name
        season = "summer" if day.month in (3, 4, 5) else "winter" if day.month in (11, 12, 1) else "mild"
        # Scheduled maintenance power cut: second Tuesday of each month.
        power_cut = day.weekday() == 1 and 8 <= day.day <= 14
        rows.append((day.isoformat(), day.strftime("%A"), kind, season, power_cut))
        day += timedelta(days=1)
    return pd.DataFrame(rows, columns=["date", "weekday", "day_type", "season", "power_cut"])


ITEM = ITEMS.set_index("item_id").to_dict("index")
NEEDS_WOK = set(ITEMS.loc[ITEMS["needs_wok"].eq(True), "item_id"])
LAUNCHED_BY = {i: c for i, c in zip(ITEMS["item_id"], ITEMS["launched_by"]) if isinstance(c, str)}


def after(change, day):
    return day >= CHANGE_DATE[change]


def on_menu(site_id, item_id, day):
    launched = LAUNCHED_BY.get(item_id)
    if launched and not after(launched, day):
        return False
    if item_id in VEG_TO_CHICKEN and after("C3", day):
        return False
    if site_id == "FJ-ENG" and item_id in NEEDS_WOK:
        return False  # no exhaust there, so no wok stove
    return True


def expected_demand(site, item_id, day, cal):
    """Demand anyone could have planned for: menu, calendar, season, power cuts."""
    brand, location = site["brand"], site["location"]
    weekday = day.weekday()
    if location == "college" and weekday == 6:
        return 0.0
    factor = DAY_FACTOR[(brand, location)][cal["day_type"]]
    if location == "college" and weekday == 5:
        factor *= 0.5
    if location == "hostel" and weekday == 6:
        factor *= 0.8

    base = BASE[site["site_id"]][item_id]
    if after("C3", day) and item_id in VEG_TO_CHICKEN.values():
        moved = [v for v, c in VEG_TO_CHICKEN.items() if c == item_id]
        base += 0.5 * sum(BASE[site["site_id"]][v] for v in moved)
    if cal["season"] == "summer":
        factor *= 1.4 if item_id in COLD else 0.8 if item_id in HOT else 1.0
    elif cal["season"] == "winter":
        factor *= 0.7 if item_id in COLD else 1.25 if item_id in HOT else 1.0
    if cal["power_cut"]:
        factor *= 0.2 if item_id in BLENDER else 0.85

    if brand == "SnackJack":
        launches = sum(after(c, day) for c in ("C5", "C7", "C8"))
        factor *= 1.05 ** launches  # each new item brought more students to the counter
    if after("C1", day) and item_id in ADD_ONS:
        factor *= 1.15
    return base * factor


def generate(seed=SEED):
    rng = np.random.default_rng(seed)
    cal = calendar()
    sales, bills, fj_waste, sj_waste = [], [], [], []
    episode_left = {s: 0 for s in SITES["site_id"]}

    for c in cal.itertuples(index=False):
        day = date.fromisoformat(c.date)
        c = c._asdict()
        for site in SITES.to_dict("records"):
            sid = site["site_id"]
            if day < date.fromisoformat(site["opened"]):
                continue
            # A group of friends starts eating somewhere else for a few days.
            if episode_left[sid] == 0 and rng.random() < (0.015 if after("C2", day) else 0.08):
                episode_left[sid] = int(rng.integers(2, 6))
            switching = episode_left[sid] > 0
            dip = (0.85 if after("C2", day) else 0.7) if switching else 1.0
            episode_left[sid] = max(0, episode_left[sid] - 1)

            total_units = 0
            for item_id in BASE[sid]:
                if not on_menu(sid, item_id, day):
                    continue
                expected = expected_demand(site, item_id, day, c)
                if expected == 0:
                    continue
                demand = int(rng.poisson(expected * dip))
                it = ITEM[item_id]

                if it["prep_type"] == "batch":
                    if after("C4", day):
                        prepared = int(round(expected * 1.10))
                    else:
                        regular = expected_demand(site, item_id, _ordinary_day(day), _ordinary_cal(c))
                        if item_id in VEG_TO_CHICKEN and not after("C3", day):
                            partner = VEG_TO_CHICKEN[item_id]
                            regular = (regular + expected_demand(site, partner, _ordinary_day(day),
                                                                 _ordinary_cal(c))) / 2
                        prepared = int(round(regular * 1.10))
                    sold = min(demand, prepared)
                    wasted = prepared - sold
                    if it["measured_by"] == "kg":
                        fj_waste.append((c["date"], sid, item_id, round(prepared * it["portion_kg"], 1),
                                         round(wasted * it["portion_kg"], 1)))
                    else:
                        sj_waste.append((c["date"], sid, item_id, prepared, wasted))
                else:
                    sold = demand
                if sold:
                    sales.append((c["date"], sid, item_id, sold))
                    total_units += sold

            if total_units:
                per_bill = 1.6 if after("C1", day) else 1.35
                bills.append((c["date"], sid, max(1, int(round(total_units / per_bill * rng.uniform(0.95, 1.05))))))

    return (
        pd.DataFrame(sales, columns=["date", "site_id", "item_id", "qty"]),
        pd.DataFrame(bills, columns=["date", "site_id", "bills"]),
        pd.DataFrame(fj_waste, columns=["date", "site_id", "item_id", "cooked_kg", "binned_kg"]),
        pd.DataFrame(sj_waste, columns=["date", "site_id", "item_id", "prepared_units", "wasted_units"]),
    )


def _ordinary_day(day):
    """The same weekday, treated as an ordinary college day (what a fixed prep sheet assumes)."""
    return day if day.weekday() < 5 else day - timedelta(days=day.weekday() - 4)


def _ordinary_cal(cal):
    return {**cal, "day_type": "regular", "season": "mild", "power_cut": False}


def main():
    DATA_DIR.mkdir(exist_ok=True)
    sales, bills, fj, sj = generate()
    SITES.to_csv(DATA_DIR / "sites.csv", index=False)
    ITEMS.to_csv(DATA_DIR / "items.csv", index=False)
    CHANGES.to_csv(DATA_DIR / "changes.csv", index=False)
    calendar().to_csv(DATA_DIR / "calendar.csv", index=False)
    sales.to_csv(DATA_DIR / "billing_item_sales.csv", index=False)
    bills.to_csv(DATA_DIR / "billing_daily.csv", index=False)
    fj.to_csv(DATA_DIR / "foodjack_waste_log.csv", index=False)
    sj.to_csv(DATA_DIR / "snackjack_waste_log.csv", index=False)
    print(f"Wrote {len(sales):,} sales rows, {len(bills):,} daily bill totals, "
          f"{len(fj):,} FoodJack and {len(sj):,} SnackJack waste rows to {DATA_DIR}")


if __name__ == "__main__":
    main()
