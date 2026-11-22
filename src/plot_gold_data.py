import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

data = pd.read_csv("data/processed/match_features.csv")

minutes = [5, 10, 15]

gold_data = []
labels = []

for minute in minutes:

    minute_data = data[data["minute"] == minute]

    blue_wins = minute_data[minute_data["blue_win"] == 1]
    red_wins = minute_data[minute_data["blue_win"] == 0]

    blue_gold = blue_wins["gold_diff"]
    red_gold = red_wins["gold_diff"]

    gold_data.append(blue_gold)
    gold_data.append(red_gold)

    labels.append(str(minute) + " Blue Win")
    labels.append(str(minute) + " Red Win")

    print()
    print("Minute:", minute)
    print("Blue win median gold difference:", blue_gold.median())
    print("Red win median gold difference:", red_gold.median())

plt.figure(figsize=(12, 6))

plt.boxplot(gold_data)

plt.xticks(range(1, 7), labels, rotation=20)

plt.axhline(y=0, linestyle="--", color="gray")

plt.title("Gold Difference by Match Winner")
plt.xlabel("Game Time and Winning Team")
plt.ylabel("Gold Difference (Blue - Red)")

plt.grid(axis="y")

folder = Path("figures")
folder.mkdir(parents=True, exist_ok=True)

plt.savefig("figures/gold_distribution.png",
            dpi=300, bbox_inches="tight")

plt.show()

print()
print("Saved graph to figures/gold_distribution.png")