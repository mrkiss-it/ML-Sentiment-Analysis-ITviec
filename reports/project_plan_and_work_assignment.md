# KẾ HOẠCH & PHÂN CHIA CÔNG VIỆC ĐỒ ÁN MÔN HỌC MÁY HỌC
## ĐỀ TÀI: PHÂN TÍCH CẢM XÚC (SENTIMENT ANALYSIS) ĐÁNH GIÁ ITVIEC

- **Thời gian thực hiện:** 3 tuần (21 ngày)
- **Trạng thái dự án:** 🔄 **Giai đoạn 1 & 2 hoàn thành (TV1 + TV2 = 50%) ✅ | Giai đoạn 3 (TV3) sẵn sàng triển khai ⏳**
- **Danh sách thành viên:**
  1. **TV1: Hoàng Hôn** (Trưởng nhóm) - `Business Understanding, Data Processing & Report Management`
  2. **TV2: Văn Duy** - `Feature Engineering, Exploratory Data Analysis (EDA) & Data Splitting`
  3. **TV3: Duy Khang** - `Machine Learning Modeling, Hyperparameter Tuning & Cross-Validation`
  4. **TV4: Thành Trung** - `Model Evaluation, Error Analysis, Sentiment Insights & Demo Deployment`

---

## 👥 I. BẢNG PHÂN CHIA NHIỆM VỤ THEO VAI TRÒ (RACI MATRIX)

| Thành viên | Phân công | Nhiệm vụ kỹ thuật chi tiết | Phần Báo cáo phụ trách |
| :--- | :--- | :--- | :--- |
| **👑 TV1: Hoàng Hôn**<br>*(Trưởng nhóm)* | **Business & Data Processing** | - **Business Understanding:** Xác định mục tiêu bài toán phân loại cảm xúc đa lớp (Positive, Neutral, Negative), thiết kế luồng pipeline ML tổng thể.<br>- **Data Preprocessing:** Xây dựng module `src/preprocessing.py`: chuẩn hóa Unicode NFC, xử lý emoji/emojicon, dịch teencode, sửa lỗi chính tả, lọc stopwords, tách từ `underthesea` / `pyvi`.<br>- **Tạo dữ liệu sạch:** Gán nhãn cảm xúc và xuất `data/processed/reviews_cleaned.xlsx` bàn giao cho TV2 & TV3.<br>- **Quản lý chung:** Tổng hợp toàn văn Báo cáo & thiết kế Slide thuyết trình. | - **Mục 1:** Mục tiêu đề tài<br>- **Mục 3.2:** Quy trình tiền xử lý văn bản<br>- **Tổng hợp toàn bộ Báo cáo Word & Slide thuyết trình** |
| **👨‍💻 TV2: Văn Duy** | **Feature Engineering & EDA** | - **EDA:** Chạy `01_data_exploration_eda.ipynb`, phân tích phân bố số sao rating, độ dài review, mất cân bằng lớp, tương quan điểm khía cạnh với rating tổng.<br>- **Feature Engineering:** Xây dựng `src/features.py`: trích xuất đặc trưng **TF-IDF N-gram (1, 2)** với `sublinear_tf=True`, `max_features=5000`.<br>- **Data Splitting:** Phân chia Stratified Split 80% Development / 20% Final Test (khóa độc lập chống rò rỉ dữ liệu). | - **Mục 2:** Mô tả bộ dữ liệu & Phân chia tập<br>- **Mục 3.1:** Khám phá dữ liệu (EDA) & 9 biểu đồ trực quan<br>- **Mục 3.2 (Feature):** Lý thuyết trích xuất TF-IDF |
| **👨‍💻 TV3: Duy Khang** | **ML Modeling & Tuning** | - **Machine Learning Modeling:** Xây dựng `src/models.py`, chạy `03_sentiment_modeling_ml.ipynb` với **5 thuật toán ML**: Multinomial Naive Bayes, Logistic Regression, Linear SVM, Random Forest, Stacking Ensemble Classifier.<br>- **Handling Imbalance & Tuning:** Xử lý mất cân bằng bằng `class_weight='balanced'`, tinh chỉnh siêu tham số bằng Stratified 5-Fold Cross Validation trên tập Development.<br>- **Lưu trữ model:** Lưu model tốt nhất vào `models/best_sentiment_model.joblib`. | - **Mục 3.3:** Thiết kế các mô hình Machine Learning & Xử lý mất cân bằng<br>- **Mục 3.4 & 5.1 (Training):** Bảng số liệu Cross-Validation & Lựa chọn siêu tham số |
| **👨‍💻 TV4: Thành Trung** | **Evaluation, Insights & Demo** | - **Evaluation & Error Analysis:** Đánh giá mô hình tốt nhất trên tập Final Test độc lập (Macro F1, Accuracy, Precision, Recall), vẽ **Confusion Matrix**, phân tích các dạng lỗi sai thường gặp.<br>- **Overfitting/Underfitting:** Đánh giá chênh lệch giữa Train CV và Final Test.<br>- **Company Sentiment Insights:** Chạy `05_company_sentiment_insights.ipynb`, tạo WordCloud Tích cực/Tiêu cực theo từng công ty IT.<br>- **Deployment:** Xây dựng giao diện Demo web tương tác (Streamlit / Gradio). | - **Mục 3.4 & 3.5:** Bảng so sánh hiệu suất, Confusion Matrix & Phân tích lỗi (Error Analysis)<br>- **Mục 5 & 6:** Phân tích Insight doanh nghiệp, Kết luận & Hướng phát triển |

---

## 📅 II. TIMELINE THỰC HIỆN 3 TUẦN (21 NGÀY)

```mermaid
gantt
    title Lịch trình thực hiện Đồ án Môn học Máy học
    dateFormat  YYYY-MM-DD
    section Giai đoạn 1: Dữ liệu, EDA & Tiền xử lý
    TV1: Thiết lập Repo, Pipeline & Tiền xử lý text (Hoàng Hôn) :done, a1, 2026-08-28, 3d
    TV1: Gán nhãn & Xuất reviews_cleaned.xlsx (Hoàng Hôn)        :done, a2, after a1, 1d
    TV2: Thực hiện phân tích EDA & Xuất 9 biểu đồ (Văn Duy)      :done, a3, 2026-08-29, 4d
    TV2: Trích xuất TF-IDF & Đóng gói Artifacts (Văn Duy)        :done, a4, after a3, 3d

    section Giai đoạn 2: Huấn luyện, Tinh chỉnh & So sánh ML
    TV3: Huấn luyện 5 mô hình ML (Naive Bayes, SVM, LR, RF, Stacking) :active, b1, 2026-09-03, 4d
    TV3: Tinh chỉnh Hyperparameters & K-Fold CV (Duy Khang)     :b2, 2026-09-06, 4d
    TV3: Khóa model tốt nhất & Lưu checkpoint (Duy Khang)       :b3, 2026-09-09, 2d
    TV1 & TV2: Soạn thảo nội dung Báo cáo Mục 1, 2, 3           :done, b4, 2026-09-05, 5d

    section Giai đoạn 3: Đánh giá, Demo, Báo cáo & Slide
    TV4: Đánh giá Final Test & Trực quan Confusion Matrix (Trung):c1, 2026-09-10, 3d
    TV4: Phân tích lỗi sai (Error Analysis) & Overfitting (Trung) :c2, 2026-09-12, 3d
    TV4: Trích xuất WordCloud theo công ty & Xây Demo Web (Trung):c3, 2026-09-11, 4d
    TV1 & Cả nhóm: Tổng hợp Báo cáo Word/PDF hoàn chỉnh          :c4, 2026-09-14, 4d
    TV1 & Cả nhóm: Hoàn thiện Slide thuyết trình & Tập dượt      :c5, 2026-09-16, 3d
```

---

## 🎯 BẢNG GIAO HẸN SẢN PHẨM (DELIVERABLES)

| STT | Sản phẩm bàn giao | Người phụ trách chính | Trạng thái |
| :---: | :--- | :--- | :---: |
| 1 | Khởi tạo dự án & Từ điển `data/dictionaries/` | **TV1 (Hoàng Hôn)** | ✅ **Đã hoàn thành** |
| 2 | File dữ liệu sạch `data/processed/reviews_cleaned.xlsx` (8.417 mẫu) | **TV1 (Hoàng Hôn)** | ✅ **Đã hoàn thành** |
| 3 | Báo cáo EDA (9 biểu đồ) + Module đặc trưng `src/features.py` + Artifacts `models/` | **TV2 (Văn Duy)** | ✅ **Đã hoàn thành** |
| 4 | Notebook huấn luyện 5 mô hình ML + File model `best_sentiment_model.joblib` | **TV3 (Duy Khang)** | ⏳ **Sẵn sàng triển khai** |
| 5 | Bảng đánh giá Final Test, Confusion Matrix, Error Analysis & Demo Web | **TV4 (Thành Trung)** | ✅ **Hoàn thành** |
| 6 | Báo cáo toàn văn Word/PDF theo chuẩn yêu cầu môn Máy học | **TV1 (Hoàng Hôn)** & Nhóm | ⏳ **Giai đoạn cuối** |
| 7 | Slide thuyết trình PowerPoint báo cáo đồ án | **TV1 (Hoàng Hôn)** & Nhóm | ⏳ **Giai đoạn cuối** |
