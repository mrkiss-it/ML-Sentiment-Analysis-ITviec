import os
from pathlib import Path
from typing import Any, Dict, List

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from scipy import sparse
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV, cross_val_predict, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

RANDOM_STATE = 2026

# Thứ tự base learners cho Stacking Ensemble: [MNB, LR, LinearSVC, RF] -> meta LR.
STACKING_BASE_ORDER = [
    "Multinomial Naive Bayes",
    "Logistic Regression",
    "Linear SVM",
    "Random Forest",
]

_SHORT_NAMES = {
    "Multinomial Naive Bayes": "mnb",
    "Logistic Regression": "lr",
    "Linear SVM": "svm",
    "Random Forest": "rf",
}

# Lưới siêu tham số mặc định cho GridSearchCV.
PARAM_GRIDS: Dict[str, Dict[str, List[Any]]] = {
    "Multinomial Naive Bayes": {"clf__alpha": [0.1, 0.5, 1.0, 2.0]},
    "Logistic Regression": {"clf__C": [0.1, 1.0, 3.0, 10.0]},
    "Linear SVM": {"clf__C": [0.01, 0.1, 1.0, 10.0]},
    "Random Forest": {
        "clf__n_estimators": [200, 400],
        "clf__max_depth": [None, 30, 50],
    },
}


def build_base_models(random_state: int = RANDOM_STATE) -> Dict[str, Any]:
    """5 mô hình cơ sở, dùng class_weight='balanced' làm chiến lược mất cân bằng mặc định."""
    return {
        "Multinomial Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=random_state
        ),
        "Linear SVM": LinearSVC(class_weight="balanced", random_state=random_state),
        "Random Forest": RandomForestClassifier(
            class_weight="balanced", random_state=random_state, n_jobs=-1
        ),
    }


def build_variant(model: Any, strategy: str, random_state: int = RANDOM_STATE, k_neighbors: int = 5) -> ImbPipeline:
    """Bọc model trong Pipeline để chọn chiến lược mất cân bằng.

    - "balanced": không resample, giữ nguyên class_weight='balanced' của model (nếu có).
    - "smote": resample bằng SMOTE bên trong Pipeline để chỉ tác động lên fold train trong CV,
      tránh rò rỉ dữ liệu (data leakage) giữa các fold.
    """
    clf = clone(model)
    if strategy == "balanced":
        sampler = "passthrough"
    elif strategy == "smote":
        sampler = SMOTE(random_state=random_state, k_neighbors=k_neighbors)
        if "class_weight" in clf.get_params():
            clf.set_params(class_weight=None)
    else:
        raise ValueError(f"Chiến lược mất cân bằng không hợp lệ: {strategy!r}")
    return ImbPipeline(steps=[("smote", sampler), ("clf", clf)])


def compare_imbalance_strategies(
    X_train: sparse.spmatrix,
    y_train,
    cv,
    random_state: int = RANDOM_STATE,
    n_jobs: int = -1,
) -> pd.DataFrame:
    """So sánh class_weight='balanced' vs SMOTE cho từng model bằng CV Macro F1 trên tập train (Development)."""
    rows = []
    for name, model in build_base_models(random_state=random_state).items():
        for strategy in ("balanced", "smote"):
            variant = build_variant(model, strategy=strategy, random_state=random_state)
            scores = cross_val_score(variant, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=n_jobs)
            rows.append(
                {
                    "Model": name,
                    "Strategy": strategy,
                    "CV Macro F1 Mean": scores.mean(),
                    "CV Macro F1 Std": scores.std(),
                }
            )
    return pd.DataFrame(rows)


def select_strategy_per_model(comparison: pd.DataFrame) -> Dict[str, str]:
    """Chọn chiến lược mất cân bằng tốt nhất (theo CV Macro F1 trung bình) cho mỗi model."""
    best_idx = comparison.groupby("Model")["CV Macro F1 Mean"].idxmax()
    winners = comparison.loc[best_idx]
    return dict(zip(winners["Model"], winners["Strategy"]))


def tune_models(
    X_train: sparse.spmatrix,
    y_train,
    strategies: Dict[str, str],
    cv,
    param_grids: Dict[str, Dict[str, List[Any]]] | None = None,
    random_state: int = RANDOM_STATE,
    n_jobs: int = -1,
) -> Dict[str, GridSearchCV]:
    """Tinh chỉnh siêu tham số từng model (GridSearchCV, scoring='f1_macro') chỉ trên X_train."""
    grids = param_grids or PARAM_GRIDS
    results: Dict[str, GridSearchCV] = {}
    for name, model in build_base_models(random_state=random_state).items():
        strategy = strategies.get(name, "balanced")
        variant = build_variant(model, strategy=strategy, random_state=random_state)
        search = GridSearchCV(variant, grids[name], scoring="f1_macro", cv=cv, n_jobs=n_jobs)
        search.fit(X_train, y_train)
        results[name] = search
    return results


def build_stacking(tuned: Dict[str, GridSearchCV], random_state: int = RANDOM_STATE, cv: int = 5) -> StackingClassifier:
    """Stacking Ensemble: base learners = [MNB, LR, LinearSVC, RF] (đã tune) -> meta-learner Logistic Regression."""
    estimators = [
        (_SHORT_NAMES[name], clone(tuned[name].best_estimator_)) for name in STACKING_BASE_ORDER
    ]
    return StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(max_iter=2000, random_state=random_state),
        cv=cv,
        n_jobs=-1,
    )


def summarize_results(tuned: Dict[str, GridSearchCV], stacking_scores: np.ndarray) -> pd.DataFrame:
    """Bảng tổng hợp CV Macro F1 của các model đã tune và Stacking, sắp xếp giảm dần (phục vụ Mục 3.4 báo cáo)."""
    rows = [
        {
            "Model": name,
            "CV Macro F1 Mean": search.best_score_,
            "CV Macro F1 Std": search.cv_results_["std_test_score"][search.best_index_],
            "Best Params": search.best_params_,
        }
        for name, search in tuned.items()
    ]
    rows.append(
        {
            "Model": "Stacking Ensemble",
            "CV Macro F1 Mean": stacking_scores.mean(),
            "CV Macro F1 Std": stacking_scores.std(),
            "Best Params": {"cv": len(stacking_scores)},
        }
    )
    return pd.DataFrame(rows).sort_values("CV Macro F1 Mean", ascending=False).reset_index(drop=True)


def lock_best_model(estimator: Any, X_train: sparse.spmatrix, y_train) -> Any:
    """Huấn luyện lại (refit) model tốt nhất trên toàn bộ tập Development (X_train). Không nhận X_test."""
    locked = clone(estimator)
    locked.fit(X_train, y_train)
    return locked


def save_model(model: Any, filepath: str | os.PathLike[str]) -> None:
    """Lưu model đã khóa để phục vụ bước đánh giá độc lập."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def plot_cv_confusion_matrix(
    estimator: Any,
    X_train: sparse.spmatrix,
    y_train,
    cv,
    labels: List[str],
    save_path: str | os.PathLike[str] | None = None,
    n_jobs: int = -1,
) -> None:
    """Confusion matrix chẩn đoán trên dự đoán out-of-fold của CV (Development set) — KHÔNG dùng Final Test."""
    y_pred = cross_val_predict(estimator, X_train, y_train, cv=cv, n_jobs=n_jobs)
    cm = confusion_matrix(y_train, y_pred, labels=labels)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title("Confusion Matrix (CV out-of-fold trên Development set)")
    plt.xlabel("Dự đoán (Predicted)")
    plt.ylabel("Thực tế (Actual)")
    plt.tight_layout()

    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=300)
        print(f"Đã lưu biểu đồ tại: {path}")
    plt.show()
