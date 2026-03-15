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

load_dotenv(Path(__file__).parent.parent / ".env")

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

# intitial work for the input population slider
min_pop = int(df_merged["total_pop"].min())
max_pop = int(df_merged["total_pop"].max())

# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
# MAX_TOKENS = 300  # token limit

# FIX API KEY
# os.environ["ANTHROPIC_API_KEY"] =


# ── querychat (Tab 1)
qc = querychat.QueryChat(
    df_merged.copy(),
    "Statistics",
    greeting="""👋 Ask me anything about US crime statistics.

* <span class="suggestion">Filter to Los Angeles only</span>
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
    # client="anthropic/claude-haiku-4-5-20251001",
    client=ChatGithub(model="gpt-4.1-mini"),
)

# # Commented out LLM frontend UI code
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

app_ui = ui.page_navbar(
    # PAGE 1: Dashboard
    ui.nav_panel(
        "Dashboard",
        ui.page_sidebar(
            # Filter Section
            ui.sidebar(
                ui.div(
                    ui.h4("Filters"),
                    ui.hr(),
                    {"class": "sidebar-fixed-header"},
                ),
                # ui.p("Date Range filter"),
                ui.input_slider(
                    "year_range",
                    "Date Range",
                    min=int(df_merged["year"].min()),
                    max=int(df_merged["year"].max()),
                    value=[
                        int(df_merged["year"].max()) - 4,
                        int(df_merged["year"].max()),
                    ],
                    step=1,
                    sep="",
                ),
                ui.input_slider(
                    "population_range",
                    "Population range",
                    min=min_pop,
                    max=max_pop,
                    value=(min_pop, max_pop),
                ),
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
                    "Violent Crime Rate Range (per 100k)",
                    min=int(df_raw["violent_per_100k"].min()),
                    max=int(df_raw["violent_per_100k"].max()),
                    value=(
                        int(df_raw["violent_per_100k"].min()),
                        int(df_raw["violent_per_100k"].max()),
                    ),
                ),
                ui.input_action_button(
                    "reset_filters", "Reset Filters", class_="btn btn-outline-danger"
                ),
            ),
            ui.tags.style(
                """
                /* Make navbar a flex container to separate title and nav items */
                .navbar {
                    display: flex !important;
                    align-items: center !important;
                    width: 100% !important;
                }

                /* Place navbar title on the left and keep current text styling */
                .navbar-brand {
                    position: static;
                    transform: none;
                    flex-shrink: 0;
                    font-size: 1.6rem;
                    font-weight: 600;
                }

                /* Push navbar collapse (contains both buttons) to the right */
                .navbar-collapse {
                    margin-left: auto !important;
                    width: auto !important;
                    flex-grow: 0 !important;
                }

                .navbar-nav {
                    display: flex !important;
                    flex-direction: row !important;
                    margin-left: 0 !important;
                }
                
                /* Base styles for the sidebar collapse toggle button */
                .bslib-sidebar-layout > .collapse-toggle {
                    position: fixed;
                    right: auto !important;
                    z-index: 1031;
                }

                /* Position collapse button when sidebar is expanded */
                .bslib-sidebar-layout > .collapse-toggle[aria-expanded="true"] {
                    top: 68px !important;
                    left: calc(var(--_sidebar-width, 250px) - 40px) !important;
                    transform: none;
                }

                /* Position collapse button when sidebar is collapsed */
                .bslib-sidebar-layout > .collapse-toggle[aria-expanded="false"] {
                    top: 50% !important;
                    left: 10px !important;
                    transform: translateY(-50%);
                }

                /* Fix sidebar position and make it scrollable */
                .bslib-sidebar-layout > .sidebar {
                    position: fixed;
                    top: 56px;
                    bottom: 0;
                    width: var(--_sidebar-width, 250px);
                    background: white;
                    overflow-y: auto;
                    overflow-x: hidden;
                }

                /* Keep the sidebar resize handle fixed and visible while page scrolls */
                .bslib-sidebar-layout > .sidebar-resizer {
                    width: 6px !important;
                    z-index: 1032 !important;
                    cursor: col-resize;
                }

                /* Keep "Filters" header fixed at top of sidebar */
                .bslib-sidebar-layout > .sidebar .sidebar-fixed-header {
                    position: fixed;
                    top: 56px;
                    left: 25px;
                    width: calc(var(--_sidebar-width, 250px) - 30px);
                    z-index: 1030;
                    background: white;
                    padding-top: 0.75rem;
                    padding-bottom: 0.75rem;
                }

                /* Remove default margin from "Filters" heading */
                .bslib-sidebar-layout > .sidebar .sidebar-fixed-header h4 {
                    margin: 0;
                }

                /* Adjust spacing of horizontal line in header */
                .bslib-sidebar-layout > .sidebar .sidebar-fixed-header hr {
                    margin-top: 0.75rem;
                    margin-bottom: 0;
                }
                
                /* Add spacing below fixed header to prevent content overlap */
                .bslib-sidebar-layout > .sidebar > :not(.sidebar-fixed-header) {
                    margin-top: 25px;
                }
                
                /* Style the fixed KPI header section */
                .fixed-main-header {
                    position: fixed;
                    z-index: 1020;
                    background: white;
                    border-bottom: 1px solid #ddd;
                    padding-top: 0.4rem;
                    padding-bottom: 0.2rem;
                    box-sizing: border-box;
                }

                /* Remove default margins from h1 in fixed header */
                .fixed-main-header h1 {
                    margin-top: 0;
                    margin-bottom: 0.2rem;
                }

                /* Add top offset for AI Assistant tab under fixed navbar */
                .ai-assistant-offset {
                    margin-top: 56px;
                }
            """
            ),
            ui.tags.script(
                """
                function syncFixedMainHeader() {
                    const header = document.querySelector('.fixed-main-header');
                    const main = document.querySelector('.bslib-page-main');
                    const navbar = document.querySelector('.navbar');

                    if (!header || !main) return;

                    const navHeight = navbar ? navbar.offsetHeight : 56;
                    const rect = main.getBoundingClientRect();

                    header.style.left = rect.left + 'px';
                    header.style.width = rect.width + 'px';
                    header.style.top = navHeight + 'px';
                    main.style.paddingTop = (navHeight + header.offsetHeight + 4) + 'px';
                }

                function syncSidebarResizer() {
                    const navbar = document.querySelector('.navbar');
                    const sidebar = document.querySelector('.bslib-sidebar-layout > .sidebar');

                    if (!sidebar) return;

                    const resizer = document.querySelector(
                        '.bslib-sidebar-layout > .sidebar-resizer, ' +
                        '.bslib-sidebar-layout .sidebar-resizer, ' +
                        '.bslib-sidebar-layout [title="Drag to resize sidebar"], ' +
                        '.bslib-sidebar-layout [aria-label="Drag to resize sidebar"]'
                    );

                    if (!resizer) return;

                    const navHeight = navbar ? navbar.offsetHeight : 56;
                    const sidebarRect = sidebar.getBoundingClientRect();

                    resizer.style.setProperty('position', 'fixed', 'important');
                    resizer.style.setProperty('top', navHeight + 'px', 'important');
                    resizer.style.setProperty('bottom', '0', 'important');
                    resizer.style.setProperty('left', (sidebarRect.right - 3) + 'px', 'important');
                    resizer.style.setProperty('width', '6px', 'important');
                    resizer.style.setProperty('height', 'auto', 'important');
                    resizer.style.setProperty('z-index', '1032', 'important');
                    resizer.style.setProperty('cursor', 'col-resize', 'important');
                }

                window.addEventListener('load', syncFixedMainHeader);
                window.addEventListener('load', syncSidebarResizer);
                window.addEventListener('resize', syncFixedMainHeader);
                window.addEventListener('resize', syncSidebarResizer);
                window.addEventListener('scroll', () => setTimeout(syncSidebarResizer, 0), true);
                document.addEventListener('click', () => setTimeout(syncFixedMainHeader, 50));
                document.addEventListener('click', () => setTimeout(syncSidebarResizer, 50));

                const observer = new MutationObserver(() => {
                    setTimeout(syncFixedMainHeader, 50);
                    setTimeout(syncSidebarResizer, 50);
                });

                window.addEventListener('load', () => {
                    observer.observe(document.body, {
                        attributes: true,
                        childList: true,
                        subtree: true
                    });
                });
            """
            ),
            # Visualization and Summary Section
            ui.div(
                {"class": "fixed-main-header"},
                # KPI and Summary
                ui.layout_columns(
                    ui.value_box(
                        "Total Crimes",
                        ui.div(
                            ui.output_text("total_crimes"),
                            ui.div(
                                {"style": "font-size:12px; color:gray;"},
                                ui.output_ui("total_crimes_change"),
                            ),
                        ),
                    ),
                    ui.value_box(
                        "Crime Rate (per 100k)",
                        ui.div(
                            ui.output_text("crime_rate"),
                            ui.div(
                                {"style": "font-size:12px; color:gray;"},
                                ui.output_ui("crime_rate_change"),
                            ),
                        ),
                    ),
                    ui.value_box(
                        "Population",
                        ui.div(
                            ui.output_text("pop_kpi"),
                            ui.div(
                                {"style": "font-size:12px; color:gray;"},
                                ui.output_ui("pop_change"),
                            ),
                        ),
                    ),
                    # ADDED: KPI — MOST COMMON CRIME
                    ui.card(
                        ui.h5("Most Common Crime"), ui.output_text("kpi_most_common")
                    ),
                ),
            ),
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
                        ui.h5("Crime Rate Over Time (per 100k)"),
                        output_widget("line_plot"),
                    ),
                ),
                ui.column(
                    12,
                    ui.card(
                        ui.h5(ui.output_text("change_table_title")),
                        ui.div(
                            {"style": "font-size:12px; color:gray; margin-top:4px;"},
                            ui.output_text("aggregation_note"),
                        ),
                        ui.output_data_frame("kpi_change_table"),
                    ),
                ),
            ),
            ui.hr(),
        ),
    ),
    # PAGE 2: AI Assistant
    ui.nav_panel(
        "AI Assistant",
        ui.layout_sidebar(
            ui.sidebar(
                # ui.div(
                #     ui.h4("Filters"),
                #     ui.hr(),
                #     {"class": "sidebar-fixed-header"},
                # ),
                ui.input_select(
                    "chat_crime_category",
                    "Crime Category:",
                    {
                        "violent": "All",
                        "homs": "Homicide",
                        "rape": "Rape",
                        "rob": "Robbery",
                        "agg_ass": "Aggravated Assault",
                    },
                ),
                ui.h5("Data Assistant"),
                ui.div(
                    qc.ui(),
                    ui.hr(),
                    ui.download_button("download_data", "Download Filtered CSV"),
                    style="height: calc(100vh); overflow-y: auto;",  # Forces scrolling inside the div
                ),
                width="clamp(250px, 30vw, 500px)",
            ),
            ui.hr(),
            # --- Map ---
            ui.card(
                ui.h5(ui.output_text("chat_map_title")),
                output_widget("chat_map_plot"),
            ),
            ui.hr(),
            # --- Visual Summaries ---
            ui.layout_columns(
                # --- Line Chart ---
                ui.column(
                    12,
                    ui.card(
                        ui.h5("Violent Crime Over Time"),
                        output_widget("chat_line_plot"),
                        # fill=True,
                    ),
                ),
                # --- Rate Change Table ---
                ui.column(
                    12,
                    ui.card(
                        ui.card_header(ui.output_text("chat_title")),
                        ui.output_data_frame("chat_table"),
                        fill=True,
                    ),
                ),
            ),
            fillable=True,
        ),
        value="llm_interface",
        # ui.layout_columns(
        #     {"class": "ai-assistant-offset"},
        #     ui.card(
        #         ui.h3("AI Assistant"),
        #         ui.input_text_area(
        #             "ai_user_input",
        #             "Ask the AI about the dataset:",
        #             placeholder="e.g., summarize crime trends in Texas",
        #             rows=4,
        #         ),
        #         ui.input_action_button("ai_send_btn", "Send"),
        #         ui.hr(),
        #         ui.h4("AI Response"),
        #         ui.output_text_verbatim("ai_chat_output"),
        #         ui.hr(),
        #         ui.h4("Filtered DataFrame"),
        #         ui.output_data_frame("ai_dataframe_output"),
        #     ),
        # ),
    ),
    title=ui.output_text("dashboard_title"),
    position="fixed-top",
    bg="#2c4750",  # Background color (Hex code)
    inverse=True,  # Light text for dark backgrounds
    footer=ui.tags.div(
        # ui.markdown("---"),
        ui.p("2026 MDS DSCI 532 Group 13 | System Status: Online"),
        style="padding: 10px; text-align: center; font-size: 0.8em;",
    ),
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

        category = input.crime_category()

        if category == "violent":
            crime_col = "violent_crime"

        elif category == "homs":
            crime_col = "homs_sum"

        elif category == "rape":
            crime_col = "rape_sum"

        elif category == "rob":
            crime_col = "rob_sum"

        elif category == "agg_ass":
            crime_col = "agg_ass_sum"

        tot = int(df_latest[crime_col].sum())

        return f"{tot:,}"

    @render.text
    def total_crimes_change():

        df = filtered_df().copy()
        if df.empty:
            return ""

        yr_min, yr_max = input.year_range()
        category = input.crime_category()

        if category == "violent":
            crime_col = "violent_crime"
        elif category == "homs":
            crime_col = "homs_sum"
        elif category == "rape":
            crime_col = "rape_sum"
        elif category == "rob":
            crime_col = "rob_sum"
        elif category == "agg_ass":
            crime_col = "agg_ass_sum"

        df_latest = df[df["year"] == yr_max]
        df_prev = df[(df["year"] >= yr_min) & (df["year"] < yr_max)]

        latest_total = df_latest[crime_col].sum()

        prev_yearly_total = df_prev.groupby("year")[crime_col].sum()

        prev_avg_total = prev_yearly_total.mean()

        pct_change = ((latest_total - prev_avg_total) / prev_avg_total) * 100
        pct_change = round(pct_change, 2)

        color = "red" if pct_change > 0 else "green"
        sign = "+" if pct_change > 0 else ""

        return ui.span(
            f"{sign}{pct_change}% vs {yr_min}-{yr_max-1} avg",
            style=f"font-size:12px; color:{color};",
        )

    @render.text
    def crime_rate():
        df = filtered_df().copy()
        latest_year = df["year"].max()
        df_latest = df[df["year"] == latest_year]

        category = input.crime_category()

        if category == "violent":
            crime_col = "violent_crime"
        elif category == "homs":
            crime_col = "homs_sum"
        elif category == "rape":
            crime_col = "rape_sum"
        elif category == "rob":
            crime_col = "rob_sum"
        elif category == "agg_ass":
            crime_col = "agg_ass_sum"

        total_crime = df_latest[crime_col].sum()
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

        return f"{pop:,}"

    @render.text
    def pop_change():

        df = filtered_df().copy()
        if df.empty:
            return ""

        yr_min, yr_max = input.year_range()

        # latest year
        df_latest = df[df["year"] == yr_max]

        # previous years
        df_prev = df[(df["year"] >= yr_min) & (df["year"] < yr_max)]

        latest_pop = df_latest.drop_duplicates(["city", "state_id"])["total_pop"].sum()

        prev_yearly_pop = df_prev.groupby("year").apply(
            lambda x: x.drop_duplicates(["city", "state_id"])["total_pop"].sum()
        )

        prev_avg_pop = prev_yearly_pop.mean()

        pct_change = ((latest_pop - prev_avg_pop) / prev_avg_pop) * 100
        pct_change = round(pct_change, 2)

        color = "green" if pct_change > 0 else "red"
        sign = "+" if pct_change > 0 else ""

        return ui.span(
            f"{sign}{pct_change}% vs {yr_min}-{yr_max-1} avg",
            style=f"font-size:12px; color:{color};",
        )

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
        per_100k_col = config["per_100k_column"]
        crime_title = config["title"]

        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df[per_100k_col] = pd.to_numeric(df[per_100k_col], errors="coerce")

        df = df.dropna(subset=["year", per_100k_col])

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
            plot_df = df.groupby(["year", "city"], as_index=False)[per_100k_col].mean()

            return (
                alt.Chart(plot_df)
                .mark_line()
                .encode(
                    x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
                    y=alt.Y(f"{per_100k_col}:Q", title=f"{crime_title} (per 100k)"),
                    color=alt.Color("city:N", title="City/Dept"),
                    tooltip=[
                        alt.Tooltip("year:Q", title="Year", format="d"),
                        "city:N",
                        f"{per_100k_col}:Q",
                    ],
                )
                .properties(width="container", height=340)
            )

        # All Cities (aggregated)
        plot_df = df.groupby("year", as_index=False)[per_100k_col].mean()

        return (
            alt.Chart(plot_df)
            .mark_line()
            .encode(
                x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
                y=alt.Y(f"{per_100k_col}:Q", title=f"{crime_title} (per 100k)"),
                tooltip=[
                    alt.Tooltip("year:Q", title="Year", format="d"),
                    f"{per_100k_col}:Q",
                ],
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
            "Aggravated Assault": d["agg_ass_sum"].sum(),
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
        category = input.crime_category()

        if category == "violent":
            rate_col = "violent_per_100k"
            title = "Violent Crime"

        elif category == "homs":
            rate_col = "homs_per_100k"
            title = "Homicide"

        elif category == "rape":
            rate_col = "rape_per_100k"
            title = "Rape"

        elif category == "rob":
            rate_col = "rob_per_100k"
            title = "Robbery"

        elif category == "agg_ass":
            rate_col = "agg_ass_per_100k"
            title = "Aggravated Assault"

        yearly = (
            d.groupby("year").agg({rate_col: "mean"}).reset_index().sort_values("year")
        )

        yearly["Change in crime rate (%)"] = round(
            yearly[rate_col].pct_change(periods=1) * 100, 2
        )
        yearly[rate_col] = yearly[rate_col].round(3)

        yearly = yearly.rename(
            columns={
                "year": "Year",
                rate_col: f"{title} Rate (per 100k)",
                "Change in crime rate (%)": f"Change in {title} Rate (%)",
            }
        )

        return yearly

    @output
    @render.text
    def change_table_title():
        category = input.crime_category()
        yr_min, yr_max = input.year_range()

        if category == "violent":
            title = "Violent Crime"
        elif category == "homs":
            title = "Homicide"
        elif category == "rape":
            title = "Rape"
        elif category == "rob":
            title = "Robbery"
        elif category == "agg_ass":
            title = "Aggravated Assault"

        return f"Change in {title} Rate ({yr_min}-{yr_max})"

    @render.text
    def aggregation_note():
        selected = list(input.cities())

        if selected and "All" not in selected and len(selected) > 1:
            return "Note: Table values are aggregated across selected cities."

        return ""

    @output
    @render.text
    def crime_rate_change():

        df = filtered_df().copy()
        if df.empty:
            return ""

        category = input.crime_category()

        if category == "violent":
            crime_col = "violent_crime"
            title = "Violent Crime"

        elif category == "homs":
            crime_col = "homs_sum"
            title = "Homicide"

        elif category == "rape":
            crime_col = "rape_sum"
            title = "Rape"

        elif category == "rob":
            crime_col = "rob_sum"
            title = "Robbery"

        elif category == "agg_ass":
            crime_col = "agg_ass_sum"
            title = "Aggravated Assault"

        yr_min, yr_max = input.year_range()

        df_latest = df[df["year"] == yr_max]
        df_prev = df[(df["year"] >= yr_min) & (df["year"] < yr_max)]

        latest_crime = df_latest[crime_col].sum()
        latest_pop = df_latest.drop_duplicates(["city", "state_id"])["total_pop"].sum()
        latest_rate = (latest_crime / latest_pop) * 100000

        prev_crime = df_prev[crime_col].sum()
        prev_pop = df_prev.drop_duplicates(["city", "state_id"])["total_pop"].sum()
        prev_rate = (prev_crime / prev_pop) * 100000
        prev_rate = prev_rate / (yr_max - yr_min)

        pct_change = ((latest_rate - prev_rate) / prev_rate) * 100
        pct_change = round(pct_change, 2)

        color = "red" if pct_change > 0 else "green"
        sign = "+" if pct_change > 0 else ""

        return ui.span(
            f"{sign}{pct_change}% vs {yr_min}-{yr_max-1} avg",
            style=f"font-size:12px; color:{color};",
        )

    @render.text
    def dashboard_title():
        yr_min, yr_max = input.year_range()
        return f"USA Crime Dashboard ({yr_min}–{yr_max})"

    @reactive.Effect  # Used Ai for help figuring out how to do reset the filter
    @reactive.event(input.reset_filters)
    def _():

        ui.update_slider(
            "year_range",
            value=[int(df_merged["year"].max()) - 4, int(df_merged["year"].max())],
        )

        ui.update_slider("population_range", value=(min_pop, max_pop))

        ui.update_select("state_id", selected=0)

        ui.update_selectize("cities", selected=["All"])

        ui.update_select("crime_category", selected="violent")

        ui.update_slider(
            "violent_range",
            value=(
                int(df_raw["violent_crime"].min()),
                int(df_raw["violent_crime"].max()),
            ),
        )

    @output
    @render.data_frame
    def kpi_change_table():
        return crime_change_table()

    # @reactive.Effect
    # @reactive.event(input.ai_send_btn)
    # def _():
    #     user_input = input.ai_user_input()

    #     if not user_input:
    #         output.ai_chat_output.set("Please enter a question.")
    #         return

    #     output.ai_chat_output.set("Thinking...")

    #     async def call_ai():
    #         try:
    #             response = await asyncio.to_thread(
    #                 client.messages.create,
    #                 model="claude-haiku-4-5-20251001",
    #                 max_tokens=MAX_TOKENS,
    #                 messages=[{"role": "user", "content": user_input}],
    #             )
    #             return response.content[0].text
    #         except Exception as e:
    #             return f"Error calling Anthropic API: {e}"

    #     task = reactive.Task(call_ai())

    #     @task.on_done
    #     def _(result):
    #         output.ai_chat_output.set(result)

    # # Filtered df
    # @output
    # @render.data_frame
    # def ai_dataframe_output():
    #     return filtered_df()

    # # ── Tab 2: querychat
    # qc_vals = qc.server()

    # @render.text
    # def chat_title():
    #     return qc_vals.title() or "US Crime dataset"

    # @render.data_frame
    # def chat_table():
    #     return qc_vals.df()

    # --- Tab 2: querychat ---
    qc_vals = qc.server()

    @render.text
    def chat_title():
        return qc_vals.title() or "Crime Statistics Dataset"

    @render.data_frame
    def chat_table():
        return qc_vals.df()

    # filtered_df_reactive = querychat_server("chat_logic", data=pd.read_csv("data.csv"))

    @reactive.calc
    def chat_filtered_data():
        # This gets the data currently visible in your chat_table,
        # taking into account the AI's filters AND any manual selections.
        selected_df = chat_table.data_view(selected=True)

        # If nothing is selected, maybe return the whole chat-filtered df
        if selected_df.empty:
            return qc_vals.df()

        return selected_df

    # Define download handler
    @render.download(filename="filtered_data.csv")
    def download_data():
        # Access the current state of the filtered dataframe
        df = chat_filtered_data()

        # Yield the CSV content
        yield df.to_csv(index=False)

    @render.text
    def chat_map_title():
        df = chat_filtered_data().copy()
        yr_max = df["year"].max()
        yr_min = df["year"].min()
        if yr_max == yr_min:
            return f"Crime Map ({yr_min})"
        return f"Crime Map ({yr_min}-{yr_max})"

    # --- Chart 1: LLM filtered Line Chart ---
    @render_altair
    def chat_line_plot():
        df = chat_filtered_data().copy()

        category = str(input.chat_crime_category())
        config = CRIME_CONFIG.get(category, CRIME_CONFIG["violent"])
        per_100k_col = config["per_100k_column"]
        crime_title = config["title"]

        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df[per_100k_col] = pd.to_numeric(df[per_100k_col], errors="coerce")

        df = df.dropna(subset=["year", per_100k_col])

        if df.empty:
            return (
                alt.Chart(pd.DataFrame({"msg": ["No data after filtering"]}))
                .mark_text(size=16)
                .encode(text="msg:N")
            )

        selected = list(df["city"].unique())
        multi = (len(selected) > 1) and (len(selected) != 57)

        # If multiple cities are selected, show lines for each city. Otherwise, show aggregated line for all cities.
        if multi:
            plot_df = df.groupby(["year", "city"], as_index=False)[per_100k_col].mean()

            return (
                alt.Chart(plot_df)
                .mark_line()
                .encode(
                    x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
                    y=alt.Y(f"{per_100k_col}:Q", title=f"{crime_title} (per 100k)"),
                    color=alt.Color("city:N", title="City/Dept"),
                    tooltip=[
                        alt.Tooltip("year:Q", title="Year", format="d"),
                        "city:N",
                        f"{per_100k_col}:Q",
                    ],
                )
                .properties(width="container", height=340)
            )

        # All Cities (aggregated)
        plot_df = df.groupby("year", as_index=False)[per_100k_col].mean()

        return (
            alt.Chart(plot_df)
            .mark_line()
            .encode(
                x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
                y=alt.Y(f"{per_100k_col}:Q", title=f"{crime_title} (per 100k)"),
                tooltip=[
                    alt.Tooltip("year:Q", title="Year", format="d"),
                    f"{per_100k_col}:Q",
                ],
            )
            .properties(width="container", height=340)
        )

    # --- Chart 2: LLM Filtered Map Plot ---

    @render_altair
    def chat_map_plot():

        # need to filter df on years still!
        # need to change to collect inputs!

        df = chat_filtered_data().copy()

        category = str(input.chat_crime_category())
        config = CRIME_CONFIG.get(category, CRIME_CONFIG["violent"])

        # State Level View
        state_id_to_show = 0
        state_view = not (state_id_to_show == 0)

        # Multi City Selection
        selected = list(df["city"].unique())
        multi = (len(selected) > 1) and (len(selected) != 57)

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
                        # legend=alt.Legend(title=None),
                        title=f"Avg {config['title']} per 100K",
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
                    # legend=alt.Legend(title=None),
                    title=f"Avg {config['title']} per 100K",
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


app = App(app_ui, server)
