"""Build the 15-slide Dark-tech defense deck (12 minutes) for the ITviec sentiment project.

Usage:
    python scripts/build_presentation_slides.py [-o reports/slides/ITviec_Sentiment_Analysis.pptx]

Requires: python-pptx (pip install python-pptx). All figures/metrics are read from
reports/ (figures, evaluation, company_insights); no model loading is needed.
Speaker notes on every slide carry the target duration; they sum to 720 s (12:00).
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
EVAL = ROOT / "reports" / "evaluation"
INSIGHT = ROOT / "reports" / "company_insights"

# ---- Dark-tech palette (mirrors src/app_theme.py so slides match the Streamlit demo) ----
BG = "080B10"
SURF = "141B26"
SURF2 = "1B2433"
BORDER = "2A3444"
TEXT = "F1F5F9"
MUTED = "9EABBA"
BLUE = "7AA7FF"
MINT = "50E3A4"
YELLOW = "F4D35E"
ORANGE = "FF994F"
RED = "FF6677"
FONT = "Calibri"
MONO = "Consolas"

W, H = 13.333, 7.5
MX = 0.6
CW = W - 2 * MX
TOTAL = 15


def rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)


def blend(base: str, top: str, a: float) -> str:
    b = [int(base[i:i + 2], 16) for i in (0, 2, 4)]
    t = [int(top[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x + (y - x) * a):02X}" for x, y in zip(b, t))


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------- primitives
def text(slide, x, y, w, h, content, size=14, color=TEXT, bold=False, font=FONT,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, italic=False):
    """content: str, or list of paragraphs; a paragraph is str or list of (text, {opts}) runs."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing is not None:
            p.space_after = Pt(spacing)
        runs = para if isinstance(para, list) else [(para, {})]
        for t, o in runs:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = o.get("font", font)
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = rgb(o.get("color", color))
    return box


def card(slide, x, y, w, h, fill=SURF, line=BORDER, radius=0.05):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = radius
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(0.75)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    return s


def badge(slide, x, y, label, color=BLUE, size=12, w=None):
    """Circle-ish mono tag used as the deck motif (numbered / labelled chip)."""
    w = w or max(0.5, 0.16 + 0.11 * len(label))
    s = card(slide, x, y, w, 0.34, fill=blend(BG, color, 0.16), line=blend(BG, color, 0.5), radius=0.5)
    tf = s.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.name, r.font.size, r.font.bold = MONO, Pt(size), True
    r.font.color.rgb = rgb(color)
    return s


def arrow(slide, x, y, w=0.4, h=0.3, color=BLUE):
    s = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(color)
    s.line.fill.background()
    return s


def picture(slide, path: Path, x, y, w, h):
    """Insert an image scaled to fit (x,y,w,h) box, centred, aspect preserved."""
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    return slide.shapes.add_picture(str(path), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2),
                                    Inches(pw), Inches(ph))


def new_slide(prs, n, eyebrow, title, seconds, notes):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(BG)
    if n > 1:
        text(s, MX, 0.42, 8, 0.3, eyebrow.upper(), size=12, color=BLUE, bold=True, font=MONO)
        text(s, MX, 0.74, CW, 0.75, title, size=32, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, MX, 7.02, 8, 0.25, "ITviec Sentiment Analysis  ·  Nhóm Máy học", size=10, color=MUTED)
        text(s, W - MX - 2, 7.02, 2, 0.25, f"{n:02d} / {TOTAL}", size=10, color=MUTED, font=MONO,
             align=PP_ALIGN.RIGHT)
    mm, ss = divmod(seconds, 60)
    s.notes_slide.notes_text_frame.text = f"[Thời lượng mục tiêu: {seconds}s ({mm}:{ss:02d})]\n{notes}"
    return s


def style_chart(chart, legend=False):
    chart.font.name = FONT
    chart.font.size = Pt(12)
    chart.font.color.rgb = rgb(MUTED)
    chart.has_title = False
    chart.has_legend = legend
    if legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.legend.font.color.rgb = rgb(MUTED)
        chart.legend.font.size = Pt(11)
    va, ca = chart.value_axis, chart.category_axis
    va.major_gridlines.format.line.color.rgb = rgb(BORDER)
    va.major_gridlines.format.line.width = Pt(0.5)
    va.format.line.fill.background()
    ca.format.line.color.rgb = rgb(BORDER)
    va.tick_labels.font.color.rgb = rgb(MUTED)
    ca.tick_labels.font.color.rgb = rgb(TEXT)


# --------------------------------------------------------------------------- data
def load_metrics():
    m = read_csv(EVAL / "final_test_metrics.csv")[0]
    cv = read_csv(EVAL / "model_ranking_cv.csv")
    cm = read_csv(EVAL / "confusion_matrix.csv")
    per_class = read_csv(EVAL / "final_test_per_class.csv")
    dist = read_csv(INSIGHT / "company_sentiment_distribution.csv")
    return m, cv, cm, per_class, dist


# --------------------------------------------------------------------------- slides
def s01_cover(prs):
    s = new_slide(prs, 1, "", "", 20,
                  "Chào Hội đồng. Giới thiệu đề tài, nhóm và GVHD. Nêu nhanh: 8.417 review ITviec, "
                  "phân loại 3 lớp cảm xúc, có demo web. (~20s)")
    # decorative "token grid" motif on the right
    import random
    rnd = random.Random(7)
    cols = [BLUE, MINT, YELLOW, ORANGE, RED]
    for gx in range(6):
        for gy in range(9):
            if rnd.random() < 0.55:
                c = cols[rnd.randrange(len(cols))]
                sq = card(s, 9.2 + gx * 0.62, 1.0 + gy * 0.62, 0.46, 0.46,
                          fill=blend(BG, c, rnd.choice([0.10, 0.18, 0.3])), line=None, radius=0.2)
    badge(s, MX, 1.0, "ĐỒ ÁN MÔN HỌC MÁY HỌC  ·  UIT", BLUE, 12, w=4.1)
    text(s, MX, 1.75, 8.2, 2.4, [
        [("PHÂN TÍCH CẢM XÚC", {})],
        [("ĐÁNH GIÁ CÔNG TY ", {}), ("ITVIEC", {"color": MINT})],
    ], size=44, bold=True, spacing=2)
    text(s, MX, 3.75, 8, 0.8,
         "Sentiment Analysis 3 lớp (Negative · Neutral · Positive) với TF-IDF và các mô hình Machine Learning cổ điển",
         size=18, color=MUTED)
    card(s, MX, 4.95, 8.2, 1.65)
    text(s, MX + 0.3, 5.1, 7.6, 0.35, "GIẢNG VIÊN HƯỚNG DẪN", size=11, color=BLUE, bold=True, font=MONO)
    text(s, MX + 0.3, 5.42, 7.6, 0.35, "[Điền tên GVHD]", size=16, bold=True)
    text(s, MX + 0.3, 5.85, 7.6, 0.3, "NHÓM THỰC HIỆN", size=11, color=BLUE, bold=True, font=MONO)
    text(s, MX + 0.3, 6.17, 7.6, 0.35, "Hoàng Hôn  ·  Văn Duy  ·  Duy Khang  ·  Thành Trung", size=16, bold=True)


def s02_problem(prs):
    s = new_slide(prs, 2, "01 · Đặt vấn đề", "Bài toán & thách thức dữ liệu ITviec", 40,
                  "Nhà tuyển dụng/ứng viên cần đọc hàng nghìn review. Mục tiêu: tự động gán nhãn cảm xúc. "
                  "Điểm khó nhất là mất cân bằng 11:1, kế đến teencode, trộn Anh-Việt, và review vừa khen vừa chê. (~40s)")
    card(s, MX, 1.8, 4.0, 4.95, fill=SURF2)
    text(s, MX + 0.3, 2.05, 3.4, 0.3, "MẤT CÂN BẰNG LỚP", size=11, color=ORANGE, bold=True, font=MONO)
    text(s, MX + 0.3, 2.5, 3.4, 1.4, "11 : 1", size=72, bold=True, color=ORANGE, font=MONO)
    text(s, MX + 0.3, 3.95, 3.4, 0.9, "Positive so với Negative trên 8.417 review — Accuracy dễ đánh lừa, cần Macro F1.",
         size=14, color=MUTED)
    for i, (lbl, pct, c) in enumerate([("Positive", 73.8, MINT), ("Neutral", 19.5, YELLOW), ("Negative", 6.8, RED)]):
        y = 5.0 + i * 0.55
        text(s, MX + 0.3, y, 0.95, 0.3, lbl, size=12, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
        card(s, MX + 1.3, y + 0.04, 1.6, 0.22, fill=SURF, line=None, radius=0.5)
        card(s, MX + 1.3, y + 0.04, max(0.12, 1.6 * pct / 73.8), 0.22, fill=c, line=None, radius=0.5)
        text(s, MX + 3.0, y, 0.7, 0.3, f"{pct}%", size=12, color=c, bold=True, font=MONO, anchor=MSO_ANCHOR.MIDDLE)

    items = [
        ("Teencode & viết tắt", "“ko”, “dc”, “ok”, emoji, emojicon xen lẫn trong câu.", BLUE),
        ("Từ lóng Anh – Việt", "OT, deadline, onsite, fresher, benefit… trộn ngôn ngữ trong cùng review.", MINT),
        ("Khen chê đan xen", "“Môi trường tốt nhưng lương thấp, OT nhiều” — nhiều vế, cảm xúc đối lập.", YELLOW),
        ("Nhãn nhiễu theo sao", "Nhãn suy ra từ rating 1–5 sao, không phải người đọc gán thủ công.", RED),
    ]
    x0, gw = MX + 4.3, 3.9
    for i, (h, d, c) in enumerate(items):
        x = x0 + (i % 2) * (gw + 0.3)
        y = 1.8 + (i // 2) * 2.5
        card(s, x, y, gw, 2.3)
        badge(s, x + 0.3, y + 0.28, f"0{i + 1}", c, 12, w=0.55)
        text(s, x + 0.3, y + 0.8, gw - 0.6, 0.4, h, size=18, bold=True)
        text(s, x + 0.3, y + 1.3, gw - 0.6, 0.9, d, size=13, color=MUTED)


def s03_pipeline(prs):
    s = new_slide(prs, 3, "02 · Kiến trúc", "Pipeline End-to-End", 30,
                  "Toàn bộ luồng: thu thập → tiền xử lý → TF-IDF → huấn luyện 5 mô hình có SMOTE → đóng gói thành web Streamlit. (~30s)")
    steps = [
        ("01", "Thu thập", "8.417 review\nITviec", BLUE),
        ("02", "Tiền xử lý", "Unicode NFC\nunderthesea", MINT),
        ("03", "TF-IDF", "N-gram (1,2)\n5.000 chiều", YELLOW),
        ("04", "Huấn luyện", "5 mô hình ML\nSMOTE + 5-fold CV", ORANGE),
        ("05", "Web App", "Streamlit\nDự đoán real-time", RED),
    ]
    bw, gap = 2.06, 0.45
    y = 2.35
    for i, (n, t, d, c) in enumerate(steps):
        x = MX + i * (bw + gap)
        card(s, x, y, bw, 2.6, fill=SURF2, line=blend(BG, c, 0.45))
        badge(s, x + 0.2, y + 0.22, n, c, 12, w=0.55)
        text(s, x + 0.2, y + 0.85, bw - 0.4, 0.4, t, size=18, bold=True)
        text(s, x + 0.2, y + 1.45, bw - 0.4, 1.0, d.split("\n"), size=13, color=MUTED, spacing=2)
        if i < 4:
            arrow(s, x + bw + 0.04, y + 1.15, 0.37, 0.3, c)
    card(s, MX, 5.4, CW, 1.25)
    text(s, MX + 0.4, 5.6, CW - 0.8, 0.4, "KẾT QUẢ ĐẦU RA", size=11, color=BLUE, bold=True, font=MONO)
    text(s, MX + 0.4, 5.95, CW - 0.8, 0.6, [[
        ("Mô hình chọn: ", {"color": MUTED}), ("Logistic Regression (C=1.0, SMOTE)", {"bold": True, "color": MINT}),
        ("   ·   Final Test: ", {"color": MUTED}), ("Accuracy 73,74%", {"bold": True}),
        ("   ·   ", {"color": MUTED}), ("Macro F1 0,5714", {"bold": True}),
    ]], size=16)


def s04_preprocessing(prs):
    s = new_slide(prs, 4, "03 · Tiền xử lý", "Làm sạch văn bản tiếng Việt chuyên sâu", 50,
                  "Năm bước: chuẩn hóa Unicode NFC, xử lý emoji/emojicon, sửa teencode, tách từ bằng underthesea, lọc từ dừng. "
                  "Ví dụ bên phải cho thấy câu thô thành chuỗi token sạch. (~50s)")
    steps = [
        ("Unicode NFC", "Thống nhất dấu tiếng Việt, tránh cùng chữ khác mã", BLUE),
        ("Emoji / emojicon", "Chuyển thành tín hiệu văn bản hoặc loại bỏ nhiễu", MINT),
        ("Teencode", "Ánh xạ ko → không, dc → được, … về dạng chuẩn", YELLOW),
        ("Tách từ underthesea", "“quản lý” → quản_lý: giữ nguyên nghĩa từ ghép", ORANGE),
        ("Lọc từ dừng", "Bỏ từ chức năng, giữ từ mang sắc thái", RED),
    ]
    for i, (t, d, c) in enumerate(steps):
        y = 1.8 + i * 0.99
        card(s, MX, y, 6.2, 0.86)
        badge(s, MX + 0.2, y + 0.26, str(i + 1), c, 12, w=0.4)
        text(s, MX + 0.85, y + 0.1, 5.2, 0.32, t, size=16, bold=True)
        text(s, MX + 0.85, y + 0.44, 5.2, 0.35, d, size=12, color=MUTED)
    x = MX + 6.5
    w = CW - 6.5
    card(s, x, 1.8, w, 4.85, fill=SURF2)
    text(s, x + 0.3, 2.0, w - 0.6, 0.3, "VÍ DỤ  ·  RAW", size=11, color=RED, bold=True, font=MONO)
    text(s, x + 0.3, 2.35, w - 0.6, 1.1,
         "Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương.",
         size=17, font=MONO, color=TEXT)
    arrow(s, x + w / 2 - 0.2, 3.6, 0.4, 0.3, BLUE)
    s.shapes[-1].rotation = 90
    text(s, x + 0.3, 4.15, w - 0.6, 0.3, "CLEAN TOKENS", size=11, color=MINT, bold=True, font=MONO)
    text(s, x + 0.3, 4.5, w - 0.6, 1.0,
         "lương thấp quản_lý thiếu minh_bạch thường_xuyên phải ot không lương",
         size=17, font=MONO, color=MINT)
    text(s, x + 0.3, 5.75, w - 0.6, 0.7, "Từ ghép được nối bằng “_” để TF-IDF coi là một đặc trưng duy nhất.",
         size=12, color=MUTED)


def s05_eda(prs):
    s = new_slide(prs, 5, "04 · EDA", "Khám phá dữ liệu: lệch nhãn, độ dài, khía cạnh", 50,
                  "8.417 review; 73,8% tích cực, 19,5% trung tính, 6,8% tiêu cực. Độ dài review lệch phải. "
                  "Các khía cạnh đánh giá tương quan dương với nhau, cho thấy hiệu ứng halo khiến nhãn theo sao nhiễu. (~50s)")
    for i, (lbl, pct, c, cnt) in enumerate([("POSITIVE", "73,8%", MINT, "rating 4–5★"),
                                            ("NEUTRAL", "19,5%", YELLOW, "rating 3★"),
                                            ("NEGATIVE", "6,8%", RED, "rating 1–2★")]):
        y = 1.8 + i * 1.66
        card(s, MX, y, 3.2, 1.5, fill=SURF2, line=blend(BG, c, 0.4))
        text(s, MX + 0.25, y + 0.18, 2.7, 0.3, lbl, size=11, color=c, bold=True, font=MONO)
        text(s, MX + 0.25, y + 0.45, 2.7, 0.75, pct, size=44, bold=True, color=c, font=MONO)
        text(s, MX + 0.25, y + 1.15, 2.7, 0.28, cnt, size=11, color=MUTED)
    x2 = MX + 3.5
    card(s, x2, 1.8, 4.6, 4.95, fill=SURF)
    text(s, x2 + 0.25, 1.95, 4.1, 0.3, "TƯƠNG QUAN CÁC KHÍA CẠNH", size=11, color=BLUE, bold=True, font=MONO)
    picture(s, FIG / "eda_aspect_correlation.png", x2 + 0.2, 2.35, 4.2, 4.25)
    x3 = x2 + 4.9
    w3 = CW - (x3 - MX)
    card(s, x3, 1.8, w3, 2.5, fill=SURF)
    text(s, x3 + 0.2, 1.95, w3 - 0.4, 0.3, "PHÂN BỐ ĐỘ DÀI", size=11, color=BLUE, bold=True, font=MONO)
    picture(s, FIG / "eda_text_length_distribution.png", x3 + 0.15, 2.35, w3 - 0.3, 1.85)
    card(s, x3, 4.5, w3, 2.25, fill=SURF2)
    text(s, x3 + 0.25, 4.7, w3 - 0.5, 1.9, [
        [("Review dài, lệch phải ", {"bold": True}), ("→ cần TF-IDF thay vì đếm thô.", {"color": MUTED})],
        [("Khía cạnh tương quan cao ", {"bold": True}), ("→ sao tổng thể che lấp ý kiến từng mặt.", {"color": MUTED})],
    ], size=13, spacing=8)


def s06_tfidf(prs):
    s = new_slide(prs, 6, "05 · Đặc trưng", "Trích xuất TF-IDF N-gram (1,2)", 50,
                  "Cấu hình TF-IDF: ngram (1,2), sublinear_tf, 5.000 đặc trưng. Chia Stratified 80/20: 6.734 train (Development), "
                  "1.683 test khóa. Khóa tập test trước, mọi tuning chỉ trên Development. (~50s)")
    cfg = [("ngram_range", "(1, 2)", BLUE), ("sublinear_tf", "True", MINT), ("max_features", "5.000", YELLOW)]
    for i, (k, v, c) in enumerate(cfg):
        y = 1.8 + i * 1.25
        card(s, MX, y, 5.2, 1.1, fill=SURF2)
        text(s, MX + 0.3, y + 0.2, 2.6, 0.35, k, size=14, color=MUTED, font=MONO)
        text(s, MX + 0.3, y + 0.5, 2.6, 0.5, "cấu hình TF-IDF", size=11, color=MUTED)
        text(s, MX + 2.7, y + 0.15, 2.3, 0.8, v, size=34, bold=True, color=c, font=MONO, align=PP_ALIGN.RIGHT)
    card(s, MX, 5.6, 5.2, 1.15)
    text(s, MX + 0.3, 5.75, 4.6, 0.85,
         "Unigram + bigram bắt được cụm mang sắc thái: “không lương”, “thường_xuyên ot”.", size=13, color=MUTED)
    x = MX + 5.5
    w = CW - 5.5
    card(s, x, 1.8, w, 2.85, fill=SURF)
    text(s, x + 0.25, 1.95, w - 0.5, 0.3, "SO SÁNH N-GRAM (CV)", size=11, color=BLUE, bold=True, font=MONO)
    picture(s, FIG / "eda_tfidf_ngram_comparison.png", x + 0.2, 2.3, w - 0.4, 2.25)
    card(s, x, 4.85, w, 1.9, fill=SURF2)
    text(s, x + 0.25, 5.0, w - 0.5, 0.3, "CHIA TẬP STRATIFIED 80 / 20", size=11, color=BLUE, bold=True, font=MONO)
    tw = w - 0.5
    card(s, x + 0.25, 5.45, tw * 0.8, 0.5, fill=blend(BG, BLUE, 0.35), line=None, radius=0.3)
    card(s, x + 0.25 + tw * 0.8 + 0.05, 5.45, tw * 0.2 - 0.05, 0.5, fill=blend(BG, ORANGE, 0.45), line=None, radius=0.3)
    text(s, x + 0.25, 5.45, tw * 0.8, 0.5, "Development · 6.734 mẫu", size=13, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.25 + tw * 0.8, 5.45, tw * 0.2, 0.5, "Test 1.683", size=12, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.25, 6.15, tw, 0.45, "Tập test khóa: chỉ dùng đúng một lần để báo cáo cuối.", size=12, color=MUTED)


def s07_models(prs):
    s = new_slide(prs, 7, "06 · Mô hình", "5 mô hình ML & SMOTE chống rò rỉ dữ liệu", 55,
                  "Năm mô hình: Naive Bayes, Logistic Regression, Linear SVM, Random Forest, Stacking. "
                  "Mất cân bằng xử lý bằng class_weight hoặc SMOTE. Điểm mấu chốt: SMOTE bọc trong Pipeline, "
                  "chỉ áp dụng trên fold train của mỗi lần CV nên fold validation không bị rò rỉ. (~55s)")
    models = [("MNB", "Multinomial\nNaive Bayes", BLUE), ("LR", "Logistic\nRegression", MINT),
              ("SVM", "Linear\nSVM", YELLOW), ("RF", "Random\nForest", ORANGE), ("STK", "Stacking\nEnsemble", RED)]
    bw, gap = 2.2, 0.283
    for i, (tag, name, c) in enumerate(models):
        x = MX + i * (bw + gap)
        card(s, x, 1.8, bw, 1.75, fill=SURF2, line=blend(BG, c, 0.45))
        badge(s, x + 0.2, 1.98, tag, c, 12, w=0.7)
        text(s, x + 0.2, 2.5, bw - 0.4, 0.9, name.split("\n"), size=16, bold=True)
    card(s, MX, 3.85, CW, 2.9)
    text(s, MX + 0.3, 4.0, 8, 0.3, "SMOTE TRONG PIPELINE  ·  MỖI FOLD CV", size=11, color=BLUE, bold=True, font=MONO)
    stages = [("Train fold", "4/5 dữ liệu\nDevelopment", BLUE, False), ("SMOTE", "Sinh mẫu thiểu số\nchỉ trên train fold", ORANGE, True),
              ("Fit model", "Học trên dữ liệu\nđã cân bằng", MINT, False), ("Validate", "1/5 fold còn lại\nNGUYÊN BẢN", YELLOW, False)]
    bw2, gap2 = 2.5, 0.63
    for i, (t, d, c, hot) in enumerate(stages):
        x = MX + 0.3 + i * (bw2 + gap2)
        card(s, x, 4.5, bw2, 1.9, fill=blend(SURF, c, 0.14 if hot else 0.05), line=blend(BG, c, 0.6))
        text(s, x + 0.2, 4.65, bw2 - 0.4, 0.4, t, size=17, bold=True, color=c)
        text(s, x + 0.2, 5.2, bw2 - 0.4, 1.1, d.split("\n"), size=13, color=MUTED, spacing=2)
        if i < 3:
            arrow(s, x + bw2 + 0.1, 5.3, 0.43, 0.3, c)


def s08_leaderboard(prs, cv):
    s = new_slide(prs, 8, "07 · Kết quả CV", "Bảng xếp hạng trên Development Set", 45,
                  "Xếp hạng theo Macro F1 của Stratified 5-fold CV. Logistic Regression (C=1.0, SMOTE) cao nhất 0,5727, "
                  "sát Linear SVM 0,5724 nhưng LR trả xác suất trực tiếp nên được chọn cho demo. Stacking không giúp vì các base learner tương quan lỗi. (~45s)")
    cd = CategoryChartData()
    cd.categories = [r["Model"] for r in cv]
    cd.add_series("CV Macro F1", [round(float(r["CV Macro F1 Mean"]), 4) for r in cv])
    card(s, MX, 1.8, 7.6, 4.95, fill=SURF)
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(MX + 0.2), Inches(2.0), Inches(7.2), Inches(4.6), cd)
    ch = gf.chart
    style_chart(ch)
    ch.category_axis.reverse_order = True
    ch.value_axis.minimum_scale = 0.5
    ch.value_axis.maximum_scale = 0.6
    ch.value_axis.major_unit = 0.02
    ch.value_axis.tick_labels.number_format = "0.00"
    ch.value_axis.tick_labels.number_format_is_linked = False
    pl = ch.plots[0]
    pl.gap_width = 55
    pl.has_data_labels = True
    dl = pl.data_labels
    dl.number_format, dl.number_format_is_linked = "0.0000", False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size, dl.font.bold = Pt(13), True
    dl.font.color.rgb = rgb(TEXT)
    for i in range(len(cv)):
        pt = pl.series[0].points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(MINT if i == 0 else blend(SURF, BLUE, 0.55))
    x = MX + 7.9
    w = CW - 7.9
    card(s, x, 1.8, w, 2.4, fill=SURF2, line=blend(BG, MINT, 0.5))
    text(s, x + 0.25, 1.95, w - 0.5, 0.3, "MÔ HÌNH ĐƯỢC CHỌN", size=11, color=MINT, bold=True, font=MONO)
    text(s, x + 0.25, 2.3, w - 0.5, 0.5, "Logistic Regression", size=22, bold=True)
    text(s, x + 0.25, 2.85, w - 0.5, 0.9, "0,5727", size=44, bold=True, color=MINT, font=MONO)
    text(s, x + 0.25, 3.65, w - 0.5, 0.4, "C = 1.0  ·  SMOTE", size=13, color=MUTED, font=MONO)
    card(s, x, 4.4, w, 2.35)
    text(s, x + 0.25, 4.55, w - 0.5, 2.1, [
        [("Vì sao LR? ", {"bold": True, "color": BLUE})],
        [("Điểm CV cao nhất, độ lệch nhỏ (±0,011)", {"color": MUTED})],
        [("predict_proba trực tiếp cho demo", {"color": MUTED})],
        [("Random Forest & Stacking không vượt trội trên TF-IDF thưa", {"color": MUTED})],
    ], size=13, spacing=6)


def s09_final_test(prs, m, cm, per_class):
    s = new_slide(prs, 9, "08 · Final Test", "Kết quả độc lập & ma trận nhầm lẫn", 60,
                  "Chạy đúng một lần trên 1.683 mẫu khóa: Accuracy 73,74%, Macro F1 0,5714 — khớp CV 0,5727 nên không overfit. "
                  "Nhưng Accuracy cao vì lớp Positive chiếm áp đảo; Macro F1 mới phản ánh thực: Negative F1 chỉ 0,38. Đây là bẫy Accuracy. (~60s)")
    stats = [("ACCURACY", f"{float(m['accuracy']) * 100:.2f}%", MUTED), ("MACRO F1", f"{float(m['macro_f1']):.4f}", MINT),
             ("WEIGHTED F1", f"{float(m['weighted_f1']):.4f}", BLUE)]
    sw = 3.55
    for i, (k, v, c) in enumerate(stats):
        x = MX + i * (sw + 0.3)
        card(s, x, 1.75, sw, 1.2, fill=SURF2, line=blend(BG, c, 0.4) if c != MUTED else BORDER)
        text(s, x + 0.25, 1.9, sw - 0.5, 0.3, k, size=11, color=c, bold=True, font=MONO)
        text(s, x + 0.25, 2.2, sw - 0.5, 0.65, v, size=34, bold=True, color=c if c != MUTED else TEXT, font=MONO)
    # confusion matrix from CSV (heat-mapped grid)
    labels = ["Negative", "Neutral", "Positive"]
    grid = [[int(r[l]) for l in labels] for r in cm]
    cx, cy, cs = MX + 0.9, 3.85, 1.0
    card(s, MX, 3.2, 5.6, 3.55)
    text(s, MX + 0.25, 3.3, 5, 0.3, "CONFUSION MATRIX  ·  n = 1.683", size=11, color=BLUE, bold=True, font=MONO)
    for j, l in enumerate(labels):
        text(s, cx + 0.7 + j * (cs + 0.08), cy - 0.02, cs, 0.25, l[:3].upper(), size=10, color=MUTED, font=MONO,
             align=PP_ALIGN.CENTER)
    for i, row in enumerate(grid):
        tot = sum(row)
        text(s, MX + 0.2, cy + 0.35 + i * (cs * 0.72 + 0.08), 1.0, 0.5, labels[i][:3].upper(), size=10, color=MUTED,
             font=MONO, anchor=MSO_ANCHOR.MIDDLE)
        for j, v in enumerate(row):
            frac = v / tot
            base = MINT if i == j else RED
            x = cx + 0.7 + j * (cs + 0.08)
            y = cy + 0.25 + i * (cs * 0.72 + 0.08)
            card(s, x, y, cs, cs * 0.72, fill=blend(SURF, base, 0.15 + 0.7 * frac), line=None, radius=0.1)
            text(s, x, y, cs, cs * 0.72, [[(f"{v}", {"bold": True, "size": 16})], [(f"{frac * 100:.0f}%", {"size": 10, "color": TEXT})]],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, cx + 0.7, cy + 2.62, 3.3, 0.25, "Hàng = thực tế · Cột = dự đoán", size=10, color=MUTED, align=PP_ALIGN.CENTER)
    # per class + trap callout
    x = MX + 5.9
    w = CW - 5.9
    card(s, x, 3.2, w, 1.85)
    text(s, x + 0.25, 3.3, w - 0.5, 0.3, "F1 THEO LỚP", size=11, color=BLUE, bold=True, font=MONO)
    colors = {"Negative": RED, "Neutral": YELLOW, "Positive": MINT}
    for i, r in enumerate(per_class):
        y = 3.7 + i * 0.44
        text(s, x + 0.25, y, 1.2, 0.3, r["Label"], size=13, anchor=MSO_ANCHOR.MIDDLE)
        card(s, x + 1.5, y + 0.06, w - 2.7, 0.2, fill=SURF2, line=None, radius=0.5)
        card(s, x + 1.5, y + 0.06, max(0.1, (w - 2.7) * float(r["F1"])), 0.2, fill=colors[r["Label"]], line=None, radius=0.5)
        text(s, x + w - 1.0, y, 0.8, 0.3, f"{float(r['F1']):.2f}", size=13, bold=True, font=MONO,
             color=colors[r["Label"]], align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    card(s, x, 5.25, w, 1.5, fill=blend(SURF, ORANGE, 0.1), line=blend(BG, ORANGE, 0.5))
    text(s, x + 0.25, 5.38, w - 0.5, 0.3, "BẪY ACCURACY", size=11, color=ORANGE, bold=True, font=MONO)
    text(s, x + 0.25, 5.72, w - 0.5, 0.95,
         "Đoán toàn “Positive” đã đạt ~74% Accuracy. Chỉ Macro F1 (0,57) lộ ra Negative/Neutral còn yếu.",
         size=13)


def s10_errors(prs, m):
    s = new_slide(prs, 10, "09 · Error Analysis", "Vì sao mô hình sai? 3 nhóm nguyên nhân", 50,
                  "442 trên 1.683 mẫu sai (26,3%). Phân tích 15 ca điển hình cho ba nhóm: review nhiều vế khen chê đan xen "
                  "khiến tín hiệu tích cực đầu review lấn át; nhãn nhiễu do rating sao; review ngắn thiếu ngữ cảnh. (~50s)")
    err, tot = int(m["error_count"]), int(m["test_count"])
    card(s, MX, 1.8, 3.2, 4.95, fill=SURF2, line=blend(BG, RED, 0.4))
    text(s, MX + 0.3, 2.05, 2.6, 0.3, "SAI TRÊN FINAL TEST", size=11, color=RED, bold=True, font=MONO)
    text(s, MX + 0.3, 2.45, 2.7, 1.0, str(err), size=60, bold=True, color=RED, font=MONO)
    text(s, MX + 0.3, 3.55, 2.6, 0.5, f"trên {tot:,} mẫu".replace(",", "."), size=15, color=MUTED)
    text(s, MX + 0.3, 4.2, 2.6, 0.8, f"{err / tot * 100:.1f}% tỉ lệ lỗi", size=22, bold=True)
    text(s, MX + 0.3, 5.1, 2.6, 1.4, "Phần lớn lỗi là Neutral ↔ lớp lân cận, không phải đảo cực Positive ↔ Negative.",
         size=12, color=MUTED)
    cards = [
        ("Nhiều vế khen–chê", "Từ tích cực ở đầu review lấn át phần phàn nàn về OT/lương.",
         "“Môi trường tốt… chính sách OT thiếu minh bạch” → dự đoán Positive (97%)", YELLOW),
        ("Nhãn nhiễu theo sao", "Nhãn suy ra từ rating; người dùng cho 2★ nhưng viết nhiều ý tích cực.",
         "“Môi trường năng động… OT quá nhiều, lương thấp” (2★) → Positive", ORANGE),
        ("Review ngắn", "Quá ít token, TF-IDF không đủ tín hiệu để phân biệt Neutral với Positive.",
         "Vài từ chung chung như “ổn”, “tạm được” → Neutral / Positive lẫn lộn", BLUE),
    ]
    x0, w = MX + 3.5, CW - 3.5
    for i, (t, d, ex, c) in enumerate(cards):
        y = 1.8 + i * 1.7
        card(s, x0, y, w, 1.55)
        badge(s, x0 + 0.25, y + 0.22, f"0{i + 1}", c, 12, w=0.55)
        text(s, x0 + 1.05, y + 0.2, w - 1.3, 0.4, t, size=18, bold=True)
        text(s, x0 + 1.05, y + 0.62, w - 1.3, 0.45, d, size=13, color=MUTED)
        text(s, x0 + 1.05, y + 1.08, w - 1.3, 0.4, ex, size=12, color=c, font=MONO)


def s11_insight(prs, dist):
    s = new_slide(prs, 11, "10 · Insight ngành IT", "Cảm xúc theo công ty & từ khóa nổi bật", 55,
                  "WordCloud cho thấy khen: môi trường, đồng nghiệp, học hỏi; chê: OT, lương, quản lý. "
                  "So sánh 5 công ty: KMS và VNG có tỉ lệ tích cực cao nhất, Bosch thấp nhất với 15% tiêu cực. (~55s)")
    order = ["KMS Technology", "VNG Corporation", "NashTech", "FPT Software",
             "Bosch Global Software Technologies Company Limited"]
    short = {"KMS Technology": "KMS", "VNG Corporation": "VNG", "NashTech": "NashTech", "FPT Software": "FPT",
             "Bosch Global Software Technologies Company Limited": "Bosch"}
    pct = {(r["Company Name"], r["sentiment"]): float(r["percentage"]) for r in dist}
    cd = CategoryChartData()
    cd.categories = [short[c] for c in order]
    for lab in ("Positive", "Neutral", "Negative"):
        cd.add_series(lab, [round(pct[(c, lab)], 1) for c in order])
    card(s, MX, 1.8, 6.0, 4.95, fill=SURF)
    text(s, MX + 0.25, 1.95, 5.5, 0.3, "CẢM XÚC THEO CÔNG TY (%)", size=11, color=BLUE, bold=True, font=MONO)
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED_100, Inches(MX + 0.15), Inches(2.3), Inches(5.7), Inches(4.35), cd)
    ch = gf.chart
    style_chart(ch, legend=True)
    ch.category_axis.reverse_order = True
    ch.value_axis.tick_labels.font.size = Pt(10)
    pl = ch.plots[0]
    pl.gap_width = 45
    pl.overlap = 100
    pl.has_data_labels = True
    pl.data_labels.number_format, pl.data_labels.number_format_is_linked = "0", False
    pl.data_labels.position = XL_LABEL_POSITION.CENTER
    pl.data_labels.font.size = Pt(11)
    pl.data_labels.font.bold = True
    pl.data_labels.font.color.rgb = rgb(BG)
    for ser, c in zip(pl.series, (MINT, YELLOW, RED)):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = rgb(c)
    x = MX + 6.3
    w = CW - 6.3
    hw = (w - 0.3) / 2
    for k, (fn, lab, c) in enumerate([("wordcloud_positive_all.png", "TÍCH CỰC", MINT), ("wordcloud_negative_all.png", "TIÊU CỰC", RED)]):
        cx = x + k * (hw + 0.3)
        card(s, cx, 1.8, hw, 2.9, fill=SURF)
        text(s, cx + 0.2, 1.93, hw - 0.4, 0.3, f"WORDCLOUD · {lab}", size=10, color=c, bold=True, font=MONO)
        picture(s, FIG / fn, cx + 0.15, 2.3, hw - 0.3, 2.3)
    card(s, x, 4.9, w, 1.85, fill=SURF2)
    text(s, x + 0.25, 5.05, w - 0.5, 1.6, [
        [("Khen: ", {"bold": True, "color": MINT}), ("môi trường, đồng nghiệp, học hỏi", {"color": MUTED})],
        [("Chê: ", {"bold": True, "color": RED}), ("OT, lương, quản lý, thưởng", {"color": MUTED})],
        [("Bosch ", {"bold": True, "color": ORANGE}), ("có 15% tiêu cực — cao nhất trong 5 công ty", {"color": MUTED})],
    ], size=13, spacing=8)


def s12_demo(prs):
    s = new_slide(prs, 12, "11 · Web Demo", "Ứng dụng Streamlit Dark-tech · 5 phân hệ", 60,
                  "Giới thiệu 5 trang. Chuyển sang LIVE DEMO hoặc mở video: trang Dự đoán real-time, nhập câu review khó "
                  "và cho thấy nhãn cùng token kích hoạt. Nếu thiếu thời gian, chỉ demo trang Dự đoán. (~60s)")
    pages = [("Tổng quan", "KPI dữ liệu, phân bố nhãn, kiến trúc pipeline", BLUE),
             ("Insight doanh nghiệp", "Chọn công ty, xem WordCloud & từ khóa", MINT),
             ("Benchmark", "Bảng xếp hạng 5 mô hình theo CV Macro F1", YELLOW),
             ("Đánh giá lỗi", "Confusion matrix & 15 ca sai điển hình", ORANGE),
             ("Dự đoán real-time", "Nhập review → nhãn, xác suất, token kích hoạt", RED)]
    for i, (t, d, c) in enumerate(pages):
        y = 1.8 + i * 0.99
        hot = i == 4
        card(s, MX, y, 6.6, 0.86, fill=blend(SURF, c, 0.12) if hot else SURF, line=blend(BG, c, 0.55 if hot else 0.25))
        badge(s, MX + 0.2, y + 0.26, f"0{i + 1}", c, 12, w=0.55)
        text(s, MX + 0.95, y + 0.1, 5.4, 0.32, t, size=16, bold=True)
        text(s, MX + 0.95, y + 0.45, 5.4, 0.35, d, size=12, color=MUTED)
    x = MX + 6.9
    w = CW - 6.9
    card(s, x, 1.8, w, 4.85, fill=SURF2, line=blend(BG, RED, 0.4))
    text(s, x + 0.3, 2.0, w - 0.6, 0.3, "LIVE DEMO  ·  REAL-TIME PREDICTION", size=11, color=RED, bold=True, font=MONO)
    text(s, x + 0.3, 2.45, w - 0.6, 1.3,
         "“Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương.”", size=17, font=MONO)
    text(s, x + 0.3, 3.95, w - 0.6, 0.3, "KẾT QUẢ DỰ ĐOÁN", size=11, color=MUTED, bold=True, font=MONO)
    text(s, x + 0.3, 4.3, w - 0.6, 0.8, [[("NEGATIVE ", {"color": RED, "bold": True}), ("77,3%", {"color": TEXT})]],
         size=36, font=MONO)
    text(s, x + 0.3, 5.35, w - 0.6, 1.1, "streamlit run app.py  →  mở trình duyệt, chọn phân hệ “Dự đoán”.",
         size=12, color=MUTED, font=MONO)


def s13_features(prs):
    s = new_slide(prs, 13, "12 · Explainability", "Token TF-IDF nào kích hoạt quyết định?", 65,
                  "Với câu khó, mô hình xuất Negative 77,3%. Các token TF-IDF mạnh nhất là “thường_xuyên không”, “minh_bạch”, "
                  "“thường_xuyên”, “không lương”, “quản_lý” — đều là cụm than phiền. Bigram giúp bắt cụm phủ định mà unigram bỏ sót. "
                  "Đây là tính diễn giải của mô hình tuyến tính. (~65s)")
    tokens = [("thường_xuyên không", 0.605), ("minh_bạch", 0.438), ("thường_xuyên", 0.366),
              ("không lương", 0.351), ("quản_lý", 0.310), ("lương", 0.270), ("không", 0.126)]
    cd = CategoryChartData()
    cd.categories = [t for t, _ in tokens]
    cd.add_series("TF-IDF", [v for _, v in tokens])
    card(s, MX, 1.8, 7.4, 4.95, fill=SURF)
    text(s, MX + 0.25, 1.95, 6.9, 0.3, "TOP TOKEN TF-IDF TRONG CÂU", size=11, color=BLUE, bold=True, font=MONO)
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(MX + 0.15), Inches(2.3), Inches(7.1), Inches(4.35), cd)
    ch = gf.chart
    style_chart(ch)
    ch.category_axis.reverse_order = True
    ch.category_axis.tick_labels.font.name = MONO
    ch.value_axis.minimum_scale = 0
    ch.value_axis.maximum_scale = 0.7
    ch.value_axis.tick_labels.number_format = "0.0"
    ch.value_axis.tick_labels.number_format_is_linked = False
    pl = ch.plots[0]
    pl.gap_width = 50
    pl.has_data_labels = True
    pl.data_labels.number_format, pl.data_labels.number_format_is_linked = "0.000", False
    pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    pl.data_labels.font.size, pl.data_labels.font.bold = Pt(12), True
    pl.data_labels.font.color.rgb = rgb(TEXT)
    ser = pl.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(RED)
    x = MX + 7.7
    w = CW - 7.7
    card(s, x, 1.8, w, 2.75, fill=SURF2, line=blend(BG, RED, 0.4))
    text(s, x + 0.25, 1.95, w - 0.5, 0.3, "XÁC SUẤT DỰ ĐOÁN", size=11, color=RED, bold=True, font=MONO)
    for i, (lab, p, c) in enumerate([("Negative", 77.3, RED), ("Neutral", 21.4, YELLOW), ("Positive", 1.4, MINT)]):
        y = 2.4 + i * 0.7
        text(s, x + 0.25, y, 1.1, 0.35, lab, size=13, anchor=MSO_ANCHOR.MIDDLE)
        card(s, x + 1.4, y + 0.08, w - 2.7, 0.2, fill=SURF, line=None, radius=0.5)
        card(s, x + 1.4, y + 0.08, max(0.08, (w - 2.7) * p / 100), 0.2, fill=c, line=None, radius=0.5)
        text(s, x + w - 1.2, y, 0.95, 0.35, f"{p:.1f}%".replace(".", ","), size=13, bold=True, font=MONO, color=c,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    card(s, x, 4.75, w, 2.0)
    text(s, x + 0.25, 4.9, w - 0.5, 1.8, [
        [("Bigram quan trọng: ", {"bold": True, "color": BLUE}), ("“không lương”, “thường_xuyên không” bắt phủ định mà unigram bỏ sót.", {"color": MUTED})],
        [("Diễn giải được ", {"bold": True, "color": MINT}), ("nhờ mô hình tuyến tính trên TF-IDF.", {"color": MUTED})],
    ], size=13, spacing=8)


def s14_lessons(prs):
    s = new_slide(prs, 14, "13 · Tổng kết", "Thành tựu, bài học & hạn chế", 55,
                  "Thành tựu: pipeline hoàn chỉnh, đánh giá không rò rỉ, app chạy được. Bài học: với dữ liệu lệch phải dùng Macro F1, "
                  "SMOTE đặt trong Pipeline, khóa tập test. Hạn chế: nhãn nhiễu theo sao, Neutral khó, chưa hiểu ngữ cảnh sâu. (~55s)")
    cols = [
        ("THÀNH TỰU", MINT, ["Pipeline end-to-end trên 8.417 review", "5 mô hình, chọn bằng CV Macro F1",
                             "Final Test độc lập 1.683 mẫu", "Web demo Streamlit 5 phân hệ"]),
        ("BÀI HỌC", BLUE, ["Accuracy đánh lừa khi lệch 11:1 → dùng Macro F1", "SMOTE phải nằm trong Pipeline theo fold",
                           "Mô hình đơn giản (LR) thắng RF/Stacking trên TF-IDF", "Khóa tập test, chỉ dùng một lần"]),
        ("HẠN CHẾ", ORANGE, ["Nhãn suy ra từ sao → nhiễu", "Neutral & Negative F1 còn thấp (0,48 / 0,38)",
                             "Review nhiều vế dễ bị dự đoán lệch", "TF-IDF chưa nắm ngữ cảnh sâu"]),
    ]
    cw = (CW - 0.6) / 3
    for i, (t, c, items) in enumerate(cols):
        x = MX + i * (cw + 0.3)
        card(s, x, 1.8, cw, 4.95, fill=SURF2, line=blend(BG, c, 0.4))
        badge(s, x + 0.3, 2.05, t, c, 12, w=1.6)
        paras = [[("▸ ", {"color": c, "bold": True}), (it, {})] for it in items]
        text(s, x + 0.3, 2.75, cw - 0.6, 3.8, paras, size=15, spacing=14)


def s15_closing(prs):
    s = new_slide(prs, 15, "14 · Kết luận", "Kết luận & hướng phát triển", 35,
                  "Tóm tắt: đã xây dựng hệ thống phân tích cảm xúc ITviec hoàn chỉnh. Hướng mở rộng: ABSA phân tích theo khía cạnh, "
                  "LLM/transformer tiếng Việt. Cảm ơn GVHD và Hội đồng; mời Q&A / live demo. (~35s)")
    card(s, MX, 1.8, 6.0, 4.95, fill=SURF2)
    text(s, MX + 0.3, 2.0, 5.4, 0.3, "ĐÓNG GÓP CHÍNH", size=11, color=MINT, bold=True, font=MONO)
    text(s, MX + 0.3, 2.45, 5.4, 4.0, [
        [("▸ ", {"color": MINT, "bold": True}), ("Hệ thống 3 lớp cảm xúc end-to-end", {})],
        [("▸ ", {"color": MINT, "bold": True}), ("Logistic Regression + SMOTE: Macro F1 0,5714", {})],
        [("▸ ", {"color": MINT, "bold": True}), ("Insight văn hóa làm việc 5 công ty IT", {})],
        [("▸ ", {"color": MINT, "bold": True}), ("Web demo dự đoán real-time", {})],
    ], size=16, spacing=14)
    x = MX + 6.3
    w = CW - 6.3
    card(s, x, 1.8, w, 2.35)
    text(s, x + 0.3, 2.0, w - 0.6, 0.3, "HƯỚNG PHÁT TRIỂN", size=11, color=BLUE, bold=True, font=MONO)
    for i, (t, d, c) in enumerate([("ABSA", "Cảm xúc theo từng khía cạnh: lương, OT, quản lý", BLUE),
                                   ("LLM / PhoBERT", "Hiểu ngữ cảnh, xử lý review nhiều vế", YELLOW)]):
        y = 2.5 + i * 0.78
        badge(s, x + 0.3, y + 0.05, t, c, 11, w=1.7)
        text(s, x + 2.2, y + 0.06, w - 2.5, 0.6, d, size=13, color=MUTED, anchor=MSO_ANCHOR.TOP)
    card(s, x, 4.35, w, 2.4, fill=blend(SURF, MINT, 0.08), line=blend(BG, MINT, 0.5))
    text(s, x + 0.3, 4.6, w - 0.6, 0.9, "Xin cảm ơn!", size=40, bold=True, color=MINT)
    text(s, x + 0.3, 5.5, w - 0.6, 1.1,
         ["Cảm ơn GVHD và Hội đồng đã lắng nghe.", "Sẵn sàng Q&A và Live Demo."], size=15, color=TEXT, spacing=4)


# --------------------------------------------------------------------------- main
def build(out: Path):
    m, cv, cm, per_class, dist = load_metrics()
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    s01_cover(prs)
    s02_problem(prs)
    s03_pipeline(prs)
    s04_preprocessing(prs)
    s05_eda(prs)
    s06_tfidf(prs)
    s07_models(prs)
    s08_leaderboard(prs, cv)
    s09_final_test(prs, m, cm, per_class)
    s10_errors(prs, m)
    s11_insight(prs, dist)
    s12_demo(prs)
    s13_features(prs)
    s14_lessons(prs)
    s15_closing(prs)
    assert len(prs.slides) == TOTAL
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    print(f"Saved {out} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", type=Path, default=ROOT / "reports" / "slides" / "ITviec_Sentiment_Analysis.pptx")
    build(ap.parse_args().output)
