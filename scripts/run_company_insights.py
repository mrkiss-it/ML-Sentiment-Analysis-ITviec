"""Generate TV4 company sentiment tables, WordClouds, and report artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.tv4_analysis import ASPECT_COLUMNS, top_keywords

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "reviews_cleaned.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "company_insights"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _wordcloud(text: str, title: str, output: Path, colormap: str) -> None:
    if not text.strip():
        return
    cloud = WordCloud(
        width=1600,
        height=800,
        background_color="#0b1220",
        colormap=colormap,
        max_words=160,
        collocations=True,
        prefer_horizontal=0.92,
        random_state=2026,
    ).generate(text)
    fig, axis = plt.subplots(figsize=(12, 6), facecolor="#0b1220")
    axis.imshow(cloud, interpolation="bilinear")
    axis.axis("off")
    axis.set_title(title, color="white", fontsize=17, fontweight="bold", pad=18)
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def _recommendation(row: pd.Series) -> str:
    aspect_values = {column: float(row[column]) for column in ASPECT_COLUMNS}
    weakest = min(aspect_values, key=aspect_values.get)
    mapping = {
        "Salary & benefits": "Rà soát lương, thưởng và phúc lợi theo benchmark thị trường.",
        "Training & learning": "Tăng ngân sách đào tạo, mentoring và lộ trình phát triển nghề nghiệp.",
        "Management cares about me": "Cải thiện 1:1, phản hồi hai chiều và năng lực quản lý con người.",
        "Culture & fun": "Tăng hoạt động gắn kết và cơ chế ghi nhận minh bạch.",
        "Office & workspace": "Rà soát không gian làm việc, thiết bị và chính sách hybrid.",
    }
    return mapping[weakest]


def run(top_n: int = 5) -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    data = pd.read_excel(DATA_PATH)
    required = {"Company Name", "sentiment", "clean_advance_text", *ASPECT_COLUMNS}
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError("Thiếu cột: " + ", ".join(missing))

    selected = data["Company Name"].value_counts().head(top_n).index.tolist()
    selected_data = data[data["Company Name"].isin(selected)].copy()
    distribution = (
        selected_data.groupby(["Company Name", "sentiment"]).size().rename("review_count").reset_index()
    )
    totals = distribution.groupby("Company Name")["review_count"].transform("sum")
    distribution["percentage"] = distribution["review_count"] / totals * 100
    distribution.to_csv(OUTPUT_DIR / "company_sentiment_distribution.csv", index=False, encoding="utf-8-sig")

    aspects = selected_data.groupby("Company Name")[list(ASPECT_COLUMNS)].mean().round(3).reset_index()
    counts = selected_data.groupby("Company Name").size().rename("review_count")
    aspects = aspects.merge(counts, on="Company Name")
    aspects["recommendation"] = aspects.apply(_recommendation, axis=1)
    aspects.to_csv(OUTPUT_DIR / "company_aspect_summary.csv", index=False, encoding="utf-8-sig")

    global_outputs = {}
    for sentiment, cmap in (("Positive", "viridis"), ("Negative", "magma")):
        text = " ".join(data.loc[data["sentiment"] == sentiment, "clean_advance_text"].dropna().astype(str))
        output = FIGURE_DIR / f"wordcloud_{sentiment.lower()}_all.png"
        _wordcloud(text, f"{sentiment} keywords - All companies", output, cmap)
        global_outputs[sentiment] = str(output.relative_to(PROJECT_ROOT)).replace("\\", "/")

    keyword_rows = []
    company_outputs = []
    for company in selected:
        company_data = selected_data[selected_data["Company Name"] == company]
        slug = _slug(company)
        item = {"company": company, "review_count": int(len(company_data)), "wordclouds": {}}
        for sentiment, cmap in (("Positive", "viridis"), ("Negative", "magma")):
            texts = company_data.loc[
                company_data["sentiment"] == sentiment, "clean_advance_text"
            ].dropna().astype(str)
            for rank, (keyword, count) in enumerate(top_keywords(texts, limit=20), start=1):
                keyword_rows.append(
                    {"Company Name": company, "sentiment": sentiment, "rank": rank, "keyword": keyword, "count": count}
                )
            output = FIGURE_DIR / f"wordcloud_{slug}_{sentiment.lower()}.png"
            _wordcloud(" ".join(texts), f"{company} - {sentiment}", output, cmap)
            if output.exists():
                item["wordclouds"][sentiment] = str(output.relative_to(PROJECT_ROOT)).replace("\\", "/")
        company_outputs.append(item)
    keywords = pd.DataFrame(keyword_rows)
    keywords.to_csv(OUTPUT_DIR / "company_top_keywords.csv", index=False, encoding="utf-8-sig")

    report_rows = []
    for company in selected:
        dist = distribution[distribution["Company Name"] == company].set_index("sentiment")
        aspect = aspects[aspects["Company Name"] == company].iloc[0]
        report_rows.append(
            f"### {company} ({int(aspect['review_count'])} reviews)\n\n"
            f"- Positive: **{float(dist.loc['Positive', 'percentage']) if 'Positive' in dist.index else 0:.1f}%**; "
            f"Neutral: **{float(dist.loc['Neutral', 'percentage']) if 'Neutral' in dist.index else 0:.1f}%**; "
            f"Negative: **{float(dist.loc['Negative', 'percentage']) if 'Negative' in dist.index else 0:.1f}%**.\n"
            f"- Khía cạnh thấp nhất: **{min(ASPECT_COLUMNS, key=lambda column: float(aspect[column]))}**.\n"
            f"- Đề xuất: {aspect['recommendation']}"
        )
    report = f"""# TV4 - Company Sentiment Insights

Phân tích mô tả trên **{len(data):,} reviews**, **{data['Company Name'].nunique()} công ty**. Năm case study được chọn theo số review lớn nhất để giảm rủi ro kết luận từ mẫu quá nhỏ.

## WordCloud toàn bộ dữ liệu

![Positive WordCloud](figures/wordcloud_positive_all.png)

![Negative WordCloud](figures/wordcloud_negative_all.png)

## Case study 5 công ty

{chr(10).join(report_rows)}

## Giới hạn

- Nhãn sentiment là weak label suy ra từ rating, không phải nhãn cảm xúc được chuyên gia gán thủ công.
- WordCloud phản ánh tần suất từ, không chứng minh nguyên nhân hay mức độ quan trọng.
- Không dùng kết quả này như bảng xếp hạng chất lượng doanh nghiệp.
"""
    (PROJECT_ROOT / "reports" / "tv4_company_sentiment_insights.md").write_text(report, encoding="utf-8")
    manifest = {
        "source_rows": int(len(data)),
        "company_count": int(data["Company Name"].nunique()),
        "selected_companies": company_outputs,
        "global_wordclouds": global_outputs,
    }
    (OUTPUT_DIR / "insights_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
