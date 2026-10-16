import json
from pathlib import Path
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, brier_score_loss

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
train_matches = matches[:train_end]
val_matches = matches[train_end:val_end]
test_matches = matches[val_end:]
train_ids = [match_id for start_time, match_id in train_matches]
val_ids = [match_id for start_time, match_id in val_matches]

print("Training matches:", len(train_ids))
print("Validation matches:", len(val_ids))
print("Test matches:", len(test_matches))

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

for minute in [5, 10, 15]:
    print()
    print("=" * 40)
    print("MINUTE:", minute)
    print("=" * 40)

    minute_data = data[data["minute"] == minute]
    train_data = minute_data[minute_data["match_id"].isin(train_ids)]
    val_data = minute_data[minute_data["match_id"].isin(val_ids)]

    X_train = train_data[features]
    y_train = train_data["blue_win"]
    X_val = val_data[features]
    y_val = val_data["blue_win"]

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    predictions = model.predict(X_val)
    probabilities = model.predict_proba(X_val)[:, 1]
    accuracy = accuracy_score(y_val, predictions)
    loss = log_loss(y_val, probabilities, labels=[0, 1])
    brier = brier_score_loss(y_val, probabilities)

    print("Validation games:", len(val_data))
    print("Accuracy:", round(accuracy * 100, 2), "%")
    print("Log Loss:", round(loss, 4))
    print("Brier Score:", round(brier, 4))

    if len(y_val.unique()) == 2:
        auc = roc_auc_score(y_val, probabilities)
        print("ROC-AUC:", round(auc, 4))
    else:
        print("ROC-AUC: Not available")