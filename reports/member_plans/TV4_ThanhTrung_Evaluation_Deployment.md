# KẾ HOẠCH CHI TIẾT - THÀNH VIÊN 4: THÀNH TRUNG
**Đề tài:** Phân tích cảm xúc đánh giá ITviec  
**Môn học:** Máy học (Machine Learning)  
**Phân công:** `Model Evaluation, Error Analysis, Sentiment Insights & Demo Deployment`  
**Thời gian thực hiện:** 5 Ngày cốt lõi (Giai đoạn 3) & Phối hợp hoàn thiện báo cáo  

---

## 📌 I. DANH SÁCH NHIỆM VỤ CHI TIẾT (CHECKLIST)

### 🟢 Giai đoạn 1: Đánh giá mô hình & Phân tích lỗi (Error Analysis)
- [x] **Đánh giá trên tập Final Test độc lập (20% - 1.683 mẫu):**
  - Nhận mô hình tối ưu `models/best_sentiment_model.joblib` từ TV3.
  - Chạy dự đoán đúng **một lần duy nhất** trên tập Final Test độc lập (chống rò rỉ dữ liệu).
  - Tính toán các chỉ số đánh giá: **Macro F1-Score, Weighted F1-Score, Accuracy, Precision, Recall** theo từng lớp.
  - **Phân tích per-class chi tiết:** so sánh Precision, Recall, F1 riêng biệt cho từng lớp Positive / Neutral / Negative để phân tích lớp nào khó phân loại nhất.
- [x] **Bảng so sánh hiệu suất giữa các mô hình (Model Ranking):**
  - Lập bảng tổng hợp kết quả 5 mô hình: Accuracy, Macro F1, Weighted F1, thời gian huấn luyện.
  - Xếp hạng rõ ràng: Mô hình nào tốt nhất? Chênh lệch bao nhiêu? Lý giải vì sao (liên hệ đặc điểm dữ liệu TF-IDF).
- [x] **Trực quan hóa ma trận nhầm lẫn (Confusion Matrix):**
  - Vẽ Heatmap Confusion Matrix và Normalized Confusion Matrix.
  - Phân tích lớp nào bị dự đoán nhầm lẫn nhiều nhất (ví dụ: Neutral bị nhầm sang Positive do từ ngữ khen áp đảo).
- [x] **Phân tích lỗi sai chuyên sâu (Error Analysis):**
  - Lọc và phân loại các mẫu dự đoán sai thành các nhóm nguyên nhân cụ thể:
    1. Câu mang tính châm biếm, mỉa mai.
    2. Câu có cấu trúc ngữ pháp phức tạp hoặc chứa cả ý khen lẫn ý chê.
    3. Mâu thuẫn giữa nội dung review và số sao rating người dùng chấm (Label Noise).
- [x] **Đánh giá hiện tượng Overfitting / Underfitting:**
  - So sánh khoảng cách điểm số giữa tập Train CV và tập Final Test.

### 🟢 Giai đoạn 2: Phân tích Insight doanh nghiệp & Xây dựng Demo
- [x] **Chạy [notebooks/05_company_sentiment_insights.ipynb](../../notebooks/05_company_sentiment_insights.ipynb):**
  - Trích xuất WordCloud từ khóa Tích cực / Tiêu cực đặc trưng cho 3-5 công ty IT tiêu biểu.
  - Thống kê tỷ lệ hài lòng nhân viên theo từng khía cạnh (Lương, OT, Quản lý).
- [x] **Xây dựng ứng dụng Demo (Streamlit):**
  - Tạo giao diện web trực quan: Người dùng nhập văn bản đánh giá $\rightarrow$ Hệ thống tiền xử lý $\rightarrow$ Trích xuất TF-IDF $\rightarrow$ Mô hình ML dự đoán sắc thái cảm xúc kèm biểu đồ xác suất phần trăm theo thời gian thực.

### 🟢 Giai đoạn 3: Soạn thảo Báo cáo môn Máy học
- [x] **Viết nội dung Báo cáo:**
  - **Mục 3.4 & 3.5:** Bảng so sánh kết quả thực nghiệm toàn diện, biểu đồ Confusion Matrix và phần Phân tích lỗi (Error Analysis).
  - **Mục 5 & 6:** Phân tích Insight doanh nghiệp, đề xuất giải pháp thực tế, kết luận đề tài và hướng phát triển tương lai.

---

## 📦 II. ĐẦU VÀO & ĐẦU RA (INPUTS & OUTPUTS)

* **Đầu vào (Inputs):**
  - Model tốt nhất `models/best_sentiment_model.joblib` và tập Final Test từ TV3.
* **Đầu ra (Outputs bàn giao):**
  - Bảng tổng hợp số liệu đánh giá (Accuracy, Precision, Recall, Macro F1).
  - Biểu đồ Confusion Matrix và báo cáo Phân tích lỗi (Error Analysis).
  - Notebook hoàn chỉnh [notebooks/05_company_sentiment_insights.ipynb](../../notebooks/05_company_sentiment_insights.ipynb) và [notebooks/06_model_evaluation_error_analysis.ipynb](../../notebooks/06_model_evaluation_error_analysis.ipynb).
  - Mã nguồn ứng dụng Demo (Streamlit/Gradio).
