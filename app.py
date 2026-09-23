from pathlib import Path

import streamlit as st

from src.app_theme import apply_app_style
from src.app_services import load_json, start_inference_loading


ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Sentiment ML Lab",
    page_icon=":material/psychology:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Đồ án Machine Learning phân tích cảm xúc review ITviec."},
)

st.logo(
    ROOT / "assets" / "sentiment-ml-logo.svg",
    size="large",
    icon_image=ROOT / "assets" / "sentiment-ml-mark.svg",
)

apply_app_style()

pages = {
    "Khám phá": [
        st.Page("app_pages/overview.py", title="Tổng quan", icon=":material/home:", default=True),
        st.Page("app_pages/insights.py", title="Insight doanh nghiệp", icon=":material/domain:"),
    ],
    "Mô hình": [
        st.Page("app_pages/benchmark.py", title="Benchmark", icon=":material/leaderboard:"),
        st.Page("app_pages/evaluation.py", title="Đánh giá & lỗi", icon=":material/analytics:"),
        st.Page("app_pages/predict.py", title="Phân tích review", icon=":material/psychology:"),
    ],
}

with st.sidebar:
    with st.container(border=True, key="sidebar_status"):
        st.caption("MÔ HÌNH TRIỂN KHAI")
        artifacts_present = all((ROOT / "models" / "retrained_v2" / name).is_file() for name in ("best_sentiment_model.joblib", "text_tfidf_vectorizer.joblib"))
        st.badge("Đã có model & TF-IDF" if artifacts_present else "Thiếu model hoặc TF-IDF", color="green" if artifacts_present else "orange")
        snapshot = load_json("reports/evaluation/retrained_v2/final_test_snapshot.json")
        st.metric("Final Macro F1", f"{snapshot['metrics']['macro_f1']:.4f}")
        st.caption("LOGISTIC REGRESSION · SMOTE · BẢN SỬA TIỀN XỬ LÝ")
    st.caption(f"{snapshot['metrics']['test_count']:,} mẫu Final Test đã dùng để đối chiếu hai phiên bản\n\nSentiment ML Lab · ITviec")

current_page = st.navigation(pages, position="sidebar", expanded=True)
current_page.run()
# Start the one-time tokenizer/model warm-up only after the page has rendered.
start_inference_loading()
