from utils.filtering import apply_filters
from pathlib import Path
from shiny import App, ui, reactive, render
import anthropic
import os
import querychat
from chatlas import ChatGithub
from dotenv import load_dotenv

import pandas as pd
import altair as alt
from shinywidgets import output_widget, render_altair
from vega_datasets import data
import ibis

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
states = alt.topo_feature(data.us_10m.url, feature="states")

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

CRIME_CONFIG = {
    "violent": {
        "color": "#800000",
        "column": "violent_crime",
        "per_100k_column": "violent_per_100k",
        "title": "Violent Crime",
    },
    "homs": {
        "color": "#191970",
        "column": "homs_sum",
        "per_100k_column": "homs_per_100k",
        "title": "Homicides",
    },
    "rape": {
        "color": "#006064",
        "column": "rape_sum",
        "per_100k_column": "rape_per_100k",
        "title": "Rapes",
    },
    "rob": {
        "color": "#A0522D",
        "column": "rob_sum",
        "per_100k_column": "rob_per_100k",
        "title": "Robberies",
    },
    "agg_ass": {
        "color": "#2F4F4F",
        "column": "agg_ass_sum",
        "per_100k_column": "agg_ass_per_100k",
        "title": "Aggravated Assault",
    },
}


def test_filter_by_city():
    """Filtering by city should return all rows for that city in the dataset."""
    expected = df_merged[df_merged["city"] == "Seattle"]
    result = apply_filters(
        df_merged,
        cities=["Seattle"],
        crime_category="violent",
        crime_config=CRIME_CONFIG
    )
    assert len(result) == len(expected)

def test_filter_by_year():
    """Filtering by year should return all rows for that year in the dataset."""
    expected = df_merged[df_merged["year"] == 2020]
    result = apply_filters(
        df_merged,
        year_range=(2020, 2020),
        crime_category="violent",
        crime_config=CRIME_CONFIG
    )
    assert len(result) == len(expected)

def test_empty_filter_returns_all():
    """No filters applied should return the same rows the app would show with default settings."""
    
    expected = df_merged.copy()
    col = CRIME_CONFIG["violent"]["column"]
    expected = expected[expected[col].notnull()]
    
    result = apply_filters(
        df_merged,
        crime_category="violent",
        crime_config=CRIME_CONFIG
    )
    
    assert len(result) == len(expected)

def test_nonexistent_city_returns_empty():
    """Filtering for a city not in the dataset should return zero rows."""
    expected = df_merged[df_merged["city"] == "Vancouver"]
    result = apply_filters(
        df_merged,
        cities=["Vancouver"],
        crime_category="violent",
        crime_config=CRIME_CONFIG
    )
    assert len(result) == 0

def test_aggregation_correctness():
    """Ensures violent_crime equals the sum of its components, preventing incorrect totals in the dataset."""
    required = ["homs_sum", "rape_sum", "rob_sum", "agg_ass_sum", "violent_crime"]
    subset = df_merged.dropna(subset=required)

    expected = (
        subset["homs_sum"]
        + subset["rape_sum"]
        + subset["rob_sum"]
        + subset["agg_ass_sum"]
    )

    assert (subset["violent_crime"] == expected).all()

def test_year_boundary_condition():
    """Checks that filtering at the dataset's min/max year returns the correct rows, matching slider boundaries."""
    min_year = df_merged["year"].min()
    max_year = df_merged["year"].max()
    col = CRIME_CONFIG["violent"]["column"]

    expected_min = df_merged[
        (df_merged["year"] == min_year) &
        (df_merged[col].notnull())
    ]
    expected_max = df_merged[
        (df_merged["year"] == max_year) &
        (df_merged[col].notnull())
    ]

    result_min = apply_filters(
        df_merged,
        year_range=(min_year, min_year),
        crime_category="violent",
        crime_config=CRIME_CONFIG
    )
    result_max = apply_filters(
        df_merged,
        year_range=(max_year, max_year),
        crime_category="violent",
        crime_config=CRIME_CONFIG
    )

    assert len(result_min) == len(expected_min)
    assert len(result_max) == len(expected_max)
