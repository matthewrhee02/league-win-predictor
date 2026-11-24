import json
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, brier_score_loss
from xgboost import XGBClassifier

data = pd.read_csv("data/processed/match_features.csv")

with open("splits/match_split.json", "r") as file:
    splits = json.load(file)

train_ids = splits["train"] + splits["validation"]
test_ids = splits["test"]

print("Final training matches:", len(train_ids))
print("Final test matches:", len(test_ids))

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


def show_results(name, actual, predictions, probabilities):

    print()
    print(name)

    accuracy = accuracy_score(actual, predictions)
    loss = log_loss(actual, probabilities, labels=[0, 1])
    brier = brier_score_loss(actual, probabilities)

    print("Accuracy:", round(accuracy * 100, 2), "%")
    print("Log Loss:", round(loss, 4))
    print("Brier Score:", round(brier, 4))

    if len(np.unique(actual)) == 2:
        auc = roc_auc_score(actual, probabilities)
        print("ROC-AUC:", round(auc, 4))


for minute in [5, 10, 15]:

    print()
    print("=" * 40)
    print("MINUTE:", minute)
    print("=" * 40)

    minute_data = data[data["minute"] == minute]

    train_data = minute_data[
        minute_data["match_id"].isin(train_ids)
    ]

    test_data = minute_data[
        minute_data["match_id"].isin(test_ids)
    ]

    X_train = train_data[features]
    y_train = train_data["blue_win"]

    X_test = test_data[features]
    y_test = test_data["blue_win"]

    print("Training games:", len(train_data))
    print("Test games:", len(test_data))

    # Majority baseline
    if y_train.mean() >= 0.5:
        majority_prediction = 1
    else:
        majority_prediction = 0

    majority_predictions = np.full(
        len(y_test), majority_prediction
    )

    print()
    print("Majority Baseline")
    print(
        "Accuracy:",
        round(accuracy_score(y_test, majority_predictions) * 100, 2),
        "%"
    )

    # Gold baseline
    gold_predictions = []

    for gold in test_data["gold_diff"]:

        if gold > 0:
            gold_predictions.append(1)
        elif gold < 0:
            gold_predictions.append(0)
        else:
            gold_predictions.append(majority_prediction)

    print()
    print("Gold Baseline")
    print(
        "Accuracy:",
        round(accuracy_score(y_test, gold_predictions) * 100, 2),
        "%"
    )

    # Gold-only Logistic Regression
    gold_features = ["gold_diff"]

    gold_scaler = StandardScaler()

    X_train_gold = gold_scaler.fit_transform(
        train_data[gold_features]
    )

    X_test_gold = gold_scaler.transform(
        test_data[gold_features]
    )

    gold_model = LogisticRegression(max_iter=1000)

    gold_model.fit(X_train_gold, y_train)

    predictions = gold_model.predict(X_test_gold)
    probabilities = gold_model.predict_proba(X_test_gold)[:, 1]

    show_results(
        "Gold-only Logistic Regression",
        y_test,
        predictions,
        probabilities
    )

    # Full Logistic Regression
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logistic_model = LogisticRegression(max_iter=1000)

    logistic_model.fit(X_train_scaled, y_train)

    predictions = logistic_model.predict(X_test_scaled)
    probabilities = logistic_model.predict_proba(X_test_scaled)[:, 1]

    show_results(
        "Full Logistic Regression",
        y_test,
        predictions,
        probabilities
    )

    # Random Forest
    forest_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_leaf=3,
        random_state=42
    )

    forest_model.fit(X_train, y_train)

    predictions = forest_model.predict(X_test)
    probabilities = forest_model.predict_proba(X_test)[:, 1]

    show_results(
        "Random Forest",
        y_test,
        predictions,
        probabilities
    )

    # XGBoost
    xgboost_model = XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42
    )

    xgboost_model.fit(X_train, y_train)

    predictions = xgboost_model.predict(X_test)
    probabilities = xgboost_model.predict_proba(X_test)[:, 1]

    show_results(
        "XGBoost",
        y_test,
        predictions,
        probabilities
    )