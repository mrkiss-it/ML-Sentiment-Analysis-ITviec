"""Compare model-selection metrics on identical Development CV folds.

This experiment varies n-grams and imbalance handling for Logistic Regression
with C=1.0. It never uses Final Test to choose a configuration.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.features import load_feature_split
from src.preprocessing import TextPreprocessor


OUT = ROOT / "reports" / "evaluation" / "metric_selection_ablation.json"
NGRAMS = {"Unigram": (1, 1), "Bigram": (2, 2), "Unigram + Bigram": (1, 2)}
STRATEGIES = ("Không cân bằng", "Class weight", "SMOTE")


def make_pipeline(ngram_range: tuple[int, int], strategy: str) -> Pipeline:
    class_weight = "balanced" if strategy == "Class weight" else None
    sampler = SMOTE(random_state=2026, k_neighbors=5) if strategy == "SMOTE" else "passthrough"
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=ngram_range, min_df=2, sublinear_tf=True)),
            ("smote", sampler),
            ("clf", LogisticRegression(C=1.0, max_iter=2000, random_state=2026, class_weight=class_weight)),
        ]
    )


def main() -> None:
    original = load_feature_split(ROOT / "models" / "train_test_features.joblib")
    source = pd.read_excel(ROOT / "data" / "processed" / "reviews_cleaned.xlsx")
    indices = np.asarray(original["train_indices"])
    labels = pd.Series(original["y_train"].to_numpy(), index=indices)
    if not source.loc[indices, "sentiment"].eq(labels).all():
        raise ValueError("Development labels do not match the locked split")
    preprocessor = TextPreprocessor(ROOT / "data" / "dictionaries")
    texts = source.loc[indices, "raw_review_text"].fillna("").map(preprocessor.clean_advance_text).astype(str)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2026)
    rows = []
    # A valid "no n-gram" reference: use no text features and always predict
    # the most frequent label in the training fold.
    no_text = cross_validate(
        DummyClassifier(strategy="most_frequent"), np.zeros((len(labels), 1)), labels,
        cv=cv, scoring={"accuracy": "accuracy", "macro_f1": "f1_macro"}, n_jobs=1,
    )
    baseline = {
        "ngram": "Không dùng văn bản (đa số)", "strategy": "Không áp dụng",
        "cv_accuracy_mean": float(no_text["test_accuracy"].mean()),
        "cv_accuracy_std": float(no_text["test_accuracy"].std()),
        "cv_macro_f1_mean": float(no_text["test_macro_f1"].mean()),
        "cv_macro_f1_std": float(no_text["test_macro_f1"].std()),
        "fold_accuracy": no_text["test_accuracy"].tolist(),
        "fold_macro_f1": no_text["test_macro_f1"].tolist(),
    }
    for ngram_name, ngram_range in NGRAMS.items():
        for strategy in STRATEGIES:
            print(f"CV: {ngram_name} / {strategy}", flush=True)
            result = cross_validate(
                make_pipeline(ngram_range, strategy), texts, labels,
                cv=cv, scoring={"accuracy": "accuracy", "macro_f1": "f1_macro"},
                n_jobs=1, error_score="raise",
            )
            rows.append({
                "ngram": ngram_name,
                "strategy": strategy,
                "cv_accuracy_mean": float(result["test_accuracy"].mean()),
                "cv_accuracy_std": float(result["test_accuracy"].std()),
                "cv_macro_f1_mean": float(result["test_macro_f1"].mean()),
                "cv_macro_f1_std": float(result["test_macro_f1"].std()),
                "fold_accuracy": result["test_accuracy"].tolist(),
                "fold_macro_f1": result["test_macro_f1"].tolist(),
            })
    by_accuracy = max(rows, key=lambda row: row["cv_accuracy_mean"])
    by_macro_f1 = max(rows, key=lambda row: row["cv_macro_f1_mean"])
    payload = {
        "method": "Same Development rows and Stratified 5-Fold CV; TF-IDF refit and SMOTE restricted to train fold; Logistic Regression C=1.0; no Final Test selection",
        "development_count": len(labels),
        "no_text_baseline": baseline,
        "configurations": rows,
        "selected_by_accuracy": {"ngram": by_accuracy["ngram"], "strategy": by_accuracy["strategy"]},
        "selected_by_macro_f1": {"ngram": by_macro_f1["ngram"], "strategy": by_macro_f1["strategy"]},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"accuracy": payload["selected_by_accuracy"], "macro_f1": payload["selected_by_macro_f1"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
