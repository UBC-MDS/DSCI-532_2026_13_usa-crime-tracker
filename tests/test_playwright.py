#running test: 
# python -m pytest tests/test_playwright.py -v --browser firefox
from shiny.playwright import controller
from shiny.run import ShinyAppProc
from shiny.pytest import create_app_fixture
from playwright.sync_api import Page

from pathlib import Path
from shiny import App, ui, reactive, render
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import time

app = create_app_fixture("../src/app.py")

# Load and Clean Raw Crime Data
df_raw = pd.read_csv("data/raw/crime_rate_data_raw.csv").drop(columns=["source", "url"])
df_raw = df_raw.rename(columns={"department_name": "city", "ORI": "state_id"})
df_raw["city"] = df_raw["city"].str.partition(",")[0]
df_raw["state_id"] = df_raw["state_id"].str[:2]

# Load and Clean US Cities Data
cities = pd.read_csv("data/raw/uscities_raw.csv")
cities = cities[cities["state_name"] != "Puerto Rico"]
cities = cities[["city", "state_id", "lat", "lng"]]

# Merge Crime and City Data for Map Plot
df_merged = pd.merge(df_raw, cities, how="inner", on=["city", "state_id"])

# Get all cities
selected_cities = sorted(df_merged["city"].dropna().unique().tolist())

# Geographic data for the background map
# states = alt.topo_feature(data.us_10m.url, feature="states")

# Get the State Names as a map to ids in states data
state_id_map = {
    0: "All",
    1: "Alabama (AL)",
    2: "Alaska (AK)",
    4: "Arizona (AZ)",
    5: "Arkansas (AR)",
    6: "California (CA)",
    8: "Colorado (CO)",
    9: "Connecticut (CT)",
    10: "Delaware (DE)",
    11: "District of Columbia (DC)",
    12: "Florida (FL)",
    13: "Georgia (GA)",
    15: "Hawaii (HI)",
    16: "Idaho (ID)",
    17: "Illinois (IL)",
    18: "Indiana (IN)",
    19: "Iowa (IA)",
    20: "Kansas (KS)",
    21: "Kentucky (KY)",
    22: "Louisiana (LA)",
    23: "Maine (ME)",
    24: "Maryland (MD)",
    25: "Massachusetts (MA)",
    26: "Michigan (MI)",
    27: "Minnesota (MN)",
    28: "Mississippi (MS)",
    29: "Missouri (MO)",
    30: "Montana (MT)",
    31: "Nebraska (NE)",
    32: "Nevada (NV)",
    33: "New Hampshire (NH)",
    34: "New Jersey (NJ)",
    35: "New Mexico (NM)",
    36: "New York (NY)",
    37: "North Carolina (NC)",
    38: "North Dakota (ND)",
    39: "Ohio (OH)",
    40: "Oklahoma (OK)",
    41: "Oregon (OR)",
    42: "Pennsylvania (PA)",
    44: "Rhode Island (RI)",
    45: "South Carolina (SC)",
    46: "South Dakota (SD)",
    47: "Tennessee (TN)",
    48: "Texas (TX)",
    49: "Utah (UT)",
    50: "Vermont (VT)",
    51: "Virginia (VA)",
    53: "Washington (WA)",
    54: "West Virginia (WV)",
    55: "Wisconsin (WI)",
    56: "Wyoming (WY)",
}

# Convert Mapping id's to a data frame
mapping_df = pd.DataFrame(list(state_id_map.items()), columns=["id", "state_name"])

def wait_for_change(output, old_value, timeout=8):
    start = time.time()
    while time.time() - start < timeout:
        val = output.get_value()
        if val != old_value:
            return True
        time.sleep(0.1)
    return False


def wait_for_nonempty(output, timeout=8):
    start = time.time()
    while time.time() - start < timeout:
        val = output.get_value()
        if val and str(val).strip() != "":
            return val
        time.sleep(0.1)
    return output.get_value()


def test_year_slider_changes_kpi(page: Page, app: ShinyAppProc):
    """Verify that adjusting the year-range slider updates the total crimes KPI."""
    page.goto(app.url)

    total = controller.OutputText(page, "total_crimes")
    before = wait_for_nonempty(total)

    slider = controller.InputSliderRange(page, "year_range")

    # Set to a narrower range — this ALWAYS works
    slider.set(("2000", "2010"))

    assert wait_for_change(total, before)

def test_total_crimes_correct(page: Page, app: ShinyAppProc):
    """Ensure the app's displayed total crimes value matches the computed latest-year total from the dataset."""
    page.goto(app.url)

    total = controller.OutputText(page, "total_crimes")
    app_value = int(wait_for_nonempty(total).replace(",", ""))

    df = df_merged.copy()
    latest_year = df["year"].max()
    df_latest = df[df["year"] == latest_year]

    expected = int(df_latest["violent_crime"].sum())

    assert app_value == expected


def test_state_filter_total_crimes_correct(page: Page, app: ShinyAppProc):
    """Confirm that selecting a state filters the data correctly and the app's total crimes value matches the expected result."""
    page.goto(app.url)

    state = controller.InputSelect(page, "state_id")
    # Alabama
    state.set("1")  

    total = controller.OutputText(page, "total_crimes")
    app_value = int(wait_for_nonempty(total).replace(",", ""))

    df = df_merged.copy()

    st_abbr = state_id_map[1][-3:-1]
    df = df[df["state_id"] == st_abbr]

    latest_year = df["year"].max()
    df_latest = df[df["year"] == latest_year]

    expected = int(df_latest["violent_crime"].sum())

    assert app_value == expected

