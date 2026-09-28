"""Insert the Development metric-selection experiment into the Word report."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "final_report" / "Bao_Cao_Do_An_May_Hoc_ITviec.docx"
RESULT = ROOT / "reports" / "evaluation" / "metric_selection_ablation.json"
MODEL_RESULT = ROOT / "reports" / "evaluation" / "model_imbalance_ablation.json"
MARKER = "4.1.1. Ảnh hưởng của thước đo chọn cấu hình"
MODEL_MARKER = "4.1.2. So sánh class weight theo từng mô hình"


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    doc = Document(SOURCE)
    target = next(p for p in doc.paragraphs if p.text.startswith("4.2. So sánh các mô hình"))
    if not any(MARKER in paragraph.text for paragraph in doc.paragraphs):
        target.insert_paragraph_before(MARKER, style="Heading 3")
        target.insert_paragraph_before(
            "F1 là thước đo sau dự đoán, không phải bước xử lý được bật/tắt. Để xem thước đo ảnh hưởng đến lựa chọn ra sao, nhóm giữ Logistic Regression C = 1,0, cùng 6.731 mẫu Development và cùng Stratified 5-Fold CV; chỉ thay đổi n-gram và cách xử lý mất cân bằng. TF-IDF được fit trong fold train và SMOTE chỉ áp dụng trên fold train. Tập Final Test không tham gia phép chọn này."
        )
        target.insert_paragraph_before(
            "Bảng 4.1a. So sánh chọn cấu hình theo Accuracy và Macro F1 trên Development CV",
            style="Caption",
        )
        table = doc.add_table(rows=1, cols=4)
        table.style = "Table Grid"
        table.autofit = False
        for cell, value in zip(table.rows[0].cells, ("N-gram", "Cân bằng lớp", "Accuracy", "Macro F1")):
            cell.text = value
        for row in [result["no_text_baseline"], *result["configurations"]]:
            cells = table.add_row().cells
            for cell, value in zip(cells, (
                row["ngram"], row["strategy"],
                f"{row['cv_accuracy_mean']:.4f}".replace(".", ","),
                f"{row['cv_macro_f1_mean']:.4f}".replace(".", ","),
            )):
                cell.text = value
        format_table(table, (Cm(4.1), Cm(3.8), Cm(2.5), Cm(2.5)))
        target._p.addprevious(table._tbl)
        accuracy = max(result["configurations"], key=lambda item: item["cv_accuracy_mean"])
        macro_f1 = max(result["configurations"], key=lambda item: item["cv_macro_f1_mean"])
        smote = next(item for item in result["configurations"] if item["ngram"] == "Unigram + Bigram" and item["strategy"] == "SMOTE")
        target.insert_paragraph_before(
            f"Mốc không dùng đặc trưng văn bản luôn đoán lớp đông nhất: Accuracy {result['no_text_baseline']['cv_accuracy_mean']:.4f}, Macro F1 {result['no_text_baseline']['cv_macro_f1_mean']:.4f}. "
            f"Nếu chọn theo Accuracy, unigram + bigram không xử lý mất cân bằng đứng đầu: Accuracy {accuracy['cv_accuracy_mean']:.4f}, nhưng Macro F1 chỉ {accuracy['cv_macro_f1_mean']:.4f}. "
            f"Nếu chọn theo Macro F1, unigram + bigram với class weight đứng đầu: Macro F1 {macro_f1['cv_macro_f1_mean']:.4f} và Accuracy {macro_f1['cv_accuracy_mean']:.4f}. "
            f"Cấu hình SMOTE đang triển khai đạt Macro F1 {smote['cv_macro_f1_mean']:.4f} trong cùng phép thử. "
            "Các điểm này chỉ thuộc Development CV; Final Test không tham gia chọn cấu hình."
        )
    else:
        ngram_table = next(table for table in doc.tables if table.rows[0].cells[0].text == "N-gram")
        if not any("Không dùng văn bản" in row.cells[0].text for row in ngram_table.rows):
            row = ngram_table.add_row()
            baseline = result["no_text_baseline"]
            for cell, value in zip(row.cells, (
                baseline["ngram"], baseline["strategy"],
                f"{baseline['cv_accuracy_mean']:.4f}".replace(".", ","),
                f"{baseline['cv_macro_f1_mean']:.4f}".replace(".", ","),
            )):
                cell.text = value
            format_table(ngram_table, (Cm(4.1), Cm(3.8), Cm(2.5), Cm(2.5)))
        summary = next(p for p in doc.paragraphs if "Nếu chọn theo Accuracy, unigram + bigram" in p.text)
        if "Mốc không dùng đặc trưng" not in summary.text:
            baseline = result["no_text_baseline"]
            summary.text = (
                f"Mốc không dùng đặc trưng văn bản luôn đoán lớp đông nhất: Accuracy {baseline['cv_accuracy_mean']:.4f}, "
                f"Macro F1 {baseline['cv_macro_f1_mean']:.4f}. " + summary.text
            )
    if not any(MODEL_MARKER in paragraph.text for paragraph in doc.paragraphs):
        models = json.loads(MODEL_RESULT.read_text(encoding="utf-8"))
        target.insert_paragraph_before(MODEL_MARKER, style="Heading 3")
        target.insert_paragraph_before(
            "Nhóm giữ unigram + bigram TF-IDF và 5 fold Development, rồi so sánh không xử lý mất cân bằng, class weight và SMOTE cho từng mô hình với tham số cố định. Trong Stacking, class weight áp dụng cho Logistic Regression, Linear SVM, Random Forest và meta learner; Multinomial Naive Bayes không hỗ trợ class_weight."
        )
        target.insert_paragraph_before("Bảng 4.1b. Macro F1 CV theo mô hình và cách xử lý mất cân bằng", style="Caption")
        table = doc.add_table(rows=1, cols=4)
        table.style = "Table Grid"
        for cell, value in zip(table.rows[0].cells, ("Mô hình", "Không xử lý", "Class weight", "SMOTE")):
            cell.text = value
        for name in ("Multinomial Naive Bayes", "Logistic Regression", "Linear SVM", "Random Forest", "Stacking Ensemble"):
            cells = table.add_row().cells
            cells[0].text = name
            for i, strategy in enumerate(("Không xử lý", "Class weight", "SMOTE"), start=1):
                row = next(item for item in models["rows"] if item["model"] == name and item["strategy"] == strategy)
                cells[i].text = f"{row['cv_macro_f1_mean']:.4f}".replace(".", ",") if row["status"] == "measured" else "N/A"
        format_table(table, (Cm(5.0), Cm(2.9), Cm(2.9), Cm(2.9)))
        target._p.addprevious(table._tbl)
        target.insert_paragraph_before(
            "Đây là phép so sánh bổ sung với tham số cố định và tiền xử lý đã hiệu chỉnh, nên không thay thế bảng xếp hạng GridSearchCV ban đầu hay kết quả Final Test của model demo. Chi tiết điểm Accuracy và theo từng fold được lưu trong reports/evaluation/model_imbalance_ablation.json."
        )
    model_heading = next(paragraph for paragraph in doc.paragraphs if MODEL_MARKER in paragraph.text)
    if not any("Xét riêng từng cách xử lý mất cân bằng" in paragraph.text for paragraph in doc.paragraphs):
        model_heading.insert_paragraph_before(
            "Xét riêng từng cách xử lý mất cân bằng, kết hợp unigram và bigram luôn đạt Macro F1 cao hơn khi chỉ dùng một loại: "
            "không xử lý lần lượt là 0,4702 so với 0,4624 và 0,4239; với class weight là 0,5839 so với 0,5645 và 0,5510; "
            "với SMOTE là 0,5815 so với 0,5582 và 0,5369. Bigram bổ sung tín hiệu từ cụm hai từ, nhưng chỉ dùng bigram thì mất đi các tín hiệu từ đơn hữu ích."
        )
        model_heading.insert_paragraph_before(
            "Mốc không dùng văn bản chỉ đoán nhãn đông nhất trong mỗi fold, không phải một cấu hình TF-IDF có n-gram bằng không. "
            "Nó vẫn đạt Accuracy 0,7376 nhưng Macro F1 chỉ 0,2830 vì hầu như bỏ qua các lớp ít mẫu. "
            "Trong mỗi fold, cả Accuracy và Macro F1 được tính trên cùng một lượt dự đoán; F1 không phải một thành phần được bật hoặc tắt khi huấn luyện. "
            "Khác biệt nằm ở thước đo dùng để chọn cấu hình sau khi đánh giá."
        )
    if not any("Với class weight, Macro F1" in paragraph.text for paragraph in doc.paragraphs):
        target.insert_paragraph_before(
            "Với class weight, Macro F1 của Logistic Regression tăng từ 0,4702 lên 0,5839; Linear SVM từ 0,4139 lên 0,5762; "
            "Random Forest từ 0,3574 lên 0,5333; Stacking chỉ tăng nhẹ từ 0,5673 lên 0,5713. "
            "Multinomial Naive Bayes không có tham số class_weight nên ô tương ứng được ghi N/A, không được xem là điểm bằng không."
        )
        target.insert_paragraph_before(
            "SMOTE đạt điểm cao nhất trong các phương án đã thử cho Naive Bayes (0,5599) và Linear SVM (0,5817), "
            "còn class weight nhỉnh hơn trong Logistic Regression (0,5839), Random Forest (0,5333) và Stacking (0,5713). "
            "Vì tham số mô hình được giữ cố định và chênh lệch một số trường hợp rất nhỏ, bảng này chỉ minh họa tác động của cách cân bằng lớp, "
            "không chứng minh một chiến lược luôn tốt nhất. Model demo vẫn là Logistic Regression + SMOTE đã triển khai trước đó."
        )
    if not any("Thực nghiệm N-gram bổ sung sau hiệu chỉnh" in p.text for p in doc.paragraphs):
        original_conclusion = next(
            p for p in doc.paragraphs
            if p.text.startswith("Cấu hình kết hợp unigram và bigram cao hơn 0,0153 Macro F1")
        )
        paragraph = original_conclusion.insert_paragraph_before(
            "Thực nghiệm N-gram bổ sung sau hiệu chỉnh tiền xử lý còn kiểm tra bigram riêng. "
            "Với cùng Logistic Regression và class weight, Macro F1 CV của unigram, bigram và "
            "unigram + bigram lần lượt là 0,5645; 0,5510; 0,5839. "
            "Đây là một phép thử khác với Bảng 3.2; kết quả đầy đủ theo cả ba cách cân bằng lớp "
            "được trình bày tại Bảng 4.1a."
        )
        paragraph._p.replace(paragraph._p.get_or_add_pPr(), deepcopy(original_conclusion._p.get_or_add_pPr()))
    model_heading.paragraph_format.page_break_before = False
    harmonize_experiment_format(doc)
    temp = SOURCE.with_name(SOURCE.stem + ".metric-selection.tmp.docx")
    doc.save(temp)
    temp.replace(SOURCE)
    print(f"Updated {SOURCE}")


def format_table(table, widths) -> None:
    table.autofit = False
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = width
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)


def harmonize_experiment_format(doc) -> None:
    """Use the report's existing table/caption/body formatting for additions."""
    lecturer = next((p for p in doc.paragraphs if "Nguyễn Đình Hiển" in p.text), None)
    if lecturer is not None:
        for run in lecturer.runs:
            if "Nguyễn Đình Hiển" in run.text:
                run.text = run.text.replace("PGS.TS. Nguyễn Đình Hiển", "Thầy Cáp Phạm Đình Thăng")
    table_list_anchor = next(
        p for p in doc.paragraphs
        if p.style.name == "Normal" and p.text.startswith("Bảng 4.1. Xếp hạng năm mô hình")
    )
    for caption in (
        "Bảng 4.1a. So sánh chọn cấu hình theo Accuracy và Macro F1 trên Development CV",
        "Bảng 4.1b. Macro F1 CV theo mô hình và cách xử lý mất cân bằng",
    ):
        list_index = next(i for i, p in enumerate(doc.paragraphs) if p._p is table_list_anchor._p)
        if not any(p.text == caption for p in doc.paragraphs[:list_index]):
            entry = table_list_anchor.insert_paragraph_before(caption)
            entry._p.replace(entry._p.get_or_add_pPr(), deepcopy(table_list_anchor._p.get_or_add_pPr()))
    for paragraph in doc.paragraphs:
        if paragraph._p is table_list_anchor._p:
            break
        if paragraph.text.startswith(("Bảng 4.1a.", "Bảng 4.1b.")):
            value = paragraph.text
            paragraph._p.replace(paragraph._p.get_or_add_pPr(), deepcopy(table_list_anchor._p.get_or_add_pPr()))
            paragraph.text = value
    reference_table = next(t for t in doc.tables if t.rows[0].cells[0].text == "Hạng")
    reference_caption = next(
        p for p in doc.paragraphs
        if p.style.name == "Caption" and p.text.startswith("Bảng 4.1. Xếp hạng")
    )
    reference_body = next(p for p in doc.paragraphs if p.text.startswith("Bảng 4.2 trình bày"))
    width_sets = {
        "N-gram": (2600, 2200, 2135, 2136),
        "Mô hình": (3000, 2024, 2024, 2023),
    }
    for table in doc.tables:
        header = table.rows[0].cells[0].text
        if header not in width_sets or (
            header == "Mô hình" and table.rows[0].cells[1].text != "Không xử lý"
        ):
            continue
        widths = width_sets[header]
        if header == "N-gram":
            for row in table.rows[1:]:
                if row.cells[0].text.startswith("Không dùng văn bản"):
                    row.cells[0].text = "Không dùng văn bản"
        table.style = reference_table.style
        table.autofit = False
        table._tbl.replace(table._tbl.tblPr, deepcopy(reference_table._tbl.tblPr))
        grid = table._tbl.tblGrid
        for child in list(grid):
            grid.remove(child)
        for width in widths:
            col = OxmlElement("w:gridCol")
            col.set(qn("w:w"), str(width))
            grid.append(col)
        for row_index, row in enumerate(table.rows):
            if row_index == 0:
                tr_pr = row._tr.get_or_add_trPr()
                if tr_pr.find(qn("w:tblHeader")) is None:
                    tr_pr.append(OxmlElement("w:tblHeader"))
            for col_index, (cell, width) in enumerate(zip(row.cells, widths)):
                source_cell = reference_table.cell(0 if row_index == 0 else 1, 0)
                cell._tc.replace(cell._tc.get_or_add_tcPr(), deepcopy(source_cell._tc.get_or_add_tcPr()))
                cell._tc.get_or_add_tcPr().find(qn("w:tcW")).set(qn("w:w"), str(width))
                for paragraph in cell.paragraphs:
                    paragraph.alignment = (
                        WD_ALIGN_PARAGRAPH.LEFT if row_index and col_index == 0
                        else WD_ALIGN_PARAGRAPH.CENTER
                    )
                    for run in paragraph.runs:
                        run.font.size = Pt(11)
                        run.bold = row_index == 0 or (row_index > 0 and col_index == 0)
    for paragraph in doc.paragraphs:
        if paragraph.style.name == "Caption" and paragraph.text.startswith(("Bảng 4.1a.", "Bảng 4.1b.")):
            paragraph._p.replace(paragraph._p.get_or_add_pPr(), deepcopy(reference_caption._p.get_or_add_pPr()))
            prefix, rest = paragraph.text.split(". ", 1)
            paragraph.clear()
            label = paragraph.add_run(prefix + ". ")
            label.bold = True
            label.font.size = Pt(12)
            title = paragraph.add_run(rest)
            title.italic = True
            title.font.size = Pt(12)
    in_experiment = False
    for paragraph in doc.paragraphs:
        if paragraph.text.startswith(MARKER):
            in_experiment = True
        elif paragraph.text.startswith("4.2. So sánh các mô hình"):
            break
        if in_experiment and paragraph.style.name == "Normal" and paragraph.text.strip():
            paragraph._p.replace(paragraph._p.get_or_add_pPr(), deepcopy(reference_body._p.get_or_add_pPr()))
        if paragraph.text.startswith(("Mốc không dùng đặc trưng văn bản", "Đây là phép so sánh bổ sung")):
            paragraph.paragraph_format.space_before = Pt(12)
        if paragraph.text.startswith("Mốc không dùng đặc trưng văn bản"):
            paragraph.paragraph_format.keep_together = True


if __name__ == "__main__":
    main()
