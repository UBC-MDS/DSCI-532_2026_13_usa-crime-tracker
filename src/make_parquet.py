import pandas as pd

# Load and clean raw crime data
df_raw = pd.read_csv("data/raw/crime_rate_data_raw.csv").drop(columns=["source", "url"])
df_raw = df_raw.rename(columns={"department_name": "city", "ORI": "state_id"})
df_raw["city"] = df_raw["city"].str.partition(",")[0]
df_raw["state_id"] = df_raw["state_id"].str[:2]

# Load and clean city coordinates data
cities = pd.read_csv("data/raw/uscities_raw.csv")
cities = cities[cities["state_name"] != "Puerto Rico"]
cities = cities[["city", "state_id", "lat", "lng"]]

# Merge datasets
df_merged = pd.merge(df_raw, cities, how="inner", on=["city", "state_id"])

# Save as parquet
df_merged.to_parquet("data/processed/crime_merged.parquet", index=False)

print("Saved parquet file to data/processed/crime_merged.parquet")