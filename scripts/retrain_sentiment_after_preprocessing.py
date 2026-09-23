"""Build a revised, isolated text-only model on the original train/test indices.

Model selection uses Development data only. The saved test matrix is for a
single, explicitly documented evaluation after the candidate is selected.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.features import FeatureExtractor, FeatureSplit, load_feature_split, save_feature_split
from src.preprocessing import TextPreprocessor

OUTPUT = ROOT / "models" / "retrained_v2"


def vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True
    )


def classifier() -> Pipeline:
    return Pipeline(
        [
            ("smote", SMOTE(random_state=2026, k_neighbors=5)),
            ("clf", LogisticRegression(C=1.0, max_iter=2000, random_state=2026)),
        ]
    )


def cv_scores(texts: pd.Series, labels: pd.Series) -> np.ndarray:
    # Fit TF-IDF afresh in every fold, then resample that fold's training part.
    pipeline = Pipeline([("tfidf", vectorizer()), *classifier().steps])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2026)
    return cross_val_score(
        pipeline, texts, labels, cv=cv, scoring="f1_macro", n_jobs=1
    )


def main() -> None:
    original = load_feature_split(ROOT / "models" / "train_test_features.joblib")
    source = pd.read_excel(ROOT / "data" / "processed" / "reviews_cleaned.xlsx")
    train_indices = np.asarray(original["train_indices"])
    test_indices = np.asarray(original["test_indices"])
    y_train = pd.Series(original["y_train"].to_numpy(), index=train_indices)
    y_test = pd.Series(original["y_test"].to_numpy(), index=test_indices)
    if not source.loc[train_indices, "sentiment"].eq(y_train).all():
        raise ValueError("Development labels no longer match original split.")
    if not source.loc[test_indices, "sentiment"].eq(y_test).all():
        raise ValueError("Final Test labels no longer match original split.")

    preprocessor = TextPreprocessor(ROOT / "data" / "dictionaries")
    print("Cleaning Development texts...", flush=True)
    new_train = source.loc[train_indices, "raw_review_text"].fillna("").map(
        preprocessor.clean_advance_text
    )
    print("Cleaning Final Test texts with the same rules...", flush=True)
    new_test = source.loc[test_indices, "raw_review_text"].fillna("").map(
        preprocessor.clean_advance_text
    )
    old_train = source.loc[train_indices, "clean_advance_text"].fillna("").astype(str)
    new_train = new_train.astype(str)
    new_test = new_test.astype(str)
    print("Cross-validating original preprocessing...", flush=True)
    old_scores = cv_scores(old_train, y_train)
    print("Cross-validating revised preprocessing...", flush=True)
    new_scores = cv_scores(new_train, y_train)
    print("Original CV:", old_scores.tolist(), "mean:", old_scores.mean(), flush=True)
    print("Revised CV:", new_scores.tolist(), "mean:", new_scores.mean(), flush=True)

    extractor = vectorizer()
    X_train = extractor.fit_transform(new_train).tocsr()
    X_test = extractor.transform(new_test).tocsr()
    model = classifier().fit(X_train, y_train)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUTPUT / "best_sentiment_model.joblib")
    joblib.dump(extractor, OUTPUT / "text_tfidf_vectorizer.joblib")
    split = FeatureSplit(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        train_indices=train_indices,
        test_indices=test_indices,
    )
    feature_extractor = FeatureExtractor()
    feature_extractor.vectorizer = extractor
    save_feature_split(
        split,
        OUTPUT / "train_test_features.joblib",
        extractor=feature_extractor,
        metadata={"reason": "Revised sentiment preprocessing", "source_split": "original indices"},
    )
    audit = {
        "original_cv_macro_f1": old_scores.tolist(),
        "revised_cv_macro_f1": new_scores.tolist(),
        "original_cv_mean": float(old_scores.mean()),
        "revised_cv_mean": float(new_scores.mean()),
        "train_count": len(train_indices),
        "test_count": len(test_indices),
        "feature_count": int(X_train.shape[1]),
    }
    (OUTPUT / "training_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
