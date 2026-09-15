import altair as alt
import pandas as pd
import streamlit as st

from src.app_services import load_csv
from src.app_theme import SENTIMENT_COLORS, keyword_cloud_svg, page_header, section_label, style_chart


page_header(
    "Company intelligence",
    "Insight doanh nghiệp",
    "Một góc nhìn trực quan vào cảm xúc, trải nghiệm nhân viên và ngôn ngữ nổi bật của từng công ty.",
    [":blue-badge[5 case studies]", ":green-badge[12 WordClouds]", ":orange-badge[Descriptive insights]"],
)

distribution = load_csv("reports/company_insights/company_sentiment_distribution.csv")
aspects = load_csv("reports/company_insights/company_aspect_summary.csv")
keywords = load_csv("reports/company_insights/company_top_keywords.csv")
companies = aspects.sort_values("review_count", ascending=False)["Company Name"].tolist()

with st.container(border=True, key="insight_filter"):
    select_col, context_col = st.columns([1.1, 1], gap="medium", vertical_alignment="center")
    with select_col:
        company = st.selectbox("Doanh nghiệp", companies, key="insights_company", bind="query-params")
    with context_col:
        st.caption("5 công ty có nhiều review nhất · Nhãn cảm xúc được suy ra từ rating của người đánh giá.")

company_dist = distribution[distribution["Company Name"] == company].copy()
company_aspects = aspects[aspects["Company Name"] == company].iloc[0]
company_keywords = keywords[keywords["Company Name"] == company]
percentages = company_dist.set_index("sentiment")["percentage"].to_dict()

section_label("Bức tranh cảm xúc")
with st.container(horizontal=True, key="insight_metrics"):
    st.metric("Reviews", f"{int(company_aspects['review_count']):,}", border=True)
    with st.container(key="kpi_positive"):
        st.metric("Positive", f"{percentages.get('Positive', 0):.1f}%", border=True)
    with st.container(key="kpi_neutral"):
        st.metric("Neutral", f"{percentages.get('Neutral', 0):.1f}%", border=True)
    with st.container(key="kpi_negative"):
        st.metric("Negative", f"{percentages.get('Negative', 0):.1f}%", border=True)

left, right = st.columns([.92, 1.18], gap="large")
with left:
    with st.container(border=True, key="insight_sentiment", height="stretch"):
        st.subheader("Cơ cấu cảm xúc", icon=":material/donut_large:")
        donut = (
            alt.Chart(company_dist)
            .mark_arc(innerRadius=56, outerRadius=82, cornerRadius=5, padAngle=.025)
            .encode(
                theta=alt.Theta("percentage:Q"),
                color=alt.Color("sentiment:N", scale=alt.Scale(domain=list(SENTIMENT_COLORS), range=list(SENTIMENT_COLORS.values())), legend=alt.Legend(title=None, orient="bottom")),
                tooltip=[alt.Tooltip("sentiment:N", title="Cảm xúc"), alt.Tooltip("review_count:Q", title="Reviews", format=","), alt.Tooltip("percentage:Q", title="Tỷ lệ", format=".1f")],
            )
            .properties(height=230)
        )
        center = alt.Chart(pd.DataFrame([{"value": f"{int(company_aspects['review_count']):,}"}])).mark_text(font="JetBrains Mono", fontSize=26, color="#f1f5f9").encode(text="value:N")
        st.altair_chart(style_chart(donut + center), width="stretch")
        st.caption("Mỗi phần thể hiện tỷ lệ review theo cảm xúc.")
with right:
    with st.container(border=True, key="insight_aspects", height="stretch"):
        st.subheader("Điểm trải nghiệm", icon=":material/equalizer:")
        aspect_columns = ["Salary & benefits", "Training & learning", "Management cares about me", "Culture & fun", "Office & workspace"]
        labels = ["Lương & phúc lợi", "Đào tạo", "Quản lý", "Văn hóa", "Văn phòng"]
        aspect_frame = pd.DataFrame([{"Khía cạnh": label, "Điểm": float(company_aspects[column])} for column, label in zip(aspect_columns, labels)])
        aspect_chart = (
            alt.Chart(aspect_frame)
            .mark_bar(cornerRadiusEnd=7, height=21, color="#7aa7ff")
            .encode(
                x=alt.X("Điểm:Q", scale=alt.Scale(domain=[0, 5]), title="Điểm trung bình · thang 1–5"),
                y=alt.Y("Khía cạnh:N", sort="-x", title=None),
                tooltip=[alt.Tooltip("Khía cạnh:N"), alt.Tooltip("Điểm:Q", format=".2f")],
            )
            .properties(height=230)
        )
        st.altair_chart(style_chart(aspect_chart), width="stretch")
        lowest = aspect_frame.loc[aspect_frame["Điểm"].idxmin()]
        st.caption(f"Khía cạnh thấp nhất: {lowest['Khía cạnh']} · {lowest['Điểm']:.2f}/5")

st.info(str(company_aspects["recommendation"]), icon=":material/lightbulb:")

section_label("Ngôn ngữ nổi bật")
sentiment = st.segmented_control("Góc nhìn WordCloud", ["Positive", "Negative"], default="Negative", required=True, key="insights_sentiment")
cloud_keywords = company_keywords[company_keywords["sentiment"] == sentiment].sort_values("rank")
current = cloud_keywords.head(12).copy()

wordcloud_col, keyword_col = st.columns([1.42, .8], gap="large")
with wordcloud_col:
    with st.container(border=True, key="wordcloud_panel", height="stretch"):
        st.subheader(f"{sentiment} WordCloud", icon=":material/cloud:")
        st.caption(f"{company} · {len(cloud_keywords)} từ / cụm từ phổ biến nhất")
        if cloud_keywords.empty:
            st.info("Chưa có từ khóa cho lựa chọn này.")
        else:
            frequencies = dict(zip(cloud_keywords["keyword"], cloud_keywords["count"].astype(int)))
            st.image(keyword_cloud_svg(frequencies, sentiment), width="stretch")
with keyword_col:
    with st.container(border=True, key="keyword_panel", height="stretch"):
        st.subheader("Từ khóa thường gặp", icon=":material/tag:")
        st.caption("12 từ / cụm từ được nhắc nhiều nhất")
        keyword_chart = (
            alt.Chart(current.sort_values("count"))
            .mark_bar(cornerRadiusEnd=6, height=16, color=SENTIMENT_COLORS[sentiment])
            .encode(
                x=alt.X("count:Q", title="Số lần xuất hiện"),
                y=alt.Y("keyword:N", sort="-x", title=None),
                tooltip=[alt.Tooltip("rank:Q", title="#"), "keyword", alt.Tooltip("count:Q", format=",")],
            )
            .properties(height=340)
        )
        st.altair_chart(style_chart(keyword_chart), width="stretch")

st.caption("WordCloud biểu diễn tần suất từ, không chứng minh nguyên nhân hoặc chất lượng tổng thể của doanh nghiệp.")
