import json
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("data/processed/match_features.csv")

with open("splits/match_split.json", "r") as file:
    splits = json.load(file)

train_ids = splits["train"]
val_ids = splits["validation"]
test_ids = splits["test"]

print("Training matches:", len(train_ids))
print("Validation matches:", len(val_ids))
print("Test matches:", len(test_ids))

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

training_data = data[
    (data["minute"] == 5) &
    (data["match_id"].isin(train_ids))
]

blue_wins = training_data["blue_win"].sum()

if blue_wins >= len(training_data) / 2:
    majority_prediction = 1
else:
    majority_prediction = 0

rng = np.random.default_rng(42)

samples = rng.integers(
    0,
    len(val_ids),
    size=(5000, len(val_ids))
)

for minute in [5, 10, 15]:

    print()
    print("=" * 40)
    print("MINUTE:", minute)
    print("=" * 40)

    minute_data = data[data["minute"] == minute]

    train_data = minute_data[
        minute_data["match_id"].isin(train_ids)
    ]

    val_data = minute_data.set_index("match_id").loc[val_ids]

    X_train = train_data[features]
    y_train = train_data["blue_win"]

    X_val = val_data[features]
    y_val = val_data["blue_win"].to_numpy()

    gold_predictions = []

    for gold in val_data["gold_diff"]:

        if gold > 0:
            gold_predictions.append(1)
        elif gold < 0:
            gold_predictions.append(0)
        else:
            gold_predictions.append(majority_prediction)

    gold_predictions = np.array(gold_predictions)

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    logistic_model = LogisticRegression(max_iter=1000)
    logistic_model.fit(X_train_scaled, y_train)

    logistic_predictions = logistic_model.predict(X_val_scaled)

    forest_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_leaf=3,
        random_state=42
    )

    forest_model.fit(X_train, y_train)

    forest_predictions = forest_model.predict(X_val)

    predictions = {
        "Gold": gold_predictions,
        "Logistic": logistic_predictions,
        "Random Forest": forest_predictions
    }

    correct_results = {}

    for name in predictions:

        correct = predictions[name] == y_val
        correct_results[name] = correct

        accuracy = correct.mean() * 100

        print(name, "accuracy:", round(accuracy, 2), "%")

    comparisons = [
        ("Logistic", "Gold"),
        ("Random Forest", "Gold"),
        ("Random Forest", "Logistic")
    ]

    print()
    print("MODEL COMPARISONS")

    for model1, model2 in comparisons:

        correct1 = correct_results[model1]
        correct2 = correct_results[model2]

        accuracy1 = correct1.mean() * 100
        accuracy2 = correct2.mean() * 100

        difference = accuracy1 - accuracy2

        bootstrap1 = correct1[samples].mean(axis=1) * 100
        bootstrap2 = correct2[samples].mean(axis=1) * 100

        differences = bootstrap1 - bootstrap2

        lower = np.percentile(differences, 2.5)
        upper = np.percentile(differences, 97.5)

        print()
        print(model1, "vs", model2)
        print("Accuracy difference:", round(difference, 2), "points")
        print("95% CI:", round(lower, 2), "to", round(upper, 2))