"""Utilities for TV4 final evaluation, company insights, and web inference."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from src.preprocessing import TextPreprocessor


LABELS = ("Negative", "Neutral", "Positive")


class InsufficientSignalError(ValueError):
    """The trained vocabulary provides too little evidence for a prediction."""


ASPECT_COLUMNS = (
    "Salary & benefits",
    "Training & learning",
    "Management cares about me",
    "Culture & fun",
    "Office & workspace",
)
TV3_CV_RESULTS = (
    ("Logistic Regression", 0.572705, 0.010803, "SMOTE", "C=1.0"),
    ("Linear SVM", 0.572392, 0.025989, "Balanced", "C=0.1"),
    ("Random Forest", 0.566381, 0.013763, "Balanced", "max_depth=30, n_estimators=400"),
    ("Stacking Ensemble", 0.556037, 0.023712, "Mixed", "cv=5"),
    ("Multinomial Naive Bayes", 0.553418, 0.018340, "SMOTE", "alpha=0.5"),
)

MANUAL_ERROR_NOTES = {
    1418: ("Mixed sentiment", "Nhiều tín hiệu tích cực ở đầu review lấn át phần phàn nàn về chính sách OT."),
    4736: ("Label noise", "Nội dung gần như hoàn toàn tích cực nhưng rating 3 sao sinh nhãn Neutral."),
    8121: ("Mixed sentiment", "Khen môi trường nhưng nêu OT và chính sách khác nhau theo product."),
    7529: ("Label noise", "Rating 4 sao sinh Positive dù nội dung có nhiều phàn nàn mạnh về OT và lương."),
    2884: ("Mixed sentiment", "Phần khen môi trường đi kèm chê lương và trang thiết bị."),
    5329: ("Label noise", "Nội dung tiêu cực rất mạnh nhưng rating 3 sao sinh nhãn Neutral."),
    127: ("Mixed sentiment", "Nhiều ý khen phúc lợi, nhưng có bất tiện về khoảng cách và mùa OT."),
    2399: ("Mixed sentiment", "Khen cơ hội học hỏi nhưng chê lương thấp và tăng chậm."),
    2668: ("Mixed sentiment", "Mở đầu tích cực, kết thúc bằng OT lặp lại, lương và thưởng thấp."),
    2592: ("Mixed sentiment", "Câu khen môi trường chiếm nhiều token trước phần chê lương, OT và quản lý."),
    3130: ("Mixed sentiment", "Review khen học hỏi và phúc lợi nhưng chê áp lực, OT qua đêm và lương."),
    2440: ("Mixed sentiment", "Cơ hội học tập tốt đi cùng lương thấp, quy trình rườm rà và quản lý kém."),
    3016: ("Label noise", "Nội dung chủ yếu tiêu cực nhưng rating 4 sao sinh nhãn Positive."),
    950: ("Multi-aspect long review", "Review rất dài, nhiều khía cạnh và thời điểm; một nhãn ba lớp không giữ được sắc thái."),
    466: ("Mixed sentiment", "Khen môi trường nhưng chê OT, lương và cơ hội kỹ thuật."),
}


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_cv_ranking() -> pd.DataFrame:
    """Return the frozen CV ranking handed over by TV3."""
    frame = pd.DataFrame(
        TV3_CV_RESULTS,
        columns=["Model", "CV Macro F1 Mean", "CV Macro F1 Std", "Strategy", "Best Params"],
    )
    frame.insert(0, "Rank", np.arange(1, len(frame) + 1))
    frame["Evaluation Set"] = "Development / Stratified 5-Fold CV"
    return frame


def evaluate_predictions(y_true: Iterable[str], y_pred: Iterable[str]) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Compute final-test metrics and count/normalized confusion matrices."""
    true = np.asarray(list(y_true), dtype=object)
    pred = np.asarray(list(y_pred), dtype=object)
    precision, recall, f1, support = precision_recall_fscore_support(
        true, pred, labels=LABELS, zero_division=0
    )
    rows = [
        {
            "Label": label,
            "Precision": float(precision[index]),
            "Recall": float(recall[index]),
            "F1": float(f1[index]),
            "Support": int(support[index]),
        }
        for index, label in enumerate(LABELS)
    ]
    per_class = pd.DataFrame(rows)
    matrix = confusion_matrix(true, pred, labels=LABELS)
    normalized = confusion_matrix(true, pred, labels=LABELS, normalize="true")
    return per_class, matrix, normalized


def summarize_metrics(y_true: Iterable[str], y_pred: Iterable[str]) -> dict[str, float | int]:
    true = np.asarray(list(y_true), dtype=object)
    pred = np.asarray(list(y_pred), dtype=object)
    return {
        "test_count": int(len(true)),
        "accuracy": float(accuracy_score(true, pred)),
        "macro_f1": float(f1_score(true, pred, average="macro")),
        "weighted_f1": float(f1_score(true, pred, average="weighted")),
        "error_count": int(np.sum(true != pred)),
    }


def classify_error_reason(raw_text: str, actual: str, predicted: str) -> str:
    """Assign an auditable heuristic category for manual error review."""
    text = str(raw_text or "").lower()
    contrast = ("nhưng", "tuy nhiên", "mặc dù", "dù", "bên cạnh", "however", "but")
    negation = ("không", "chẳng", "chưa", "chẳng thể", "không thể", "not ", "never")
    sarcasm = ("tuyệt vời", "quá tuyệt", "hay lắm", "=))", ":))", "haha")
    if any(token in text for token in contrast):
        return "Mixed sentiment / nhiều vế ý"
    if any(token in text for token in negation):
        return "Phủ định hoặc cấu trúc phức tạp"
    if any(token in text for token in sarcasm) and actual != predicted:
        return "Khả năng châm biếm / mỉa mai"
    if len(text.split()) < 8:
        return "Văn bản ngắn, thiếu ngữ cảnh"
    return "Label noise hoặc tín hiệu TF-IDF chưa đủ"


def build_error_table(
    source_data: pd.DataFrame,
    test_indices: Iterable[int],
    y_true: Iterable[str],
    y_pred: Iterable[str],
    probabilities: np.ndarray,
    classes: Iterable[str],
) -> pd.DataFrame:
    """Join incorrect predictions back to their original reviews."""
    classes = list(classes)
    true = np.asarray(list(y_true), dtype=object)
    pred = np.asarray(list(y_pred), dtype=object)
    indices = np.asarray(list(test_indices))
    wrong_positions = np.flatnonzero(true != pred)
    records: list[dict] = []
    for position in wrong_positions:
        row = source_data.loc[indices[position]]
        record = {
            "source_index": int(indices[position]),
            "company": str(row.get("Company Name", "")),
            "rating": row.get("Rating", np.nan),
            "review": str(row.get("raw_review_text", row.get("clean_basic_text", ""))),
            "actual": str(true[position]),
            "predicted": str(pred[position]),
            "confidence": float(np.max(probabilities[position])),
            "error_reason": classify_error_reason(
                str(row.get("raw_review_text", "")), str(true[position]), str(pred[position])
            ),
        }
        for class_index, label in enumerate(classes):
            record[f"p_{label.lower()}"] = float(probabilities[position, class_index])
        records.append(record)
    return pd.DataFrame(records).sort_values(
        ["actual", "confidence"], ascending=[True, False]
    ).reset_index(drop=True)


def select_error_examples(errors: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    """Select a diverse, deterministic set of errors for the report."""
    if errors.empty:
        return errors.copy()
    selected = (
        errors.sort_values("confidence", ascending=False)
        .groupby(["actual", "predicted", "error_reason"], group_keys=False)
        .head(2)
    )
    if len(selected) < limit:
        remaining = errors.loc[~errors.index.isin(selected.index)]
        selected = pd.concat([selected, remaining.head(limit - len(selected))])
    return selected.head(limit).sort_values("confidence", ascending=False).reset_index(drop=True)


def add_manual_error_review(examples: pd.DataFrame) -> pd.DataFrame:
    """Attach human-reviewed categories and explanations to selected examples."""
    reviewed = examples.copy()
    reviewed["manual_category"] = reviewed["source_index"].map(
        lambda index: MANUAL_ERROR_NOTES.get(int(index), ("Cần rà soát", ""))[0]
    )
    reviewed["manual_analysis"] = reviewed["source_index"].map(
        lambda index: MANUAL_ERROR_NOTES.get(int(index), ("", "Cần đọc và gán nhóm thủ công."))[1]
    )
    return reviewed


def ensure_estimator_compatibility(estimator: object) -> None:
    """Ensure estimators unpickled across scikit-learn versions remain operational.

    For example, models pickled with scikit-learn >=1.8/1.9 where LogisticRegression.multi_class
    was removed/deprecated will raise AttributeError in scikit-learn <=1.6 if multi_class is missing.
    """
    if hasattr(estimator, "steps"):
        for _, step in getattr(estimator, "steps", []):
            ensure_estimator_compatibility(step)
    if hasattr(estimator, "named_steps"):
        for step in getattr(estimator, "named_steps", {}).values():
            ensure_estimator_compatibility(step)
    if hasattr(estimator, "estimators_"):
        for sub_est in getattr(estimator, "estimators_", []):
            ensure_estimator_compatibility(sub_est)
    if getattr(estimator, "__class__", None) is not None:
        if estimator.__class__.__name__ == "LogisticRegression":
            if not hasattr(estimator, "multi_class"):
                estimator.multi_class = "auto"


def load_inference_bundle(project_root: str | Path, model_dir: str = "models") -> dict:
    """Load and validate the deployable text-only inference artifacts."""
    root = Path(project_root)
    model_path = root / model_dir / "best_sentiment_model.joblib"
    vectorizer_path = root / model_dir / "text_tfidf_vectorizer.joblib"
    model = joblib.load(model_path)
    ensure_estimator_compatibility(model)
    vectorizer = joblib.load(vectorizer_path)
    model_width = int(getattr(model, "n_features_in_", -1))
    vectorizer_width = len(getattr(vectorizer, "vocabulary_", {}))
    if model_width <= 0 or model_width != vectorizer_width:
        raise ValueError(
            f"Feature contract mismatch: model={model_width}, vectorizer={vectorizer_width}."
        )
    if not hasattr(model, "predict_proba"):
        raise TypeError("Mô hình triển khai không hỗ trợ predict_proba().")
    preprocessor = TextPreprocessor(root / "data" / "dictionaries")
    # Pay the tokenizer's one-time import cost while the cached resource loads,
    # so the first user prediction has the same responsive latency as later ones.
    sample_text = preprocessor.clean_advance_text("môi trường làm việc tốt")
    # Warm up model prediction to verify inference pipeline
    sample_mat = vectorizer.transform([sample_text])
    model.predict_proba(sample_mat)
    return {
        "model": model,
        "vectorizer": vectorizer,
        "preprocessor": preprocessor,
        "classes": tuple(str(label) for label in model.classes_),
        "feature_count": model_width,
        "model_sha256": sha256_file(model_path),
        "vectorizer_sha256": sha256_file(vectorizer_path),
    }


def predict_review(bundle: dict, raw_text: str) -> dict:
    """Run raw text through the exact text-only deployment contract."""
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("Review không được để trống.")
    clean_text = bundle["preprocessor"].clean_advance_text(raw_text)
    if not clean_text:
        raise ValueError("Review không còn token hợp lệ sau tiền xử lý.")
    matrix = bundle["vectorizer"].transform([clean_text])
    if matrix.shape[1] != bundle["feature_count"]:
        raise ValueError("Chiều TF-IDF không khớp model.")
    if matrix.nnz == 0:
        raise InsufficientSignalError("Review không có từ nào trong từ vựng đã học; hãy nhập nội dung cụ thể hơn.")
    if matrix.nnz == 1 and len(clean_text.split()) > 1:
        raise InsufficientSignalError("Review chỉ còn một đặc trưng được model nhận ra; hãy mô tả cụ thể hơn để tránh dự đoán thiếu căn cứ.")
    probabilities = bundle["model"].predict_proba(matrix)[0]
    prediction = str(bundle["model"].classes_[int(np.argmax(probabilities))])
    names = bundle["vectorizer"].get_feature_names_out()
    active = matrix.nonzero()[1]
    weights = matrix.data
    top_tokens = [
        {"token": str(names[index]), "tfidf": float(weight)}
        for index, weight in sorted(zip(active, weights), key=lambda item: item[1], reverse=True)[:10]
    ]
    return {
        "label": prediction,
        "clean_text": clean_text,
        "probabilities": {
            str(label): float(probability)
            for label, probability in zip(bundle["model"].classes_, probabilities)
        },
        "top_tokens": top_tokens,
        "active_feature_count": int(matrix.nnz),
    }


def top_keywords(texts: Iterable[str], stopwords: set[str] | None = None, limit: int = 20) -> list[tuple[str, int]]:
    """Return frequent unigrams for transparent company insight summaries."""
    ignored = stopwords or set()
    counter: Counter[str] = Counter()
    for text in texts:
        tokens = re.findall(r"[\w_]+", str(text).lower(), flags=re.UNICODE)
        counter.update(token for token in tokens if len(token) > 1 and token not in ignored)
    return counter.most_common(limit)


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
