from pathlib import Path
from shiny import App, ui, reactive, render
import os
from dotenv import load_dotenv

import pandas as pd
from shinywidgets import output_widget, render_altair
from vega_datasets import data
import numpy as np

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


def apply_filters(
    df_merged,
    year_range=None,
    state_id=None,
    state_id_map=None,
    cities=None,
    violent_range=None,
    crime_category=None,
    crime_config=None,
    population_range=None,
):
    """
    Pure-Python version of the Shiny filtered_df() logic.
    This allows unit testing without Shiny or DuckDB.
    """

    filtered = df_merged.copy()

    # Year filter
    if year_range:
        yr_min, yr_max = year_range
        filtered = filtered[(filtered["year"] >= yr_min) & (filtered["year"] <= yr_max)]

    # State filter
    if state_id and state_id != 0:
        st_abbr = state_id_map[state_id][-3:-1]
        filtered = filtered[filtered["state_id"] == st_abbr]

    # City filter
    if cities and "All" not in cities:
        filtered = filtered[filtered["city"].isin(cities)]

    # Violent range filter
    if violent_range:
        vmin, vmax = violent_range
        filtered = filtered[
            (filtered["violent_per_100k"] >= vmin)
            & (filtered["violent_per_100k"] <= vmax)
        ]

    # Crime category filter
    if crime_category and crime_config:
        col = crime_config[crime_category]["column"]
        filtered = filtered[filtered[col].notnull()]

    # Population filter
    if population_range:
        pmin, pmax = population_range
        filtered = filtered[
            (filtered["total_pop"] >= pmin) & (filtered["total_pop"] <= pmax)
        ]

    return filtered
