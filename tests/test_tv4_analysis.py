import numpy as np

from src.tv4_analysis import (
    add_manual_error_review,
    build_cv_ranking,
    classify_error_reason,
    evaluate_predictions,
    load_inference_bundle,
    predict_review,
    summarize_metrics,
)


def test_cv_ranking_is_frozen_and_sorted():
    ranking = build_cv_ranking()
    assert ranking.iloc[0]["Model"] == "Logistic Regression"
    assert ranking["CV Macro F1 Mean"].is_monotonic_decreasing
    assert len(ranking) == 5


def test_evaluation_uses_fixed_label_order():
    actual = ["Negative", "Neutral", "Positive", "Positive"]
    predicted = ["Neutral", "Neutral", "Positive", "Negative"]
    per_class, matrix, normalized = evaluate_predictions(actual, predicted)
    assert per_class["Label"].tolist() == ["Negative", "Neutral", "Positive"]
    assert matrix.shape == (3, 3)
    assert np.allclose(normalized.sum(axis=1), 1.0)
    assert summarize_metrics(actual, predicted)["error_count"] == 2


def test_error_reason_detects_mixed_review():
    reason = classify_error_reason("Môi trường tốt nhưng lương thấp", "Negative", "Positive")
    assert reason == "Mixed sentiment / nhiều vế ý"


def test_manual_review_notes_are_attached():
    import pandas as pd

    reviewed = add_manual_error_review(pd.DataFrame({"source_index": [4736]}))
    assert reviewed.iloc[0]["manual_category"] == "Label noise"
    assert "rating 3" in reviewed.iloc[0]["manual_analysis"]


def test_load_inference_bundle_and_predict_review():
    from pathlib import Path
    import pytest

    bundle = load_inference_bundle(Path(__file__).resolve().parents[1])
    assert bundle["feature_count"] == 5000
    assert bundle["classes"] == ("Negative", "Neutral", "Positive")

    result = predict_review(bundle, "Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương.")
    assert result["label"] in ("Negative", "Neutral", "Positive")
    assert sum(result["probabilities"].values()) == pytest.approx(1.0, rel=1e-3)
    assert result["active_feature_count"] > 0
    assert len(result["top_tokens"]) > 0

    with pytest.raises(ValueError, match="không có từ nào trong từ vựng"):
        predict_review(bundle, "abcdef xyzq")


def test_retrained_demo_preserves_sentiment_terms():
    from pathlib import Path
    import pytest

    bundle = load_inference_bundle(
        Path(__file__).resolve().parents[1], model_dir="models/retrained_v2"
    )
    result = predict_review(bundle, "Công ty lương thấp, họp nhiều.")
    assert result["clean_text"] == "công_ty lương thấp họp nhiều"
    assert result["label"] == "Negative"

    with pytest.raises(ValueError, match="chỉ còn một đặc trưng"):
        predict_review(bundle, "công_ty rắn độc")
