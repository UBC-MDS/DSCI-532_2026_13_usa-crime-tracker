# DSCI-532_2025_13_usa_crime-tracker
DSCI 532 Dashboard Projects

# Project Summary 

Moving to a new country presents many challenges. One key factor that new immigrants must consider is safety. The USA Crime Tracker Dashboard is an interactive Shiny application that enables users to explore historical crime trends across the United States of America. Through coordinated visualizations and summary metrics, the app helps users identify geographic patterns, temporal trends, and relative crime risk to empower immigrants in making informed decisions about their safety when moving to the USA.

Link to Published Stable Dashboard: <https://019ca5bd-b008-a68f-3889-89a1f04e0011.share.connect.posit.cloud/>

Link to Published Preview Dashboard: <https://019cceb6-3ded-e7e0-6b99-b2912a2ee701.share.connect.posit.cloud/>

# Users

Moving to a new country comes with many important decisions, and safety is often one of the top concerns for immigrants. The USA Crime Tracker Dashboard is an interactive Shiny application that allows users to explore historical crime trends across reporting cities in the United States. Through dynamic visualizations and key summary metrics, the dashboard highlights geographic patterns, changes over time, and relative crime rates. By presenting the data in an accessible and interactive format, the app helps prospective immigrants make more informed decisions about their safety when relocating to the U.S.

## DEMO

Below is a gif demo on how to use the dashboard: 
![Demo of the app](img/demo.gif)

# AI Assistant

The dashboard includes an AI-powered assistant that allows users to ask questions about the crime dataset using natural language.

The assistant uses the Anthropic Claude API to generate responses to user prompts. Users can ask questions such as:
- "Filter to Los Angeles only"
- "Which cities have the highest crime rates?"
- "How has crime changed over the last five years?"

The AI assistant processes the query and returns a text response, while also displaying the filtered dataset used by the dashboard.

### Environment Variable Requirement

To use the AI assistant, a Github Models API key must be provided as an environment variable:

```bash
GITHUB_TOKEN = ...
```

The application accesses this key in the code using:
```python
load_dotenv(Path(__file__).parent.parent / ".env")
```

When deploying the application (e.g., on Posit Connect Cloud), this variable must be added to the deployment's **Environment Variables** so the AI assistant can communicate with the Anthropic API.

# Running the App Locally 

## 1. Close the Repository 

```bash
git clone https://github.com/UBC-MDS/DSCI-532_2026_13_usa-crime-tracker.git
cd DSCI-532_2026_13_usa-crime-tracker
```

## 2. Create the Conda Environment 

```bash
conda env create -f environment.yml
conda activate usa-crime-tracker
```

## 3. Run the Shiny App 

```bash
shiny run src/app.py
```

Open your web browser and navigate to the url below:

<http://127.0.0.1:8000>


## 4.Stop the App
In the terminal, enter: 
```bash
Ctrl + C
```

## 5. Running Playwright Tests

Install dependencies:

    pip install -r requirements.txt

Run all tests (Playwright):

    python -m pytest tests/test_playwright.py -v --browser firefox

This command works in a clean environment.

test_year_slider_changes_kpi(page: Page, app: ShinyAppProc):
Verify that adjusting the year-range slider updates the total crimes KPI.

test_total_crimes_correct(page: Page, app: ShinyAppProc):
Ensure the app's displayed total crimes value matches the computed latest-year total from the dataset.

test_state_filter_total_crimes_correct(page: Page, app: ShinyAppProc):
Confirm that selecting a state actually filters the data.

## 6. Running Unit Tests

Install dependencies:

    pip install -r requirements.txt

Run all tests (pytest + Playwright):

    pytest

This command works in a clean environment.

test_filter_by_city():
Filtering by city should return all rows for that city in the dataset.

test_filter_by_year():
Filtering by year should return all rows for that year in the dataset.

test_empty_filter_returns_all():
No filters applied should return the same rows the app would show with default settings.

test_nonexistent_city_returns_empty():
Filtering for a city not in the dataset should return zero rows.

test_aggregation_correctness():
Ensures violent_crime equals the sum of its components, preventing incorrect totals in the dataset.

test_year_boundary_condition():
Checks that filtering at the dataset's min/max year returns the correct rows, matching slider boundaries.

# Contributors
 If you are looking to contribute ot the project please refer to the guidelines in this document: 
 [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
