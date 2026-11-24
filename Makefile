PYTHON = python

.PHONY: all validate models plots final

all: validate models plots

validate:
	$(PYTHON) src/validate_data.py

models:
	$(PYTHON) src/gold_baseline.py
	$(PYTHON) src/gold_only_model.py
	$(PYTHON) src/logistic_model.py
	$(PYTHON) src/random_forest.py
	$(PYTHON) src/xgboost_model.py

plots:
	$(PYTHON) src/plot_results.py
	$(PYTHON) src/plot_gold_data.py
	$(PYTHON) src/feature_importance.py
	$(PYTHON) src/plot_final_results.py

final:
	$(PYTHON) src/final_test.py