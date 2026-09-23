import altair as alt
import streamlit as st

from src.app_services import load_json, load_reviews
from src.app_theme import SENTIMENT_COLORS, page_header, section_label, style_chart


page_header(
    "Overview",
    "Sentiment ML Lab",
    "Biến review nhân viên thành tín hiệu cảm xúc có thể đo lường, kiểm chứng và giải thích.",
    [":blue-badge[TF-IDF 1–2 grams]", ":green-badge[Logistic Regression]", ":orange-badge[SMOTE]", ":violet-badge[3 classes]"],
)

data = load_reviews()
snapshot = load_json("reports/evaluation/retrained_v2/final_test_snapshot.json")
metrics = snapshot["metrics"]

section_label("Dữ liệu & kết quả")
with st.container(horizontal=True, key="overview_metrics"):
    with st.container(key="kpi_reviews"):
        st.metric("Reviews đã xử lý", f"{len(data):,}", help="Tổng dữ liệu sạch dùng trong đồ án", border=True)
    with st.container(key="kpi_companies"):
        st.metric("Doanh nghiệp", f"{data['Company Name'].nunique():,}", border=True)
    with st.container(key="kpi_speed"):
        st.metric("Final Test", f"{metrics['test_count']:,}", border=True)
    with st.container(key="kpi_positive"):
        st.metric("Macro F1", f"{metrics['macro_f1']:.4f}", delta=f"{snapshot['cv_to_final_gap']:+.4f} vs CV", delta_color="off", border=True)

left, right = st.columns([1.18, 1], gap="large")
with left:
    with st.container(border=True, key="overview_pipeline", height="stretch"):
        st.subheader("Từ văn bản đến dự đoán", icon=":material/account_tree:")
        st.caption("4 BƯỚC TỪ REVIEW ĐẾN CẢM XÚC")
        st.html(
            """
            <div class="ml-step"><div class="ml-step-index">01</div><div><strong>Review thô</strong><span>Unicode, emoji, teencode và tách từ tiếng Việt</span></div></div>
            <div class="ml-step"><div class="ml-step-index">02</div><div><strong>Biểu diễn TF-IDF</strong><span>Unigram + bigram, tối đa 5.000 đặc trưng</span></div></div>
            <div class="ml-step"><div class="ml-step-index">03</div><div><strong>Logistic Regression</strong><span>Mô hình đã khóa sau 5-fold cross-validation</span></div></div>
            <div class="ml-step"><div class="ml-step-index">04</div><div><strong>Kết quả có thể quan sát</strong><span>Ba xác suất cảm xúc và token TF-IDF nổi bật</span></div></div>
            """
        )
with right:
    with st.container(border=True, key="overview_metric_note", height="stretch"):
        st.subheader("Vì sao dùng Macro F1?", icon=":material/balance:")
        distribution = data["sentiment"].value_counts().rename_axis("Sentiment").reset_index(name="Reviews")
        distribution["Share"] = distribution["Reviews"] / distribution["Reviews"].sum()
        chart = (
            alt.Chart(distribution)
            .mark_bar(cornerRadiusEnd=6, height=18)
            .encode(
                x=alt.X("Share:Q", axis=alt.Axis(format="%"), title=None),
                y=alt.Y("Sentiment:N", sort=["Positive", "Neutral", "Negative"], title=None),
                color=alt.Color("Sentiment:N", scale=alt.Scale(domain=list(SENTIMENT_COLORS), range=list(SENTIMENT_COLORS.values())), legend=None),
                tooltip=["Sentiment", alt.Tooltip("Reviews:Q", format=","), alt.Tooltip("Share:Q", format=".1%")],
            )
            .properties(height=138)
        )
        st.altair_chart(style_chart(chart), width="stretch")
        positive_share = distribution.set_index("Sentiment").loc["Positive", "Share"]
        st.html(f'<div class="ml-hero-note">Positive chiếm <b>{positive_share:.1%}</b>. Macro F1 cho ba lớp trọng số ngang nhau, nên phản ánh tốt hơn năng lực trên lớp thiểu số.</div>')
        st.caption("Bản sửa được chọn bằng CV trên Development; Final Test cũ được dùng lại để đối chiếu, không phải test mới.")

section_label("Bắt đầu khám phá")
cards = st.columns(3, gap="medium")
features = [
    ("feature_insights", ":material/domain:", "Insight doanh nghiệp", "So sánh cảm xúc, điểm khía cạnh và từ khóa của 5 doanh nghiệp.", "app_pages/insights.py", "Khám phá doanh nghiệp"),
    ("feature_evaluation", ":material/analytics:", "Đánh giá mô hình", "Đọc ma trận nhầm lẫn, metric theo lớp và 15 lỗi đại diện.", "app_pages/evaluation.py", "Xem kết quả đánh giá"),
    ("feature_predict", ":material/psychology:", "Thử một review", "Nhập nội dung mới, xem xác suất và các tín hiệu TF-IDF.", "app_pages/predict.py", "Bắt đầu phân tích"),
]
for column, (key, icon, title, description, page, action) in zip(cards, features):
    with column:
        with st.container(border=True, height="stretch", key=key):
            st.markdown(f"### {icon} {title}")
            st.write(description)
            if st.button(action, icon=":material/arrow_forward:", icon_position="right", key=f"open_{key}", width="stretch"):
                st.switch_page(page)

st.caption("Dữ liệu và kết quả phục vụ mục đích học tập; nhãn sentiment được suy ra từ rating.")
