import csv
import json
from pathlib import Path

with open("data/processed/match_features.csv", "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

match_ids = set()
for row in rows:
    match_ids.add(row["match_id"])

matches = []
for match_id in match_ids:
    match_file = Path("data/raw") / f"{match_id}_match.json"
    with open(match_file, "r") as file:
        match_data = json.load(file)
    start_time = match_data["info"]["gameStartTimestamp"]
    matches.append((start_time, match_id))
matches.sort()
total = len(matches)

train_end = int(total * 0.70)
val_end = train_end + int(total * 0.15)
train_matches = matches[:train_end]
val_matches = matches[train_end:val_end]
test_matches = matches[val_end:]

train_ids = [match_id for time, match_id in train_matches]
val_ids = [match_id for time, match_id in val_matches]
test_ids = [match_id for time, match_id in test_matches]

splits = {
    "train": train_ids,
    "validation": val_ids,
    "test": test_ids
}

folder = Path("splits")
folder.mkdir(parents=True, exist_ok=True)
output_file = folder / "match_split.json"
if output_file.exists():
    print("Match split already exists. Nothing changed.")
    quit()
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(splits, file, indent=2)

print("Match split saved successfully.")
print("Training matches:", len(train_ids))
print("Validation matches:", len(val_ids))
print("Final test matches:", len(test_ids))
print("Saved to:", output_file)