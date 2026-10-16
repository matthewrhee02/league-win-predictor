import matplotlib.pyplot as plt
from pathlib import Path

minutes = [5, 10, 15]
majority_accuracy = [47.06, 47.06, 47.06]
gold_accuracy = [52.94, 58.82, 82.35]
logistic_accuracy = [58.82, 58.82, 70.59]

plt.figure(figsize=(9, 6))
plt.plot(minutes, majority_accuracy, marker='o',
         label="Majority Baseline")
plt.plot(minutes, gold_accuracy, marker="o",
         label="Gold Baseline")
plt.plot(minutes, logistic_accuracy, marker="o",
         label="Logistic Regression")
plt.title("League of Legends Win Prediction Accuracy")
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