# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Default 5-year comparison added to KPI cards (Total Crimes, Crime Rate, Population)
- KPI comparison now shows % change vs previous years
- Color indicators added for KPI comparisons (red = increase in crime, green = decrease)
- Added reset filters button
- Added note explaining aggregation when multiple cities are selected
- Improved readability of KPI values with comma formatting

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
- Crime change table now updates based on selected crime category and improved to show the change as a percentage. 
- Table title now updates based on selected crime type and year range
- Dashboard title now reflects selected crime type and year range


### Known Issues

- Removed the filtered data frame place holder output on the shiny app skeleton 
- The filters values are not reactive to each other. For example, if I select a city, the crime rate range filter does not update its upper and lower bounds to show only cities within that range.

### Reflection
- Job stories 1–7 are all implemented in the dashboard for this release.
- Reactive filtering supports filtering for all our input components: state, city, crime category, and crime range selections.
- Reduced visual complexity from M1 to improve clarity and focus on core analytical tasks.
