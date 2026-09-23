# Đánh giá bản tiền xử lý sửa lỗi

Bản này giữ nguyên chỉ số hàng Development/Final Test từ phiên bản gốc. TF-IDF được fit lại trên Development; Logistic Regression (`C=1.0`) + SMOTE được train lại. Chọn bản sửa dựa trên Stratified 5-Fold CV: Macro F1 **0.5708 → 0.5815**. Lần so sánh này fit TF-IDF riêng trong từng fold ở cả hai cấu hình.

Final Test 1.683 mẫu đã được nhóm sử dụng ở bản gốc; con số bên dưới là **đánh giá lại để so sánh sau sửa lỗi**, không phải phép kiểm thử độc lập mới. Không dùng nó để chọn quy tắc tiền xử lý.

| Chỉ số | Bản gốc | Bản sửa |
| --- | ---: | ---: |
| Accuracy | 0.7374 | 0.7433 |
| Macro F1 | 0.5714 | 0.5764 |
| Số lỗi | 442 | 432 |
| Recall Negative | 0.4474 | 0.4561 |

Ma trận nhầm lẫn (hàng = nhãn thật, cột = nhãn đoán; thứ tự Negative, Neutral, Positive):

```text
[[52, 41, 21], [56, 168, 104], [44, 166, 1031]]
```

Trong app, 15 lỗi minh họa của bản sửa được nhóm theo heuristic và **chưa được đọc, gán nguyên nhân thủ công**. Nhãn huấn luyện vẫn suy từ rating toàn review nên các câu ngắn hoặc vừa khen vừa chê còn có thể sai.
