# Chương 5. Insight doanh nghiệp và Demo

Phân tích gồm 8.417 review thuộc 180 công ty. Để hạn chế kết luận từ mẫu nhỏ, case study chỉ chọn 5 công ty có nhiều review nhất: FPT Software, NashTech, Bosch Global Software Technologies, VNG Corporation và KMS Technology.

## 5.1. WordCloud theo sentiment

WordCloud Positive và Negative được tạo cho toàn bộ dữ liệu và riêng từng công ty. Hình ảnh giúp nhận diện nhanh các chủ đề xuất hiện thường xuyên, nhưng kích thước từ chỉ biểu diễn tần suất, không phải mức độ tác động.

## 5.2. Insight theo khía cạnh

Năm điểm khía cạnh được tổng hợp theo công ty: lương và phúc lợi, đào tạo, sự quan tâm của quản lý, văn hóa và không gian làm việc. FPT Software, NashTech, Bosch và KMS có điểm thấp nhất ở lương/phúc lợi; VNG thấp nhất ở sự quan tâm của quản lý. Đây là tín hiệu để HR ưu tiên khảo sát sâu hơn, không phải bằng chứng nhân quả.

## 5.3. Web Demo

Ứng dụng Streamlit gồm năm phân hệ: Tổng quan, Insight doanh nghiệp, Benchmark, Evaluation và Phân tích review thời gian thực. Luồng suy luận nạp đúng `text_tfidf_vectorizer.joblib` và `best_sentiment_model.joblib`, kiểm tra contract 5.000 đặc trưng, sau đó hiển thị ba xác suất và token TF-IDF nổi bật.

# Chương 6. Kết luận và hướng phát triển

Logistic Regression + SMOTE đạt Accuracy 73,74%, Macro F1 0,5714 và Weighted F1 0,7489 trên 1.683 mẫu Final Test. Macro F1 chỉ thấp hơn CV 0,0014, vì vậy chưa có dấu hiệu overfitting nghiêm trọng. Tuy nhiên, Negative Recall chỉ đạt 44,74%; đây là hạn chế quan trọng trong bối cảnh dữ liệu mất cân bằng.

Hướng phát triển gồm: gán nhãn thủ công một tập audit lớn hơn; tách sentiment theo khía cạnh thay vì ép một nhãn cho toàn review; thử mô hình ngữ cảnh tiếng Việt; hiệu chỉnh xác suất trên validation set; và theo dõi data drift khi triển khai. Mọi policy threshold tương lai phải được chọn trên validation/OOF, không tối ưu trên Final Test đã khóa.
