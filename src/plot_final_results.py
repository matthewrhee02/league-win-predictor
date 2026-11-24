import matplotlib.pyplot as plt

minutes = [5, 10, 15]

majority_accuracy = [51.11, 51.11, 51.11]
gold_accuracy = [62.22, 66.67, 77.78]
gold_logistic_accuracy = [60.00, 66.67, 80.00]
logistic_accuracy = [53.33, 64.44, 75.56]
random_forest_accuracy = [66.67, 60.00, 73.33]
xgboost_accuracy = [73.33, 60.00, 73.33]

plt.figure(figsize=(10, 6))

plt.plot(minutes, majority_accuracy, marker="o",
         label="Majority Baseline")

plt.plot(minutes, gold_accuracy, marker="o",
         label="Gold Baseline")

plt.plot(minutes, gold_logistic_accuracy, marker="o",
         label="Gold-only Logistic Regression")

plt.plot(minutes, logistic_accuracy, marker="o",
         label="Full Logistic Regression")

plt.plot(minutes, random_forest_accuracy, marker="o",
         label="Random Forest")

plt.plot(minutes, xgboost_accuracy, marker="o",
         label="XGBoost")

plt.title("Final Test Accuracy by Game Time")
plt.xlabel("Game Time (Minutes)")
plt.ylabel("Accuracy (%)")

plt.xticks(minutes)
plt.ylim(40, 100)

plt.grid(True)
plt.legend()

plt.tight_layout()

plt.savefig("figures/final_test_accuracy.png", dpi=300)

plt.show()