"""Measure reproducible full-development refit time for TV4's model table."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from types import SimpleNamespace

from sklearn.base import clone

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.features import load_feature_split
from src.models import build_base_models, build_stacking, build_variant
from src.tv4_analysis import build_cv_ranking


def build_frozen_estimators() -> dict:
    base = build_base_models()
    estimators = {
        "Multinomial Naive Bayes": build_variant(base["Multinomial Naive Bayes"], "smote").set_params(clf__alpha=0.5),
        "Logistic Regression": build_variant(base["Logistic Regression"], "smote").set_params(clf__C=1.0),
        "Linear SVM": build_variant(base["Linear SVM"], "balanced").set_params(clf__C=0.1),
        "Random Forest": build_variant(base["Random Forest"], "balanced").set_params(
            clf__max_depth=30, clf__n_estimators=400
        ),
    }
    frozen_searches = {
        name: SimpleNamespace(best_estimator_=estimator) for name, estimator in estimators.items()
    }
    estimators["Stacking Ensemble"] = build_stacking(frozen_searches, cv=5)
    return estimators


def run() -> None:
    split = load_feature_split(PROJECT_ROOT / "models" / "train_test_features.joblib")
    durations = {}
    for name, estimator in build_frozen_estimators().items():
        started = time.perf_counter()
        clone(estimator).fit(split["X_train"], split["y_train"])
        durations[name] = time.perf_counter() - started
        print(f"{name}: {durations[name]:.4f} s")

    ranking = build_cv_ranking()
    ranking["Refit Time (s)"] = ranking["Model"].map(durations)
    ranking["Timing Scope"] = "1 refit / full Development set / local machine"
    output = PROJECT_ROOT / "reports" / "evaluation" / "model_ranking_cv.csv"
    ranking.to_csv(output, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    run()
