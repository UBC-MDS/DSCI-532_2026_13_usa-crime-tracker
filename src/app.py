from shiny import App, ui, reactive, render
import pandas as pd
import altair as alt
from shinywidgets import output_widget, render_altair
from vega_datasets import data

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

# Configure plot settings for bubbles in map_plot
CRIME_CONFIG = {
    "violent": {
        "color": "#800000",
        "column": "violent_crime",
        "title": "Violent Crime",
    },
    "homs": {"color": "#191970", "column": "homs_sum", "title": "Homicides"},
    "rape": {"color": "#006064", "column": "rape_sum", "title": "Rapes"},
    "rob": {"color": "#A0522D", "column": "rob_sum", "title": "Robberies"},
    "agg_ass": {
        "color": "#2F4F4F",
        "column": "agg_ass_sum",
        "title": "Aggravated Assault",
    },
}

# intitial work for the input population slider
min_pop = int(df_merged["total_pop"].min())
max_pop = int(df_merged["total_pop"].max())

import querychat

#FIX API KEY
#os.environ["ANTHROPIC_API_KEY"] =


# ── querychat (Tab 1) 
qc = querychat.QueryChat(
    df_merged.copy(),
    "Statistics",
    greeting="""👋 Ask me anything about US crime statistics.

* <span class="suggestion">Filter to New York City only</span>
* <span class="suggestion">Which city has the highest crime rate?</span>
""",

    data_description="""
Violent Crime Statistics in the USA (for 57 cities from 32 states).
- state_id: state id code, for example: CA for california
- year: The year for a given set of crime statistics for a given city
- city: A city in the USA
- total_pop: total population of a given city in a given year
- homs_sum: total number of homicides for a given city in a given year
- rape_sum: total number of rapes for a given city in a given year
- rob_sum: total number of robberies for a given city in a given year
- agg_ass_sum: total number of aggravated assaults for a given city in a given year
- violent_crime: total number of violent crimes for a given city in a given year
- months_reported: number of months of the year reported in the crime stats
- violent_per_100k: number of violent crimes for a given city in a given year per 100k people
- homs_per_100k: number of homicides for a given city in a given year per 100k people
- rape_per_100k: number of rapes for a given city in a given year per 100k people
- rob_per_100k: number of robberies for a given city in a given year per 100k people
- agg_ass_per_100k: number of aggravated assaults for a given city in a given year per 100k people
- lat: latitude of a given city
- lng: longitude of a given city
""",
    extra_instructions="""
Use this dictionary to map State names to state_id's for filtering.
If someone asks for "California" you can use this to find the state code "CA" to filter state_id on:
state_mapping = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
}
""",
    client="anthropic/claude-haiku-4-5-20251001"
    #client=ChatGithub(model="gpt-4.1-mini"),
)
    # Code for LLM chat frontend UI
    # ui.nav_panel(
    #     "LLM Chat",
    #     ui.layout_sidebar(
    #         qc.sidebar(),
    #         ui.card(
    #             ui.card_header(ui.output_text("chat_title")),
    #             ui.output_data_frame("chat_table"),
    #             fill=True,
    #         ),
    #         fillable=True,
    #     ),
    # )

app_ui = ui.page_sidebar(
    # Filter Section
    ui.sidebar(
        ui.h4("Filters"),
        ui.hr(),
        ui.h5("Date Range and Population"),
        # ADDED: DATE SLIDER
        ui.h5("Date Range"),
        #ui.p("Date Range filter"),
        ui.input_slider(
            "year_range",
            "Select Year",
            min=int(df_merged["year"].min()),
            max=int(df_merged["year"].max()),
            value=[int(df_merged["year"].min()), int(df_merged["year"].max())],
            step=1
        ),
        ui.hr(),
        ui.input_slider(
            "population_range",
            "Population range",
            min=min_pop,
            max=max_pop,
            value=(min_pop, max_pop),
        ),
        ui.hr(),
        ui.h5("Geography"),
        ui.input_select("state_id", "State", state_id_map),
        ui.input_selectize(
            "cities",
            "City / Department",
            choices=["All"] + selected_cities,
            selected=["All"],
            multiple=True,
            options={
                "plugins": ["remove_button"],
                "placeholder": "All (default) or search cities...",
                "maxOptions": 150,
                "closeAfterSelect": True,
            },
        ),
        ui.hr(),
        ui.h5("Crime Details"),
        ui.input_select(
            "crime_category",
            "Crime Category:",
            {
                "violent": "All",
                "homs": "Homocide",
                "rape": "Rape",
                "rob": "Robery",
                "agg_ass": "Aggravated Assault",
            },
        ),
        # Aggregated crime filter
        ui.input_slider(
            "violent_range",
            "Violent Crime Range",
            min=int(df_raw["violent_crime"].min()),
            max=int(df_raw["violent_crime"].max()),
            value=(
                int(df_raw["violent_crime"].min()),
                int(df_raw["violent_crime"].max()),
            ),
        ),
    ),
    # Visualization and Summary Section
    ui.h1("USA Crime Dashboard"),
    # KPI and Summary
    ui.layout_columns(
        ui.value_box("Total Crimes", ui.output_text("total_crimes")),
        ui.value_box("Crime Rate (per 100k)", ui.output_text("crime_rate")),
        ui.value_box("Population", ui.output_text("pop_kpi")),
        # ADDED: KPI — MOST COMMON CRIME
        ui.card(
            ui.h5("Most Common Crime"),
            ui.output_text("kpi_most_common")
        ),
    ),
    ui.hr(),
    # Map Visuals
    ui.card(
        ui.h5("Crime Map"),
        output_widget("map_plot"),
    ),
    ui.hr(),
    # Modified: Aggregated Crime Line Plot + KPI table in same row
    ui.layout_columns(
        ui.column(
            12,
            ui.card(
                ui.h5("Violent crime over time"),
                output_widget("line_plot"),
            )
        ),
    
        ui.column(
            12,
            ui.card(
                ui.h5("Change in Crime Rate"),
                ui.output_data_frame("kpi_change_table")
            )
        )
    ),
    
    ui.hr()
)


def server(input, output, session):
    @reactive.calc
    def filtered_df():
        df = df_merged.copy()

        # Year filter
        try:
            yr_min, yr_max = input.year_range()
            # coerce year before comparing
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
            df = df.dropna(subset=["year"])
            df = df[(df["year"] >= yr_min) & (df["year"] <= yr_max)]
        except Exception:
            pass

        # State filter
        state_id_to_show = int(input.state_id())
        if state_id_to_show != 0:
            # state_id_map values look like "Alabama (AL)" -> grab "AL"
            st_abbr = state_id_map[state_id_to_show][-3:-1]
            df = df[df["state_id"] == st_abbr]

        # City filter
        selected = list(input.cities())
        if selected and "All" not in selected:
            df = df[df["city"].isin(selected)]

        # Violent range filter
        df["violent_crime"] = pd.to_numeric(df["violent_crime"], errors="coerce")
        df = df.dropna(subset=["violent_crime"])
        vmin, vmax = input.violent_range()
        df = df[(df["violent_crime"] >= vmin) & (df["violent_crime"] <= vmax)]

        # Crime category filter
        category = str(input.crime_category())
        config = CRIME_CONFIG.get(category, CRIME_CONFIG["violent"])
        col = config["column"]
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(subset=[col])

        # Population filter
        if hasattr(input, "population_range") and ("total_pop" in df.columns):
            pmin, pmax = input.population_range()
            df = df[(df["total_pop"] >= pmin) & (df["total_pop"] <= pmax)]

        return df

    @render.text
    def total_crimes():
        df = filtered_df().copy()
        latest_year = df["year"].max()
        df_latest = df[df["year"] == latest_year]
        tot = int(df_latest["violent_crime"].sum())
        return tot

    @render.text
    def crime_rate():
        df = filtered_df().copy()
        latest_year = df["year"].max()
        df_latest = df[df["year"] == latest_year]

        total_crime = df_latest["violent_crime"].sum()
        total_pop = df_latest.drop_duplicates(["city", "state_id"])["total_pop"].sum()
        rate = int((total_crime / total_pop) * 100000)

        return rate

    @render.text
    def pop_kpi():
        df = filtered_df().copy()
        latest_year = df["year"].max()
        df_latest = df[df["year"] == latest_year]
        duplicates_cities = df_latest.drop_duplicates(subset=["city", "state_id"])
        pop = int(duplicates_cities["total_pop"].sum())
        return pop

    @render.text
    def debug_line_plot():
        df = filtered_df()
        return (
            f"rows: {len(df)}\n"
            f"cities: {list(input.cities())}\n"
            f"violent_range: {input.violent_range()}\n"
        )

    @render_altair
    def line_plot():
        df = filtered_df().copy()

        category = str(input.crime_category())
        config = CRIME_CONFIG.get(category, CRIME_CONFIG["violent"])
        crime_col = config["column"]
        crime_title = config["title"]

        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df[crime_col] = pd.to_numeric(df[crime_col], errors="coerce")

        df = df.dropna(subset=["year", crime_col])

        if df.empty:
            return (
                alt.Chart(pd.DataFrame({"msg": ["No data after filtering"]}))
                .mark_text(size=16)
                .encode(text="msg:N")
            )

        selected = list(input.cities())
        multi = selected and ("All" not in selected)

        # If multiple cities are selected, show lines for each city. Otherwise, show aggregated line for all cities.
        if multi:
            plot_df = df.groupby(["year", "city"], as_index=False)[crime_col].sum()

            return (
                alt.Chart(plot_df)
                .mark_line()
                .encode(
                    x=alt.X("year:Q", title="Year"),
                    y=alt.Y(f"{crime_col}:Q", title=f"{crime_title} (count)"),
                    color=alt.Color("city:N", title="City/Dept"),
                    tooltip=["year:Q", "city:N", f"{crime_col}:Q"],
                )
                .properties(width="container", height=340)
            )

        # All Cities (aggregated)
        plot_df = df.groupby("year", as_index=False)[crime_col].sum()

        return (
            alt.Chart(plot_df)
            .mark_line()
            .encode(
                x=alt.X("year:Q", title="Year"),
                y=alt.Y(f"{crime_col}:Q", title=f"{crime_title} (count)"),
                tooltip=["year:Q", f"{crime_col}:Q"],
            )
            .properties(width="container", height=340)
        )

    @render_altair
    def map_plot():

        # need to filter df on years still!
        # need to change to collect inputs!

        df = df_merged.copy()

        state_id_to_show = int(input.state_id())
        selected = list(input.cities())
        category = str(input.crime_category())
        config = CRIME_CONFIG.get(category, CRIME_CONFIG["violent"])

        # Year filter
        try:
            yr_min, yr_max = input.year_range()
            # coerce year before comparing
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
            df = df.dropna(subset=["year"])
            df = df[(df["year"] >= yr_min) & (df["year"] <= yr_max)]
        except Exception:
            yr_min, yr_max = df["year"].min(), df["year"].max()

        # State filter
        state_id_to_show = int(input.state_id())
        if state_id_to_show != 0:
            # state_id_map values look like "Alabama (AL)" -> grab "AL"
            st_abbr = state_id_map[state_id_to_show][-3:-1]
            df = df[df["state_id"] == st_abbr]

        # Violent range filter
        df["violent_crime"] = pd.to_numeric(df["violent_crime"], errors="coerce")
        df = df.dropna(subset=["violent_crime"])
        vmin, vmax = input.violent_range()
        df = df[(df["violent_crime"] >= vmin) & (df["violent_crime"] <= vmax)]

        # Crime category filter
        category = str(input.crime_category())
        config = CRIME_CONFIG.get(category, CRIME_CONFIG["violent"])
        col = config["column"]
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(subset=[col])

        # Population filter
        if hasattr(input, "population_range") and ("total_pop" in df.columns):
            pmin, pmax = input.population_range()
            df = df[(df["total_pop"] >= pmin) & (df["total_pop"] <= pmax)]

        # State Level View
        state_view = not (state_id_to_show == 0)

        # Multi City Selection
        multi = selected and ("All" not in selected)

        if state_view:
            # Isolate the specific state
            background = (
                alt.Chart(states)
                .mark_geoshape(fill="#f0f0f0", stroke="white")
                .transform_filter(alt.datum.id == state_id_to_show)
                .transform_lookup(
                    lookup="id",
                    from_=alt.LookupData(mapping_df, "id", ["state_name"]),
                )
                .encode(tooltip=["state_name:N"])
            )

            # Plotting df
            plot_df = df

            # Get cities in the state
            state_cities = sorted(plot_df["city"].dropna().unique().tolist())

            # Keep only selected cities that are in the state
            selected = list(set(selected) & set(state_cities))

            # Aggregate State Level Data
            plot_df = plot_df.groupby(["city", "state_id"]).agg(["mean"])
            plot_df.columns = [c[0] for c in plot_df.columns]
            plot_df = plot_df.reset_index()

        else:
            # Country View
            background = (
                alt.Chart(states)
                .mark_geoshape(fill="#f0f0f0", stroke="white")
                .transform_lookup(
                    lookup="id", from_=alt.LookupData(mapping_df, "id", ["state_name"])
                )
                .encode(tooltip=["state_name:N"])
            )

            # Get country level data
            plot_df = df.groupby(["city", "state_id"]).agg(["mean"])
            plot_df.columns = [c[0] for c in plot_df.columns]
            plot_df = plot_df.reset_index()

        # Color Selected Cities
        if multi:

            # Create Cities Layer
            cities = (
                alt.Chart(plot_df)
                .mark_circle()
                .encode(
                    longitude="lng:Q",
                    latitude="lat:Q",
                    size=alt.Size(
                        f"{category}_per_100k:Q",
                        title=f"Avg {config['title']} per 100K ({yr_min}-{yr_max})",
                    ),
                    color=alt.condition(
                        alt.FieldOneOfPredicate(field="city", oneOf=selected),
                        alt.value(config["color"]),
                        alt.value("#DCDCDC"),
                    ),
                    tooltip=[
                        "city:N",
                        "state_id:N",
                        f"{config['column']}:Q",
                        f"{category}_per_100k:Q",
                    ],
                )
            )

            return (
                # Layer Cities on Background
                alt.layer(background, cities)
                .configure_view(stroke=None)
                .project("albersUsa")
                .properties(width="container", height=500)
            )

        # Color All Cities

        # Create Cities Layer
        cities = (
            alt.Chart(plot_df)
            .mark_circle()
            .encode(
                longitude="lng:Q",
                latitude="lat:Q",
                size=alt.Size(
                    f"{category}_per_100k:Q",
                    title=f"Avg {config['title']} per 100K ({yr_min}-{yr_max})",
                ),
                color=alt.value(config["color"]),
                tooltip=[
                    "city:N",
                    "state_id:N",
                    f"{config['column']}:Q",
                    f"{category}_per_100k:Q",
                ],
            )
        )
        return (
            # Layer Cities on Background
            alt.layer(background, cities)
            .configure_view(stroke=None)
            .project("albersUsa")
            .properties(width="container", height=500)
        )
    # ADDED: KPI — MOST COMMON CRIME (USING *_sum COLUMNS)
    @reactive.Calc
    def most_common_crime():
        d = filtered_df().copy()
        if d.empty:
            return "No data"

        crime_totals = {
            "Homicide": d["homs_sum"].sum(),
            "Rape": d["rape_sum"].sum(),
            "Robbery": d["rob_sum"].sum(),
            "Aggravated Assault": d["agg_ass_sum"].sum()
        }

        return max(crime_totals, key=crime_totals.get)

    @output
    @render.text
    def kpi_most_common():
        return most_common_crime()

    # ADDED: KPI — CHANGE IN CRIME RATE (violent_per_100k)
    @reactive.Calc
    def crime_change_table():
        d = filtered_df().copy()
        if d.empty:
            return pd.DataFrame({"message": ["No data available"]})

        # Compute average violent crime rate per year
        yearly = (
            d.groupby("year")["violent_per_100k"]
            .mean()
            .reset_index()
            .sort_values("year")
        )

        # ROUND ALL NUMERIC COLUMNS TO 2 DECIMAL PLACES 
        yearly["previous"] = round(yearly["violent_per_100k"].shift(1),2)
        yearly["change"] = round(yearly["violent_per_100k"] - yearly["previous"],2)
        yearly["violent_per_100k"] = round(yearly["violent_per_100k"],2)
        
        return yearly

    @output
    @render.data_frame
    def kpi_change_table():
        return crime_change_table()        

    # ── Tab 1: querychat 
    qc_vals = qc.server()

    @render.text
    def chat_title():
        return qc_vals.title() or "US Crime dataset"

    @render.data_frame
    def chat_table():
        return qc_vals.df()

        
app = App(app_ui, server)
