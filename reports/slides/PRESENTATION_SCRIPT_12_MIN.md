# Kịch bản thuyết trình khoảng 12 phút 40 giây (Bản rút gọn chuẩn năm 1)

**Đề tài:** Phân tích cảm xúc đánh giá công ty ITviec
**Vị thế người trình bày:** Sinh viên năm nhất UIT học môn Máy Học
**Số slide:** 15 slide
**Thời lượng mục tiêu:** 8 phút 30 giây (Slide lý thuyết) + 4 phút 10 giây (Live Demo) $\approx$ **12 phút 40 giây tổng thể**
**Phong cách trình bày:** Lễ phép, khiêm tốn, mạch lạc, giải thích bản chất dễ hiểu, tập trung vào điều nhóm đã làm được và nhìn nhận thẳng thắn hạn chế.

---

## Bảng phân bổ thời gian mục tiêu (Đã tối ưu rút gọn)

| Phần                   | Slide | Nội dung chính                                          | Thời lượng | Mốc thời gian |
| :---------------------- | ----: | :-------------------------------------------------------- | ------------: | --------------: |
| **Mở đầu**     |     1 | Giới thiệu đề tài & dữ liệu 8.414 review           |           25s |            0:25 |
| **Vấn đề**     |     2 | Dữ liệu lệch 11:1 & bài toán nhãn yếu              |           35s |            1:00 |
|                         |     3 | Quy trình Pipeline 5 bước thực nghiệm                |           35s |            1:35 |
| **Kỹ thuật**    |     4 | Tiền xử lý 2 tầng & giữ từ cảm xúc then chốt     |           35s |            2:10 |
|                         |     5 | Khám phá EDA: Tương quan lương & quản lý          |           30s |            2:40 |
|                         |     6 | Trích xuất đặc trưng TF-IDF & Bigram                 |           35s |            3:15 |
| **Thực nghiệm** |     7 | Thử nghiệm 5 mô hình & SMOTE chống rò rỉ dữ liệu |           35s |            3:50 |
|                         |     8 | Đánh giá Cross-Validation & phép CV riêng            |           40s |            4:30 |
| **Đánh giá**   |     9 | Kết quả Final Test & điểm nghẽn lớp Negative        |           45s |            5:15 |
|                         |    10 | Phân loại 15 trường hợp lỗi đại diện             |           35s |            5:50 |
| **Ứng dụng**    |    11 | Insight doanh nghiệp: Điểm chạm lương & quản lý   |           35s |            6:25 |
|                         |    12 | Minh họa đặc trưng TF-IDF trên câu thực tế        |           35s |            7:00 |
| **Tổng kết**    |    13 | Đánh giá tổng quan & hạn chế cốt lõi              |           35s |            7:35 |
|                         |    14 | Đóng góp & hướng phát triển tương lai            |           30s |            8:05 |
|                         |    15 | Chuyển giao phần trình bày sang Live Demo             |           25s |            8:30 |
| **Phần B**       |  Demo | Thao tác Streamlit thực tế (Duy Khang)                 |        4m 10s | **12:40** |

---

# PHẦN A — THUYẾT TRÌNH SLIDE (8:30)

*(Người trình bày chính: Trần Hoàng Hôn)*

---

### Slide 1 — Giới thiệu đề tài

**Thời lượng:** 25 giây *(Mốc: 0:25)*

> "Dạ em xin kính chào Thầy cùng toàn thể các bạn!
>
> Với đồ án này, nhóm em chọn bài toán: **Phân tích cảm xúc các đánh giá công ty trên nền tảng ITviec**.
>
> Từ 8.417 dữ liệu thô ban đầu, sau khi loại bỏ trùng lặp, nhóm dùng **8.414 review** để xây dựng mô hình phân loại 3 lớp: Tích cực, Trung tính và Tiêu cực. Hôm nay, nhóm xin báo cáo về quy trình thực nghiệm, kết quả đạt được và những điểm nhóm còn cần cải thiện ạ."

---

### Slide 2 — Dữ liệu lệch mạnh và bài toán nhãn yếu

**Thời lượng:** 35 giây *(Mốc: 1:00)*

> "Khi bắt tay vào bài toán, nhóm em gặp ngay hai thử thách lớn:
>
> Thứ nhất là **mất cân bằng lớp nghiêm trọng**. Lớp Tích cực chiếm tới gần 74%, trong khi Tiêu cực chỉ có khoảng 6,8% — tức là cứ 11 lời khen mới có 1 lời chê. Nếu mô hình đoán mò tất cả là Tích cực thì Accuracy vẫn đạt gần 74%. Vì vậy, nhóm em thống nhất dùng **Macro F1** làm thước đo chính, nhằm coi trọng độ chính xác của cả 3 lớp như nhau.
>
> Thử thách thứ hai là **nhãn yếu**: nhãn được quy đổi từ số sao đánh giá, trong khi lời review của người dùng thường vừa khen môi trường nhưng lại chê lương hoặc quản lý."

---

### Slide 3 — Pipeline tổng thể

**Thời lượng:** 35 giây *(Mốc: 1:35)*

> "Quy trình thực nghiệm của nhóm em đi qua 5 bước:
>
> Đầu tiên, nhóm ghép nối tiêu đề và nội dung thành một review hoàn chỉnh. Sau đó, văn bản tiếng Việt được làm sạch qua bộ tiền xử lý và chuyển hóa thành vector số bằng kỹ thuật TF-IDF.
>
> Tiếp theo, nhóm thử nghiệm 5 mô hình trên tập Development qua phương pháp 5-Fold Cross Validation (**Phai-Phô Cờ-rót Va-li-đây-sần - ***Kiểm chứng chéo 5 phần*****).
>
> *Đặc biệt, khi thử nghiệm câu ngắn, nhóm phát hiện bộ tiền xử lý cũ xóa mất từ cảm xúc. Nhóm đã tinh chỉnh lại pipeline và huấn luyện  **phiên bản cải tiến tiền xử lý** , đạt **Macro F1 0,5764 trên tập Test cũ** để làm đối chứng minh bạch ạ*."

---

### Slide 4 — Tiền xử lý tiếng Việt

**Thời lượng:** 35 giây *(Mốc: 2:10)*

> "Văn bản review công nghệ có đặc thù là trộn lẫn tiếng Việt, tiếng Anh chuyên ngành, teencode và icon. Nhóm em chia tiền xử lý làm hai tầng:
>
> - **Tầng 1:** Chuẩn hóa Unicode, đưa về chữ thường, xử lý URL, email, teencode và thuật ngữ IT.
> - **Tầng 2:** Tách từ tiếng Việt và lọc từ dừng.
>
> Điểm then chốt mà nhóm em rút ra là: **tuyệt đối không xóa các từ phủ định** như *'không', 'chưa'* và các từ chỉ mức độ như *'thấp', 'thiếu'*. Như ví dụ bên phải: cụm *'lương thấp'*, *'thiếu minh_bạch'* hay *'không lương'* đều được giữ nguyên vẹn để mô hình không hiểu ngược nghĩa của câu."

---

### Slide 5 — Khám phá dữ liệu (EDA)

**Thời lượng:** 30 giây *(Mốc: 2:40)*

> "Qua bước phân tích khám phá EDA, nhóm em nhận thấy:
>
> Điểm đánh giá về **Lương** và **Quản lý** có tương quan thuận cao nhất với mức độ hài lòng chung của nhân viên, đều đạt trên 0,73. Trong khi điểm Văn phòng có mức tương quan thấp hơn nhiều, chỉ khoảng 0,54.
>
> Tuy nhiên, tương quan không đồng nghĩa với quan hệ nhân quả. Khi người dùng nhập một review mới ngoài thực tế, họ thường không chấm các điểm thành phần này. Vì vậy, pipeline phân loại của nhóm chỉ dựa hoàn toàn trên văn bản review."

---

### Slide 6 — Trích xuất đặc trưng TF-IDF

**Thời lượng:** 35 giây *(Mốc: 3:15)*

> "Để mô hình học máy đọc được văn bản, nhóm sử dụng TF-IDF. Nhóm đã thử nghiệm hai cấu hình:
>
> - Khi chỉ dùng từng từ đơn lẻ (Unigram), Macro F1 chỉ đạt 55,69%.
> - Khi bổ sung thêm cụm 2 từ liền kề (Bigram), kết quả tăng rõ rệt lên **57,22%**.
>
> Bigram giúp mô hình nắm bắt được các ngữ cảnh then chốt như *'không lương'* hay *'thiếu minh bạch'* thay vì nhìn từng từ rời rạc. Cấu hình cuối cùng được nhóm chọn có 5.000 đặc trưng, loại bỏ các từ chỉ xuất hiện đúng một lần trong toàn bộ tập dữ liệu."

---

### Slide 7 — Thử nghiệm mô hình & SMOTE

**Thời lượng:** 35 giây *(Mốc: 3:50)*

> "Theo yêu cầu đồ án, nhóm em đã thử nghiệm 5 thuật toán: Naive Bayes, Logistic Regression, Linear SVM, Random Forest và Stacking. Mọi mô hình đều được đo đạc công bằng trên cùng tập dữ liệu.
>
> Để hỗ trợ lớp Tiêu cực vốn quá ít mẫu, nhóm thử nghiệm kỹ thuật sinh mẫu tổng hợp SMOTE.
>
> Một chi tiết kỹ thuật quan trọng mà nhóm em tuân thủ nghiêm ngặt là: **chỉ áp dụng SMOTE bên trong tập huấn luyện của từng fold**. Nếu sinh mẫu trước khi chia fold, dữ liệu kiểm tra sẽ bị rò rỉ vào tập train, dẫn đến điểm ảo — đây là lỗi Data Leakage mà nhóm đã chủ động phòng tránh."

---

### Slide 8 — Kết quả Cross Validation

**Thời lượng:** 40 giây *(Mốc: 4:30)*

> "Ở lần thử nghiệm ban đầu, Logistic Regression và Linear SVM bám đuổi rất sát nhau với Macro F1 lần lượt là 0,5727 và 0,5724 — chênh lệch rất nhỏ. Logistic Regression được chọn làm mô hình triển khai vì đạt  **hiệu năng cân bằng nhất trên thực nghiệm** , tốc độ suy luận nhanh và phân phối xác suất mềm ổn định, rất phù hợp cho ứng dụng thực tế.
>
> *Sau khi tinh chỉnh bộ tiền xử lý, nhóm tiến hành chạy lại **Phai-phô Si-Vi** độc lập trên tập train. Kết quả cho thấy chỉ số **Macro F1** cải thiện rõ rệt, tăng từ **0,57 lên 0,5815**.*
>
> *Nhóm xin lưu ý: *đây là phép kiểm định chéo riêng biệt nhằm chọn ra phiên bản tiền xử lý tối ưu nhất, chứ nhóm **không so sánh khập khiễng với các kết quả cũ khi không gian đặc trưng đã thay đổi****"

---

### Slide 9 — Kết quả Final Test

**Thời lượng:** 45 giây *(Mốc: 5:15)*

> "Kiểm tra phiên bản sửa trên tập Final Test độc lập gồm 1.683 mẫu, mô hình đạt Accuracy 74,33% và Macro F1 đạt 0,5764, số lượng dự đoán sai giảm được 10 mẫu.
>
> Tuy nhiên, nhìn sâu vào ma trận nhầm lẫn ở lớp Tiêu cực: trong 114 review thực sự tiêu cực, mô hình đoán đúng 52 review, nhưng bỏ sót 62 review sang lớp Trung tính và Tích cực. Độ nhạy (Recall) của lớp này chỉ đạt **45,6%** và F1 đạt 0,3910.
>
> Kết quả này cho nhóm em một bài học thực tế: Accuracy cao chưa nói lên tất cả, và việc nhận diện lời chê trong bài toán lệch lớp vẫn là thách thức lớn nhất mà nhóm cần tiếp tục cải thiện."

---

### Slide 10 — Phân loại 15 trường hợp lỗi

**Thời lượng:** 35 giây *(Mốc: 5:50)*

> "*Để phân tích 432 ca dự đoán sai, nhóm đã sử dụng các dấu hiệu văn bản để lọc ra  **15 trường hợp lỗi đại diện** , tập trung vào **3 nhóm nguyên nhân chính** sau đây*:
>
> - Có 7 câu chứa **nhiều vế đối lập**: người viết vừa khen môi trường nhưng lại vừa phàn nàn về lương.
> - Có 6 câu có **cấu trúc phủ định phức tạp** hoặc dùng từ ngữ mỉa mai ở xa nhau mà TF-IDF chưa bắt kịp.
> - Có 2 câu do nhãn ban đầu từ số sao chưa thật sự rõ ràng.
>
> 15 mẫu này giúp nhóm hiểu được ranh giới quyết định của mô hình, thay vì chỉ nhìn vào các con số thống kê khô khan."

---

### Slide 11 — Khám phá Insight doanh nghiệp

**Thời lượng:** 35 giây *(Mốc: 6:25)*

> "Nhóm cũng tận dụng dữ liệu để quan sát 5 công ty có số lượng review lớn nhất:
>
> Điểm chung thú vị là ở 4 trên 5 công ty (FPT Software, NashTech, Bosch, KMS), khía cạnh **Lương & đãi ngộ** luôn là điểm thấp nhất. Riêng VNG, khía cạnh có điểm thấp nhất lại rơi vào sự quan tâm của cấp quản lý.
>
> Nhóm em xin lưu ý: biểu đồ này chỉ mang tính mô tả trên mẫu dữ liệu thu thập được từ ITviec, nhóm không xem đây là thước đo xếp hạng doanh nghiệp ngoài đời thực"

---

### Slide 12 — Minh họa đặc trưng TF-IDF

**Thời lượng:** 35 giây *(Mốc: 7:00)*

> "Trên màn hình là ví dụ câu review: *'Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương'*. Bản sửa mới nhất nhận diện chính xác nhãn Tiêu cực với **độ tin cậy** lên tới **99,0%**.
>
> Biểu đồ bên cạnh thể hiện các đặc trưng có trọng số TF-IDF nổi bật nhất: cụm *'thường_xuyên ot'*, *'minh_bạch'*, *'thiếu'* và *'không lương'*. Trục biểu đồ nhân 100 để dễ quan sát độ lớn của từ đầu vào, chứ không phải xác suất của lớp. Điều này minh chứng cho thấy bộ tiền xử lý và Bigram của nhóm đang hoạt động đúng như mong đợi."

---

### Slide 13 — Đánh giá và hạn chế

**Thời lượng:** 35 giây *(Mốc: 7:35)*

> "Qua đồ án môn học này, nhóm em đã tự tay xây dựng trọn vẹn một pipeline học máy hoàn chỉnh từ dữ liệu thô đến mô hình hóa và triển khai giao diện.
>
> Tuy nhiên, nhóm em nhìn nhận khách quan 2 hạn chế lớn nhất:
>
> 1. **Vấn đề nhãn yếu**: Số sao không phản ánh 100% ngữ nghĩa của bài viết.
> 2. **Hạn chế của mô hình truyền thống**: TF-IDF kết hợp Logistic Regression chưa nắm bắt được ngữ cảnh ngữ nghĩa sâu, các câu đảo ngữ hay câu dài nhiều vế."

---

### Slide 14 — Kết luận & Hướng phát triển

**Thời lượng:** 30 giây *(Mốc: 8:05)*

> "Tóm lại, đồ án đã mang lại cho nhóm em những trải nghiệm thực tế về xử lý văn bản tiếng Việt và tư duy thực nghiệm trong Machine Learning.
>
> Nếu có cơ hội phát triển tiếp, nhóm mong muốn:
>
> - Tự gán nhãn thủ công một tập dữ liệu chuẩn nhỏ để đánh giá mức độ nhiễu.
> - Mở rộng phân tích cảm xúc theo từng khía cạnh riêng biệt (ABSA).
> - Thử nghiệm các mô hình ngôn ngữ tiếng Việt chuyên sâu như PhoBERT hay ViSoBERT.
>
> Phần trình bày slide của em xin được tạm dừng tại đây. Tiếp theo, em xin bạn **Nguyễn Duy Khang** đại diện nhóm tiến hành phần Live Demo ứng dụng ạ!"

---

### Slide 15 — Dẫn vào Live Demo

**Thời lượng:** 25 giây *(Mốc: 8:30)*

> *(Duy Khang bước lên/bật mic):*
> "Dạ em xin chào Thầy và các bạn, em là Duy Khang. Em xin phép chuyển sang giao diện ứng dụng Streamlit đã được nhóm chuẩn bị sẵn để thao tác trực tiếp 3 tính năng chính: quan sát bức tranh doanh nghiệp, kiểm tra chất lượng mô hình và thử nghiệm phân tích review mới theo thời gian thực ạ!"

---

# PHẦN B — KỊCH BẢN LIVE DEMO (4:10)

*(Người thao tác & thuyết minh: Nguyễn Duy Khang)*

---

### Bước 1: Insight doanh nghiệp (45 giây)

**Thao tác:** Bấm tab **Insight doanh nghiệp** ở menu bên trái.

* Chọn công ty **FPT Software** (công ty có nhiều mẫu nhất — 2.014 review).
* Chỉ nhanh vào biểu đồ tròn Donut (Tích cực 57,7%) và biểu đồ 5 khía cạnh.
* Cuộn xuống WordCloud: Bấm sang **Tích cực** để thấy các từ khóa khen ngợi, sau đó bấm lại **Tiêu cực** và chỉ vào các từ như *'ot'*, *'lương'*, *'dự_án'*.

> **Lời nói:**
> "Đầu tiên... em mở trang Insight doanh nghiệp. Trang này cho thấy tỷ lệ review Tích cực, Trung tính, Tiêu cực của từng công ty... cùng điểm đánh giá về lương, quản lý và văn hóa.
> Phía dưới là bản đồ từ khóa: khi em chuyển sang nhóm Tiêu cực, các cụm từ nổi cộm như 'ot', 'lương' và 'áp lực' xuất hiện với tần suất rất cao."

---

### Bước 2: Mô hình & Đánh giá (50 giây)

**Thao tác:** Bấm tab **Mô hình & đánh giá** ở menu bên trái.

* Chỉ nhanh vào biểu đồ So sánh 5 mô hình ban đầu (Logistic Regression dẫn đầu ~0.572).
* Cuộn xuống Ma trận nhầm lẫn: chỉ vào hàng Tiêu cực (tìm đúng 52/114 mẫu).
* Cuộn xuống khung **Khám phá 15 lỗi minh họa**: Lọc nhãn thật **Negative**, bấm chọn review `#2592`.

> **Lời nói:**
> "Tiếp theo là trang Mô hình & đánh giá. Phần trên là kết quả so sánh 5 thuật toán ban đầu. Cuộn xuống ma trận nhầm lẫn, Thầy có thể thấy mô hình tìm đúng 52 trên 114 review tiêu cực và bị nhầm mất 62 review.
> Ngay bên dưới, nhóm thiết kế bảng đọc lỗi trực quan. Ví dụ mẫu 2592: review này người viết vừa khen môi trường nhưng lại chê lương thấp và hay OT, chính vì câu chứa cả hai thái cực nên mô hình đã dự đoán nhầm sang Trung tính."

---

### Bước 3: Phân tích review theo thời gian thực (2 phút)

**Thao tác:** Bấm tab **Phân tích review** ở menu bên trái.

* Lần lượt bấm bốn mẫu **Tích cực → Trung tính → Tiêu cực → Nhiều vế**. Mỗi lần chọn, ứng dụng tự phân tích; chỉ nhanh vào nhãn kết quả và ba thanh xác suất.
* Ở mẫu **Nhiều vế**, dừng lại lâu hơn: chỉ **Trung tính 58,7%** và thanh **Tiêu cực 30,0%** để giải thích vì sao không nên đọc một nhãn riêng lẻ.
* Cuộn xuống khung **Từ review đến vector**: chỉ *'môi_trường'*, *'lương thấp'*, *'chưa'*, rồi chuyển sang bảng **Token TF-IDF nổi bật**.

> **Lời nói:**
> "Bây giờ em chuyển sang phân tích review mới. Trên màn hình có bốn mẫu để thử; em sẽ bấm lần lượt và ứng dụng tự đưa ra kết quả cho từng câu.
>
> (Ví dụ lời khen) Đầu tiên là lời khen về môi trường và đồng nghiệp. Model dự đoán **Tích cực, khoảng 66,7%**.

> (Vd trung tính)  Tiếp theo, câu nói công việc ổn và quy trình bình thường được dự đoán **Trung tính, khoảng 93,1%**.
>
> (Vd tiêu cực) Bây giờ em thử lời phàn nàn về lương thấp, quản lý thiếu minh bạch và OT không lương. Model dự đoán **Tiêu cực, khoảng 99% cho câu này**. Các từ 'thấp', 'thiếu' và 'không' được giữ ở bước tiền xử lý để không làm mất ý chê.
>
> (vd nhiều vế) Cuối cùng là mẫu 'Nhiều vế': vừa khen môi trường tốt, vừa chê lương thấp và quản lý chưa quan tâm. Model chọn **Trung tính, khoảng 58,7%**, nhưng Tiêu cực cũng khoảng **30%**. Ba thanh là mức model nghiêng về từng nhãn đối với câu này, không phải độ chính xác chung. Với review nhiều ý, mình cần đọc cả nội dung thay vì chỉ nhìn nhãn.
>
> Em cuộn xuống xem hệ thống xử lý mẫu này. Bên trái là câu sau chuẩn hóa và tách từ, như 'môi_trường'; 'lương thấp' và 'chưa' vẫn được giữ. Bên phải là những token TF-IDF nổi bật trong vector số đưa vào Logistic Regression. Một token có trọng số cao không tự quyết định nhãn; model kết hợp các đặc trưng để tính ba xác suất phía trên."

---

### Bước 4: Kết thúc và mở phần Q&A (35 giây)

**Thao tác:** Giữ nguyên màn hình web app ở trang Phân tích review, hướng mắt về Thầy và Hội đồng.

> **Lời nói:**
> "Dạ vừa rồi là toàn bộ phần demo ứng dụng của nhóm chúng em. Qua đồ án này, nhóm sinh viên năm nhất chúng em đã học hỏi được rất nhiều bài học thực tiễn về quy trình xử lý dữ liệu và đánh giá mô hình học máy.
>
> Chúng em xin chân thành cảm ơn Thầy Cáp Phạm Đình Thăng và các bạn đã chú ý lắng nghe! Nhóm em rất mong nhận được những nhận xét và góp ý quý báu từ Thầy ạ!"
