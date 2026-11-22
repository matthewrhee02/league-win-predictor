import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

data = pd.read_csv("data/processed/match_features.csv")

with open("splits/match_split.json", "r") as file:
    splits = json.load(file)

train_ids = splits["train"]
val_ids = splits["validation"]

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

folder = Path("figures")
folder.mkdir(parents=True, exist_ok=True)

for minute in [5, 10, 15]:

    print()
    print("=" * 40)
    print("MINUTE:", minute)
    print("=" * 40)

    minute_data = data[data["minute"] == minute]

    train_data = minute_data[
        minute_data["match_id"].isin(train_ids)
    ]

    val_data = minute_data[
        minute_data["match_id"].isin(val_ids)
    ]

    X_train = train_data[features]
    y_train = train_data["blue_win"]

    X_val = val_data[features]
    y_val = val_data["blue_win"]

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_leaf=3,
        random_state=42
    )

    model.fit(X_train, y_train)

    results = permutation_importance(
        model,
        X_val,
        y_val,
        scoring="roc_auc",
        n_repeats=20,
        random_state=42
    )

    importance_data = pd.DataFrame()

    importance_data["feature"] = features
    importance_data["importance"] = results.importances_mean

    importance_data = importance_data.sort_values(
        by="importance",
        ascending=False
    )

    print()
    print("Feature Importance:")

    for index, row in importance_data.iterrows():
        print(row["feature"], ":", round(row["importance"], 4))

    # Create a graph
    plt.figure(figsize=(10, 6))

    plt.barh(
        importance_data["feature"],
        importance_data["importance"]
    )

    plt.gca().invert_yaxis()

    plt.axvline(x=0, color="gray", linestyle="--")

    plt.title("Feature Importance at " + str(minute) + " Minutes")
    plt.xlabel("Decrease in ROC-AUC When Shuffled")
    plt.ylabel("Feature")

    plt.tight_layout()

    filename = "figures/feature_importance_" + str(minute) + ".png"

    plt.savefig(filename, dpi=300, bbox_inches="tight")

    plt.show()

    print("Saved graph to:", filename)