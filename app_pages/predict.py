from html import escape
import time

import altair as alt
import pandas as pd
import streamlit as st

from src.app_services import analyze_review, load_json
from src.app_theme import SENTIMENT_COLORS, page_header, section_label, style_chart
from src.tv4_analysis import InsufficientSignalError


page_header(
    "Interactive inference",
    "Nhận diện cảm xúc từ review",
    "Nhập nội dung, chạy model và xem những tín hiệu đứng sau dự đoán.",
    [":blue-badge[TF-IDF + Logistic Regression]", ":gray-badge[3 lớp cảm xúc]"],
)

examples = {
    "Tích cực": "Môi trường làm việc chuyên nghiệp, đồng nghiệp hỗ trợ và có nhiều cơ hội học hỏi.",
    "Trung tính": "Công việc ổn, quy trình bình thường và chưa có điều gì quá nổi bật.",
    "Tiêu cực": "Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương.",
    "Nhiều vế": "Môi trường tốt nhưng lương thấp và quản lý chưa thật sự quan tâm nhân viên.",
}
st.session_state.setdefault("predict_example", "Nhiều vế")
st.session_state.setdefault("prediction_text", examples[st.session_state.predict_example])
st.session_state.setdefault("ml_prediction", None)
st.session_state.setdefault("ml_prediction_error", None)
st.session_state.setdefault("ml_prediction_warning", None)
current_model_sha = load_json("reports/evaluation/retrained_v2/final_test_snapshot.json")["model_sha256"]
if st.session_state.get("ml_prediction_model_sha") != current_model_sha:
    st.session_state.ml_prediction = None
    st.session_state.ml_prediction_error = None
    st.session_state.ml_prediction_warning = None
    st.session_state.ml_prediction_model_sha = current_model_sha


def sync_example_text() -> None:
    chosen = st.session_state.get("predict_example")
    if chosen in examples:
        st.session_state.prediction_text = examples[chosen]
        st.session_state.ml_prediction = None
        st.session_state.ml_prediction_error = None
        st.session_state.ml_prediction_warning = None


section_label("Phòng thử nghiệm")
input_col, output_col = st.columns([1.05, 1], gap="medium")
with input_col:
    with st.container(border=True, key="predict_form", height="stretch"):
        st.subheader("Nội dung review", icon=":material/edit_note:")
        st.segmented_control(
            "Thử một tình huống", list(examples), key="predict_example", required=True,
            on_change=sync_example_text, persist_state="session",
        )
        with st.form("prediction_form", border=False):
            review = st.text_area(
                "Review cần phân tích", height=180, max_chars=3000,
                placeholder="Nhập cảm nhận về môi trường, lương thưởng, quản lý, OT…",
                key="prediction_text", persist_state="session", label_visibility="collapsed",
            )
            submitted = st.form_submit_button(
                "Phân tích cảm xúc", icon=":material/auto_awesome:", type="primary", width="stretch",
            )
        st.caption("Chọn mẫu hoặc nhập câu của bạn. Nhãn dự đoán có thể khác nhãn của tình huống mẫu.")
        if submitted:
            try:
                started = time.perf_counter()
                with st.spinner("Đang phân tích review…", show_time=True):
                    result = analyze_review(review)
                st.session_state.ml_prediction = {
                    "result": result,
                    "text": review,
                    "latency_ms": (time.perf_counter() - started) * 1000,
                }
                st.session_state.ml_prediction_model_sha = current_model_sha
                st.session_state.ml_prediction_error = None
                st.session_state.ml_prediction_warning = None
            except InsufficientSignalError as error:
                st.session_state.ml_prediction = None
                st.session_state.ml_prediction_error = None
                st.session_state.ml_prediction_warning = str(error)
            except Exception as error:
                st.session_state.ml_prediction = None
                st.session_state.ml_prediction_error = str(error)
                st.session_state.ml_prediction_warning = None
        if st.session_state.ml_prediction_warning:
            st.warning(st.session_state.ml_prediction_warning, icon=":material/warning:")
        if st.session_state.ml_prediction_error:
            st.error(st.session_state.ml_prediction_error, icon=":material/error:")

prediction = st.session_state.ml_prediction
with output_col:
    with st.container(border=True, key="probability_panel", height="stretch"):
        st.subheader("Kết quả phân tích", icon=":material/psychology:")
        if prediction is None:
            st.html(
                '<div class="ml-empty-result"><div class="ml-empty-symbol">[ … ]</div>'
                '<h3>Review của bạn mang cảm xúc gì?</h3>'
                '<p>Chạy phân tích để xem nhãn cảm xúc và xác suất của cả ba lớp.</p></div>'
            )
        else:
            result = prediction["result"]
            label = result["label"]
            confidence = result["probabilities"][label]
            st.html(
                f'<div class="ml-result" style="--result-color:{SENTIMENT_COLORS[label]}">'
                '<div class="ml-result-label">CẢM XÚC DỰ ĐOÁN</div>'
                f'<div class="ml-result-value">{escape(label)}</div>'
                f'<div class="ml-result-sub">Xác suất của lớp được chọn · {confidence:.1%}</div></div>'
            )
            probabilities = pd.DataFrame([
                {"Sentiment": key, "Probability": value}
                for key, value in result["probabilities"].items()
            ])
            base = alt.Chart(probabilities).encode(
                y=alt.Y("Sentiment:N", sort=["Positive", "Neutral", "Negative"], title=None),
                x=alt.X("Probability:Q", scale=alt.Scale(domain=[0, 1.16]), axis=alt.Axis(values=[0, .25, .5, .75, 1], format="%"), title=None),
                tooltip=["Sentiment", alt.Tooltip("Probability:Q", format=".1%")],
            )
            bars = base.mark_bar(cornerRadiusEnd=5, height=18).encode(
                color=alt.Color("Sentiment:N", scale=alt.Scale(domain=list(SENTIMENT_COLORS), range=list(SENTIMENT_COLORS.values())), legend=None),
            )
            values = base.mark_text(align="left", dx=8, color="#dce5f2", font="JetBrains Mono", fontSize=12).encode(text=alt.Text("Probability:Q", format=".1%"))
            st.altair_chart(style_chart((bars + values).properties(height=132)), width="stretch")
            st.caption("Xác suất model chưa phải độ chính xác được bảo đảm cho từng review.")
            if len(result["clean_text"].split()) <= 2:
                st.warning("Review quá ngắn để có đủ ngữ cảnh. Hãy viết thêm chi tiết trước khi dùng kết quả.", icon=":material/warning:")

if prediction is not None:
    result = prediction["result"]
    with st.container(horizontal=True, key="predict_metrics"):
        st.metric("Đặc trưng kích hoạt", f"{result['active_feature_count']:,}", border=True)
        with st.container(key="kpi_speed"):
            st.metric("Thời gian xử lý", f"{prediction['latency_ms']:.0f} ms", border=True)
        st.metric("Số lớp cảm xúc", "3", border=True)

    section_label("Tín hiệu trong văn bản")
    text_col, token_col = st.columns([1.05, 1], gap="medium")
    with text_col:
        with st.container(border=True, key="pipeline_trace", height="stretch"):
            st.subheader("Từ review đến vector", icon=":material/account_tree:")
            st.caption("REVIEW ĐÃ PHÂN TÍCH")
            st.write(prediction["text"])
            st.caption("SAU CHUẨN HÓA & TÁCH TỪ")
            st.code(result["clean_text"], language=None, wrap_lines=True)
            st.caption("Văn bản → chuẩn hóa → TF-IDF → Logistic Regression → xác suất")
    with token_col:
        with st.container(border=True, key="token_panel", height="stretch"):
            st.subheader("Token TF-IDF nổi bật", icon=":material/token:")
            tokens = pd.DataFrame(result["top_tokens"])
            if tokens.empty:
                st.warning("Không có từ nào khớp từ vựng đã học. Dự đoán này thiếu tín hiệu từ nội dung.")
            else:
                st.dataframe(
                    tokens, hide_index=True, width="stretch",
                    height=min(360, 38 + 32 * len(tokens)),
                    column_config={
                        "token": st.column_config.TextColumn("Từ / cụm từ", width="medium"),
                        "tfidf": st.column_config.ProgressColumn("Trọng số TF-IDF", min_value=0, max_value=max(tokens["tfidf"].max(), .01), format="%.3f"),
                    },
                )
            st.caption("Trọng số phản ánh độ nổi bật của token; không thể hiện chiều tác động lên nhãn.")
