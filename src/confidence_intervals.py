import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("data/processed/match_features.csv")

matches = []
for match_id in data["match_id"].unique():
    match_file = Path("data/raw") / f"{match_id}_match.json"
    with open(match_file, "r", encoding="utf-8") as file:
        match_data = json.load(file)
    start_time = match_data["info"]["gameStartTimestamp"]
    matches.append((start_time, match_id))
matches.sort()
total = len(matches)

train_end = int(total * 0.70)
val_end = train_end + int(total * 0.15)
train_ids = [match_id for time, match_id in matches[:train_end]]
val_ids = [match_id for time, match_id in matches[train_end:val_end]]

print("Training matches:", len(train_ids))
print("Validation matches:", len(val_ids))
print("Final test matches:", len(matches[val_end:]))

features = [
    "gold_diff",
    "xp_diff",
    "cs_diff",
    "jungle_cs_diff",
    "kill_diff",
    "tower_diff",
    "dragon_diff",
    "grub_diff",
    "first_blood",
    "first_tower",
    "first_dragon"
]

training_wins = data[
    (data["minute"] == 5) &
    (data["match_id"].isin(train_ids))
]

blue_wins = training_wins["blue_win"].sum()
if blue_wins >= len(train_ids) / 2:
    majority_prediction = 1
else:
    majority_prediction = 0

results = {}

for minute in [5, 10, 15]:
    minute_data = data[data["minute"] == minute]
    train_data = minute_data[
        minute_data["match_id"].isin(train_ids)
    ]
    val_data = minute_data.set_index("match_id").loc[val_ids]
    X_train = train_data[features]
    y_train = train_data["blue_win"]
    X_val = val_data[features]
    y_val = val_data["blue_win"].to_numpy()

    gold_diff = val_data["gold_diff"].to_numpy()
    gold_predictions = np.where(
        gold_diff > 0,
        1,
        np.where(gold_diff < 0, 0, majority_prediction)
    )

    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    logistic_predictions = model.predict(X_val)
    results[minute] = {
        "actual": y_val,
        "gold": gold_predictions,
        "logistic": logistic_predictions
    }

assert np.array_equal(results[5]["actual"], results[10]["actual"])
assert np.array_equal(results[5]["actual"], results[15]["actual"])

rng = np.random.default_rng(42)
num_bootstraps = 5000
num_matches = len(val_ids)

samples = rng.integers(
    0,
    num_matches,
    size=(num_bootstraps, num_matches)
)

bootstrap_results = {}
for model_name in ["gold", "logistic"]:
    bootstrap_results[model_name] = {}

    print()
    print("=" * 45)
    print(model_name.upper(), "BASELINE" if model_name == "gold" else "REGRESSION")
    print("=" * 45)

    for minute in [5, 10, 15]:
        actual = results[minute]["actual"]
        predicted = results[minute][model_name]
        correct = predicted == actual
        accuracy = correct.mean() * 100
        bootstrap_accuracy = correct[samples].mean(axis=1) * 100
        bootstrap_results[model_name][minute] = bootstrap_accuracy
        lower = np.percentile(bootstrap_accuracy, 2.5)
        upper = np.percentile(bootstrap_accuracy, 97.5)

        print()
        print("Minute:", minute)
        print("Accuracy:", round(accuracy, 2), "%")
        print(
            "95% Confidence Interval:",
            round(lower, 2), "% to",
            round(upper, 2), "%"
        )

print()
print("=" * 45)
print("ACCURACY IMPROVEMENTS")
print("=" * 45)

for model_name in ["gold", "logistic"]:
    for earlier_minute in [5, 10]:
        differences = (
            bootstrap_results[model_name][15] -
            bootstrap_results[model_name][earlier_minute]
        )
        lower = np.percentile(differences, 2.5)
        upper = np.percentile(differences, 97.5)
        actual_earlier = (
            results[earlier_minute][model_name] ==
            results[earlier_minute]["actual"]
        ).mean() * 100

        actual_later = (
            results[15][model_name] ==
            results[15]["actual"]
        ).mean() * 100

        improvement = actual_later - actual_earlier

        print()
        print(model_name, "15 vs", earlier_minute, "minutes")
        print("Accuracy difference:", round(improvement, 2), "points")
        print(
            "95% Confidence Interval:",
            round(lower, 2), "to",
            round(upper, 2), "points"
        )