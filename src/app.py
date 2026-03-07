from shiny import App, ui, reactive, render
import anthropic
import os

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

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MAX_TOKENS = 300   # token limit

app_ui = ui.page_navbar(

    # PAGE 1: Dashboard
    ui.nav_panel(
        "Dashboard",
        ui.page_sidebar(
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

            ui.tags.style("""
                .bslib-sidebar-layout > .collapse-toggle {
                    top: 56px !important;
                }
                
                .fixed-main-header {
                    position: fixed;
                    z-index: 1020;
                    background: white;
                    border-bottom: 1px solid #ddd;
                    padding-top: 0.4rem;
                    padding-bottom: 0.2rem;
                    box-sizing: border-box;
                }

                .fixed-main-header h1 {
                    margin-top: 0;
                    margin-bottom: 0.2rem;
                }
            """),

            ui.tags.script("""
                function syncFixedMainHeader() {
                    const header = document.querySelector('.fixed-main-header');
                    const main = document.querySelector('.bslib-page-main');
                    const navbar = document.querySelector('.navbar');

                    if (!header || !main) return;

                    const rect = main.getBoundingClientRect();
                    const navHeight = navbar ? navbar.offsetHeight : 56;

                    header.style.left = rect.left + 'px';
                    header.style.width = rect.width + 'px';
                    header.style.top = navHeight + 'px';
                    main.style.paddingTop = (header.offsetHeight + 4) + 'px';
                }

                window.addEventListener('load', syncFixedMainHeader);
                window.addEventListener('resize', syncFixedMainHeader);
                document.addEventListener('click', () => setTimeout(syncFixedMainHeader, 50));

                const observer = new MutationObserver(() => {
                    setTimeout(syncFixedMainHeader, 50);
                });

                window.addEventListener('load', () => {
                    observer.observe(document.body, {
                        attributes: true,
                        childList: true,
                        subtree: true
                    });
                });
            """),

            ui.div(
                {"class": "fixed-main-header"},
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

    ),

    # PAGE 2: AI Assistant
    ui.nav_panel(
        "AI Assistant",
        ui.layout_columns(
            ui.card(
                ui.h3("AI Assistant"),

                ui.input_text_area(
                    "ai_user_input",
                    "Ask the AI about the dataset:",
                    placeholder="e.g., summarize crime trends in Texas",
                    rows=4
                ),

                ui.input_action_button("ai_send_btn", "Send"),

                ui.hr(),

                ui.h4("AI Response"),
                ui.output_text_verbatim("ai_chat_output"),

                ui.hr(),

                ui.h4("Filtered DataFrame"),
                ui.output_data_frame("ai_dataframe_output")

            )
        )
    ),
    position="fixed-top",
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


    @reactive.Effect
    @reactive.event(input.ai_send_btn)
    def _():
        user_input = input.ai_user_input()
    
        if not user_input:
            output.ai_chat_output.set("Please enter a question.")
            return
    
        output.ai_chat_output.set("Thinking...")
    
        async def call_ai():
            try:
                response = await asyncio.to_thread(
                    client.messages.create,
                    model="claude-haiku-4-5-20251001",
                    max_tokens=MAX_TOKENS,
                    messages=[{"role": "user", "content": user_input}]
                )
                return response.content[0].text
            except Exception as e:
                return f"Error calling Anthropic API: {e}"
    
        task = reactive.Task(call_ai())
    
        @task.on_done
        def _(result):
            output.ai_chat_output.set(result)


    # Filtered df
    @output
    @render.data_frame
    def ai_dataframe_output():
        return filtered_df()




app = App(app_ui, server)
