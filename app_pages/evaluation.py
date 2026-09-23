from html import escape

import altair as alt
import pandas as pd
import streamlit as st

from src.app_services import load_csv, load_json
from src.app_theme import SENTIMENT_COLORS, page_header, section_label, style_chart


page_header(
    "Final test laboratory",
    "Đánh giá & phân tích lỗi",
    "Kết quả bản sửa trên Final Test đã dùng trước đó, cùng các mẫu dự đoán sai để đọc trực tiếp.",
    [":green-badge[Revised preprocessing]", ":blue-badge[1,683 samples]", ":orange-badge[432 errors]", ":red-badge[Negative recall 45.6%]"],
)

snapshot = load_json("reports/evaluation/retrained_v2/final_test_snapshot.json")
per_class = load_csv("reports/evaluation/retrained_v2/final_test_per_class.csv")
matrix = load_csv("reports/evaluation/retrained_v2/confusion_matrix.csv").rename(columns={"Unnamed: 0": "Actual"})
errors = load_csv("reports/evaluation/retrained_v2/error_examples_15.csv")
metrics = snapshot["metrics"]

section_label("Kết quả trên tập kiểm thử độc lập")
with st.container(horizontal=True, key="eval_metrics"):
    st.metric("Accuracy", f"{metrics['accuracy']:.2%}", border=True)
    st.metric("Macro F1", f"{metrics['macro_f1']:.4f}", border=True)
    with st.container(key="kpi_positive"):
        st.metric("Weighted F1", f"{metrics['weighted_f1']:.4f}", border=True)
    with st.container(key="kpi_error"):
        st.metric("Error rate", f"{metrics['error_count'] / metrics['test_count']:.2%}", delta=f"{metrics['error_count']} mẫu", delta_color="off", border=True)

matrix_long = matrix.melt(id_vars="Actual", var_name="Predicted", value_name="Count")
matrix_long["Share"] = matrix_long.groupby("Actual")["Count"].transform(lambda values: values / values.sum())
heatmap = (
    alt.Chart(matrix_long)
    .mark_rect(cornerRadius=5, stroke="#080b10", strokeWidth=3)
    .encode(
        x=alt.X("Predicted:N", sort=["Negative", "Neutral", "Positive"], title="Nhãn dự đoán", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Actual:N", sort=["Negative", "Neutral", "Positive"], title="Nhãn thật"),
        color=alt.Color("Share:Q", scale=alt.Scale(domain=[0, 1], range=["#17202d", "#7aa7ff"]), legend=None),
        tooltip=["Actual", "Predicted", alt.Tooltip("Count:Q", format=","), alt.Tooltip("Share:Q", format=".1%")],
    )
)
heat_text = heatmap.mark_text(font="JetBrains Mono", fontSize=15, fontWeight=600).encode(
    text="Count:Q", color=alt.condition("datum.Share > 0.7", alt.value("#08101d"), alt.value("#f1f5f9"))
)

left, right = st.columns([1.12, 1], gap="large")
with left:
    with st.container(border=True, key="eval_matrix", height="stretch"):
        st.subheader("Confusion Matrix", icon=":material/grid_on:")
        st.caption("HÀNG = NHÃN THẬT · CỘT = NHÃN DỰ ĐOÁN")
        st.altair_chart(style_chart((heatmap + heat_text).properties(height=290)), width="stretch")
        st.caption("Số trong ô = số review. Độ sáng = tỷ lệ trong từng hàng; đường chéo là dự đoán đúng.")
with right:
    with st.container(border=True, key="eval_class", height="stretch"):
        st.subheader("Chất lượng theo lớp", icon=":material/equalizer:")
        class_long = per_class.melt(id_vars=["Label", "Support"], value_vars=["Precision", "Recall", "F1"], var_name="Metric", value_name="Score")
        class_chart = (
            alt.Chart(class_long)
            .mark_bar(cornerRadiusEnd=5)
            .encode(
                x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 1]), title=None),
                y=alt.Y("Metric:N", title=None),
                row=alt.Row("Label:N", sort=["Positive", "Neutral", "Negative"], title=None, header=alt.Header(labelColor="#cbd5e1", labelFontSize=12)),
                color=alt.Color("Label:N", scale=alt.Scale(domain=list(SENTIMENT_COLORS), range=list(SENTIMENT_COLORS.values())), legend=None),
                tooltip=["Label", "Metric", alt.Tooltip("Score:Q", format=".1%"), "Support"],
            )
            .properties(height=72)
        )
        st.altair_chart(style_chart(class_chart), width="stretch")
        negative = per_class.loc[per_class["Label"] == "Negative"].iloc[0]
        st.warning(f"Negative là lớp khó nhất: Recall {negative['Recall']:.1%}, F1 {negative['F1']:.4f}.", icon=":material/warning:")

section_label("Khám phá 15 lỗi minh họa")
with st.container(border=True, key="error_filters"):
    filters = st.columns([1, 1, 1.35], gap="medium")
    with filters[0]:
        actual = st.selectbox("Nhãn thật", ["Tất cả", *sorted(errors["actual"].unique())], key="eval_actual")
    with filters[1]:
        reason = st.selectbox("Dạng lỗi gợi ý", ["Tất cả", *sorted(errors["error_reason"].unique())], key="eval_reason")

    filtered = errors.copy()
    if actual != "Tất cả":
        filtered = filtered[filtered["actual"] == actual]
    if reason != "Tất cả":
        filtered = filtered[filtered["error_reason"] == reason]
    filtered = filtered.reset_index(drop=True)
    if st.session_state.get("eval_filter_signature") != (actual, reason):
        st.session_state.eval_sample = 0 if not filtered.empty else None
        st.session_state.eval_filter_signature = (actual, reason)
    with filters[2]:
        sample_index = st.selectbox(
            "Mẫu cần đọc",
            range(len(filtered)),
            format_func=lambda index: f"#{int(filtered.iloc[index]['source_index'])} · {filtered.iloc[index]['company']}" if len(filtered) else "Không có mẫu",
            key="eval_sample",
            disabled=filtered.empty,
        )
    st.caption(f"{len(filtered)} / {len(errors)} mẫu khớp bộ lọc · Đọc nhận xét và review gốc ngay bên dưới.")

if filtered.empty:
    st.info("Không có lỗi phù hợp với bộ lọc hiện tại.", icon=":material/search_off:")
else:
    sample = filtered.iloc[sample_index]
    badge_colors = {"Positive": "green", "Neutral": "orange", "Negative": "red"}
    with st.container(border=True, key="error_detail"):
        top, score = st.columns([1.45, .55], gap="large")
        with top:
            st.caption(f"{sample['company']} · {int(sample['rating'])} SAO · SOURCE #{int(sample['source_index'])}")
            st.subheader(str(sample["error_reason"]), icon=":material/troubleshoot:")
            st.write("Đây là nhóm lỗi được gợi ý tự động. Đọc review bên dưới để xem vì sao nhãn thật và dự đoán khác nhau.")
        with score:
            st.metric("Confidence", f"{sample['confidence']:.1%}", border=True)
        with st.container(horizontal=True):
            st.badge(f"Actual · {sample['actual']}", color=badge_colors[str(sample["actual"])])
            st.badge(f"Predicted · {sample['predicted']}", color=badge_colors[str(sample["predicted"])])
        st.html(f'<div class="ml-review-quote">{escape(str(sample["review"])).replace(chr(10), "<br>")}</div>')
        probability = pd.DataFrame({"Sentiment": ["Negative", "Neutral", "Positive"], "Probability": [sample["p_negative"], sample["p_neutral"], sample["p_positive"]]})
        probability_chart = alt.Chart(probability).mark_bar(cornerRadiusEnd=5, height=13).encode(
            x=alt.X("Probability:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", tickCount=5), title=None),
            y=alt.Y("Sentiment:N", sort=["Positive", "Neutral", "Negative"], title=None),
            color=alt.Color("Sentiment:N", scale=alt.Scale(domain=list(SENTIMENT_COLORS), range=list(SENTIMENT_COLORS.values())), legend=None),
            tooltip=["Sentiment", alt.Tooltip("Probability:Q", format=".1%")],
        ).properties(height=105)
        st.altair_chart(style_chart(probability_chart), width="stretch")

st.caption("15 lỗi minh họa được chọn từ 432 lỗi của bản sửa. Nhóm nguyên nhân là gợi ý tự động, chưa được gán nhãn thủ công.")
