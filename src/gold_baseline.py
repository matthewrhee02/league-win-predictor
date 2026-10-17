import csv
import json
from pathlib import Path

with open("data/processed/match_features.csv", "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

features = {}
for row in rows:
    match_id = row["match_id"]
    minute = int(row["minute"])
    features[(match_id, minute)] = row

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

print("Training matches:", len(train_matches))
print("Validation matches:", len(val_matches))
print("Test matches:", len(test_matches))

blue_wins = 0

for start_time, match_id in train_matches:
    row = features[(match_id, 5)]
    if int(row["blue_win"]) == 1:
        blue_wins += 1

if blue_wins >= len(train_matches) / 2:
    majority_prediction = 1
else:
    majority_prediction = 0

for minute in [5, 10, 15]:
    gold_correct = 0
    majority_correct = 0
    for start_time, match_id in val_matches:
        row = features[(match_id, minute)]
        gold_diff = float(row["gold_diff"])
        actual_winner = int(row["blue_win"])
        if gold_diff > 0:
            gold_prediction = 1
        elif gold_diff < 0:
            gold_prediction = 0
        else:
            gold_prediction = majority_prediction
        if gold_prediction == actual_winner:
            gold_correct += 1
        if majority_prediction == actual_winner:
            majority_correct += 1
    gold_accuracy = gold_correct / len(val_matches) * 100
    majority_accuracy = majority_correct / len(val_matches) * 100

    print()
    print("Minute:", minute)
    print("Gold baseline accuracy:", round(gold_accuracy, 2), "%")
    print("Majority baseline accuracy:", round(majority_accuracy, 2), "%")