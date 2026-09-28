from html import escape

import altair as alt
import pandas as pd
import streamlit as st

from src.app_services import load_csv, load_json
from src.app_theme import SENTIMENT_COLORS, page_header, section_label, style_chart


page_header(
    "Model performance",
    "Mô hình & đánh giá",
    "Từ so sánh mô hình đến kết quả kiểm thử và những trường hợp dự đoán sai.",
    [":blue-badge[5-fold CV]", ":green-badge[Logistic Regression]", ":orange-badge[Final Test]"],
)

ranking = load_csv("reports/evaluation/model_ranking_cv.csv")
snapshot = load_json("reports/evaluation/retrained_v2/final_test_snapshot.json")
baseline = load_json("reports/evaluation/final_test_snapshot.json")
per_class = load_csv("reports/evaluation/retrained_v2/final_test_per_class.csv")
matrix = load_csv("reports/evaluation/retrained_v2/confusion_matrix.csv").rename(columns={"Unnamed: 0": "Actual"})
errors = load_csv("reports/evaluation/retrained_v2/error_examples_15.csv")
ablation = load_json("reports/evaluation/metric_selection_ablation.json")
imbalance_ablation = load_json("reports/evaluation/model_imbalance_ablation.json")
metrics = snapshot["metrics"]
negative = per_class.loc[per_class["Label"] == "Negative"].iloc[0]

section_label("01 / So sánh mô hình")
with st.container(horizontal=True, key="model_summary"):
    st.metric("Model được chọn", "Logistic Regression", border=True)
    st.metric("CV Macro F1 · bản sửa", f"{snapshot['cv_macro_f1']:.4f}", border=True)
    st.metric("Final Macro F1", f"{metrics['macro_f1']:.4f}", border=True)

chart_frame = ranking.sort_values("CV Macro F1 Mean").copy()
chart_frame["Selected"] = chart_frame["Rank"].eq(1)
chart_frame["Low"] = chart_frame["CV Macro F1 Mean"] - chart_frame["CV Macro F1 Std"]
chart_frame["High"] = chart_frame["CV Macro F1 Mean"] + chart_frame["CV Macro F1 Std"]
ranking_base = alt.Chart(chart_frame).encode(
    y=alt.Y("Model:N", sort=alt.SortField("CV Macro F1 Mean", order="descending"), title=None, axis=alt.Axis(labelLimit=220)),
    tooltip=["Rank", "Model", alt.Tooltip("CV Macro F1 Mean:Q", format=".4f"), alt.Tooltip("CV Macro F1 Std:Q", format=".4f"), "Strategy"],
)
ranking_points = ranking_base.mark_point(filled=True, size=140).encode(
    x=alt.X("CV Macro F1 Mean:Q", scale=alt.Scale(domain=[0.51, 0.62], zero=False), title="Macro F1 · trung bình và ±1 độ lệch chuẩn"),
    color=alt.condition("datum.Selected", alt.value("#50e3a4"), alt.value("#7aa7ff")),
)
ranking_intervals = ranking_base.mark_rule(strokeWidth=3, opacity=.55, color="#7aa7ff").encode(x="Low:Q", x2="High:Q")
ranking_labels = ranking_base.mark_text(align="left", dx=10, color="#dce5f2", font="JetBrains Mono", fontSize=12).encode(
    x="High:Q", text=alt.Text("CV Macro F1 Mean:Q", format=".4f")
)
with st.container(border=True, key="benchmark_chart"):
    st.subheader("So sánh 5 mô hình ban đầu", icon=":material/leaderboard:")
    st.caption("Chấm tròn là điểm trung bình; đường ngang thể hiện biến động qua 5 folds. Chênh lệch nhỏ chưa chứng minh ưu thế thống kê.")
    st.altair_chart(style_chart((ranking_intervals + ranking_points + ranking_labels).properties(height=250)), width="stretch")

with st.expander("Xem bảng kết quả 5 mô hình"):
    st.dataframe(
        ranking,
        column_order=["Rank", "Model", "CV Macro F1 Mean", "CV Macro F1 Std", "Strategy", "Refit Time (s)"],
        hide_index=True,
        width="stretch",
        column_config={
            "Rank": st.column_config.NumberColumn("#", width="small"),
            "CV Macro F1 Mean": st.column_config.NumberColumn("Macro F1", format="%.4f"),
            "CV Macro F1 Std": st.column_config.NumberColumn("Std", format="%.4f"),
            "Refit Time (s)": st.column_config.NumberColumn("Refit", format="%.3f s"),
        },
    )
    st.caption("Refit Time là một lần fit cấu hình đã chọn trên toàn Development set; không phải tổng thời gian GridSearchCV.")

st.info(
    f"Biểu đồ là lần so sánh ban đầu (Logistic Regression: {baseline['cv_macro_f1']:.4f}). "
    f"Sau khi sửa tiền xử lý, model này đạt {snapshot['cv_macro_f1']:.4f} qua 5-fold CV. "
    "Bảng xếp hạng phía trên là GridSearchCV ban đầu; phép thử tham số cố định với tiền xử lý mới được trình bày bên dưới.",
    icon=":material/info:",
)

experiments = pd.DataFrame(ablation["configurations"])
accuracy_pick = experiments.loc[experiments["cv_accuracy_mean"].idxmax()]
f1_pick = experiments.loc[experiments["cv_macro_f1_mean"].idxmax()]
with st.container(border=True, key="metric_selection_experiment"):
    st.subheader("Chọn cấu hình bằng Accuracy hay Macro F1?", icon=":material/experiment:")
    st.caption("Cùng 6.731 review Development, cùng 5 fold và Logistic Regression C=1.0. Mỗi cấu hình được chấm bằng cả hai thước đo; Final Test không tham gia chọn.")
    left_pick, right_pick = st.columns(2, gap="medium")
    with left_pick:
        st.markdown("**Nếu chọn theo Accuracy**")
        st.metric("CV Accuracy", f"{accuracy_pick['cv_accuracy_mean']:.4f}", border=True)
        st.caption(f"{accuracy_pick['ngram']} · {accuracy_pick['strategy']} · Macro F1 {accuracy_pick['cv_macro_f1_mean']:.4f}")
    with right_pick:
        st.markdown("**Nếu chọn theo Macro F1**")
        st.metric("CV Macro F1", f"{f1_pick['cv_macro_f1_mean']:.4f}", border=True)
        st.caption(f"{f1_pick['ngram']} · {f1_pick['strategy']} · Accuracy {f1_pick['cv_accuracy_mean']:.4f}")
    smote_reference = experiments.loc[(experiments["ngram"] == "Unigram + Bigram") & (experiments["strategy"] == "SMOTE")].iloc[0]
    st.write(
        f"Accuracy ưu tiên {accuracy_pick['strategy'].lower()}; Macro F1 ưu tiên {f1_pick['strategy'].lower()}. "
        f"Macro F1 của cấu hình này ({f1_pick['cv_macro_f1_mean']:.4f}) và SMOTE ({smote_reference['cv_macro_f1_mean']:.4f}) "
        "rất sát nhau, nên chưa thể khẳng định một cách xử lý luôn tốt hơn."
    )
    ngram_chart = alt.Chart(experiments).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("ngram:N", title="Đặc trưng", sort=["Unigram", "Bigram", "Unigram + Bigram"]),
        y=alt.Y("cv_macro_f1_mean:Q", title="CV Macro F1", scale=alt.Scale(domain=[0, 0.65])),
        color=alt.Color("strategy:N", title="Xử lý mất cân bằng"),
        xOffset="strategy:N",
        tooltip=["ngram:N", "strategy:N", alt.Tooltip("cv_accuracy_mean:Q", format=".4f"), alt.Tooltip("cv_macro_f1_mean:Q", format=".4f")],
    ).properties(height=235)
    st.altair_chart(style_chart(ngram_chart), width="stretch")
    with st.expander("Xem đủ 9 cấu hình thực nghiệm"):
        display = experiments[["ngram", "strategy", "cv_accuracy_mean", "cv_macro_f1_mean"]].rename(columns={
            "ngram": "Đặc trưng", "strategy": "Cân bằng lớp", "cv_accuracy_mean": "CV Accuracy", "cv_macro_f1_mean": "CV Macro F1"
        })
        st.dataframe(display, hide_index=True, width="stretch", column_config={
            "CV Accuracy": st.column_config.NumberColumn(format="%.4f"),
            "CV Macro F1": st.column_config.NumberColumn(format="%.4f"),
        })
    baseline_no_text = ablation["no_text_baseline"]
    st.caption(
        f"Mốc không dùng đặc trưng văn bản: luôn đoán lớp đông nhất, "
        f"CV Accuracy {baseline_no_text['cv_accuracy_mean']:.4f}, "
        f"CV Macro F1 {baseline_no_text['cv_macro_f1_mean']:.4f}."
    )
    st.caption("Thí nghiệm bổ sung chỉ dùng Development CV. Model đang chạy trong demo vẫn là Logistic Regression + SMOTE với unigram + bigram; kết quả Final Test trên trang thuộc model đó.")

with st.container(border=True, key="imbalance_by_model"):
    st.subheader("Class weight ảnh hưởng đến từng mô hình thế nào?", icon=":material/balance:")
    st.caption("Cùng văn bản sau tiền xử lý, TF-IDF unigram + bigram và 5 fold Development; mỗi model được chấm với không xử lý, class weight và SMOTE.")
    by_model = pd.DataFrame(imbalance_ablation["rows"])
    measured = by_model.loc[by_model["status"] == "measured"].copy()
    chart = alt.Chart(measured).mark_bar(cornerRadiusEnd=4).encode(
        y=alt.Y("model:N", title=None, sort=["Logistic Regression", "Linear SVM", "Random Forest", "Multinomial Naive Bayes", "Stacking Ensemble"]),
        x=alt.X("cv_macro_f1_mean:Q", title="CV Macro F1", scale=alt.Scale(domain=[0, 0.7])),
        color=alt.Color("strategy:N", title="Xử lý mất cân bằng"),
        yOffset="strategy:N",
        tooltip=["model:N", "strategy:N", alt.Tooltip("cv_accuracy_mean:Q", format=".4f"), alt.Tooltip("cv_macro_f1_mean:Q", format=".4f")],
    ).properties(height=290)
    st.altair_chart(style_chart(chart), width="stretch")
    with st.expander("Xem điểm của từng model"):
        table = by_model[["model", "strategy", "cv_accuracy_mean", "cv_macro_f1_mean", "status"]].rename(columns={
            "model": "Mô hình", "strategy": "Cách xử lý", "cv_accuracy_mean": "CV Accuracy",
            "cv_macro_f1_mean": "CV Macro F1", "status": "Trạng thái",
        })
        st.dataframe(table, hide_index=True, width="stretch", column_config={
            "CV Accuracy": st.column_config.NumberColumn(format="%.4f"),
            "CV Macro F1": st.column_config.NumberColumn(format="%.4f"),
        })
    st.caption("Naive Bayes không có tham số class_weight. Trong Stacking, class weight áp dụng cho LR, SVM, RF và meta LR; NB giữ nguyên. Bảng này dùng tham số cố định nên không phải bảng GridSearchCV ban đầu.")

section_label("02 / Chất lượng trên Final Test")
with st.container(horizontal=True, key="eval_metrics"):
    st.metric("Accuracy", f"{metrics['accuracy']:.2%}", border=True)
    st.metric("Recall Tiêu cực", f"{negative['Recall']:.1%}", border=True)
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
        st.warning(f"Negative là lớp khó nhất: Recall {negative['Recall']:.1%}, F1 {negative['F1']:.4f}.", icon=":material/warning:")

section_label("03 / Khám phá 15 lỗi minh họa")
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
