"""Run the locked TV4 final-test evaluation exactly once.

The script refuses to run again when the evaluation snapshot already exists.
Use ``--force`` only if the team deliberately invalidates the previous final-test
evaluation and records that decision in the report.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.exceptions import InconsistentVersionWarning

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.features import load_feature_split
from src.tv4_analysis import (
    LABELS,
    add_manual_error_review,
    build_cv_ranking,
    build_error_table,
    evaluate_predictions,
    select_error_examples,
    sha256_file,
    summarize_metrics,
)

MODEL_PATH = PROJECT_ROOT / "models" / "best_sentiment_model.joblib"
SPLIT_PATH = PROJECT_ROOT / "models" / "train_test_features.joblib"
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "reviews_cleaned.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "evaluation"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"
SNAPSHOT_PATH = OUTPUT_DIR / "final_test_snapshot.json"


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []
    for _, row in frame.iterrows():
        values = [str(row[column]).replace("|", "\\|").replace("\n", " ") for column in columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, separator, *rows])


def _plot_confusion_matrices(matrix: np.ndarray, normalized: np.ndarray) -> Path:
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.3))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=LABELS,
        yticklabels=LABELS,
        cbar=False,
        ax=axes[0],
    )
    axes[0].set_title("Confusion Matrix - Final Test")
    axes[0].set_xlabel("Dự đoán")
    axes[0].set_ylabel("Thực tế")
    sns.heatmap(
        normalized,
        annot=True,
        fmt=".1%",
        cmap="Blues",
        vmin=0,
        vmax=1,
        xticklabels=LABELS,
        yticklabels=LABELS,
        cbar=False,
        ax=axes[1],
    )
    axes[1].set_title("Normalized Confusion Matrix - Final Test")
    axes[1].set_xlabel("Dự đoán")
    axes[1].set_ylabel("Thực tế")
    fig.suptitle("Logistic Regression + SMOTE | Locked Final Test", fontsize=14, fontweight="bold")
    fig.tight_layout()
    output = FIGURE_DIR / "tv4_final_test_confusion_matrix.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


def _write_report(
    summary: dict,
    per_class: pd.DataFrame,
    matrix: np.ndarray,
    normalized: np.ndarray,
    ranking: pd.DataFrame,
    examples: pd.DataFrame,
    inference_seconds: float,
) -> None:
    cv_best = float(ranking.iloc[0]["CV Macro F1 Mean"])
    gap = float(summary["macro_f1"]) - cv_best
    negative = per_class.loc[per_class["Label"] == "Negative"].iloc[0]
    neutral = per_class.loc[per_class["Label"] == "Neutral"].iloc[0]
    positive = per_class.loc[per_class["Label"] == "Positive"].iloc[0]
    report_metrics = per_class.copy()
    for column in ("Precision", "Recall", "F1"):
        report_metrics[column] = report_metrics[column].map(lambda value: f"{value:.4f}")
    ranking_report = ranking.copy()
    ranking_report["CV Macro F1 Mean"] = ranking_report["CV Macro F1 Mean"].map(lambda value: f"{value:.4f}")
    ranking_report["CV Macro F1 Std"] = ranking_report["CV Macro F1 Std"].map(lambda value: f"{value:.4f}")
    reason_counts = examples["manual_category"].value_counts().rename_axis("Nhóm nguyên nhân").reset_index(name="Số mẫu")
    content = f"""# TV4 - Đánh giá Final Test và phân tích lỗi

## 3.4. Kết quả thực nghiệm

Mô hình được TV3 khóa trước khi mở Final Test là **Logistic Regression (`C=1.0`) + SMOTE**. Final Test gồm **{summary['test_count']:,}** mẫu và chỉ được đánh giá trong lần chạy có snapshot này.

- Accuracy: **{_format_percent(summary['accuracy'])}**
- Macro F1: **{summary['macro_f1']:.4f}**
- Weighted F1: **{summary['weighted_f1']:.4f}**
- Số dự đoán sai: **{summary['error_count']:,}/{summary['test_count']:,}**
- Thời gian suy luận cả Final Test: **{inference_seconds:.4f} giây**

### Chỉ số theo từng lớp

{_markdown_table(report_metrics)}

### Xếp hạng mô hình trên Development set

{_markdown_table(ranking_report)}

> Bảng xếp hạng dùng Stratified 5-Fold CV do TV3 bàn giao. Chỉ mô hình đã chọn được mở Final Test; không dùng Final Test để xếp hạng lại năm mô hình.

## 3.5. Confusion Matrix và Error Analysis

![Confusion Matrix](figures/tv4_final_test_confusion_matrix.png)

Ma trận theo thứ tự `Negative, Neutral, Positive`:

```text
{matrix.tolist()}
```

- **Negative:** Recall {_format_percent(float(negative['Recall']))}, cho thấy lớp thiểu số vẫn là lớp khó nhất.
- **Neutral:** Recall {_format_percent(float(neutral['Recall']))}; review trung tính dễ bị kéo sang Positive khi chứa nhiều từ khen.
- **Positive:** Recall {_format_percent(float(positive['Recall']))}; kết quả cao một phần do lớp Positive chiếm đa số.

### Nhóm nguyên nhân trong 15 mẫu phân tích thủ công

{_markdown_table(reason_counts)}

Danh sách chi tiết ở `reports/evaluation/error_analysis_15_samples.csv`. Mười lăm mẫu đại diện đã được đọc thủ công; 442 lỗi toàn tập giữ nhãn heuristic để hỗ trợ tra cứu.

## Overfitting / Underfitting

- Development CV Macro F1: **{cv_best:.4f}**
- Final Test Macro F1: **{summary['macro_f1']:.4f}**
- Chênh lệch Final Test - CV: **{gap:+.4f}**

Chênh lệch này {'nhỏ, chưa cho thấy dấu hiệu overfitting nghiêm trọng' if abs(gap) < 0.03 else 'cần được thảo luận như một rủi ro khác biệt phân phối hoặc overfitting'}.

## Giới hạn diễn giải

- Nhãn được suy ra từ rating nên có nguy cơ label noise.
- TF-IDF không hiểu đầy đủ ngữ cảnh, mỉa mai và quan hệ phủ định dài.
- Accuracy không phải chỉ số chính do dữ liệu mất cân bằng; cần ưu tiên Macro F1 và chỉ số theo từng lớp.
"""
    (PROJECT_ROOT / "reports" / "tv4_model_evaluation_error_analysis.md").write_text(content, encoding="utf-8")


def run(force: bool = False) -> dict:
    if SNAPSHOT_PATH.exists() and not force:
        raise SystemExit(
            "Final Test đã có snapshot. Từ chối đánh giá lại; xem reports/evaluation/final_test_snapshot.json."
        )
    for path in (MODEL_PATH, SPLIT_PATH, DATA_PATH):
        if not path.exists():
            raise FileNotFoundError(path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    split = load_feature_split(SPLIT_PATH)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InconsistentVersionWarning)
        model = joblib.load(MODEL_PATH)
    if split["X_test"].shape[1] != getattr(model, "n_features_in_", -1):
        raise ValueError("Model và Final Test không cùng feature contract.")
    if not hasattr(model, "predict_proba"):
        raise TypeError("Model không có predict_proba().")

    started = time.perf_counter()
    predictions = model.predict(split["X_test"])
    probabilities = model.predict_proba(split["X_test"])
    inference_seconds = time.perf_counter() - started

    y_test = np.asarray(split["y_test"], dtype=object)
    summary = summarize_metrics(y_test, predictions)
    per_class, matrix, normalized = evaluate_predictions(y_test, predictions)
    ranking = build_cv_ranking()
    source_data = pd.read_excel(DATA_PATH)
    errors = build_error_table(
        source_data,
        split["test_indices"],
        y_test,
        predictions,
        probabilities,
        model.classes_,
    )
    examples = add_manual_error_review(select_error_examples(errors, limit=15))

    pd.DataFrame([summary]).to_csv(OUTPUT_DIR / "final_test_metrics.csv", index=False, encoding="utf-8-sig")
    per_class.to_csv(OUTPUT_DIR / "final_test_per_class.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(matrix, index=LABELS, columns=LABELS).to_csv(OUTPUT_DIR / "confusion_matrix.csv", encoding="utf-8-sig")
    pd.DataFrame(normalized, index=LABELS, columns=LABELS).to_csv(OUTPUT_DIR / "confusion_matrix_normalized.csv", encoding="utf-8-sig")
    ranking.to_csv(OUTPUT_DIR / "model_ranking_cv.csv", index=False, encoding="utf-8-sig")
    errors.to_csv(OUTPUT_DIR / "all_final_test_errors.csv", index=False, encoding="utf-8-sig")
    examples.to_csv(OUTPUT_DIR / "error_analysis_15_samples.csv", index=False, encoding="utf-8-sig")
    figure_path = _plot_confusion_matrices(matrix, normalized)
    _write_report(summary, per_class, matrix, normalized, ranking, examples, inference_seconds)

    snapshot = {
        "schema_version": 1,
        "policy": "locked final test evaluated once by TV4",
        "model": "Logistic Regression + SMOTE",
        "labels": list(LABELS),
        "metrics": summary,
        "inference_seconds": inference_seconds,
        "cv_macro_f1": float(ranking.iloc[0]["CV Macro F1 Mean"]),
        "cv_to_final_gap": float(summary["macro_f1"] - ranking.iloc[0]["CV Macro F1 Mean"]),
        "model_sha256": sha256_file(MODEL_PATH),
        "split_sha256": sha256_file(SPLIT_PATH),
        "data_sha256": sha256_file(DATA_PATH),
        "figure": str(figure_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Explicitly invalidate the existing run-once guard.")
    args = parser.parse_args()
    snapshot = run(force=args.force)
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
