"""Compare imbalance strategies for the project's five model families.

Use revised preprocessing, unigram+bigram TF-IDF and identical Development
folds. Final Test is never loaded or used here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.features import load_feature_split
from src.preprocessing import TextPreprocessor


OUTPUT = ROOT / "reports" / "evaluation" / "model_imbalance_ablation.json"
SEED = 2026
MODELS = ("Multinomial Naive Bayes", "Logistic Regression", "Linear SVM", "Random Forest", "Stacking Ensemble")
STRATEGIES = ("Không xử lý", "Class weight", "SMOTE")


def make_classifier(name: str, strategy: str):
    weighted = strategy == "Class weight"
    class_weight = "balanced" if weighted else None
    if name == "Multinomial Naive Bayes":
        if weighted:
            raise ValueError("MultinomialNB has no class_weight parameter")
        return MultinomialNB(alpha=0.5)
    if name == "Logistic Regression":
        return LogisticRegression(C=1.0, max_iter=2000, random_state=SEED, class_weight=class_weight)
    if name == "Linear SVM":
        return LinearSVC(C=0.1, random_state=SEED, class_weight=class_weight)
    if name == "Random Forest":
        return RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=1, class_weight=class_weight)
    if name == "Stacking Ensemble":
        base = [
            ("nb", MultinomialNB(alpha=0.5)),
            ("lr", LogisticRegression(C=1.0, max_iter=2000, random_state=SEED, class_weight=class_weight)),
            ("svm", LinearSVC(C=0.1, random_state=SEED, class_weight=class_weight)),
            ("rf", RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=1, class_weight=class_weight)),
        ]
        return StackingClassifier(
            estimators=base,
            final_estimator=LogisticRegression(max_iter=2000, random_state=SEED, class_weight=class_weight),
            cv=3,
            n_jobs=1,
        )
    raise ValueError(f"Unknown model: {name}")


def make_pipeline(name: str, strategy: str) -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("sampler", SMOTE(random_state=SEED, k_neighbors=5) if strategy == "SMOTE" else "passthrough"),
        ("classifier", make_classifier(name, strategy)),
    ])


def main() -> None:
    split = load_feature_split(ROOT / "models" / "train_test_features.joblib")
    source = pd.read_excel(ROOT / "data" / "processed" / "reviews_cleaned.xlsx")
    indices = np.asarray(split["train_indices"])
    labels = pd.Series(split["y_train"].to_numpy(), index=indices)
    if not source.loc[indices, "sentiment"].eq(labels).all():
        raise ValueError("Development labels differ from the original split")
    preprocessor = TextPreprocessor(ROOT / "data" / "dictionaries")
    texts = source.loc[indices, "raw_review_text"].fillna("").map(preprocessor.clean_advance_text).astype(str)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    rows = []
    for name in MODELS:
        for strategy in STRATEGIES:
            if name == "Multinomial Naive Bayes" and strategy == "Class weight":
                rows.append({"model": name, "strategy": strategy, "status": "Không áp dụng: MultinomialNB không hỗ trợ class_weight"})
                continue
            print(f"CV {name} / {strategy}", flush=True)
            result = cross_validate(
                make_pipeline(name, strategy), texts, labels, cv=cv,
                scoring={"accuracy": "accuracy", "macro_f1": "f1_macro"},
                n_jobs=1, error_score="raise",
            )
            row = {"model": name, "strategy": strategy, "status": "measured"}
            for key in ("accuracy", "macro_f1"):
                scores = result[f"test_{key}"]
                row[f"cv_{key}_mean"] = float(scores.mean())
                row[f"cv_{key}_std"] = float(scores.std())
                row[f"fold_{key}"] = scores.tolist()
            rows.append(row)
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_text(json.dumps({"method": METHOD, "development_count": len(labels), "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(rows)} model/strategy rows to {OUTPUT}", flush=True)


METHOD = (
    "Revised preprocessing; Development 6731 rows; Stratified 5-Fold CV seed 2026; "
    "TF-IDF (1,2) max_features=5000 fit inside each fold; SMOTE only on train fold; "
    "fixed models: MNB alpha=.5, LR C=1, SVM C=.1, RF 200 trees, Stacking of these "
    "four with inner cv=3 and meta LR; no Final Test. Class weight applies to LR/SVM/RF "
    "and meta LR, while MNB does not support it."
)


if __name__ == "__main__":
    main()
