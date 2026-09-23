# Kịch bản trình bày 12 phút

**Đề tài:** Phân tích cảm xúc đánh giá công ty ITviec  
**Vai trò người trình bày:** Sinh viên năm nhất học môn Máy Học  
**Số slide:** 15  
**Thời lượng mục tiêu:** 12 phút  
**Cách trình bày:** Giải thích từ kiến thức cơ bản, nói rõ điều nhóm đã làm và không phóng đại kết quả

## Phân bổ thời gian

| Slide | Nội dung | Thời lượng | Mốc kết thúc |
|---:|---|---:|---:|
| 1 | Giới thiệu đề tài | 0:40 | 0:40 |
| 2 | Bài toán và dữ liệu lệch | 0:45 | 1:25 |
| 3 | Pipeline tổng thể | 0:45 | 2:10 |
| 4 | Tiền xử lý tiếng Việt | 0:45 | 2:55 |
| 5 | Kết quả EDA | 0:50 | 3:45 |
| 6 | Đặc trưng TF-IDF | 0:45 | 4:30 |
| 7 | Mô hình và xử lý mất cân bằng | 0:45 | 5:15 |
| 8 | Kết quả Cross Validation | 0:55 | 6:10 |
| 9 | Kết quả Final Test | 1:05 | 7:15 |
| 10 | Phân tích lỗi | 0:50 | 8:05 |
| 11 | Insight doanh nghiệp | 0:50 | 8:55 |
| 12 | Giải thích kết quả dự đoán | 0:45 | 9:40 |
| 13 | Đánh giá và hạn chế | 0:50 | 10:30 |
| 14 | Kết luận | 0:35 | 11:05 |
| 15 | Dẫn vào live demo | 0:55 | 12:00 |

---

## Slide 1 — Giới thiệu đề tài

**Thời lượng: 40 giây**

Kính chào Thầy Cáp Phạm Đình Thăng cùng thầy cô và các bạn. Nhóm chúng em là sinh viên năm nhất đang học môn Máy Học thuộc Khoa Khoa học Máy tính. Với đồ án này, nhóm chọn bài toán phân tích cảm xúc từ các đánh giá công ty trên ITviec.

Mục tiêu của nhóm là áp dụng những bước cơ bản đã học trong môn: tìm hiểu dữ liệu, tiền xử lý, biến văn bản thành dữ liệu số, thử nhiều mô hình và so sánh kết quả. Dữ liệu ban đầu có 8.417 review. Sau khi kiểm tra dữ liệu trùng, nhóm dùng 8.414 review để xây dựng mô hình phân loại ba lớp Positive, Neutral và Negative.

Trong phần trình bày, nhóm xin tập trung vào cách nhóm thực hiện bài toán, kết quả đạt được và những điểm nhóm vẫn cần cải thiện.

**Chuyển ý:** Đầu tiên là hai khó khăn dễ thấy nhất trong bộ dữ liệu.

## Slide 2 — Dữ liệu lệch mạnh và nhãn yếu

**Thời lượng: 45 giây**

Khó khăn đầu tiên là số lượng mẫu giữa ba lớp không cân bằng. Positive chiếm 73,76%, còn Negative chỉ chiếm 6,77%. Như vậy, cứ một review Negative thì có gần 11 review Positive. Nếu mô hình đoán tất cả là Positive, Accuracy vẫn có thể gần 73,8%, dù mô hình không nhận ra được hai lớp còn lại.

Vì lý do đó, nhóm dùng Macro F1 làm chỉ số chính. Có thể hiểu đơn giản, chỉ số này tính F1 cho từng lớp rồi lấy trung bình, nên cả ba lớp được xem là quan trọng như nhau.

Khó khăn thứ hai là nhãn được suy ra từ số sao. Nhóm gọi đây là nhãn yếu vì nội dung review và rating có thể không hoàn toàn trùng nhau. Một review có thể vừa khen môi trường, vừa chê lương hoặc quản lý.

## Slide 3 — Pipeline tổng thể

**Thời lượng: 45 giây**

Nhóm thực hiện bài toán theo năm bước. Đầu tiên, nhóm ghép tiêu đề, phần điểm thích và phần góp ý thành một review. Sau đó, nhóm làm sạch văn bản tiếng Việt. Vì mô hình học máy không đọc trực tiếp được câu chữ, nhóm dùng TF-IDF để chuyển văn bản thành các con số.

Tiếp theo, nhóm thử năm mô hình trên tập Development. Nhóm dùng Cross Validation, nghĩa là chia tập Development thành năm phần và lần lượt dùng từng phần để kiểm tra. Sau lần chọn mô hình ban đầu, nhóm đánh giá trên Final Test.

Khi thử câu ngắn, nhóm phát hiện một số từ mang cảm xúc bị loại nhầm. Vì vậy, nhóm sửa tiền xử lý và huấn luyện lại Logistic Regression kết hợp SMOTE. Bản sửa đạt Macro F1 0,5764 khi đối chiếu trên **chính Final Test cũ**. Web demo hiện dùng bản này.

## Slide 4 — Tiền xử lý tiếng Việt

**Thời lượng: 45 giây**

Văn bản trên ITviec có cả tiếng Việt, tiếng Anh chuyên ngành, từ viết tắt và emoji. Nhóm chia bước tiền xử lý thành hai tầng để dễ kiểm tra.

Tầng đầu chuẩn hóa Unicode, loại URL và email, chuyển chữ về dạng thống nhất, đồng thời xử lý teencode và một số thuật ngữ IT. Tầng sau thực hiện tách từ tiếng Việt và bỏ các từ ít mang ý nghĩa. Nhóm giữ từ phủ định như “không”, “chưa”, cùng các từ chỉ mức độ như “thấp”, “nhiều”, vì bỏ chúng có thể làm câu bị hiểu sai.

Ví dụ bên phải cho thấy bản sửa giữ được “lương thấp”, “thiếu minh_bạch”, “OT” và “không lương”. Dấu gạch dưới nối các tiếng trong một từ sau khi tách từ. Đây là cách xử lý mà web demo hiện đang dùng.

## Slide 5 — Kết quả EDA

**Thời lượng: 50 giây**

Ở bước EDA, hay còn gọi là phân tích khám phá dữ liệu, nhóm xem phân bố lớp và mối liên hệ giữa các cột. Kết quả cho thấy điểm quản lý và điểm lương có tương quan cao nhất với rating tổng thể, lần lượt khoảng 0,7368 và 0,7343. Điểm văn phòng có tương quan thấp hơn, khoảng 0,5423.

Theo cách hiểu của nhóm, người đánh giá quan tâm khá nhiều đến quản lý và chế độ đãi ngộ. Tuy nhiên, tương quan không có nghĩa là quan hệ nguyên nhân. Nhóm cũng không đưa các điểm thành phần vào mô hình dự đoán chính, vì khi người dùng nhập một review mới thì các điểm này có thể không tồn tại.

Do đó, pipeline chính chỉ sử dụng văn bản. Các điểm khía cạnh được giữ lại để hỗ trợ phân tích dữ liệu.

## Slide 6 — Đặc trưng TF-IDF

**Thời lượng: 45 giây**

TF-IDF là cách biểu diễn mức độ nổi bật của từ trong văn bản. Nhóm thử hai cấu hình. Khi chỉ dùng từng từ riêng lẻ, CV Macro F1 đạt khoảng 55,69%. Khi thêm bigram, tức là cụm gồm hai từ liền nhau, kết quả tăng lên 57,22%.

Bigram giúp mô hình giữ được các cụm như “không lương” hoặc “thiếu minh bạch”, thay vì chỉ nhìn từng từ riêng. Cấu hình cuối dùng tối đa 5.000 đặc trưng và bỏ các token chỉ xuất hiện một lần.

Sau khi kiểm tra dữ liệu trùng, nhóm chia 8.414 mẫu thành 6.731 mẫu Development và 1.683 mẫu Final Test. Việc chia có phân tầng để giữ tỷ lệ ba lớp gần giống nhau ở hai tập.

## Slide 7 — Mô hình và xử lý mất cân bằng

**Thời lượng: 45 giây**

Theo yêu cầu của đồ án, sinh viên cần thử ít nhất ba mô hình cơ bản. Nhóm thử năm mô hình gồm Naive Bayes, Logistic Regression, Linear SVM, Random Forest và Stacking. Các mô hình dùng cùng dữ liệu đầu vào và cùng cách đánh giá để việc so sánh công bằng hơn.

Do lớp Negative có ít mẫu, nhóm thử SMOTE. Có thể hiểu đơn giản, SMOTE tạo thêm các điểm dữ liệu tổng hợp cho lớp ít mẫu. Bước này chỉ được thực hiện trong phần dữ liệu dùng để huấn luyện của từng fold. Phần validation vẫn giữ nguyên.

Nếu tạo mẫu trước khi chia fold, dữ liệu kiểm tra có thể bị liên quan đến dữ liệu huấn luyện. Khi đó điểm đánh giá sẽ cao hơn thực tế. Đây là lỗi rò rỉ dữ liệu mà nhóm cố gắng tránh.

## Slide 8 — Kết quả Cross Validation

**Thời lượng: 55 giây**

Biểu đồ bên trái là bảng xếp hạng **lần thử ban đầu**: Logistic Regression đạt Macro F1 0,5727, Linear SVM đạt 0,5724. Chênh lệch chỉ 0,0003, nên nhóm không kết luận Logistic Regression chắc chắn tốt hơn SVM ở mọi dữ liệu.

Nhóm chọn Logistic Regression vì đứng đầu lần thử đó và trả được xác suất ba lớp cho web demo. Sau khi sửa tiền xử lý, nhóm chỉ huấn luyện lại Logistic Regression, chưa xếp hạng lại bốn mô hình còn lại.

Để chọn bản sửa mà không dùng Final Test làm tiêu chí, nhóm chạy 5-fold CV trên Development, fit TF-IDF trong từng fold cho cả bản trước và bản sửa. Macro F1 tăng từ 0,5708 lên 0,5815. Đây là phép CV riêng, không lấy điểm 0,5727 trong bảng cũ trừ trực tiếp cho 0,5815.

Sau khi chọn bản sửa bằng CV, nhóm mới dùng lại Final Test cũ để đối chiếu kết quả.

## Slide 9 — Kết quả Final Test

**Thời lượng: 1 phút 05 giây**

Trên 1.683 mẫu Final Test cũ, bản sửa đạt Accuracy 74,33%, Macro F1 0,5764 và Weighted F1 0,7540. Mô hình dự đoán sai 432 mẫu, giảm 10 mẫu so với bản trước.

Accuracy khá cao nhưng gần với tỷ lệ lớp Positive trong dữ liệu. Vì vậy, nhóm xem thêm F1 từng lớp: Positive 0,8602, Neutral 0,4780, Negative 0,3910.

Nhìn vào hàng Negative của ma trận nhầm lẫn: trong 114 review thật sự Negative, model tìm đúng 52, nhầm 41 sang Neutral và 21 sang Positive. Recall Negative vì vậy khoảng 45,6%; lớp ít mẫu vẫn là phần khó nhất.

Đây là **đánh giá lại trên cùng Final Test đã dùng trước đó**, không phải một tập kiểm thử mới. Nhóm trình bày con số này như phép đối chiếu minh bạch; khả năng nhận diện Negative vẫn cần cải thiện.

## Slide 10 — Phân tích lỗi

**Thời lượng: 50 giây**

Để hiểu các trường hợp model còn sai, nhóm chọn 15 lỗi minh họa từ 432 lỗi của bản sửa. Hệ thống **gợi ý nhóm lỗi tự động**: 7 review có nhiều vế ý, 6 review có phủ định hoặc cấu trúc khó, 2 review có nhãn hoặc tín hiệu chưa rõ. Đây không phải 15 mẫu đã được nhóm gán nguyên nhân thủ công.

Ví dụ một review vừa khen môi trường vừa chê lương có thể khiến model khó chọn một nhãn chung. TF-IDF cũng khó nắm hết quan hệ phủ định hoặc nhiều ý ở xa nhau. Nhưng 15 mẫu này chỉ để minh họa, không đại diện tỷ lệ nguyên nhân cho toàn bộ 432 lỗi.

Nếu tiếp tục phát triển, nhóm cần đọc và gán nhãn nguyên nhân thủ công trên nhiều mẫu hơn, đồng thời thử phân tích cảm xúc theo từng khía cạnh.

## Slide 11 — Insight doanh nghiệp

**Thời lượng: 50 giây**

Sau phần đánh giá mô hình, nhóm thử dùng dữ liệu để quan sát năm công ty có nhiều review nhất. Với FPT, NashTech, Bosch và KMS, Salary and benefits là khía cạnh có điểm trung bình thấp nhất. Riêng VNG, khía cạnh thấp nhất là Management cares about me.

Kết quả này giúp nhóm biết chủ đề nào nên được đọc kỹ hơn trong review. Tuy nhiên, nhóm không xem đây là bảng xếp hạng công ty. Số lượng review giữa các công ty khác nhau, từ 251 review của KMS đến 2.014 review của FPT. Nhãn cảm xúc cũng được suy ra từ rating.

Vì vậy, biểu đồ chỉ mang tính mô tả trên bộ dữ liệu hiện có. Nếu muốn đưa ra kết luận cho doanh nghiệp, nhóm cần thêm dữ liệu và phương pháp kiểm chứng kỹ hơn.

## Slide 12 — Giải thích kết quả dự đoán

**Thời lượng: 45 giây**

Trước khi tổng kết, nhóm xem lại câu ở slide tiền xử lý: “Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương”. Với bản sửa, model nhận diện Negative khoảng 99,0%. Biểu đồ cho thấy các đặc trưng TF-IDF nổi bật như “thường_xuyên ot”, “minh_bạch”, “thiếu” và “không lương”.

Trục biểu đồ nhân trọng số TF-IDF lên 100 để dễ đọc, **không phải phần trăm xác suất**. Nó chỉ cho biết token nào nổi bật trong câu, chưa cho biết token đó đẩy dự đoán về lớp nào. Muốn xem chiều tác động, phải kết hợp với hệ số Logistic Regression đã học.

Trong phạm vi đồ án, nhóm dùng biểu đồ để kiểm tra đặc trưng đầu vào. Nhóm chưa xem đây là một phương pháp giải thích hoàn chỉnh cho quyết định của mô hình.

## Slide 13 — Đánh giá và hạn chế

**Thời lượng: 50 giây**

Qua đồ án, nhóm đã thực hiện được các bước chính của một bài toán Máy Học: tìm hiểu dữ liệu, tiền xử lý, huấn luyện nhiều mô hình và đánh giá trên tập riêng. Nhóm cũng xây dựng web demo để kiểm tra mô hình với review mới.

Ở bản sửa, CV Macro F1 là 0,5815 và kết quả đối chiếu trên Final Test cũ là 0,5764, chênh khoảng 0,0052. Chênh lệch này chưa lớn, nhưng không đủ để nói model đã tốt ở mọi lớp. F1 của Negative vẫn chỉ 0,3910.

Hạn chế lớn nhất là nhãn được suy ra từ rating. Ngoài ra, TF-IDF chưa hiểu tốt câu dài, mỉa mai và các quan hệ phủ định phức tạp. Đây là những điều nhóm nhận ra sau khi xem kết quả và phân tích lỗi.

## Slide 14 — Kết luận

**Thời lượng: 35 giây**

Tóm lại, đồ án giúp nhóm thực hành đầy đủ quy trình cơ bản của môn Máy Học trên dữ liệu thực tế. Logistic Regression đứng đầu bảng xếp hạng ban đầu; bản sửa tiền xử lý giúp model này cải thiện nhẹ mà không thay đổi loại thuật toán.

Kết quả hiện tại là một mốc tham khảo ban đầu, chưa phải hệ thống hoàn chỉnh để sử dụng trong thực tế. Nếu có thêm thời gian, nhóm muốn gán nhãn thủ công một tập nhỏ, phân tích cảm xúc theo từng khía cạnh và thử mô hình tiếng Việt như PhoBERT hoặc ViSoBERT.

Phần nội dung chính của nhóm xin kết thúc tại đây. Tiếp theo, nhóm xin mời bạn Nguyễn Duy Khang trình bày phần live demo.

## Slide 15 — Dẫn vào live demo

**Thời lượng: 55 giây, gồm khoảng 15 giây dẫn dắt và 40 giây thao tác trực tiếp**

**Nguyễn Duy Khang trình bày:** Em xin tiếp tục với phần live demo. Trong phần này, em sẽ minh họa ba bước: chọn một review mẫu, quan sát nhãn cùng xác suất dự đoán, sau đó kiểm tra văn bản đã xử lý và các token TF-IDF nổi bật.

Sau slide dẫn dắt này, em xin chuyển sang ứng dụng Streamlit đã mở sẵn để thao tác trực tiếp.

**Các bước thao tác trên ứng dụng (khoảng 40 giây):**

1. *(~5 giây)* Chuyển sang tab trình duyệt đã mở sẵn trang "Phân tích review" — không mở lại ứng dụng từ đầu để tránh chờ tải.
2. *(~5 giây)* Ở khung "Thử một tình huống", bấm mẫu **"Nhiều vế"** — *"Môi trường tốt nhưng lương thấp và quản lý chưa thật sự quan tâm nhân viên"*. Đây là ví dụ có cả lời khen và lời chê.
3. *(~2 giây)* Bấm nút **"Phân tích cảm xúc"**.
4. *(~8 giây)* Đọc kết quả bên phải: nhãn cảm xúc dự đoán và phần trăm xác suất của lớp đó, rồi chỉ nhanh vào biểu đồ ba thanh xác suất Positive, Neutral, Negative.
5. *(~10 giây)* Kéo xuống phần "Tín hiệu trong văn bản", đọc khung "SAU CHUẨN HÓA & TÁCH TỪ" để cho thấy văn bản đã được làm sạch và tách từ đúng như đã trình bày ở slide 4.
6. *(~10 giây)* Chỉ vào bảng "Token TF-IDF nổi bật" bên cạnh, nêu một hoặc hai token có trọng số cao nhất để nối lại với phần giải thích ở slide 12.

Phần demo của nhóm xin kết thúc. Nhóm cảm ơn thầy và các bạn đã lắng nghe, và nhóm xin sẵn sàng trả lời câu hỏi.

---

# PHẦN B — DEMO WEB TRỰC TIẾP

**Lưu ý phạm vi:** Bản rút gọn ở slide 15 (40 giây) là bản dùng trong đúng 12 phút trình bày chính. Phần B dưới đây là kịch bản demo đầy đủ, đi qua cả 4 trang của web app theo đúng thứ tự trong kế hoạch demo của nhóm (Overview → Insight doanh nghiệp → Benchmark & Đánh giá lỗi → Real-time Prediction) — dùng khi còn thời gian, khi thầy cô yêu cầu xem thêm, hoặc trong phần hỏi đáp. Không cố nhồi cả phần B vào slide 15.

## Chuẩn bị trước buổi trình bày

- Khởi động app bằng lệnh trong README (`streamlit run app.py`) và kiểm tra `http://localhost:8501/_stcore/health` trả về `ok`.
- Mở sẵn `http://localhost:8501`, chờ trang **Tổng quan** tải xong toàn bộ metric và biểu đồ.
- Để trình duyệt ở mức zoom 100%, ẩn thanh bookmark và tắt thông báo hệ thống để không bị popup che màn hình khi chia sẻ.
- Ở trang **Phân tích review**, không cần chuẩn bị câu review trong clipboard — bốn tình huống mẫu (Tích cực, Trung tính, Tiêu cực, Nhiều vế) đã có sẵn trong khung "Thử một tình huống". Ưu tiên bấm chọn mẫu thay vì gõ, để tránh gõ sai hoặc mất thời gian.
- Mở app trước giờ trình bày khoảng 10 giây để model và bộ tách từ được chuẩn bị ở nền, rồi bấm thử "Phân tích cảm xúc" một lần. Nếu bấm quá sớm, lượt đầu có thể hiện "Đang phân tích review…" và phải chờ khởi tạo tokenizer.
- Không chạy lại `scripts/build_presentation_slides.py` trước buổi trình bày; mã sinh slide cũ chưa được đồng bộ với số liệu của bản sửa.
- Không cập nhật package hoặc pull code ngay trước giờ trình bày.

## Demo 1 — Trang Tổng quan

**Thời gian:** 20 giây

**Thao tác:** Mở trang **Tổng quan** (trang mặc định khi vào app).

**Lời nói:**

> Bây giờ em xin demo nhanh ứng dụng của nhóm. Trang Tổng quan tóm tắt 8.414 review đã dùng để mô hình hóa và bốn bước của pipeline: từ review thô, qua chuẩn hóa và TF-IDF, đến Logistic Regression và kết quả. Biểu đồ bên phải cũng nhắc lại vì sao nhóm dùng Macro F1, vì lớp Positive chiếm phần lớn dữ liệu.

**Không nên:** đọc lần lượt từng KPI hoặc giải thích lại Macro F1 từ đầu — phần này đã trình bày ở slide 2.

## Demo 2 — Insight doanh nghiệp

**Thời gian:** 45 giây

**Thao tác:**

1. Chọn **Insight doanh nghiệp** ở sidebar.
2. Chọn doanh nghiệp **FPT Software** (công ty có nhiều review nhất, 2.014 review).
3. Chỉ vào biểu đồ cơ cấu cảm xúc (donut) và biểu đồ điểm trải nghiệm theo 5 khía cạnh.
4. Chuyển WordCloud từ **Positive** sang **Negative**.

**Lời nói:**

> Ở trang Insight doanh nghiệp, em chọn FPT Software vì đây là công ty có nhiều review nhất trong dữ liệu. Positive chiếm khoảng 57,7%, nhưng Salary and benefits lại là khía cạnh có điểm trung bình thấp nhất. Bản đồ từ khóa bên dưới có thể chuyển giữa nhóm Positive và Negative. Từ càng lớn nghĩa là xuất hiện càng nhiều trong nhóm đang xem, không có nghĩa đó là nguyên nhân tạo ra cảm xúc.

**Không nên:** đọc hết bảng từ khoá bên phải; chỉ cần nêu 2–3 từ đứng đầu.

## Demo 3 — Benchmark & Đánh giá lỗi

**Thời gian:** 40 giây

**Thao tác:**

1. Chọn **Benchmark** ở sidebar. Chỉ vào Logistic Regression trên biểu đồ xếp hạng gốc, rồi chỉ dòng giải thích CV bản sửa bên dưới.
2. Chọn **Đánh giá & lỗi**. Chỉ vào ma trận nhầm lẫn và biểu đồ Precision/Recall/F1 theo lớp.
3. Ở khung **Khám phá 15 lỗi minh họa**, lọc Nhãn thật là **Negative**, mở một mẫu để đọc review và dạng lỗi được gợi ý.

**Lời nói:**

> Biểu đồ Benchmark là lần xếp hạng ban đầu: Logistic Regression đứng đầu năm mô hình với Macro F1 0,5727. Sau sửa tiền xử lý, nhóm chọn bản mới bằng một phép CV riêng, đạt 0,5815; chưa chạy lại bảng xếp hạng của bốn mô hình kia. Trang Đánh giá và lỗi cho thấy bản sửa đạt Macro F1 0,5764 trên Final Test cũ. Ma trận nhầm lẫn cho thấy model tìm đúng 52 trên 114 review Negative, tức Recall 45,6%. Phần bên dưới giúp đọc từng lỗi thật; dạng lỗi hiển thị là gợi ý tự động, chưa phải kết luận đã gán thủ công.

**Không nên:** đọc hết bảng "Nhật ký thực nghiệm" của cả 5 mô hình; chỉ nêu 1–2 dòng đầu.

## Demo 4 — Phân tích review (Real-time Prediction)

**Thời gian:** 40 giây *(bản dùng trong slide 15 của phần chính)*

**Thao tác:**

1. Chọn **Phân tích review** ở sidebar.
2. Ở khung "Thử một tình huống", bấm mẫu **"Tiêu cực"** — *"Lương thấp, quản lý thiếu minh bạch và thường xuyên phải OT không lương."* Đây là câu test đã được định nghĩa sẵn trong kế hoạch demo của nhóm.
3. Bấm **"Phân tích cảm xúc"**.
4. Đọc nhãn và xác suất bên phải, sau đó kéo xuống đọc khung "SAU CHUẨN HÓA & TÁCH TỪ" và bảng "Token TF-IDF nổi bật".

**Kết quả hiện tại đã kiểm chứng** (chạy trực tiếp trên pipeline thật, khớp với con số Negative 77,3% đã ghi trong kế hoạch demo):

- Nhãn cuối: **Negative — 77,3%**.
- Xác suất ba lớp: Negative khoảng **77,3%**, Neutral khoảng **21,4%**, Positive khoảng **1,4%**.
- Văn bản sau chuẩn hoá: `lương quản_lý minh_bạch thường_xuyên không lương`.
- Token TF-IDF nổi bật nhất: `thường_xuyên không`, `minh_bạch`, `thường_xuyên`, `không lương`, `quản_lý`.

**Lời nói:**

> Kết quả là Negative, khoảng 77,3%. Văn bản sau tiền xử lý cho thấy từ phủ định "không" trong cụm "không lương" vẫn được giữ lại, đúng như nhóm đã nói ở slide 4. Token nổi bật nhất là cụm "thường_xuyên không" và "không lương" — hai cụm bigram này chính là ví dụ nhóm đã dùng để giải thích TF-IDF ở slide 12.

**Không nên:** gõ một câu mới trên sân khấu; chỉ bấm mẫu có sẵn để không tốn thời gian và tránh lỗi chính tả.

## Kết thúc demo và buổi trình bày

> Qua demo, nhóm đã thể hiện được toàn bộ luồng từ insight doanh nghiệp, phân tích một review mới, cho đến benchmark và đánh giá lỗi của mô hình. Phần demo của em đến đây là kết thúc.
>
> Nhóm xin chân thành cảm ơn thầy và các bạn đã theo dõi. Nhóm xin sẵn sàng trả lời câu hỏi.

**Thao tác:** Giữ nguyên trang đang mở trên web app, không chuyển lại PowerPoint.

**Dự phòng — không đọc trong lúc demo, chỉ nói nếu thầy hỏi thêm về hạn chế của model:**

> Trước đây câu “Công ty lương thấp, họp nhiều” bị xóa mất “thấp” và “nhiều”, nên model hiểu sai. Nhóm đã sửa từ dừng, fit lại TF-IDF và huấn luyện lại model. Bản hiện tại giữ hai từ đó và dự đoán Negative khoảng 57,5%. Tuy nhiên, một câu ngắn vẫn cần được đọc trong ngữ cảnh, không nên xem xác suất của riêng câu là bằng chứng chắc chắn.

---

## Gợi ý khi tập thử

- Giữ cách nói “trong phạm vi bài tập” hoặc “theo kết quả nhóm thử nghiệm” khi trả lời các câu hỏi rộng. Cách nói này phù hợp với vai trò sinh viên và tránh kết luận quá mức.
- Tập một lần với đồng hồ và đánh dấu mốc 6:10 ở cuối slide 8. Nếu vượt mốc, rút ngắn phần cấu hình TF-IDF ở slide 6.
- Ở slide 9, giải thích vì sao Accuracy chưa đủ trước khi đọc F1 của từng lớp. Đây là phần thể hiện nhóm hiểu cách đánh giá mô hình.
- Không cần đọc toàn bộ con số ở slide 11. Chỉ nêu kết luận 4 trên 5 công ty và ngoại lệ VNG.
- Trước khi lên trình bày, mở sẵn ứng dụng Streamlit và bấm thử "Phân tích cảm xúc" một lần. App chuẩn bị model ở nền sau khi trang đầu hiện, nhưng nếu bấm ngay lập tức thì vẫn có thể phải đợi tokenizer khởi tạo.
- Nếu live demo tải chậm, giữ nguyên slide 15 và giải thích ngắn ba bước mà nhóm dự định thao tác; không trình chiếu sẵn kết quả dự đoán trên slide.
- Khi chưa chắc một câu trả lời, có thể nói: “Phần này nhóm chưa kiểm chứng đủ trong phạm vi đồ án. Theo hiểu biết hiện tại của nhóm, chúng em dự đoán rằng...” rồi nêu giả thuyết và cách kiểm tra thêm.

## Một số câu trả lời ngắn phù hợp với sinh viên năm nhất

**Vì sao chọn Logistic Regression thay vì SVM?**  
Hai mô hình có điểm rất gần nhau. Nhóm chọn Logistic Regression vì điểm CV nhỉnh hơn một chút và mô hình trả về xác suất thuận tiện cho web demo. Nhóm không kết luận Logistic Regression luôn tốt hơn SVM.

**Vì sao Accuracy cao nhưng Macro F1 thấp hơn?**  
Vì dữ liệu có nhiều mẫu Positive. Mô hình làm tốt lớp này sẽ có Accuracy cao, nhưng vẫn có thể làm chưa tốt ở Negative và Neutral. Macro F1 cho ba lớp trọng số ngang nhau nên phản ánh rõ hơn vấn đề mất cân bằng.

**Kết quả Macro F1 0,5764 có tốt không?**
Theo nhóm, đây là kết quả tham khảo ở mức vừa phải cho pipeline cơ bản. Bản sửa có CV Macro F1 0,5815, còn trên Final Test cũ là 0,5764. F1 của Negative vẫn chỉ 0,3910, nên model còn cần cải thiện; Final Test cũ cũng không phải phép kiểm thử mới độc lập cho bản sửa.

**SMOTE có làm thay đổi dữ liệu thật không?**  
SMOTE chỉ tạo thêm điểm tổng hợp trong phần dữ liệu huấn luyện. Nhóm không thêm mẫu tổng hợp vào validation hoặc Final Test, nên các tập dùng để đánh giá vẫn giữ nguyên.

**Tương quan cao có chứng minh lương hoặc quản lý gây ra rating thấp không?**  
Không. Tương quan chỉ cho thấy hai giá trị thay đổi cùng nhau trong dữ liệu. Muốn kết luận nguyên nhân cần thiết kế phân tích khác và kiểm soát thêm nhiều yếu tố.
