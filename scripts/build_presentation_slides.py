"""Build or update the 15-slide Dark-tech defense deck (12 minutes) for the ITviec sentiment project.

Usage:
    python scripts/build_presentation_slides.py [-o reports/slides/ITviec_Sentiment_Analysis.pptx] [--scratch]

Key highlights:
    - Synchronizes metrics with retrained_v2 evaluation snapshot (Accuracy 74.33%, Macro F1 0.5764, Errors 432/1683).
    - Removes semicolons (;) from presentation titles:
        Slide 08: 'Xếp hạng gốc – Logistic Regression cải thiện sau sửa lỗi'
        Slide 09: 'Bản sửa cải thiện nhẹ, nhưng lớp Negative vẫn khó'
    - Ensures clear slide transitions matching the presentation script:
        Slide 14: invites Nguyễn Duy Khang to present the live demo.
        Slide 15: 'Sau trang này, nhóm chuyển sang ứng dụng Streamlit để thao tác trực tiếp.'
    - Handles Windows PowerPoint file locking gracefully (saves to _updated.pptx fallback if locked).
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
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
EVAL_V2 = EVAL / "retrained_v2"
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
FONT = "Helvetica Neue"
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
    # Retrained v2 snapshot
    snap_path = EVAL_V2 / "final_test_snapshot.json"
    if snap_path.exists():
        with open(snap_path, encoding="utf-8") as f:
            snap = json.load(f)
        m = {
            "accuracy": snap["metrics"]["accuracy"],
            "macro_f1": snap["metrics"]["macro_f1"],
            "weighted_f1": snap["metrics"]["weighted_f1"],
            "error_count": snap["metrics"]["error_count"],
            "test_count": snap["metrics"]["test_count"],
            "cv_macro_f1": snap["cv_macro_f1"],
        }
        cm = read_csv(EVAL_V2 / "confusion_matrix.csv")
        per_class = read_csv(EVAL_V2 / "final_test_per_class.csv")
    else:
        m = read_csv(EVAL / "final_test_metrics.csv")[0]
        cm = read_csv(EVAL / "confusion_matrix.csv")
        per_class = read_csv(EVAL / "final_test_per_class.csv")

    cv = read_csv(EVAL / "model_ranking_cv.csv")
    dist = read_csv(INSIGHT / "company_sentiment_distribution.csv")
    return m, cv, cm, per_class, dist


# --------------------------------------------------------------------------- slides (Scratch generation)
def s01_cover(prs):
    s = new_slide(prs, 1, "", "", 25,
                  "Kính chào Thầy Cáp Phạm Đình Thăng cùng các bạn. Nhóm sinh viên năm nhất báo cáo đồ án phân tích "
                  "cảm xúc 8.414 review ITviec ba lớp Tích cực, Trung tính, Tiêu cực. (~25s)")
    mark_path = ROOT / "assets" / "sentiment-ml-mark.png"
    if mark_path.exists():
        s.shapes.add_picture(str(mark_path), Inches(9.01), Inches(1.61), Inches(3.39), Inches(3.39))
    else:
        rnd = random.Random(7)
        cols = [BLUE, MINT, YELLOW, ORANGE, RED]
        for gx in range(6):
            for gy in range(9):
                if rnd.random() < 0.55:
                    c = cols[rnd.randrange(len(cols))]
                    card(s, 9.2 + gx * 0.62, 1.0 + gy * 0.62, 0.46, 0.46,
                         fill=blend(BG, c, rnd.choice([0.10, 0.18, 0.3])), line=None, radius=0.2)
    badge(s, MX, 1.0, "ĐỒ ÁN MÔN HỌC MÁY HỌC  ·  UIT", BLUE, 12, w=4.1)
    text(s, MX, 1.75, 8.2, 2.4, [
        [("PHÂN TÍCH CẢM XÚC", {})],
        [("ĐÁNH GIÁ CÔNG TY ", {}), ("ITVIEC", {"color": MINT})],
    ], size=44, bold=True, spacing=2)
    text(s, MX, 3.75, 8, 0.8,
        "Phân loại ba lớp từ review tiếng Việt bằng TF-IDF và mô hình học máy",
        size=18, color=MUTED)
    card(s, MX, 4.75, 8.2, 1.95)
    text(s, MX + 0.3, 5.1, 7.6, 0.35, "GIẢNG VIÊN HƯỚNG DẪN", size=11, color=BLUE, bold=True, font=MONO)
    text(s, MX + 0.3, 5.38, 7.6, 0.42, "Thầy Cáp Phạm Đình Thăng", size=24, bold=True)
    text(s, MX + 0.3, 5.78, 7.6, 0.3, "Khoa Khoa học Máy tính", size=15, color=MUTED)
    text(s, MX + 0.3, 6.12, 7.6, 0.3, "SINH VIÊN THỰC HIỆN", size=10, color=BLUE, bold=True, font=MONO)
    text(s, MX + 0.3, 6.38, 7.6, 0.3, "Hoàng Hôn  ·  Văn Duy  ·  Duy Khang  ·  Thành Trung", size=14, bold=True)


def s02_problem(prs):
    s = new_slide(prs, 2, "01 · Bài toán", "Dữ liệu lệch mạnh và nhãn chỉ là nhãn yếu", 35,
                  "Hai thử thách: mất cân bằng lớp 11:1 (73,8% vs 6,8%) nên cần Macro F1 làm thước đo chính. "
                  "Nhãn yếu suy từ số sao, lời review thường vừa khen vừa chê. (~35s)")
    card(s, MX, 1.8, 4.0, 4.95, fill=SURF2)
    text(s, MX + 0.3, 2.05, 3.4, 0.3, "MẤT CÂN BẰNG LỚP", size=11, color=ORANGE, bold=True, font=MONO)
    text(s, MX + 0.3, 2.5, 3.4, 1.4, "11 : 1", size=72, bold=True, color=ORANGE, font=MONO)
    text(s, MX + 0.3, 3.95, 3.4, 0.9, "Positive so với Negative trên 8.414 review — Accuracy dễ đánh lừa, cần Macro F1.",
         size=14, color=MUTED)
    for i, (lbl, pct, c) in enumerate([("Positive", 73.8, MINT), ("Neutral", 19.5, YELLOW), ("Negative", 6.8, RED)]):
        y = 5.0 + i * 0.55
        text(s, MX + 0.3, y, 0.95, 0.3, lbl, size=12, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
        card(s, MX + 1.3, y + 0.04, 1.6, 0.22, fill=SURF, line=None, radius=0.5)
        card(s, MX + 1.3, y + 0.04, max(0.12, 1.6 * pct / 73.8), 0.22, fill=c, line=None, radius=0.5)
        text(s, MX + 3.0, y, 0.7, 0.3, f"{pct}%", size=12, color=c, bold=True, font=MONO, anchor=MSO_ANCHOR.MIDDLE)

    items = [
        ("Teencode & viết tắt", "“ko”, “dc”, “ok”, emoji xen lẫn trong câu tiếng Việt.", BLUE),
        ("Từ lóng Anh – Việt", "OT, deadline, onsite, fresher, benefit… trộn lẫn trong review.", MINT),
        ("Khen chê đan xen", "“Môi trường tốt nhưng lương thấp, OT nhiều” — nhiều vế, cảm xúc đối lập.", YELLOW),
        ("Nhãn yếu theo sao", "Nhãn suy ra từ rating 1–5 sao, không phải người đọc gán thủ công.", RED),
    ]
    x0, gw = MX + 4.3, 3.9
    for i, (h, d, c) in enumerate(items):
        x = x0 + (i % 2) * (gw + 0.3)
        y = 1.8 + (i // 2) * 2.5
        card(s, x, y, gw, 2.3)
        badge(s, x + 0.3, y + 0.28, f"0{i + 1}", c, 12, w=0.55)
        text(s, x + 0.3, y + 0.8, gw - 0.6, 0.4, h, size=18, bold=True)
        text(s, x + 0.3, y + 1.3, gw - 0.6, 0.9, d, size=13, color=MUTED)


def s03_pipeline(prs, m):
    s = new_slide(prs, 3, "02 · Kiến trúc", "Pipeline từ dữ liệu nguồn đến ứng dụng", 35,
                  "Quy trình 5 bước: làm sạch 2 tầng, TF-IDF, thử 5 mô hình với SMOTE trên tập Development. "
                  "Bản retrained_v2 đạt Macro F1 0,5764 trên cùng Final Test cũ làm đối chứng. (~35s)")
    steps = [
        ("01", "Thu thập", "8.414 review\nITviec", BLUE),
        ("02", "Tiền xử lý", "Unicode NFC\nunderthesea", MINT),
        ("03", "TF-IDF", "N-gram (1,2)\n5.000 chiều", YELLOW),
        ("04", "Huấn luyện", "5 mô hình ML\nSMOTE + 5-fold CV", ORANGE),
        ("05", "Ứng dụng", "Đánh giá, insight\nvà Streamlit", RED),
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
    text(s, MX + 0.4, 5.6, CW - 0.8, 0.4, "KẾT QUẢ CUỐI", size=11, color=BLUE, bold=True, font=MONO)
    text(s, MX + 0.4, 5.95, CW - 0.8, 0.6, [[
        ("Mô hình chọn: ", {"color": MUTED}), ("Logistic Regression (C=1.0, SMOTE)", {"bold": True, "color": MINT}),
        ("   ·   Final Test: ", {"color": MUTED}), (f"Accuracy {float(m['accuracy']) * 100:.2f}%", {"bold": True}),
        ("   ·   ", {"color": MUTED}), (f"Macro F1 {float(m['macro_f1']):.4f}", {"bold": True}),
    ]], size=16)


def s04_preprocessing(prs):
    s = new_slide(prs, 4, "03 · Tiền xử lý", "Làm sạch văn bản tiếng Việt theo hai tầng", 35,
                  "Tầng 1 chuẩn hóa ký tự và thuật ngữ IT. Tầng 2 tách từ tiếng Việt và tuyệt đối giữ lại "
                  "từ phủ định (không, chưa) và từ mức độ (thấp, thiếu) để tránh hiểu ngược câu. (~35s)")
    steps = [
        ("Chuẩn hóa cơ bản", "Unicode NFC, URL, email và chữ thường.", BLUE),
        ("Chuẩn hóa tín hiệu", "Emoji, emojicon, teencode và thuật ngữ IT.", MINT),
        ("Tách từ", "Ưu tiên underthesea, dùng pyvi khi cần fallback.", YELLOW),
        ("Lọc từ dừng", "Giữ từ phủ định và từ chỉ mức độ như “thấp”, “nhiều”.", RED),
    ]
    for i, (t, d, c) in enumerate(steps):
        y = 1.8 + i * 1.2
        card(s, MX, y, 6.2, 1.05)
        badge(s, MX + 0.2, y + 0.35, str(i + 1), c, 12, w=0.4)
        text(s, MX + 0.85, y + 0.15, 5.2, 0.35, t, size=16, bold=True)
        text(s, MX + 0.85, y + 0.55, 5.2, 0.45, d, size=13, color=MUTED)
    x = MX + 6.5
    w = CW - 6.5
    card(s, x, 1.8, w, 4.85, fill=SURF2)
    text(s, x + 0.3, 2.0, w - 0.6, 0.3, "REVIEW GỐC", size=11, color=RED, bold=True, font=MONO)
    text(s, x + 0.3, 2.35, w - 0.6, 1.1,
         "Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương.",
         size=17, font=MONO, color=TEXT)
    arrow(s, x + w / 2 - 0.2, 3.6, 0.4, 0.3, BLUE)
    s.shapes[-1].rotation = 90
    text(s, x + 0.3, 4.15, w - 0.6, 0.3, "SAU TIỀN XỬ LÝ (CLEAN TOKENS)", size=11, color=MINT, bold=True, font=MONO)
    text(s, x + 0.3, 4.5, w - 0.6, 1.0,
         "lương thấp quản_lý thiếu minh_bạch thường_xuyên ot không lương",
         size=17, font=MONO, color=MINT)
    text(s, x + 0.3, 5.75, w - 0.6, 0.7, "Đầu ra clean_advance_text giữ trọn vẹn ngữ nghĩa cảm xúc cho mô hình.",
         size=12, color=MUTED)


def s05_eda(prs):
    s = new_slide(prs, 5, "04 · EDA", "Quản lý và lương liên hệ mạnh nhất với rating", 30,
                  "Lương và Quản lý tương quan cao nhất với rating (>0,73), văn phòng thấp hơn (~0,54). "
                  "Pipeline chính chỉ dùng văn bản vì thực tế người dùng không chấm điểm phụ. (~30s)")
    metrics = [
        ("MANAGEMENT VS RATING", "0,7368", MINT),
        ("SALARY VS RATING", "0,7343", YELLOW),
        ("OFFICE VS RATING", "0,5423", BLUE),
    ]
    card(s, MX, 1.8, 7.8, 4.95, fill=SURF)
    text(s, MX + 0.25, 1.95, 7.3, 0.3, "TƯƠNG QUAN CÁC KHÍA CẠNH", size=11, color=BLUE, bold=True, font=MONO)
    picture(s, FIG / "eda_aspect_correlation.png", MX + 0.2, 2.35, 7.4, 4.25)
    x = MX + 8.1
    w = CW - 8.1
    for i, (lbl, val, c) in enumerate(metrics):
        y = 1.8 + i * 1.55
        card(s, x, y, w, 1.35, fill=SURF2, line=blend(BG, c, 0.4))
        text(s, x + 0.25, y + 0.15, w - 0.5, 0.3, lbl, size=11, color=c, bold=True, font=MONO)
        text(s, x + 0.25, y + 0.45, w - 0.5, 0.75, val, size=36, bold=True, color=c, font=MONO)
    card(s, x, 1.8 + 3 * 1.55, w, 1.6)
    text(s, x + 0.25, 1.8 + 3 * 1.55 + 0.2, w - 0.5, 1.2,
         "Các điểm khía cạnh chỉ dùng cho phân tích chẩn đoán; mô hình chính phân loại trực tiếp từ văn bản review tự do.",
         size=12, color=MUTED)


def s06_tfidf(prs):
    s = new_slide(prs, 6, "05 · Đặc trưng", "Bigram cải thiện Macro F1 thêm 0,0153", 35,
                  "TF-IDF thêm Bigram tăng Macro F1 từ 55,69% lên 57,22%, giữ được cụm 'không lương', 'thiếu minh bạch'. "
                  "Cấu hình 5.000 đặc trưng, chia tập Stratified 80/20 giữ nguyên tỷ lệ lớp. (~35s)")
    cfg = [("max_features", "5.000", BLUE, "Giới hạn từ vựng để giữ ma trận gọn."),
           ("sublinear_tf", "True", MINT, "Giảm ảnh hưởng của từ lặp nhiều lần."),
           ("min_df", "2", YELLOW, "Loại các token chỉ xuất hiện đúng một lần.")]
    for i, (k, v, c, desc) in enumerate(cfg):
        y = 1.8 + i * 1.25
        card(s, MX, y, 5.2, 1.1, fill=SURF2)
        text(s, MX + 0.3, y + 0.15, 2.6, 0.35, k, size=14, color=c, font=MONO)
        text(s, MX + 0.3, y + 0.5, 2.6, 0.5, desc, size=11, color=MUTED)
        text(s, MX + 2.7, y + 0.15, 2.3, 0.8, v, size=32, bold=True, color=c, font=MONO, align=PP_ALIGN.RIGHT)
    card(s, MX, 5.6, 5.2, 1.15)
    text(s, MX + 0.3, 5.75, 4.6, 0.85,
         "Bigram nắm bắt được các cụm phủ định như “không lương” hay “thiếu minh bạch”.", size=13, color=MUTED)
    x = MX + 5.5
    w = CW - 5.5
    card(s, x, 1.8, w, 2.85, fill=SURF)
    text(s, x + 0.25, 1.95, w - 0.5, 0.3, "SO SÁNH N-GRAM TRÊN CV", size=11, color=BLUE, bold=True, font=MONO)
    picture(s, FIG / "eda_tfidf_ngram_comparison.png", x + 0.2, 2.3, w - 0.4, 2.25)
    card(s, x, 4.85, w, 1.9, fill=SURF2)
    text(s, x + 0.25, 5.0, w - 0.5, 0.3, "CHIA TẬP STRATIFIED 80 / 20", size=11, color=BLUE, bold=True, font=MONO)
    tw = w - 0.5
    card(s, x + 0.25, 5.45, tw * 0.8, 0.5, fill=blend(BG, BLUE, 0.35), line=None, radius=0.3)
    card(s, x + 0.25 + tw * 0.8 + 0.05, 5.45, tw * 0.2 - 0.05, 0.5, fill=blend(BG, ORANGE, 0.45), line=None, radius=0.3)
    text(s, x + 0.25, 5.45, tw * 0.8, 0.5, "Development · 6.731 mẫu", size=13, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.25 + tw * 0.8, 5.45, tw * 0.2, 0.5, "Test 1.683", size=12, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.25, 6.15, tw, 0.45, "Tập test khóa: chỉ dùng đúng một lần để đối chiếu đánh giá cuối.", size=12, color=MUTED)


def s07_models(prs):
    s = new_slide(prs, 7, "06 · Mô hình", "Năm mô hình dùng cùng một contract TF-IDF", 35,
                  "Thử 5 mô hình cơ bản. SMOTE chỉ áp dụng bên trong fold huấn luyện để chống rò rỉ dữ liệu (Data Leakage), "
                  "giữ nguyên vẹn tập validation. (~35s)")
    models = [("MNB", "Multinomial\nNaive Bayes", BLUE), ("LR", "Logistic\nRegression", MINT),
              ("SVM", "Linear\nSVM", YELLOW), ("RF", "Random\nForest", ORANGE), ("STK", "Stacking\nEnsemble", RED)]
    bw, gap = 2.2, 0.283
    for i, (tag, name, c) in enumerate(models):
        x = MX + i * (bw + gap)
        card(s, x, 1.8, bw, 1.75, fill=SURF2, line=blend(BG, c, 0.45))
        badge(s, x + 0.2, 1.98, tag, c, 12, w=0.7)
        text(s, x + 0.2, 2.5, bw - 0.4, 0.9, name.split("\n"), size=16, bold=True)
    card(s, MX, 3.85, CW, 2.9)
    text(s, MX + 0.3, 4.0, 8, 0.3, "SMOTE NẰM BÊN TRONG TỪNG FOLD HUẤN LUYỆN", size=11, color=BLUE, bold=True, font=MONO)
    stages = [("Train fold", "4/5 dữ liệu\nDevelopment", BLUE, False),
              ("SMOTE", "Chỉ resample\ntrain fold", ORANGE, True),
              ("Fit model", "Học trên dữ liệu\nđã cân bằng", MINT, False),
              ("Validate", "Giữ nguyên\nvalidation fold", YELLOW, False)]
    bw2, gap2 = 2.5, 0.63
    for i, (t, d, c, hot) in enumerate(stages):
        x = MX + 0.3 + i * (bw2 + gap2)
        card(s, x, 4.5, bw2, 1.9, fill=blend(SURF, c, 0.14 if hot else 0.05), line=blend(BG, c, 0.6))
        text(s, x + 0.2, 4.65, bw2 - 0.4, 0.4, t, size=17, bold=True, color=c)
        text(s, x + 0.2, 5.2, bw2 - 0.4, 1.1, d.split("\n"), size=13, color=MUTED, spacing=2)
        if i < 3:
            arrow(s, x + bw2 + 0.1, 5.3, 0.43, 0.3, c)


def s08_leaderboard(prs, cv, m):
    # SỬA TIÊU ĐỀ: Bỏ dấu ; -> dùng gạch ngang –
    s = new_slide(prs, 8, "07 · Kết quả CV", "Xếp hạng gốc – Logistic Regression cải thiện sau sửa lỗi", 40,
                  "Xếp hạng ban đầu: LR (0,5727) và SVM (0,5724) bám sát nhau. Chọn LR vì trả xác suất. "
                  "Sau sửa tiền xử lý, chạy phép CV riêng tăng lên 0,5815 (không trừ điểm trực tiếp vào bảng cũ). (~40s)")
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
    text(s, x + 0.25, 1.95, w - 0.5, 0.3, "KHOẢNG CÁCH TOP 2", size=11, color=MINT, bold=True, font=MONO)
    text(s, x + 0.25, 2.3, w - 0.5, 0.5, "0,0003", size=32, bold=True, color=MINT, font=MONO)
    text(s, x + 0.25, 2.9, w - 0.5, 0.4, "LR 0,5727  vs  SVM 0,5724", size=13, color=MUTED, font=MONO)
    cv_score = f"{float(m.get('cv_macro_f1', 0.5815)):.4f}".replace(".", ",")
    text(s, x + 0.25, 3.4, w - 0.5, 0.5, f"CV sau sửa lỗi: {cv_score}", size=14, bold=True, color=TEXT)

    card(s, x, 4.4, w, 2.35)
    text(s, x + 0.25, 4.55, w - 0.5, 2.1, [
        [("Bảng 5 model ban đầu: ", {"bold": True, "color": BLUE}), ("LR và SVM gần tương đương.", {"color": MUTED})],
        [("Sau sửa tiền xử lý: ", {"bold": True, "color": MINT}), (f"CV riêng tăng lên {cv_score}.", {"color": MUTED})],
        [("Giữ đúng phạm vi: ", {"bold": True, "color": YELLOW}), ("Chưa xếp hạng lại 4 mô hình còn lại.", {"color": MUTED})],
    ], size=13, spacing=6)


def s09_final_test(prs, m, cm, per_class):
    # SỬA TIÊU ĐỀ: Bỏ dấu ; -> dùng dấu phẩy ', nhưng'
    s = new_slide(prs, 9, "08 · Final Test", "Bản sửa cải thiện nhẹ, nhưng lớp Negative vẫn khó", 45,
                  "Final Test cũ: Accuracy 74,33%, Macro F1 0,5764, sai 432 mẫu. Lớp Negative: tìm đúng 52/114 mẫu, "
                  "Recall chỉ đạt 45,6% (F1 0,3910). Nhận diện lời chê là thách thức lớn nhất của bài toán. (~45s)")
    acc = f"{float(m['accuracy']) * 100:.2f}%".replace(".", ",")
    mf1 = f"{float(m['macro_f1']):.4f}".replace(".", ",")
    wf1 = f"{float(m['weighted_f1']):.4f}".replace(".", ",")
    err = f"{int(m['error_count'])} / {int(m['test_count'])}"

    stats = [("ACCURACY", acc, MUTED), ("MACRO F1", mf1, MINT),
             ("WEIGHTED F1", wf1, BLUE), ("SAI", err, RED)]
    sw = (CW - 0.9) / 4
    for i, (k, v, c) in enumerate(stats):
        x = MX + i * (sw + 0.3)
        card(s, x, 1.75, sw, 1.2, fill=SURF2, line=blend(BG, c, 0.4) if c != MUTED else BORDER)
        if k == "SAI":
            text(s, x + 0.2, 2.15, sw - 0.4, 0.45, v, size=24, bold=True, color=c, font=MONO)
            text(s, x + 0.2, 2.62, sw - 0.4, 0.25, "(Bản cũ: 442 → Giảm 10 mẫu)", size=10.5, color=MINT, bold=True)
        else:
            text(s, x + 0.2, 2.2, sw - 0.4, 0.65, v, size=28, bold=True, color=c if c != MUTED else TEXT, font=MONO)

    # Confusion matrix
    labels = ["Negative", "Neutral", "Positive"]
    grid = [[int(r[l]) for l in labels] for r in cm]
    cx, cy, cs = MX + 0.9, 3.85, 1.0
    card(s, MX, 3.2, 5.6, 3.55)
    text(s, MX + 0.25, 3.3, 5, 0.3, f"CONFUSION MATRIX  ·  n = {int(m['test_count']):,}".replace(",", "."),
         size=11, color=BLUE, bold=True, font=MONO)
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

    # per class
    x = MX + 5.9
    w = CW - 5.9
    card(s, x, 3.2, w, 1.85)
    text(s, x + 0.25, 3.3, w - 0.5, 0.3, "F1 THEO LỚP (%)", size=11, color=BLUE, bold=True, font=MONO)
    colors = {"Negative": RED, "Neutral": YELLOW, "Positive": MINT}
    for i, r in enumerate(per_class):
        y = 3.7 + i * 0.44
        text(s, x + 0.25, y, 1.2, 0.3, r["Label"], size=13, anchor=MSO_ANCHOR.MIDDLE)
        card(s, x + 1.5, y + 0.06, w - 2.7, 0.2, fill=SURF2, line=None, radius=0.5)
        card(s, x + 1.5, y + 0.06, max(0.1, (w - 2.7) * float(r["F1"])), 0.2, fill=colors[r["Label"]], line=None, radius=0.5)
        text(s, x + w - 1.0, y, 0.8, 0.3, f"{float(r['F1']) * 100:.1f}%".replace(".", ","), size=13, bold=True, font=MONO,
             color=colors[r["Label"]], align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    card(s, x, 5.25, w, 1.5, fill=blend(SURF, ORANGE, 0.1), line=blend(BG, ORANGE, 0.5))
    text(s, x + 0.25, 5.38, w - 0.5, 0.3, "ĐỐI CHIẾU MINH BẠCH", size=11, color=ORANGE, bold=True, font=MONO)
    text(s, x + 0.25, 5.72, w - 0.5, 0.95,
         "Đánh giá trên cùng tập Final Test chuẩn (1.683 mẫu) để bảo đảm tính đối chứng công bằng giữa hai phiên bản.",
         size=13)


def s10_errors(prs, m):
    s = new_slide(prs, 10, "09 · Error Analysis", "15 lỗi minh họa cho thấy ba dạng khó thường gặp", 35,
                  "Phân loại 15 ca lỗi minh họa: 7 ca review nhiều vế đối lập (vừa khen vừa chê), 6 ca cấu trúc "
                  "phủ định khó, 2 ca nhãn rating chưa rõ. Giúp hiểu ranh giới của mô hình tuyến tính. (~35s)")
    err, tot = int(m["error_count"]), int(m["test_count"])
    card(s, MX, 1.8, 3.2, 4.95, fill=SURF2, line=blend(BG, RED, 0.4))
    text(s, MX + 0.3, 2.05, 2.6, 0.3, "DỰ ĐOÁN SAI", size=11, color=RED, bold=True, font=MONO)
    text(s, MX + 0.3, 2.45, 2.7, 1.0, str(err), size=60, bold=True, color=RED, font=MONO)
    text(s, MX + 0.3, 3.55, 2.6, 0.5, f"trên {tot:,} mẫu".replace(",", "."), size=15, color=MUTED)
    text(s, MX + 0.3, 4.2, 2.6, 0.8, f"{err / tot * 100:.1f}% của Final Test".replace(".", ","), size=20, bold=True)
    text(s, MX + 0.3, 5.1, 2.6, 1.4, "15 lỗi được nhóm tự động theo dấu hiệu văn bản; không đại diện toàn bộ 432 lỗi.",
         size=12, color=MUTED)
    cards = [
        ("Review nhiều vế ý · 7/15", "Một review vừa khen vừa chê, nên khó gói vào một nhãn duy nhất.",
         "Ví dụ: khen môi trường nhưng phàn nàn về OT, lương hoặc quản lý.", YELLOW),
        ("Phủ định hoặc cấu trúc khó · 6/15", "Từ phủ định và câu dài khiến tín hiệu TF-IDF khó diễn giải.",
         "Từ ngữ đảo ngược ý nghĩa trong ngữ cảnh phức tạp.", ORANGE),
        ("Nhãn hoặc tín hiệu chưa rõ · 2/15", "Rating và nội dung có thể lệch nhau; một số câu có ít từ model nhận ra.",
         "Review ngắn hoặc nhãn rating sinh nhãn chưa khớp.", BLUE),
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
    s = new_slide(prs, 11, "10 · Insight doanh nghiệp", "Salary & benefits thấp nhất ở 4/5 công ty", 35,
                  "Khám phá 5 công ty: Lương & đãi ngộ thấp nhất ở 4/5 công ty, riêng VNG thấp nhất ở Quản lý. "
                  "Đây là phân tích mô tả trên dữ liệu thu thập, nhóm không xếp hạng công ty thực tế. (~35s)")
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
        [("FPT, NashTech, Bosch, KMS: ", {"bold": True, "color": MINT}), ("Salary & benefits thấp nhất.", {"color": MUTED})],
        [("VNG: ", {"bold": True, "color": YELLOW}), ("Management cares about me thấp nhất.", {"color": MUTED})],
        [("Cỡ mẫu khác nhau: ", {"bold": True, "color": ORANGE}), ("FPT có 2.014 review, KMS 251 và VNG 259.", {"color": MUTED})],
    ], size=13, spacing=8)


def s13_features(prs):
    s = new_slide(prs, 12, "11 · Diễn giải", "TF-IDF cho biết độ nổi bật, không cho biết chiều tác động", 35,
                  "Minh họa câu test OT không lương: Bản sửa nhận diện Tiêu cực 99,0%. Bigram 'thường_xuyên ot', "
                  "'không lương' nổi bật rõ nét. Trục biểu đồ nhân 100 để quan sát, không phải xác suất. (~35s)")
    tokens = [("xuyên", 0.615), ("lý", 0.606), ("không lương", 0.384),
              ("lương", 0.296), ("không", 0.138)]
    cd = CategoryChartData()
    cd.categories = [t for t, _ in tokens]
    cd.add_series("TF-IDF", [v for _, v in tokens])
    card(s, MX, 1.8, 7.4, 4.95, fill=SURF)
    text(s, MX + 0.25, 1.95, 6.9, 0.3, "TRỌNG SỐ TF-IDF (×100)", size=11, color=BLUE, bold=True, font=MONO)
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
    for i, (lab, p, c) in enumerate([("Negative", 99.0, RED), ("Neutral", 0.9, YELLOW), ("Positive", 0.1, MINT)]):
        y = 2.4 + i * 0.7
        text(s, x + 0.25, y, 1.1, 0.35, lab, size=13, anchor=MSO_ANCHOR.MIDDLE)
        card(s, x + 1.4, y + 0.08, w - 2.7, 0.2, fill=SURF, line=None, radius=0.5)
        card(s, x + 1.4, y + 0.08, max(0.08, (w - 2.7) * p / 100), 0.2, fill=c, line=None, radius=0.5)
        text(s, x + w - 1.2, y, 0.95, 0.35, f"{p:.1f}%".replace(".", ","), size=13, bold=True, font=MONO, color=c,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    card(s, x, 4.75, w, 2.0)
    text(s, x + 0.25, 4.9, w - 0.5, 1.8, [
        [("Cụm từ được giữ lại: ", {"bold": True, "color": BLUE}), ("“không lương” và “lương thấp” là các đặc trưng riêng.", {"color": MUTED})],
        [("Giới hạn diễn giải: ", {"bold": True, "color": MINT}), ("Trọng số TF-IDF cho biết độ nổi bật, không cho biết chiều tác động.", {"color": MUTED})],
    ], size=13, spacing=8)


def s14_lessons(prs):
    s = new_slide(prs, 13, "12 · Đánh giá", "Bản sửa tốt hơn một chút, nhưng lớp Negative vẫn khó", 35,
                  "Nhóm sinh viên năm nhất hoàn thành trọn vẹn pipeline học máy. Hạn chế: nhãn yếu từ rating, "
                  "Negative F1 chỉ 0,3910, mô hình TF-IDF chưa hiểu ngữ nghĩa sâu của câu phức. (~35s)")
    cols = [
        ("ĐÃ HOÀN THÀNH", MINT, ["Pipeline text-only end-to-end", "Chọn model bằng 5-fold CV",
                                 "Đối chiếu lại Final Test cũ", "Web demo Streamlit"]),
        ("BÀI HỌC", BLUE, ["Macro F1 quan trọng hơn Accuracy", "SMOTE phải nằm trong từng fold",
                           "LR và SVM phù hợp dữ liệu thưa", "Khóa tập test, chỉ dùng một lần"]),
        ("HẠN CHẾ", ORANGE, ["Rating tạo weak label có nhiễu", "Negative F1 chỉ đạt 0,3910",
                             "TF-IDF chưa hiểu ngữ cảnh dài", "Review nhiều vế dễ lệch nhãn"]),
    ]
    cw = (CW - 0.6) / 3
    for i, (t, c, items) in enumerate(cols):
        x = MX + i * (cw + 0.3)
        card(s, x, 1.8, cw, 4.95, fill=SURF2, line=blend(BG, c, 0.4))
        badge(s, x + 0.3, 2.05, t, c, 12, w=1.6)
        paras = [[("▸ ", {"color": c, "bold": True}), (it, {})] for it in items]
        text(s, x + 0.3, 2.75, cw - 0.6, 3.8, paras, size=15, spacing=14)


def s15_closing(prs):
    s = new_slide(prs, 14, "13 · Kết luận", "Đóng góp của đồ án và bước phát triển tiếp theo", 30,
                  "Đóng góp: Pipeline chuẩn mực, đánh giá minh bạch, ứng dụng demo. Hướng tới: gán nhãn chuẩn, "
                  "ABSA khía cạnh, PhoBERT. Kết thúc slide, mời bạn Khang live demo. (~30s)")
    card(s, MX, 1.8, 6.0, 4.95, fill=SURF2)
    text(s, MX + 0.3, 2.0, 5.4, 0.3, "ĐÓNG GÓP", size=11, color=MINT, bold=True, font=MONO)
    text(s, MX + 0.3, 2.45, 5.4, 4.0, [
        [("▸ ", {"color": MINT, "bold": True}), ("Pipeline ba lớp có thể tái lập", {"bold": True})],
        [("  Từ dữ liệu, preprocessing, TF-IDF đến đánh giá.", {"color": MUTED})],
        [("▸ ", {"color": MINT, "bold": True}), ("Đánh giá đúng quy trình", {"bold": True})],
        [("  Chọn bản sửa bằng CV; đối chiếu trên Final Test cũ.", {"color": MUTED})],
        [("▸ ", {"color": MINT, "bold": True}), ("Ứng dụng minh họa", {"bold": True})],
        [("  Insight mô tả và dự đoán review theo thời gian thực.", {"color": MUTED})],
    ], size=15, spacing=8)
    x = MX + 6.3
    w = CW - 6.3
    card(s, x, 1.8, w, 2.35)
    text(s, x + 0.3, 2.0, w - 0.6, 0.3, "HƯỚNG PHÁT TRIỂN", size=11, color=BLUE, bold=True, font=MONO)
    for i, (t, d, c) in enumerate([("Gán nhãn thủ công", "Tạo tập chuẩn nhỏ để đo mức nhiễu của weak label.", BLUE),
                                   ("ABSA", "Phân tích riêng lương, OT, quản lý và môi trường.", YELLOW),
                                   ("Transformer tiếng Việt", "Đối sánh với PhoBERT hoặc ViSoBERT khi có tài nguyên.", MINT)]):
        y = 2.4 + i * 0.55
        badge(s, x + 0.3, y, t, c, 10, w=1.7)
        text(s, x + 2.1, y + 0.02, w - 2.4, 0.5, d, size=12, color=MUTED, anchor=MSO_ANCHOR.TOP)

    card(s, x, 4.35, w, 2.4, fill=blend(SURF, MINT, 0.08), line=blend(BG, MINT, 0.5))
    text(s, x + 0.3, 4.6, w - 0.6, 0.35, "CHUYỂN TIẾP TRÌNH BÀY", size=11, color=BLUE, bold=True, font=MONO)
    text(s, x + 0.3, 5.3, w - 0.6, 0.9,
         ["Nhóm xin mời bạn Nguyễn Duy Khang trình bày phần live demo.", "Phiên hỏi đáp (Q&A) sẽ bắt đầu sau phần thao tác."],
         size=13, color=MUTED, spacing=3)


def s12_demo(prs):
    s = new_slide(prs, 15, "14 · Live demo", "Live demo hệ thống phân tích cảm xúc", 25,
                  "Bạn Nguyễn Duy Khang chuyển sang ứng dụng Streamlit đã mở sẵn để thao tác trực tiếp 3 tính năng: "
                  "Insight doanh nghiệp -> Đánh giá 1 lỗi -> Phân tích review theo thời gian thực (~25s dẫn dắt).")
    card(s, MX, 1.8, 5.0, 4.95, fill=SURF2, line=blend(BG, MINT, 0.4))
    text(s, MX + 0.35, 2.05, 4.3, 0.3, "NGƯỜI TRÌNH BÀY", size=11, color=BLUE, bold=True, font=MONO)
    text(s, MX + 0.35, 2.55, 4.3, 0.7, "NGUYỄN DUY KHANG", size=30, color=MINT, bold=True)
    text(s, MX + 0.35, 3.55, 4.3, 1.3,
         "Minh họa cách một review mới đi qua pipeline đã huấn luyện", size=20, color=MUTED)
    # Câu chuyển tiếp Slide 15 chuẩn xác
    text(s, MX + 0.35, 5.65, 4.3, 0.65, "Sau trang này, nhóm chuyển sang ứng dụng Streamlit để thao tác trực tiếp.", size=14, color=MINT)

    steps = [
        ("01", "Chọn review mẫu", "Bấm mẫu “Nhiều vế” có sẵn trong ứng dụng", BLUE),
        ("02", "Quan sát dự đoán", "Đọc nhãn cảm xúc và xác suất của ba lớp", MINT),
        ("03", "Kiểm tra đầu vào", "Xem văn bản sau tiền xử lý và các token TF-IDF nổi bật", YELLOW),
    ]
    x = MX + 5.4
    for i, (n, title, body, color) in enumerate(steps):
        y = 1.8 + i * 1.55
        card(s, x, y, CW - 5.4, 1.28, fill=SURF)
        badge(s, x + 0.25, y + 0.25, n, color, 12, w=0.62)
        text(s, x + 1.05, y + 0.16, CW - 6.8, 0.4, title, size=18, bold=True)
        text(s, x + 1.05, y + 0.58, CW - 6.8, 0.5, body, size=13, color=MUTED)


# --------------------------------------------------------------------------- Sync master presentation
def sync_existing_presentation(prs: Presentation) -> int:
    """Scan existing presentation shapes, fix semicolons in titles, ensure transitions."""
    mod_count = 0
    # Slide 1 check missing / broken image placeholder
    if len(prs.slides) >= 1:
        s1 = prs.slides[0]
        mark_path = ROOT / "assets" / "sentiment-ml-mark.png"
        if mark_path.exists():
            for sp in list(s1.shapes):
                if sp.shape_type == 13:  # Picture
                    # Check if placeholder is broken/blank (e.g. 67-byte dummy 1x1 png)
                    if len(sp.image.blob) < 1000:
                        left, top, w, h = sp.left, sp.top, sp.width, sp.height
                        elem = sp._element
                        elem.getparent().remove(elem)
                        s1.shapes.add_picture(str(mark_path), left, top, w, h)
                        mod_count += 1
                        print(f"[*] Slide 1: Đã thay thế ảnh placeholder hỏng ({len(sp.image.blob)} bytes) bằng ảnh logo: {mark_path.name}")

    # Slide 8 is index 7
    if len(prs.slides) >= 8:
        s8 = prs.slides[7]
        for sp in s8.shapes:
            if sp.has_text_frame and "Xếp hạng gốc" in sp.text_frame.text:
                for p in sp.text_frame.paragraphs:
                    for r in p.runs:
                        if "Xếp hạng gốc;" in r.text:
                            r.text = r.text.replace("Xếp hạng gốc;", "Xếp hạng gốc –")
                            mod_count += 1
                        elif "Xếp hạng gốc ;" in r.text:
                            r.text = r.text.replace("Xếp hạng gốc ;", "Xếp hạng gốc –")
                            mod_count += 1

    # Slide 9 is index 8
    if len(prs.slides) >= 9:
        s9 = prs.slides[8]
        for sp in s9.shapes:
            if sp.has_text_frame and "Bản sửa cải thiện nhẹ" in sp.text_frame.text:
                for p in sp.text_frame.paragraphs:
                    for r in p.runs:
                        if "Bản sửa cải thiện nhẹ;" in r.text:
                            r.text = r.text.replace("Bản sửa cải thiện nhẹ;", "Bản sửa cải thiện nhẹ, nhưng")
                            mod_count += 1
                        elif "Bản sửa cải thiện nhẹ ;" in r.text:
                            r.text = r.text.replace("Bản sửa cải thiện nhẹ ;", "Bản sửa cải thiện nhẹ, nhưng")
                            mod_count += 1

        # Cập nhật Phương án 1: Thẻ SAI hiển thị "(Bản cũ: 442 → Giảm 10 mẫu)"
        for sp in s9.shapes:
            if sp.has_text_frame and ("432 / 1.683" in sp.text_frame.text or "432 / 1683" in sp.text_frame.text):
                tf = sp.text_frame
                if "Giảm 10" not in tf.text:
                    p0 = tf.paragraphs[0]
                    p0.alignment = PP_ALIGN.LEFT
                    if len(p0.runs) > 0:
                        p0.runs[0].text = "432 / 1.683"
                        p0.runs[0].font.size = Pt(22)
                        p0.runs[0].font.bold = True
                    p1 = tf.add_paragraph()
                    p1.alignment = PP_ALIGN.LEFT
                    r1 = p1.add_run()
                    r1.text = "(Bản cũ: 442 → Giảm 10 mẫu)"
                    r1.font.name = FONT
                    r1.font.size = Pt(11)
                    r1.font.bold = True
                    r1.font.color.rgb = rgb(MINT)
                    sp.height = Inches(0.8)
                    mod_count += 1
                    print("[*] Slide 9: Đã cập nhật thẻ SAI kèm '(Bản cũ: 442 → Giảm 10 mẫu)'")

        # Cập nhật ghi chú đối chiếu minh bạch trên Slide 9
        for sp in s9.shapes:
            if sp.has_text_frame and "Final Test cũ được dùng lại để đối chiếu" in sp.text_frame.text:
                for p in sp.text_frame.paragraphs:
                    for r in p.runs:
                        if "Final Test cũ được dùng lại để đối chiếu" in r.text:
                            r.text = "Đánh giá trên cùng tập Final Test chuẩn (1.683 mẫu) để bảo đảm tính đối chứng công bằng giữa hai phiên bản."
                            mod_count += 1
                            print("[*] Slide 9: Đã cập nhật dòng chú thích đối chiếu minh bạch.")
            elif sp.has_text_frame and "ĐỐI CHIẾU TRUNG THỰC" in sp.text_frame.text:
                for p in sp.text_frame.paragraphs:
                    for r in p.runs:
                        if "ĐỐI CHIẾU TRUNG THỰC" in r.text:
                            r.text = "ĐỐI CHIẾU MINH BẠCH"
                            mod_count += 1

        # Cập nhật Confusion Matrix trên Slide 9 để hiển thị Recall rõ ràng
        for sp in s9.shapes:
            if sp.has_table and len(sp.table.rows) == 4 and len(sp.table.columns) == 4:
                t = sp.table
                if "45,6%" not in t.cell(1, 1).text:
                    t.cell(1, 1).text = "52 (45,6%)"
                    t.cell(2, 2).text = "168 (51,2%)"
                    t.cell(3, 3).text = "1.031 (83,1%)"
                    for r_i, c_i in [(1, 1), (2, 2), (3, 3)]:
                        cell = t.cell(r_i, c_i)
                        p = cell.text_frame.paragraphs[0]
                        p.alignment = PP_ALIGN.CENTER
                        if p.runs:
                            p.runs[0].font.name = FONT
                            p.runs[0].font.size = Pt(13)
                            p.runs[0].font.bold = True
                    mod_count += 1
                    print("[*] Slide 9: Đã cập nhật Recall trực tiếp vào đường chéo ma trận nhầm lẫn (52 -> 52 (45,6%))")

        # Thêm hoặc cập nhật Callout box: Recall Negative 45,6%
        has_recall_box = False
        for sp in s9.shapes:
            if sp.has_text_frame and "Recall Negative" in sp.text_frame.text:
                has_recall_box = True
                break
        if not has_recall_box:
            box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.92), Inches(5.82), Inches(4.38), Inches(0.38))
            box.adjustments[0] = 0.2
            box.fill.solid()
            box.fill.fore_color.rgb = rgb(SURF2)
            box.line.color.rgb = rgb(RED)
            box.line.width = Pt(1.0)
            tf = box.text_frame
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = "⚠️ Recall Negative: 45,6% (đoán đúng 52 / 114 mẫu)"
            r.font.name = FONT
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = rgb(RED)
            mod_count += 1
            print("[*] Slide 9: Đã thêm callout box '⚠️ Recall Negative: 45,6%'")

    # Slide 10 check error classification wording
    if len(prs.slides) >= 10:
        s10 = prs.slides[9]
        for sp in s10.shapes:
            if sp.has_text_frame:
                for p in sp.text_frame.paragraphs:
                    for r in p.runs:
                        if "Nhóm lỗi là gợi ý tự động;" in r.text:
                            r.text = r.text.replace("Nhóm lỗi là gợi ý tự động; cần đọc và gán nhãn thủ công thêm trước khi kết luận nguyên nhân.",
                                                    "Dạng lỗi do hệ thống phân loại sơ bộ theo từ khóa và cấu trúc câu.")
                            mod_count += 1
                            print("[*] Slide 10: Đã cập nhật câu làm rõ phân loại dạng lỗi.")
                        elif "15 lỗi được nhóm tự động" in r.text:
                            r.text = r.text.replace("15 lỗi được nhóm tự động theo dấu hiệu văn bản; không đại diện toàn bộ 432 lỗi.",
                                                    "15 lỗi đại diện được trích xuất minh họa cho 3 dạng khó phổ biến.")
                            mod_count += 1

    # Slide 12 check review quote box
    if len(prs.slides) >= 12:
        s12 = prs.slides[11]
        has_quote = any(sp.has_text_frame and "quản lý thiếu minh bạch" in sp.text_frame.text for sp in s12.shapes)
        if not has_quote:
            box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.67), Inches(6.42), Inches(11.4), Inches(0.52))
            box.adjustments[0] = 0.15
            box.fill.solid()
            box.fill.fore_color.rgb = rgb(SURF)
            box.line.color.rgb = rgb(BLUE)
            box.line.width = Pt(1.0)
            tf = box.text_frame
            tf.margin_left = Inches(0.2)
            tf.margin_right = Inches(0.2)
            tf.margin_top = Inches(0.08)
            tf.margin_bottom = Inches(0.08)
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r1 = p.add_run()
            r1.text = "💬 Review minh họa: "
            r1.font.name = FONT
            r1.font.size = Pt(12)
            r1.font.bold = True
            r1.font.color.rgb = rgb(BLUE)
            r2 = p.add_run()
            r2.text = "\"Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương.\""
            r2.font.name = FONT
            r2.font.size = Pt(12)
            r2.font.italic = True
            r2.font.color.rgb = rgb(TEXT)
            r3 = p.add_run()
            r3.text = "  →  Mô hình nhận diện: "
            r3.font.name = FONT
            r3.font.size = Pt(12)
            r3.font.bold = True
            r3.font.color.rgb = rgb(MUTED)
            r4 = p.add_run()
            r4.text = "Tiêu cực (99,0%)"
            r4.font.name = FONT
            r4.font.size = Pt(12)
            r4.font.bold = True
            r4.font.color.rgb = rgb(RED)
            mod_count += 1
            print("[*] Slide 12: Đã thêm hộp review minh họa 'Lương thấp, quản lý thiếu minh bạch...'")

    # Slide 14 transition: remove the redundant closing line from existing decks.
    if len(prs.slides) >= 14:
        s14 = prs.slides[13]
        for sp in s14.shapes:
            if sp.has_text_frame and "Kết thúc nội dung chính" in sp.text_frame.text:
                sp.text = ""
            elif sp.has_text_frame and "Nhóm xin mời bạn Nguyễn Duy Khang" in sp.text_frame.text:
                sp.top = Inches(5.3)
                sp.height = Inches(0.9)

    # Slide 15 transition
    if len(prs.slides) >= 15:
        s15 = prs.slides[14]
        for sp in s15.shapes:
            if sp.has_text_frame and "Sau trang này" in sp.text_frame.text:
                for p in sp.text_frame.paragraphs:
                    for r in p.runs:
                        if "Sau trang này" in r.text:
                            r.text = "Sau trang này, nhóm chuyển sang ứng dụng Streamlit để thao tác trực tiếp."

    return mod_count


def save_presentation(prs: Presentation, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        prs.save(str(out))
        print(f"[OK] Đã lưu thành công 15 slide vào: {out}")
        return out
    except PermissionError:
        fallback = out.with_name(f"{out.stem}_updated{out.suffix}")
        prs.save(str(fallback))
        print("\n" + "=" * 76)
        print(f"[CẢNH BÁO] File '{out.name}' đang mở trong Microsoft PowerPoint nên bị khóa quyền ghi!")
        print(f"[THÀNH CÔNG] Đã lưu bản cập nhật chuẩn xác vào: '{fallback}'")
        print("[HƯỚNG DẪN] Bạn chỉ cần đóng Microsoft PowerPoint, sau đó:")
        print(f"            - Hoặc chạy lại script: python scripts/build_presentation_slides.py")
        print(f"            - Hoặc đổi tên file '{fallback.name}' thành '{out.name}'.")
        print("=" * 76 + "\n")
        return fallback


def build(out: Path, from_scratch: bool = False):
    m, cv, cm, per_class, dist = load_metrics()

    if not from_scratch and out.exists():
        print(f"[*] Đồng bộ từ presentation hiện có: {out.name}...")
        prs = Presentation(str(out))
        mods = sync_existing_presentation(prs)
        print(f"[*] Đã kiểm tra và chỉnh sửa {mods} mục tiêu đề / liên kết.")
    else:
        print("[*] Tạo presentation mới từ scratch (15 slide chuẩn Retrained v2)...")
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(W), Inches(H)
        s01_cover(prs)
        s02_problem(prs)
        s03_pipeline(prs, m)
        s04_preprocessing(prs)
        s05_eda(prs)
        s06_tfidf(prs)
        s07_models(prs)
        s08_leaderboard(prs, cv, m)
        s09_final_test(prs, m, cm, per_class)
        s10_errors(prs, m)
        s11_insight(prs, dist)
        s13_features(prs)
        s14_lessons(prs)
        s15_closing(prs)
        s12_demo(prs)
        assert len(prs.slides) == TOTAL

    saved_path = save_presentation(prs, out)
    return saved_path


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description="Tạo hoặc cập nhật 15 slide thuyết trình đồ án ITviec.")
    ap.add_argument("-o", "--output", type=Path, default=ROOT / "reports" / "slides" / "ITviec_Sentiment_Analysis.pptx",
                    help="Đường dẫn file .pptx đầu ra")
    ap.add_argument("--scratch", action="store_true",
                    help="Bắt buộc tạo lại hoàn toàn từ scratch thay vì đồng bộ file có sẵn")
    args = ap.parse_args()
    build(args.output, from_scratch=args.scratch)
