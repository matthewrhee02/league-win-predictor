import csv
import json

with open("data/processed/match_features.csv", "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

features = {}
for row in rows:
    match_id = row["match_id"]
    minute = int(row["minute"])
    features[(match_id, minute)] = row

with open("splits/match_split.json", "r") as file:
    splits = json.load(file)

train_ids = splits["train"]
val_ids = splits["validation"]
test_ids = splits["test"]

print("Training matches:", len(train_ids))
print("Validation matches:", len(val_ids))
print("Test matches:", len(test_ids))

blue_wins = 0

for match_id in train_ids:
    row = features[(match_id, 5)]
    if int(row["blue_win"]) == 1:
        blue_wins += 1

if blue_wins >= len(train_ids) / 2:
    majority_prediction = 1
else:
    majority_prediction = 0

for minute in [5, 10, 15]:
    gold_correct = 0
    majority_correct = 0
    for match_id in val_ids:
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
    gold_accuracy = gold_correct / len(val_ids) * 100
    majority_accuracy = majority_correct / len(val_ids) * 100

    print()
    print("Minute:", minute)
    print("Gold baseline accuracy:", round(gold_accuracy, 2), "%")
    print("Majority baseline accuracy:", round(majority_accuracy, 2), "%")