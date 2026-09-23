import altair as alt
import streamlit as st

from src.app_services import load_csv, load_json
from src.app_theme import page_header, section_label, style_chart


page_header(
    "Model selection",
    "Benchmark mô hình",
    "Xếp hạng năm thuật toán ban đầu và kết quả của Logistic Regression sau khi sửa tiền xử lý.",
    [":blue-badge[Stratified 5-Fold CV]", ":green-badge[Revised model]", ":gray-badge[Macro F1 ranking]"],
)

ranking = load_csv("reports/evaluation/model_ranking_cv.csv")
snapshot = load_json("reports/evaluation/retrained_v2/final_test_snapshot.json")
baseline = load_json("reports/evaluation/final_test_snapshot.json")

section_label("Mô hình được chọn")
with st.container(horizontal=True, key="overview_metrics"):
    with st.container(key="benchmark_winner"):
        st.metric("Model được chọn", "Logistic Regression", border=True)
    st.metric("CV Macro F1", f"{snapshot['cv_macro_f1']:.4f}", border=True)
    with st.container(key="kpi_positive"):
        st.metric("Final Macro F1", f"{snapshot['metrics']['macro_f1']:.4f}", border=True)
    st.metric("Generalization gap", f"{snapshot['cv_to_final_gap']:+.4f}", help="Final Test − CV", border=True)

section_label("Xếp hạng cross-validation trên tiền xử lý gốc")
chart_frame = ranking.sort_values("CV Macro F1 Mean").copy()
chart_frame["Selected"] = chart_frame["Rank"].eq(1)
chart_frame["Low"] = chart_frame["CV Macro F1 Mean"] - chart_frame["CV Macro F1 Std"]
chart_frame["High"] = chart_frame["CV Macro F1 Mean"] + chart_frame["CV Macro F1 Std"]
base = alt.Chart(chart_frame).encode(
    y=alt.Y("Model:N", sort=alt.SortField("CV Macro F1 Mean", order="descending"), title=None, axis=alt.Axis(labelLimit=220)),
    tooltip=["Rank", "Model", alt.Tooltip("CV Macro F1 Mean:Q", format=".4f"), alt.Tooltip("CV Macro F1 Std:Q", format=".4f"), "Strategy"],
)
bars = base.mark_point(filled=True, size=140).encode(
    x=alt.X("CV Macro F1 Mean:Q", scale=alt.Scale(domain=[0.51, 0.62], zero=False), title="Macro F1 · trung bình và ±1 độ lệch chuẩn"),
    color=alt.condition("datum.Selected", alt.value("#50e3a4"), alt.value("#7aa7ff")),
)
intervals = base.mark_rule(strokeWidth=3, opacity=.55, color="#7aa7ff").encode(x="Low:Q", x2="High:Q")
labels = base.mark_text(align="left", dx=10, color="#dce5f2", font="JetBrains Mono", fontSize=12).encode(
    x="High:Q", text=alt.Text("CV Macro F1 Mean:Q", format=".4f")
)
with st.container(border=True, key="benchmark_chart"):
    st.subheader("Khoảng cách rất sít sao", icon=":material/leaderboard:")
    st.caption("Chấm tròn là điểm trung bình; đường ngang thể hiện biến động qua 5 folds. Chênh lệch nhỏ chưa chứng minh ưu thế thống kê.")
    st.altair_chart(style_chart((intervals + bars + labels).properties(height=250)), width="stretch")

with st.container(border=True, key="benchmark_table"):
    st.subheader("Nhật ký thực nghiệm", icon=":material/table_chart:")
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

st.info(
    f"Bảng 5 model thuộc lần thử ban đầu (Logistic Regression: {baseline['cv_macro_f1']:.4f}). "
    f"Sau khi sửa tiền xử lý, Logistic Regression đạt {snapshot['cv_macro_f1']:.4f} qua 5-fold CV và là model app đang dùng. "
    "Chưa xếp hạng lại bốn model còn lại trên bộ đặc trưng mới.",
    icon=":material/info:",
)
st.caption("Refit Time là một lần fit cấu hình đã chọn trên toàn Development set tại máy local; không phải tổng thời gian GridSearchCV.")
