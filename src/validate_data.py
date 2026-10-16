import pandas as pd

data = pd.read_csv("data/processed/match_features.csv")

print("DATASET VALIDATION")
print("-------------------------")

print("Total rows:", len(data))
print("Unique matches:", data["match_id"].nunique())
print()
print("Rows by minute:")
print(data["minute"].value_counts().sort_index())
print()
print("Missing values:", data.isnull().sum().sum())

duplicates = data.duplicated(
    subset=["match_id", "minute"]
).sum()

print("Duplicate observations:", duplicates)

invalid_matches = 0
for match_id, group in data.groupby("match_id"):
    minutes = sorted(group["minute"].tolist())
    if minutes != [5, 10, 15]:
        invalid_matches += 1
print("Matches missing snapshots:", invalid_matches)

data["time_difference"] = abs(
    data["timestamp"] - data["minute"] * 60000
)

print()
print("Largest timestamp difference:",
      data["time_difference"].max(), "milliseconds")
print()
print("Winners by team:")

five_minute_data = data[data["minute"] == 5]

print("Blue wins:",
      (five_minute_data["blue_win"] == 1).sum())
print("Red wins:",
      (five_minute_data["blue_win"] == 0).sum())
print()
print("Validation finished.")