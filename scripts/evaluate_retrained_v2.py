"""Evaluate the selected preprocessing revision, preserving the original snapshot."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.features import load_feature_split
from src.tv4_analysis import (
    LABELS,
    build_error_table,
    evaluate_predictions,
    select_error_examples,
    sha256_file,
    summarize_metrics,
)

MODEL_DIR = ROOT / "models" / "retrained_v2"
OUTPUT_DIR = ROOT / "reports" / "evaluation" / "retrained_v2"


def main() -> None:
    audit = json.loads((MODEL_DIR / "training_audit.json").read_text(encoding="utf-8"))
    split_path = MODEL_DIR / "train_test_features.joblib"
    model_path = MODEL_DIR / "best_sentiment_model.joblib"
    split = load_feature_split(split_path)
    model = joblib.load(model_path)
    y_test = np.asarray(split["y_test"], dtype=object)
    predicted = model.predict(split["X_test"])
    probabilities = model.predict_proba(split["X_test"])
    summary = summarize_metrics(y_test, predicted)
    per_class, matrix, normalized = evaluate_predictions(y_test, predicted)
    source = pd.read_excel(ROOT / "data" / "processed" / "reviews_cleaned.xlsx")
    errors = build_error_table(
        source, split["test_indices"], y_test, predicted, probabilities, model.classes_
    )
    examples = select_error_examples(errors, limit=15)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    per_class.to_csv(OUTPUT_DIR / "final_test_per_class.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(matrix, index=LABELS, columns=LABELS).to_csv(
        OUTPUT_DIR / "confusion_matrix.csv", encoding="utf-8-sig"
    )
    pd.DataFrame(normalized, index=LABELS, columns=LABELS).to_csv(
        OUTPUT_DIR / "confusion_matrix_normalized.csv", encoding="utf-8-sig"
    )
    errors.to_csv(OUTPUT_DIR / "all_final_test_errors.csv", index=False, encoding="utf-8-sig")
    examples.to_csv(OUTPUT_DIR / "error_examples_15.csv", index=False, encoding="utf-8-sig")
    cv_mean = float(audit["revised_cv_mean"])
    snapshot = {
        "schema_version": 2,
        "policy": "Preprocessing revision selected on Development CV; previously used Final Test reused for transparent comparison",
        "model": "Logistic Regression C=1.0 + SMOTE, revised preprocessing",
        "labels": list(LABELS),
        "metrics": summary,
        "cv_macro_f1": cv_mean,
        "cv_to_final_gap": float(summary["macro_f1"] - cv_mean),
        "model_sha256": sha256_file(model_path),
        "vectorizer_sha256": sha256_file(MODEL_DIR / "text_tfidf_vectorizer.joblib"),
        "split_sha256": sha256_file(split_path),
        "baseline_snapshot": "reports/evaluation/final_test_snapshot.json",
    }
    (OUTPUT_DIR / "final_test_snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    baseline = json.loads(
        (ROOT / "reports/evaluation/final_test_snapshot.json").read_text(encoding="utf-8")
    )
    negative = per_class.loc[per_class["Label"] == "Negative"].iloc[0]
    report = f"""# Đánh giá bản tiền xử lý sửa lỗi

Bản này giữ nguyên chỉ số hàng Development/Final Test từ phiên bản gốc. TF-IDF được fit lại trên Development; Logistic Regression (`C=1.0`) + SMOTE được train lại. Chọn bản sửa dựa trên Stratified 5-Fold CV: Macro F1 **{audit['original_cv_mean']:.4f} → {cv_mean:.4f}**. Lần so sánh này fit TF-IDF riêng trong từng fold ở cả hai cấu hình.

Final Test 1.683 mẫu đã được nhóm sử dụng ở bản gốc; con số bên dưới là **đánh giá lại để so sánh sau sửa lỗi**, không phải phép kiểm thử độc lập mới. Không dùng nó để chọn quy tắc tiền xử lý.

| Chỉ số | Bản gốc | Bản sửa |
| --- | ---: | ---: |
| Accuracy | {baseline['metrics']['accuracy']:.4f} | {summary['accuracy']:.4f} |
| Macro F1 | {baseline['metrics']['macro_f1']:.4f} | {summary['macro_f1']:.4f} |
| Số lỗi | {baseline['metrics']['error_count']} | {summary['error_count']} |
| Recall Negative | 0.4474 | {negative['Recall']:.4f} |

Ma trận nhầm lẫn (hàng = nhãn thật, cột = nhãn đoán; thứ tự Negative, Neutral, Positive):

```text
{matrix.tolist()}
```

Trong app, 15 lỗi minh họa của bản sửa được nhóm theo heuristic và **chưa được đọc, gán nguyên nhân thủ công**. Nhãn huấn luyện vẫn suy từ rating toàn review nên các câu ngắn hoặc vừa khen vừa chê còn có thể sai.
"""
    (ROOT / "reports" / "retrained_v2_evaluation.md").write_text(report, encoding="utf-8")
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
