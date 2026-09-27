# Thực nghiệm bổ sung: chọn cấu hình bằng Accuracy và Macro F1

F1 là thước đo đánh giá, không phải một kỹ thuật được bật/tắt trong lúc huấn luyện. Để kiểm tra ảnh hưởng của thước đo đến **quyết định chọn cấu hình**, nhóm đánh giá cùng 9 cấu hình bằng cả Accuracy và Macro F1. Một baseline không dùng văn bản được tính riêng bằng cách luôn đoán nhãn đông nhất trong fold train.

- Dữ liệu: 6.731 review Development theo đúng split cũ; không dùng Final Test để chọn.
- Mô hình cố định: Logistic Regression (`C=1.0`), TF-IDF tối đa 5.000 đặc trưng, `min_df=2`, `sublinear_tf=True`.
- Thay đổi hai yếu tố: unigram / bigram / cả hai và không cân bằng / `class_weight='balanced'` / SMOTE.
- Stratified 5-Fold CV, seed 2026. TF-IDF fit riêng trong fold train; SMOTE cũng chỉ chạy trong fold train.

| N-gram | Xử lý mất cân bằng | CV Accuracy | CV Macro F1 |
| --- | --- | ---: | ---: |
| Không dùng văn bản; đoán lớp đông nhất | Không áp dụng | 0,7376 | 0,2830 |
| Unigram | Không cân bằng | 0,7668 | 0,4624 |
| Unigram | Class weight | 0,7142 | 0,5645 |
| Unigram | SMOTE | 0,7216 | 0,5582 |
| Bigram | Không cân bằng | 0,7613 | 0,4239 |
| Bigram | Class weight | 0,7150 | 0,5510 |
| Bigram | SMOTE | 0,7103 | 0,5369 |
| Unigram + bigram | Không cân bằng | **0,7705** | 0,4702 |
| Unigram + bigram | Class weight | 0,7326 | **0,5839** |
| Unigram + bigram | SMOTE | 0,7422 | 0,5815 |

Nếu chọn theo Accuracy, cấu hình thắng là unigram + bigram **không xử lý mất cân bằng**: Accuracy 0,7705 nhưng Macro F1 chỉ 0,4702. Nếu chọn theo Macro F1, cấu hình thắng trong 9 phương án là unigram + bigram với **class weight**: Macro F1 0,5839, Accuracy 0,7326. Như vậy, thước đo chọn cấu hình ảnh hưởng đến quyết định; dùng Accuracy cao nhất làm mục tiêu dễ bỏ qua chất lượng của các lớp ít mẫu.

Class weight chỉ cao hơn SMOTE 0,0024 Macro F1 ở thí nghiệm này. Chênh lệch nhỏ chưa đủ để khẳng định class weight luôn tốt hơn. Model hiện chạy trên app vẫn là Logistic Regression + SMOTE (unigram + bigram), được chốt trong quy trình mô hình hóa trước đó. Bảng này là thí nghiệm bổ sung trên Development, **không phải kết quả Final Test của các cấu hình mới** và không thay đổi model đã triển khai.

Số liệu gốc và điểm theo từng fold: `reports/evaluation/metric_selection_ablation.json`; lệnh tái lập: `.venv/Scripts/python.exe scripts/run_metric_selection_ablation.py`.

## Class weight theo từng phương pháp

Một thí nghiệm bổ sung giữ cố định TF-IDF unigram + bigram và 5 fold Development, sau đó so sánh ba chiến lược cho Multinomial Naive Bayes, Logistic Regression, Linear SVM, Random Forest và Stacking Ensemble. Class weight không có tham số tương ứng trong Multinomial Naive Bayes nên cột đó ghi N/A. Với Stacking, class weight được đặt cho LR, SVM, RF và meta LR; Naive Bayes thành phần giữ nguyên.

| Mô hình | Không xử lý | Class weight | SMOTE |
| --- | ---: | ---: | ---: |
| Multinomial Naive Bayes | 0,4122 | N/A | 0,5599 |
| Logistic Regression | 0,4702 | **0,5839** | 0,5815 |
| Linear SVM | 0,4139 | 0,5762 | **0,5817** |
| Random Forest | 0,3574 | **0,5333** | 0,4813 |
| Stacking Ensemble | 0,5673 | **0,5713** | 0,5275 |

Các số là **CV Macro F1**, không phải điểm Final Test. Class weight cải thiện LR, SVM và RF so với không xử lý, nhưng không phải lúc nào cũng cao nhất: ở Linear SVM, SMOTE nhỉnh hơn. Stacking không cải thiện nhiều khi thêm class weight và giảm điểm với SMOTE trong phép thử này. Vì thế, không có một cách cân bằng lớp tốt nhất cho mọi mô hình.

Các model dùng tham số cố định để so sánh tác động của chiến lược mất cân bằng. Đây là phép thử bổ sung, khác bảng GridSearchCV ban đầu. Chi tiết và điểm từng fold: `reports/evaluation/model_imbalance_ablation.json`; lệnh chạy: `.venv/Scripts/python.exe scripts/run_model_imbalance_ablation.py`.
