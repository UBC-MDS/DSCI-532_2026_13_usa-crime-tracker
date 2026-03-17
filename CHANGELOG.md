# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-17

### Added
- Converted dataset to parquet format for improved performance and faster loading times.
- Data connects using ibis and duckdb for efficient querying and filtering of the parquet files.

### Changed
- Filter section redesigned to be more compact and user-friendly, with filters organized into collapsible sections to save space and improve navigation.
- Changed Violent Crime Range filter title to "Violent Crime Rate per 100k" to clarify that the filter is based on the crime rate rather than total crime count.

### Known Issues

### Release Highlight: [Name of your advanced feature]

<!-- One short paragraph describing what you built and what it does for the user. -->

- **Option chosen:** C - RAG system
- **PR:** Issue #144.
- **Why this option over the others:** 

Our initial thought was a click selection would benefit the user the most. However, we were unable to implement this due to our map implementation in altair. We decided a better alternative would be a RAG system. As our users are immigrants who know little about the US, and may not understand the different components of the dashboard, we considered that providing a resource with more information on the US would be the most beneficial resource.

- **Feature prioritization issue link:** #124

### Collaboration

<!-- Summary of workflow or collaboration improvements made since M3. -->

- **CONTRIBUTING.md:** <https://github.com/UBC-MDS/DSCI-532_2026_13_usa-crime-tracker/pull/162>

- **M3 retrospective:** 

After M3 collaboration feedback we implemented a more stingent PR review policy where each PR had to receive at least one review before merging.
The team did well with this and overall made a strong effort to ensure this commitment was met. Moving forward into M4 we made commitments to continue
this and further commited to better task assignment, clearer task assignment/descriptions, more descriptive PR comments, and last minute work rushes. 

- **M4:** 

We decided to create a reviewer role for M4. This person's job is to handle all project management aspects of the milestones - creation and distribution of tasks as issues, PR reviewing, and complete any written components. We tried splitting and assigning all tasks as issues at the beginning of the milestone to create a cleaner working environemnt.
The idea was to clearly distribute work, so everyone understood their tasks and roles for the milestone. Lastly, we implemented deadlines to avoid last minutes rushes.


### Reflection

<!-- Standard (see General Guidelines): what the dashboard does well, current limitations,
     any intentional deviations from DSCI 531 visualization best practices. -->

### Reflection
1–2 paragraphs (max 300 words) addressing:
- What the dashboard does well at this stage.
- Current limitations and planned improvements.
- Any intentional deviations from DSCI 531 visualization best practices.

<!-- Trade-offs: one sentence on feedback prioritization - full rationale is in #<issue> and ### Changed above. -->

<!-- Most useful: which lecture, material, or feedback shaped your work most this milestone,
     and anything you wish had been covered. -->


## [0.3.0] - 2026-03-08

### Added
- Fixed positioning of KPI outputs, navigation bar and filter header for a better user experience through css.
- Added adaptive position for the fixed KPI to adjust when filters are open or closed.
- Added a default value for date slider to show last 5 years of data applied across the dashboard.
- KPI comparison now shows % change vs previous years
- Color indicators added for KPI comparisons (red = increase in crime, green = decrease)
- Added reset filters button
- Added note explaining aggregation when multiple cities are selected
- Improved readability of KPI values with comma formatting
- LLM interactivity for filtering dashboard using querychat.
- Download data button to download LLM filtered Dataframes.

### Changed
- Updated the violet crime filter range to use the per 100k value instead of total 
- Updated the line plot to use the per 100k value instead of total
- Moved title to Navigation bar for better visibility and to free up space for the KPI outputs.
- Crime change table now updates based on selected crime category and improved to show the change as a percentage. 
- Table title now updates based on selected crime type and year range
- Dashboard title now reflects selected crime type and year range
  
### Known Issues
- Filter values don't update dynamically based on other filter selections. Will be addressed in the next release.
- KPI trend descriptions could be more intuitive and opinionated to quickly convey insights. Will be enhanced in the next release.
- Switching tabs back to dashboard from AI Assistant causes KPI boxes to stretch over entire screen. Cause is unkown currently, but will be looked into for next release.

### Reflection
- The KPI outputs are now fixed to the top right of the screen for better visibility and accessibility as users interact with the filters and scroll through the dashboard.
- We have a default date range applied to give an opinioned starting point for users to explore recent crime trends, while still allowing them to adjust the range as needed.
- Enhanced visual comprehension through colour and text components to better highlight key insights and trends in the data.
- AI Assistant component added to the dashboard to provide users with an interactive way to ask questions and get insights from the data in natural language, enhancing user engagement and accessibility of insights.

## [0.2.0] - 2026-02-28

### Added

- Add requirements.txt for publishing to posit
- Implemented reactive filtering using `@reactive.calc` for dashboard data.
- Added City/Department multi-select filter.
- Added Violent Crime Range slider filter.
- Added Population range slider
- Added KPI outputs based off the reactive filtered data frame
- Added Altair line chart for "Violent crime over time".
- Connected chart to reactive filtered dataset.
- Added Crime Category single-select filter.
- Added State single-select filter.
- Added map_plot.
- Added Population range slider.
- Added Date/Year slider input for temporal filtering.
- Added KPI outputs based off the reactive filtered data frame.
- Added 2 new user stories to filter on population and crime rate.
- Added links to published stable and preview dashboards to README.md
- Added m2_spec.md to reports

### Changed

- Updated background motivation in m1 proposal
- Update conda activation instuctions to include correct environment name.
- Changed shiny version to 1.4.0
- Updated environment.yml
- Updated dashboard layout from the M1 sketch to simplify the user workflow.
- Removed the filtered data frame place holder output on the shiny app skeleton.
- Removed the stacked area chart and Top-10 ranking chart; replaced with a single line comparison chart focused on temporal crime trends.
- Removed the full data table since it did not directly support current user stories.
- Reorganized layout so map and line chart serve as the primary analytical views.
- Changed placement of Change in Crime Rate table to align with line chart analysis view.
- Updated component structure to better align with implemented job stories and filtering workflow.

### Known Issues

- Removed the filtered data frame place holder output on the shiny app skeleton 
- The filters values are not reactive to each other. For example, if I select a city, the crime rate range filter does not update its upper and lower bounds to show only cities within that range.

### Reflection
- Job stories 1–7 are all implemented in the dashboard for this release.
- Reactive filtering supports filtering for all our input components: state, city, crime category, and crime range selections.
- Reduced visual complexity from M1 to improve clarity and focus on core analytical tasks.
