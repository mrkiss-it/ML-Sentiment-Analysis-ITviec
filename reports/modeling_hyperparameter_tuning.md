# Huấn luyện, xử lý mất cân bằng và tinh chỉnh siêu tham số cho bài toán phân loại cảm xúc đánh giá ITviec

*(Nội dung tương ứng Mục 4.1, 4.2 và 5.1 của [De_Cuong_Do_An_Mon_Hoc_May_Hoc.md](De_Cuong_Do_An_Mon_Hoc_May_Hoc.md); Mục 3.3 trong đề cương nội bộ [final_report_outline.md](final_report_outline.md))*

## Nguyên tắc thực nghiệm

Toàn bộ nội dung dưới đây được tính toán **chỉ trên tập Development (`X_train`, 6.731 mẫu, 80%)** được phân chia trong bước trích xuất đặc trưng, bằng Stratified 5-Fold Cross Validation (`random_state=2026`). Tập Final Test (`X_test`, 1.683 mẫu, 20%) bị khóa theo `artifact_manifest.json` (`final_test_policy: locked_not_evaluated_by_tv2`) và **không được đụng đến ở giai đoạn này** — đây là nguyên tắc chống rò rỉ đánh giá (evaluation leakage), đảm bảo con số Final Test công bố ở bước đánh giá kiểm thử độc lập phản ánh đúng khả năng tổng quát hóa của mô hình trên dữ liệu chưa từng được nhìn thấy trong suốt quá trình chọn và tune mô hình.

## 4.1. Thiết kế các mô hình Machine Learning

Năm mô hình được cài đặt trong `src/models.py` (hàm `build_base_models` và `build_stacking`), tất cả nhận đầu vào là ma trận đặc trưng TF-IDF thưa (`5.000` chiều) được trích xuất từ văn bản.

**1. Multinomial Naive Bayes (MNB) — mô hình Baseline.** Ước lượng xác suất hậu nghiệm từng lớp qua định lý Bayes với giả định ngây thơ (naive) rằng các đặc trưng độc lập có điều kiện với nhau khi biết nhãn. Tham số `alpha` là hệ số làm trơn Laplace, tránh xác suất bằng 0 với các n-gram chưa xuất hiện trong lớp. Giả định độc lập này bị vi phạm rõ với đặc trưng n-gram (1,2), vì một bigram luôn tương quan chặt với hai unigram thành phần của nó — đây là nguyên nhân chính khiến MNB là mô hình yếu nhất trong năm mô hình (xem Mục 5.1).

**2. Logistic Regression (LR).** Mô hình tuyến tính tối ưu hàm mất mát Log-loss (Cross-Entropy) qua hồi quy Softmax đa lớp, có điều chuẩn L2 với tham số `C` (nghịch đảo cường độ regularization: `C` càng nhỏ, mô hình càng bị phạt nặng để giữ trọng số nhỏ, giảm overfitting). Ranh giới quyết định là một siêu phẳng tuyến tính trong không gian 5.000 chiều — phù hợp tự nhiên với không gian TF-IDF vốn gần như khả phân tuyến tính đối với các cụm từ mang cực tính rõ rệt (*"rất tốt"*, *"quá tệ"*).

**3. Support Vector Machine — Linear SVM (`LinearSVC`).** Tìm siêu phẳng phân cách cực đại hóa biên độ (margin) giữa các lớp, tối ưu hàm mất mát Hinge Loss. Cùng là mô hình tuyến tính như LR nhưng mục tiêu tối ưu khác (margin thay vì xác suất), nên thường cho ranh giới quyết định ổn định hơn khi dữ liệu có nhiễu nhãn — một đặc điểm quan trọng ở đây vì nhãn `sentiment` là **nhãn yếu** suy ra từ `Rating`, không phải nhãn vàng.

**4. Random Forest Classifier (RF).** Ensemble Bagging của nhiều cây quyết định, mỗi cây huấn luyện trên một bootstrap sample và một tập con ngẫu nhiên đặc trưng, sau đó biểu quyết đa số. RF xử lý tốt quan hệ phi tuyến trên dữ liệu dạng bảng, nhưng mỗi lần phân nhánh (split) chỉ dựa trên **một** đặc trưng đơn lẻ (axis-aligned split). Trên ma trận TF-IDF thưa 5.000 chiều — nơi tín hiệu cảm xúc thường nằm ở *tổ hợp tuyến tính* của hàng trăm từ khóa cùng lúc chứ không phải một từ riêng lẻ — cơ chế này khiến RF khó khai thác hết thông tin so với LR/SVM (xem Mục 5.1).

**5. Stacking Ensemble Classifier.** Kết hợp bốn base learners theo đúng thứ tự trong kế hoạch nhóm — `[MNB, LR, LinearSVC, RF]` — qua một meta-learner Logistic Regression. Cơ chế: với `cv=5`, mỗi base learner tạo dự đoán out-of-fold (dự đoán trên phần dữ liệu nó chưa được huấn luyện) trên toàn bộ tập train; các dự đoán out-of-fold này trở thành đặc trưng đầu vào để huấn luyện meta-learner. Cách làm này tránh việc meta-learner học trên dự đoán "quá tự tin" (overfit) của chính base learner trên dữ liệu nó đã thấy. Stacking chỉ thực sự hiệu quả khi các base learner có **lỗi ít tương quan** với nhau; ở đây ba trong bốn base learner (MNB, LR, SVM) đều là mô hình tuyến tính trên cùng một không gian đặc trưng, nên phần bổ sung thông tin từ Stacking là hạn chế (xem Mục 5.1).

## 4.2. Xử lý mất cân bằng dữ liệu và tinh chỉnh siêu tham số

### 4.2.1. Hai chiến lược xử lý mất cân bằng

Dữ liệu mất cân bằng nghiêm trọng (Positive : Neutral : Negative ≈ 11 : 3 : 1). Hai chiến lược được cài đặt trong `build_variant()` và so sánh bằng CV Macro F1 trên `X_train`:

- **`class_weight='balanced'`**: điều chỉnh hàm mất mát để phạt nặng hơn khi mô hình đoán sai các lớp thiểu số, không sinh thêm dữ liệu.
- **SMOTE (Synthetic Minority Over-sampling Technique)**: sinh mẫu tổng hợp cho lớp thiểu số bằng nội suy tuyến tính giữa một mẫu và các láng giềng gần nhất (k-NN) của nó trong không gian đặc trưng.

**Nguyên tắc chống rò rỉ dữ liệu bắt buộc:** SMOTE được bọc bên trong một `imblearn.pipeline.Pipeline` cùng với classifier (bước `smote` → bước `clf`), thay vì áp dụng lên toàn bộ `X_train` trước khi chia CV. Nếu sinh mẫu tổng hợp trước rồi mới chia fold, một mẫu tổng hợp ở fold train có thể được nội suy từ một mẫu thật đang nằm ở fold validation của chính vòng lặp đó — khiến điểm CV bị đánh giá lạc quan giả tạo (data leakage). Với Pipeline, SMOTE chỉ `fit_resample` trên phần train của từng fold, giữ fold validation nguyên vẹn 100% dữ liệu thật.

Kết quả so sánh (CV Macro F1 Mean, Stratified 5-Fold trên `X_train`):

| Model | `class_weight='balanced'` | SMOTE | Chiến lược được chọn |
|---|---:|---:|---|
| Multinomial Naive Bayes | thấp hơn | cao hơn | **SMOTE** |
| Logistic Regression | thấp hơn | cao hơn | **SMOTE** |
| Linear SVM | cao hơn | thấp hơn | **`class_weight='balanced'`** |
| Random Forest | cao hơn | thấp hơn | **`class_weight='balanced'`** |

*(Bảng số liệu đầy đủ với độ lệch chuẩn nằm trong output của `notebooks/03_sentiment_modeling_ml.ipynb`, Mục 3.1 của notebook — hàm `compare_imbalance_strategies`.)*

**Giải thích sự khác biệt giữa các model:** MNB và LR là các mô hình xác suất/tuyến tính học trực tiếp từ *tần suất xuất hiện* của mẫu trong mỗi lớp — khi lớp thiểu số (Negative, 570 mẫu gốc) được nhân bản/nội suy thêm bằng SMOTE, chúng có nhiều "bằng chứng" hơn để ước lượng đúng vùng quyết định cho lớp đó. Ngược lại, Linear SVM đã tối ưu trực tiếp *margin* giữa các lớp thông qua trọng số lớp trong hàm mất mát Hinge — việc thêm mẫu tổng hợp gần biên quyết định có xu hướng làm nhiễu margin thay vì cải thiện nó. Random Forest với `class_weight='balanced'` đã đủ mạnh để bù mất cân bằng qua việc lấy mẫu có trọng số ở mỗi cây; mẫu SMOTE tổng hợp (vốn nằm trên đường nối giữa các điểm thật, không phải điểm thật) có thể tạo ra các vùng chia (split) giả tạo, dễ dẫn đến overfitting nhẹ trên tập train mà không cải thiện tổng quát hóa.

### 4.2.2. Tinh chỉnh siêu tham số (Hyperparameter Tuning)

Áp dụng `GridSearchCV` với `scoring='f1_macro'` trên `StratifiedKFold(n_splits=5, shuffle=True, random_state=2026)`, sử dụng đúng chiến lược mất cân bằng đã chọn ở trên cho từng model (hàm `tune_models`):

| Model | Siêu tham số & lưới tìm kiếm | Giá trị tối ưu | CV Macro F1 |
|---|---|---|---:|
| Multinomial Naive Bayes | `alpha ∈ {0.1, 0.5, 1.0, 2.0}` | `alpha = 0.5` | 0.5534 |
| Logistic Regression | `C ∈ {0.1, 1.0, 3.0, 10.0}` | `C = 1.0` | **0.5727** |
| Linear SVM | `C ∈ {0.01, 0.1, 1.0, 10.0}` | `C = 0.1` | 0.5724 |
| Random Forest | `n_estimators ∈ {200, 400}`, `max_depth ∈ {None, 30, 50}` | `n_estimators=400`, `max_depth=30` | 0.5664 |
| Stacking Ensemble (`cv=5`) | base = 4 model đã tune ở trên → meta = Logistic Regression | — | 0.5560 |

**Lý giải các giá trị tối ưu được chọn:**
- `alpha = 0.5` (nhỏ hơn mặc định `1.0`): dữ liệu có 5.000 đặc trưng nhưng chỉ 6.731 mẫu train, nên làm trơn Laplace nhẹ hơn giúp mô hình tin tưởng hơn vào tần suất từ thực tế quan sát được thay vì làm phẳng quá mức.
- `C = 1.0` cho Logistic Regression: mức regularization vừa phải, cân bằng giữa việc khớp đủ tín hiệu từ 5.000 đặc trưng thưa và tránh overfit trên các từ hiếm.
- `C = 0.1` cho Linear SVM (nhỏ hơn LR đáng kể): SVM với margin cứng nhạy cảm hơn với nhiễu nhãn (nhãn yếu suy từ Rating) khi `C` lớn — giá trị nhỏ buộc mô hình chấp nhận margin rộng hơn, đánh đổi một số điểm bị phân loại sai trong tập train để đổi lấy khả năng tổng quát hóa tốt hơn.
- `n_estimators=400, max_depth=30` cho Random Forest: cần nhiều cây (400) để giảm phương sai khi mỗi cây chỉ nhìn thấy một tập con nhỏ trong 5.000 đặc trưng thưa; `max_depth=30` (thay vì không giới hạn) giới hạn độ sâu để giảm overfitting vào các tổ hợp từ hiếm gặp chỉ xuất hiện vài lần trong tập train.

## 5.1. So sánh hiệu suất giữa các mô hình và lựa chọn mô hình cuối cùng

### Bảng tổng hợp kết quả (Stratified 5-Fold CV, tập Development)

| Xếp hạng | Model | CV Macro F1 | Chênh lệch so với hạng 1 |
|:---:|---|---:|---:|
| 1 | **Logistic Regression** | **0.5727** | — |
| 2 | Linear SVM | 0.5724 | −0.0003 |
| 3 | Random Forest | 0.5664 | −0.0063 |
| 4 | Stacking Ensemble | 0.5560 | −0.0167 |
| 5 | Multinomial Naive Bayes | 0.5534 | −0.0193 |

**Mô hình được chọn: Logistic Regression** (`C=1.0`, chiến lược SMOTE), CV Macro F1 = 0.5727. Chênh lệch với Linear SVM (hạng 2) chỉ 0.0003 — về mặt thống kê hai mô hình gần như tương đương, nhưng Logistic Regression được ưu tiên vì (a) điểm CV cao nhất trong 5 lần lặp, và (b) chi phí suy luận rẻ hơn cho bước triển khai Demo ở Chương 5 (trả về xác suất trực tiếp qua `predict_proba`, không cần calibrate như `LinearSVC`).

### Tại sao Linear SVM và Logistic Regression vượt trội hơn Naive Bayes và Random Forest trên TF-IDF?

Đây là câu hỏi trọng tâm mà đề cương yêu cầu lý giải (Mục 5.1, De_Cuong):

1. **Không gian đặc trưng thưa, chiều cao, gần khả phân tuyến tính.** TF-IDF với n-gram (1,2) và 5.000 đặc trưng tạo ra một không gian mà tín hiệu cảm xúc thường thể hiện qua *sự hiện diện có trọng số* của một tập từ khóa mang cực tính (*"tệ"*, *"tốt"*, *"OT"*, *"phúc lợi"*...). Một tổ hợp tuyến tính của các trọng số TF-IDF này (chính là điều LR và SVM học được qua vector trọng số `w`) đã đủ biểu diễn ranh giới quyết định giữa 3 lớp cảm xúc, mà không cần mô hình phi tuyến phức tạp hơn.

2. **Tỷ lệ chiều dữ liệu / số mẫu cao (5.000 chiều / 6.731 mẫu).** Trong chế độ này, các mô hình tuyến tính có độ phức tạp (VC-dimension) phù hợp với lượng dữ liệu hiện có, trong khi các mô hình phi tuyến mạnh hơn (Random Forest) có xu hướng overfit vào các tổ hợp từ hiếm gặp đặc thù của tập train, làm giảm khả năng tổng quát hóa.

3. **Random Forest chia theo từng đặc trưng đơn lẻ (axis-aligned split).** Với hàng nghìn đặc trưng TF-IDF thưa (đa số giá trị bằng 0 với mỗi mẫu), mỗi lần phân nhánh của một cây quyết định chỉ tận dụng được thông tin của **một** từ/cụm từ tại một thời điểm. Điều này kém hiệu quả hơn nhiều so với việc LR/SVM học đồng thời trọng số cho toàn bộ 5.000 từ trong một phép nhân ma trận duy nhất — nên RF cần nhiều cây (400) và vẫn đứng sau hai mô hình tuyến tính.

4. **Giả định độc lập của Naive Bayes bị vi phạm bởi đặc trưng n-gram.** Việc dùng cả unigram và bigram (ví dụ *"quản_lý"* và *"quản_lý tệ"*) phá vỡ trực tiếp giả định "các đặc trưng độc lập có điều kiện" của MNB, khiến xác suất hậu nghiệm bị lệch và MNB trở thành mô hình yếu nhất trong năm mô hình.

5. **Stacking không cải thiện thêm vì các base learner có lỗi tương quan cao.** Ba trong bốn base learner của Stacking (MNB, LR, SVM) đều học trên cùng một không gian tuyến tính, nên xu hướng đoán sai của chúng khá giống nhau (cùng nhầm giữa Neutral và các lớp lân cận — xem phân tích Confusion Matrix bên dưới). Việc trộn thêm Random Forest (yếu hơn hẳn) vào tổ hợp không bù đắp đủ, khiến điểm Stacking (0.5560) thấp hơn cả Logistic Regression đơn lẻ.

### Phân tích Confusion Matrix và hiện tượng Overfitting/Underfitting

Ma trận nhầm lẫn dưới đây là dự đoán **out-of-fold** của Logistic Regression (mô hình được chọn) trên toàn bộ `X_train`, tức mỗi dự đoán được sinh ra khi mẫu đó nằm ở fold validation — không có mẫu nào được mô hình "nhìn thấy" trước khi dự đoán nó (xem `reports/figures/tv3_cv_confusion_matrix.png`, sinh bởi `plot_cv_confusion_matrix`):

| Thực tế \\ Dự đoán | Negative | Neutral | Positive |
|---|---:|---:|---:|
| **Negative** (456) | 202 | 166 | 88 |
| **Neutral** (1.310) | 185 | 641 | 484 |
| **Positive** (4.965) | 131 | 721 | 4.113 |

| Lớp | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Negative | 0.3900 | 0.4430 | 0.4148 |
| Neutral | 0.4195 | 0.4893 | 0.4517 |
| Positive | 0.8779 | 0.8284 | 0.8524 |
| **Macro avg** | 0.5625 | 0.5869 | **0.5730** |
| Weighted avg / Accuracy | 0.7556 | — | 0.7363 / 0.7448 |

**Nhận xét:**
- Lớp **Positive** được nhận diện tốt (F1 = 0.8524) nhờ số lượng mẫu áp đảo (73,8%), phù hợp với kỳ vọng.
- Lớp **Neutral** bị nhầm nhiều nhất sang Positive (721/1.310 ≈ 55%) — đúng như dự đoán trong đề cương: review trung tính thường chứa cả ý khen lẫn ý chê với tỷ trọng gần bằng nhau, khiến trọng số TF-IDF của các từ tích cực/tiêu cực gần như triệt tiêu lẫn nhau và mô hình dễ ngả theo lớp đa số.
- Lớp **Negative** cũng bị nhầm đáng kể sang Neutral (166/456 ≈ 36%), phản ánh ranh giới mờ giữa "phàn nàn nhẹ" (Neutral) và "bức xúc" (Negative) trong cách viết đánh giá tiếng Việt.
- Vì đây là chỉ số **CV out-of-fold trên tập Development** (không phải Final Test), khoảng cách giữa Macro F1 trung bình các fold (0.5727, Mục 4.2.2) và Macro F1 tổng hợp trên toàn bộ out-of-fold predictions (0.5730) gần như bằng nhau — cho thấy mô hình **không có dấu hiệu overfitting** giữa các fold: hiệu năng ổn định và nhất quán trên các phần dữ liệu khác nhau của tập train, đúng như kỳ vọng đối với một mô hình tuyến tính có regularization phù hợp (`C=1.0`) trên không gian đặc trưng thưa. Đánh giá underfitting/overfitting **chính thức** (so với Final Test độc lập) được thực hiện ở bước đánh giá độc lập, khi so sánh con số này với Macro F1 đo được trên `X_test`.

## Lưu Trữ Mô Hình Tối Ưu

- Model đã khóa: [`models/best_sentiment_model.joblib`](../models/best_sentiment_model.joblib) — Logistic Regression (`C=1.0`), huấn luyện lại trên toàn bộ `X_train` (6.731 mẫu), **chưa từng được đánh giá trên Final Test**.
- Notebook tái lập: [`notebooks/03_sentiment_modeling_ml.ipynb`](../notebooks/03_sentiment_modeling_ml.ipynb).
- Module dùng chung: [`src/models.py`](../src/models.py).
- Tại bước đánh giá độc lập, chỉ cần `joblib.load()` model này và `load_feature_split()` để lấy `X_test`/`y_test` từ `models/train_test_features.joblib`, sau đó đánh giá **đúng một lần** trong `notebooks/05_company_sentiment_insights.ipynb`.
