# Updated Job Stories

| #   | Job Story                                                                                                                                          | Status         | Notes                  |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |----------------------- |
| 1   | When I open the dashboard I want to see crime rates per city on a map so I can incorporate geographical context in deciding where to live.         | ✅ Implemented | Currently set up to show avg crime rate over selected time period. |
| 2   | When I look at the dashboard I want to select cities so I can see locations, information, and isolate crime trends for those cities.               | ✅ Implemented | ...                    |
| 3   | When I look at the dashboard I want to select a certain state so I see locations, information, and isolate crime trends for cities in those states.| ✅ Implemented | ...                    |
| 4   | When I select cities I want to see compare crime rate types so I can fully understand the type of crime that happens in each city.                 | ✅ Implemented | ...                    |
| 5   | When I select cities I want to see crime trends over time within a time range so I can understand if crime is increasing or decreasing.            | ✅ Implemented | ...                    |
| 6   | When I look at the dashboard I want to filter for cities within a population range so I can isolate cities under or over a population size.        | ✅ Implemented | added for M2           |
| 7   | When I look at the dashboard I want to filter for cities within a crime rate range so I can isolate cities under specific crime levels.            | ✅ Implemented | added for M2           |

# Component Iventory
| ID                               | Type          | Shiny widget / renderer                        | Depends on                                  | Job story                |
|----------------------------------|---------------|------------------------------------------------|---------------------------------------------|--------------------------|
| Date/Year                        | Input         | ui.input_slider()                              | —                                           | #5                       |
| State                            | Input         | ui.input_select()                              | —                                           | #3                       |
| City                             | Input         | ui.input_selectize()                           | —                                           | #2                       |
| Population                       | Input         | ui.input_slider()                              | —                                           | #6                       |
| Category                         | Input         | ui.input_select()                              | —                                           | #4                       |
| Category (chat version)          | Input         | ui.input_select()                              | —                                           | #4                       |
| Aggregate Crime Column           | Input         | ui.input_slider()                              | —                                           | #7                       |
| Querychat LLM   (chat)           | Input         | qc.ui()                                        | —                                           | #7                       |
|  download_button (chat)          | Input         | ui.download_button()                           | —                                           | #7                       |
| filtered_df                      | Reactive calc | @reactive.calc (DuckDB/Parquet query)                                | input_year, input_region                    | #1, #2, #3, #5, #6, #7   |
| most_common_crime                | Reactive calc | @reactive.calc                                 | filtered_df                                 | #2, #3, #4               |
| crime_range_table                | Reactive calc | @reactive.calc                                 | filtered_df                                 | #2, #3, #4, #5, #6, #7   |
| chat_filtered_data (chat)        | Reactive calc | @reactive.calc                                 | querychat: qc.server(), chat_table          | #2, #3, #4, #5, #6, #7   |
| KPI (Total Crime)                | Output        | @reactive.text; ui.value_box("name"            | ui.output_text(""name_from_server_func""))m, input_year, input_region | #2, #3, #4, #5, #6, #7  |
| KPI (Crime Rate)                 | Output        | @reactive.text; ui.value_box("name"            | ui.output_text(""name_from_server_func"")), filtered_df | #2, #3, #5   |
| KPI (population)                 | Output        | @reactive.text; ui.value_box("name"            | ui.output_text(""name_from_server_func"")), filtered_df | #2, #3, #6   |
| KPI (Most Common Crime)          | Output        | @reactive.text; ui.value_box("name"            | ui.output_text(""name_from_server_func""))  | #2, #3, #4               |
| KPI (Change in Crime Rate) Table | Output        | @render.data_frame                             |                                             | #2, #3, #5               |
| map_plot  (dashboard)            | Output        | @render.altair; ui.ouput_widget("map_plot")    | merged_df                                   | #1, #2, #3, #4, #6, #7   |
| line_plot (dashboad)             | Output        | @render.altair; ui.ouput_widget("line_plot")   | filtered_df                                 | #2, #3, #4, #5, #6, #7   | 
| chat_map_plot  (chat)            | Output        | @render.altair; ui.ouput_widget("chat_map_plot")  | chat_filtered_data()                     | #1, #2, #3, #4, #6, #7   |
| chat_line_plot (Chat)            | Output        | @render.altair; ui.ouput_widget("chat_line_plot") | chat_filtered_data()                     | #2, #3, #4, #5, #6, #7   |
| chat_table (chat)                | Output        | @render.data_frame; ui.output_data_frame("chat_table")   |   querychat: qc.server()          | #1, #2, #3, #4, #6, #7   |
| chat_map_title (chat)            | Output        | @render.text; ui.output_text("chat_map_title") |   chat_filtered_data()                      | #1, #2, #3, #4, #6, #7   |
| chat_title (chat)                | Output        | @render.text; ui.output_text("chat_title")     |   querychat: qc.server()                    | #1, #2, #3, #4, #6, #7   |
| download_data (chat)             | Output        | @render.download(filename="filtered_data.csv") |   download_button.                          | #1, #2, #3, #4, #6, #7   |



# Reactivity Diagram

```mermaid
flowchart TD
  A[/input_city_dept/] --> F{{filtered_df (DuckDB/Parquet query)}}
  B[/input_population/] --> F
  S[/input_state/] --> F
  C[/input_year/] --> F
  Crime[/input_crime_cat/] --> F
  V[/input_violent_crime/] --> F
  F --> P1([plot_viol_crime_over_time])
 S --> P2([map_plot])
 A --> P2
 Crime --> P2
 B --> P2
 C --> P2

  F --> V1([out_total_crime])
  F --> V2([out_crime_rate])
  F --> V3([out_population])
  F --> V4([out_most_common_crime])
  F --> V5([out_change_rate])
  ```


# Calculation Details
For the `filtered_df` reactive calculation, the application queries the processed dataset stored in Parquet format using DuckDB through the Ibis interface. User inputs such as year, state, city, population range, crime category, and violent crime range are translated into query filters that are executed directly on the Parquet dataset. This ensures that filtering occurs before the data is loaded into memory, improving performance and reducing unnecessary data transfer. The resulting filtered dataset is then used by downstream visualizations and KPI calculations.

For the `most_common_crime` reactive calculation, we will analyze the `filtered_df` dataset to determine which crime category has the highest count for the selected year range. This will allow us to output the most common crime as a KPI.

For the `crime_range_table` reactive calculation, we will analyze the `filtered_df` dataset to calculate the change in crime rates over time for each crime category. This will allow us to output a table that shows how crime rates have changed for each category, which can help users understand trends and patterns in crime over time. Updated the crime table to to calculate the yearly crime rate for the selected crime category over the selected year range. We then compute the year-over-year percentage change in crime rate and display it in a table. This helps users understand how the selected crime category changes over time.

For the `chat_filtered_data` reactive calculation we will analyze the querychat responses to input prompts, to take the filtered data frame, and turn it into a format useful for outputs. This will allow outputs to be filtered using the querychat interface to help users efficiently search and understand trends within the data. Updated the crime table to to calculate the yearly crime rate for the selected crime category over the selected year range. We then compute the year-over-year percentage change in crime rate and display it in a table. This helps users understand how the selected crime category changes over time.

# Future Implementation
In a future version of the dashboard, we plan to add a comparison feature that identifies the cities with the highest and lowest crime rates based on the currently selected crime category and filters. This would allow users to quickly compare the best- and worst-performing cities for violent crime, homicide, robbery, rape, or aggravated assault. The feature would use the filtered dataset and calculate the crime rate per 100,000 people for each city in the most recent year of the selected range, then display the cities with the maximum and minimum values. This would provide users with a clearer comparison across locations and make the KPI section more informative.

We also plan to enhance the comprehension of our KPI titles and outputs using our filters to allow for more opinionated insights. We currently are showing trends in the data like the change in crime from the latest year compared to previous years, but we will enhance the terminology used to allow users to quickly understand the insight. 

Our current filter option are static based on inital inputs, we plan to dynamically update the filters based on the user's current selections. This will stem from the state and city as the base filters, which will then update the filter options and ranges for all other filters. For example, if a user selects a specific city, the crime rate range filter will dynamically update its upper and lower bounds to show only the crime rates for that city. This will create a more seamless and intuitive user experience as users explore the data.