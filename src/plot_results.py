import matplotlib.pyplot as plt
from pathlib import Path

minutes = [5, 10, 15]
majority_accuracy = [40.00, 40.00, 40.00]
gold_accuracy = [60.00, 66.67, 75.56]
logistic_accuracy = [62.22, 62.22, 73.33]

plt.figure(figsize=(9, 6))
plt.plot(minutes, majority_accuracy, marker='o',
         label="Majority Baseline")
plt.plot(minutes, gold_accuracy, marker="o",
         label="Gold Baseline")
plt.plot(minutes, logistic_accuracy, marker="o",
         label="Logistic Regression")
plt.title("League of Legends Win Prediction Accuracy (300 Matches)")
plt.xlabel("Game Time (Minutes)")
plt.ylabel("Validation Accuracy (%)")
plt.xticks(minutes)
plt.ylim(0, 100)
plt.grid(True)
plt.legend()

folder = Path("figures")
folder.mkdir(parents=True, exist_ok=True)
plt.savefig("figures/accuracy_comparison.png",
            dpi=300, bbox_inches="tight")
plt.show()
print("Saved graph to figures/accuracy_comparison.png")