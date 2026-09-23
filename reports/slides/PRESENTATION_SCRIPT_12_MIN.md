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

Tiếp theo, nhóm thử năm mô hình trên tập Development. Nhóm dùng Cross Validation, nghĩa là chia tập Development thành năm phần và lần lượt dùng từng phần để kiểm tra. Sau khi chọn mô hình, nhóm mới đánh giá một lần trên Final Test.

Mô hình được chọn là Logistic Regression kết hợp SMOTE. Kết quả Final Test có Macro F1 bằng 0,5714. Cuối cùng, nhóm đưa đúng quy trình này vào web demo.

## Slide 4 — Tiền xử lý tiếng Việt

**Thời lượng: 45 giây**

Văn bản trên ITviec có cả tiếng Việt, tiếng Anh chuyên ngành, từ viết tắt và emoji. Nhóm chia bước tiền xử lý thành hai tầng để dễ kiểm tra.

Tầng đầu chuẩn hóa Unicode, loại URL và email, chuyển chữ về dạng thống nhất, đồng thời xử lý teencode và một số thuật ngữ IT. Tầng sau thực hiện tách từ tiếng Việt và bỏ các từ ít mang ý nghĩa. Nhóm vẫn giữ những từ phủ định như “không”, “chưa” và “chẳng”, vì chúng có thể làm thay đổi cảm xúc của câu.

Ví dụ bên phải cho thấy sau khi làm sạch, câu ngắn hơn nhưng vẫn giữ các ý chính như “lương”, “quản lý”, “minh bạch” và “không lương”. Đây cũng là cách xử lý đang dùng trong phần demo.

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

Kết quả Cross Validation cho thấy Logistic Regression đạt Macro F1 bằng 0,5727. Linear SVM đứng thứ hai với 0,5724. Hai kết quả chỉ chênh 0,0003, nên nhóm không cho rằng Logistic Regression chắc chắn tốt hơn SVM trong mọi trường hợp.

Trong phạm vi bài tập này, nhóm chọn Logistic Regression vì đây là mô hình có điểm trung bình cao nhất trong các lần thử. Mô hình cũng có thể trả về xác suất của ba lớp, phù hợp với giao diện web demo.

Những mô hình phức tạp hơn chưa chắc cho kết quả cao hơn. Ví dụ Stacking đứng sau Random Forest trong thử nghiệm này. Qua đó, nhóm hiểu rằng cần đánh giá bằng dữ liệu thay vì chỉ chọn mô hình vì tên gọi hoặc độ phức tạp.

Sau khi chọn xong Logistic Regression, nhóm mới mở Final Test.

## Slide 9 — Kết quả Final Test

**Thời lượng: 1 phút 05 giây**

Trên 1.683 mẫu Final Test, mô hình đạt Accuracy 73,74%, Macro F1 bằng 0,5714 và Weighted F1 bằng 0,7489. Mô hình dự đoán sai 442 mẫu.

Accuracy khá cao nhưng gần bằng tỷ lệ của lớp Positive. Vì vậy, nhóm xem thêm F1 của từng lớp. Positive đạt 0,8539, Neutral đạt 0,4795, còn Negative chỉ đạt 0,3806.

Nhìn vào ma trận nhầm lẫn, trong 114 mẫu Negative, mô hình dự đoán đúng 51 mẫu. Một số mẫu bị nhầm sang Neutral và Positive. Điều này cho thấy mô hình nhận biết lớp phổ biến khá tốt nhưng vẫn gặp khó với lớp ít mẫu.

Vì đây là đồ án môn học, nhóm không muốn chỉ nêu một con số đẹp. Kết luận của nhóm là kết quả tổng thể ở mức vừa phải, còn khả năng nhận diện Negative cần được cải thiện. Macro F1 và ma trận nhầm lẫn giúp nhìn rõ hạn chế này hơn Accuracy.

## Slide 10 — Phân tích lỗi

**Thời lượng: 50 giây**

Để hiểu tại sao mô hình đoán sai, nhóm đọc thủ công 15 trường hợp đại diện. Trong số này, 10 review có cảm xúc lẫn lộn. Ví dụ, người viết khen đồng nghiệp nhưng lại chê lương hoặc quản lý. Bốn review có dấu hiệu nhãn từ rating chưa phù hợp hoàn toàn với nội dung. Một review khá dài và nói về nhiều khía cạnh khác nhau.

TF-IDF chủ yếu dựa vào từ và cụm từ, nên khó hiểu đầy đủ một review dài hoặc có nhiều ý trái ngược. Tuy nhiên, 15 mẫu là số lượng nhỏ. Nhóm chỉ dùng chúng để tìm dạng lỗi thường gặp trong mẫu đã đọc, không xem đây là tỷ lệ đại diện cho toàn bộ 442 lỗi.

Nếu tiếp tục phát triển, nhóm muốn tạo một tập nhãn thủ công nhỏ và tách cảm xúc theo từng khía cạnh.

## Slide 11 — Insight doanh nghiệp

**Thời lượng: 50 giây**

Sau phần đánh giá mô hình, nhóm thử dùng dữ liệu để quan sát năm công ty có nhiều review nhất. Với FPT, NashTech, Bosch và KMS, Salary and benefits là khía cạnh có điểm trung bình thấp nhất. Riêng VNG, khía cạnh thấp nhất là Management cares about me.

Kết quả này giúp nhóm biết chủ đề nào nên được đọc kỹ hơn trong review. Tuy nhiên, nhóm không xem đây là bảng xếp hạng công ty. Số lượng review giữa các công ty khác nhau, từ 251 review của KMS đến 2.014 review của FPT. Nhãn cảm xúc cũng được suy ra từ rating.

Vì vậy, biểu đồ chỉ mang tính mô tả trên bộ dữ liệu hiện có. Nếu muốn đưa ra kết luận cho doanh nghiệp, nhóm cần thêm dữ liệu và phương pháp kiểm chứng kỹ hơn.

## Slide 12 — Giải thích kết quả dự đoán

**Thời lượng: 45 giây**

Trước khi tổng kết, nhóm xem lại cách TF-IDF biểu diễn câu sẽ dùng trong demo cuối. Năm token có giá trị cao gồm “xuyên”, “lý”, “không lương”, “lương” và “không”. Cụm “không lương” xuất hiện như một đặc trưng riêng, cho thấy cấu hình bigram đang hoạt động.

Tuy nhiên, biểu đồ này chỉ cho biết token nào nổi bật trong câu. Nó chưa cho biết token đó làm mô hình nghiêng về Positive hay Negative. Muốn biết chiều tác động, cần kết hợp giá trị TF-IDF với hệ số mà Logistic Regression đã học cho từng lớp.

Trong phạm vi đồ án, nhóm dùng biểu đồ để kiểm tra đặc trưng đầu vào. Nhóm chưa xem đây là một phương pháp giải thích hoàn chỉnh cho quyết định của mô hình.

## Slide 13 — Đánh giá và hạn chế

**Thời lượng: 50 giây**

Qua đồ án, nhóm đã thực hiện được các bước chính của một bài toán Máy Học: tìm hiểu dữ liệu, tiền xử lý, huấn luyện nhiều mô hình và đánh giá trên tập riêng. Nhóm cũng xây dựng web demo để kiểm tra mô hình với review mới.

CV Macro F1 là 0,5727 và Final Test là 0,5714. Hai kết quả khá gần nhau, nên trong lần thử này nhóm chưa thấy dấu hiệu mô hình học quá sát tập Development. Tuy vậy, điều này không có nghĩa là mô hình đã tốt ở mọi lớp. F1 của Negative vẫn chỉ đạt 0,3806.

Hạn chế lớn nhất là nhãn được suy ra từ rating. Ngoài ra, TF-IDF chưa hiểu tốt câu dài, mỉa mai và các quan hệ phủ định phức tạp. Đây là những điều nhóm nhận ra sau khi xem kết quả và phân tích lỗi.

## Slide 14 — Kết luận

**Thời lượng: 35 giây**

Tóm lại, đồ án giúp nhóm thực hành đầy đủ quy trình cơ bản của môn Máy Học trên một bộ dữ liệu thực tế. Trong năm mô hình đã thử, Logistic Regression cho kết quả phù hợp nhất với tiêu chí Macro F1 và nhu cầu của web demo.

Kết quả hiện tại là một mốc tham khảo ban đầu, chưa phải hệ thống hoàn chỉnh để sử dụng trong thực tế. Nếu có thêm thời gian, nhóm muốn gán nhãn thủ công một tập nhỏ, phân tích cảm xúc theo từng khía cạnh và thử mô hình tiếng Việt như PhoBERT hoặc ViSoBERT.

Phần nội dung chính của nhóm xin kết thúc tại đây. Tiếp theo, nhóm xin mời bạn Nguyễn Duy Khang trình bày phần live demo.

## Slide 15 — Dẫn vào live demo

**Thời lượng: 55 giây, gồm khoảng 15 giây dẫn dắt và 40 giây thao tác trực tiếp**

**Nguyễn Duy Khang trình bày:** Em xin tiếp tục với phần live demo. Trong phần này, em sẽ minh họa ba bước: chọn một review mẫu, quan sát nhãn cùng xác suất dự đoán, sau đó kiểm tra văn bản đã xử lý và các token TF-IDF nổi bật.

Sau slide dẫn dắt này, em xin chuyển sang ứng dụng Streamlit đã mở sẵn để thao tác trực tiếp.

**Các bước thao tác trên ứng dụng (khoảng 40 giây):**

1. *(~5 giây)* Chuyển sang tab trình duyệt đã mở sẵn trang "Phân tích review" — không mở lại ứng dụng từ đầu để tránh chờ tải.
2. *(~5 giây)* Ở khung "Thử một tình huống", bấm chọn mẫu **"Nhiều vế"** — *"Môi trường tốt nhưng lương thấp và quản lý chưa thật sự quan tâm nhân viên"*. Đây cũng là ví dụ có cảm xúc lẫn lộn giống loại review nhóm đã phân tích lỗi ở slide 10.
3. *(~2 giây)* Bấm nút **"Phân tích cảm xúc"**.
4. *(~8 giây)* Đọc kết quả bên phải: nhãn cảm xúc dự đoán và phần trăm xác suất của lớp đó, rồi chỉ nhanh vào biểu đồ ba thanh xác suất Positive, Neutral, Negative.
5. *(~10 giây)* Kéo xuống phần "Tín hiệu trong văn bản", đọc khung "SAU CHUẨN HÓA & TÁCH TỪ" để cho thấy văn bản đã được làm sạch và tách từ đúng như đã trình bày ở slide 4.
6. *(~10 giây)* Chỉ vào bảng "Token TF-IDF nổi bật" bên cạnh, nêu một hoặc hai token có trọng số cao nhất để nối lại với phần giải thích ở slide 12.

Phần demo của nhóm xin kết thúc. Nhóm cảm ơn thầy và các bạn đã lắng nghe, và nhóm xin sẵn sàng trả lời câu hỏi.

---

# PHẦN B — NGUYỄN DUY KHANG DEMO WEB

**Lưu ý phạm vi:** Bản rút gọn ở slide 15 (40 giây) là bản dùng trong đúng 12 phút trình bày chính. Phần B dưới đây là kịch bản demo đầy đủ, đi qua cả 4 trang của web app — dùng khi còn thời gian, khi thầy cô yêu cầu xem thêm, hoặc trong phần hỏi đáp. Không cố nhồi cả phần B vào slide 15.

## Chuẩn bị trước buổi trình bày

- Khởi động app bằng lệnh trong README (`streamlit run app.py`) và kiểm tra `http://localhost:8501/_stcore/health` trả về `ok`.
- Mở sẵn `http://localhost:8501`, chờ trang **Tổng quan** tải xong toàn bộ metric và biểu đồ.
- Để trình duyệt ở mức zoom 100%, ẩn thanh bookmark và tắt thông báo hệ thống để không bị popup che màn hình khi chia sẻ.
- Ở trang **Phân tích review**, không cần chuẩn bị câu review trong clipboard — bốn tình huống mẫu (Tích cực, Trung tính, Tiêu cực, Nhiều vế) đã có sẵn trong khung "Thử một tình huống". Ưu tiên bấm chọn mẫu thay vì gõ, để tránh gõ sai hoặc mất thời gian.
- Bấm thử "Phân tích cảm xúc" một lần trước giờ trình bày để Logistic Regression và TF-IDF vectorizer đã nằm trong cache. Nếu bỏ qua bước này, lần bấm đầu tiên trên sân khấu sẽ hiện spinner "Đang nạp Logistic Regression và TF-IDF…" và có thể mất vài giây.
- Không cập nhật package hoặc pull code ngay trước giờ trình bày.

## Demo 1 — Trang Tổng quan

**Thời gian:** 20 giây

**Thao tác:** Mở trang **Tổng quan** (trang mặc định khi vào app).

**Lời nói:**

> Em là Nguyễn Duy Khang. Bây giờ em xin demo nhanh ứng dụng của nhóm. Trang Tổng quan tóm tắt 8.414 review đã xử lý trên 5 doanh nghiệp, cùng bốn bước của pipeline: từ review thô, qua chuẩn hoá và TF-IDF, đến Logistic Regression và kết quả có thể quan sát được. Biểu đồ bên phải cũng nhắc lại vì sao nhóm dùng Macro F1 làm chỉ số chính, vì lớp Positive chiếm phần lớn dữ liệu.

**Không nên:** đọc lần lượt từng KPI hoặc giải thích lại Macro F1 từ đầu — phần này đã trình bày ở slide 2.

## Demo 2 — Insight doanh nghiệp

**Thời gian:** 45 giây

**Thao tác:**

1. Chọn **Insight doanh nghiệp** ở sidebar.
2. Chọn doanh nghiệp **FPT Software** (công ty có nhiều review nhất, 2.014 review).
3. Chỉ vào biểu đồ cơ cấu cảm xúc (donut) và biểu đồ điểm trải nghiệm theo 5 khía cạnh.
4. Chuyển WordCloud từ **Positive** sang **Negative**.

**Lời nói:**

> Ở trang Insight doanh nghiệp, em chọn FPT Software vì đây là công ty có nhiều review nhất trong dữ liệu. Positive chiếm khoảng 57,7%, nhưng khía cạnh Salary and benefits lại có điểm trung bình thấp nhất, khoảng 3,17 trên 5 — đúng như nhóm đã nêu ở slide 11. Khi em chuyển WordCloud sang nhóm Negative, các từ khoá xuất hiện nhiều nhất là "không", "lương" và "nhân viên". Từ càng lớn nghĩa là xuất hiện càng nhiều, không có nghĩa đó là nguyên nhân trực tiếp gây ra cảm xúc tiêu cực.

**Không nên:** đọc hết bảng từ khoá bên phải; chỉ cần nêu 2–3 từ đứng đầu.

## Demo 3 — Phân tích review

**Thời gian:** 40 giây *(bản dùng trong slide 15 của phần chính)*

**Thao tác:**

1. Chọn **Phân tích review** ở sidebar.
2. Ở khung "Thử một tình huống", bấm mẫu **"Nhiều vế"** — *"Môi trường tốt nhưng lương thấp và quản lý chưa thật sự quan tâm nhân viên."*
3. Bấm **"Phân tích cảm xúc"**.
4. Đọc nhãn và xác suất bên phải, sau đó kéo xuống đọc khung "SAU CHUẨN HÓA & TÁCH TỪ" và bảng "Token TF-IDF nổi bật".

**Kết quả hiện tại đã kiểm chứng** (chạy trực tiếp trên pipeline thật, có thể lệch nhẹ nếu model được huấn luyện lại):

- Nhãn cuối: **Neutral — 53,7%**.
- Xác suất ba lớp: Neutral khoảng **53,7%**, Positive khoảng **39,2%**, Negative khoảng **7,1%**.
- Văn bản sau chuẩn hoá: `môi_trường tốt lương quản_lý chưa thật_sự quan_tâm nhân_viên`.
- Token TF-IDF nổi bật nhất: `chưa thật_sự`, `thật_sự`, `tốt lương`, `quan_tâm nhân_viên`.

**Lời nói:**

> Kết quả là Neutral, khoảng 53,7%. Xác suất Positive vẫn còn khá gần, khoảng 39,2%, vì câu này vừa khen môi trường vừa chê lương và quản lý — đúng dạng cảm xúc lẫn lộn nhóm đã nói ở slide 10. Bên dưới, văn bản sau tiền xử lý cho thấy các từ ít mang ý nghĩa đã được lược bớt nhưng từ phủ định như "chưa" vẫn được giữ lại. Token nổi bật nhất là cụm "chưa thật_sự", đúng như phần bigram nhóm đã trình bày ở slide 6.

**Không nên:** gõ một câu mới trên sân khấu; chỉ bấm mẫu có sẵn để không tốn thời gian và tránh lỗi chính tả.

## Demo 4 — Benchmark & Đánh giá lỗi

**Thời gian:** 40 giây

**Thao tác:**

1. Chọn **Benchmark** ở sidebar. Chỉ vào chấm tròn của Logistic Regression trên biểu đồ xếp hạng.
2. Chọn **Đánh giá & lỗi**. Chỉ vào ma trận nhầm lẫn và biểu đồ Precision/Recall/F1 theo lớp.
3. Ở khung "Khám phá 15 lỗi đại diện", lọc Nhãn thật là **Negative**, mở một mẫu bất kỳ để đọc nhận xét thủ công.

**Lời nói:**

> Trang Benchmark cho thấy Logistic Regression đứng đầu 5 mô hình với CV Macro F1 là 0,5727, nhỉnh hơn Linear SVM chỉ 0,0003. Trên Final Test, Macro F1 là 0,5714, gần với điểm CV nên nhóm chưa thấy dấu hiệu overfitting rõ rệt. Ở trang Đánh giá và lỗi, ma trận nhầm lẫn và biểu đồ theo lớp cho thấy Negative vẫn là lớp khó nhất, Recall chỉ khoảng 44,7%. Phần lọc lỗi bên dưới cho phép đọc từng review nhóm đã phân tích thủ công — phần lớn thuộc nhóm cảm xúc lẫn lộn, đúng như nhóm đã trình bày ở slide 10.

**Không nên:** đọc hết bảng "Nhật ký thực nghiệm" của cả 5 mô hình; chỉ nêu 1–2 dòng đầu.

## Kết thúc demo và buổi trình bày

> Qua demo, nhóm đã thể hiện được toàn bộ luồng từ insight doanh nghiệp, phân tích một review mới, cho đến benchmark và đánh giá lỗi của mô hình. Phần demo của em đến đây là kết thúc.
>
> Nhóm xin chân thành cảm ơn thầy và các bạn đã theo dõi. Nhóm xin sẵn sàng trả lời câu hỏi.

**Thao tác:** Giữ nguyên trang đang mở trên web app, không chuyển lại PowerPoint.

**Dự phòng — không đọc trong lúc demo, chỉ nói nếu thầy hỏi thêm về hạn chế của model:**

> Nhóm cũng phát hiện thêm một hạn chế khi tự thử nghiệm ngoài 15 mẫu lỗi đã đọc thủ công: bước loại bỏ stopword hiện dùng một danh sách tiếng Việt chung, trong đó có cả các từ chỉ mức độ như "thấp" và "nhiều". Ví dụ câu "Công ty lương thấp, họp nhiều" bị mô hình dự đoán là Positive với xác suất khoảng 79,5%, vì sau khi làm sạch chỉ còn lại "công ty lương họp" — mất hết "thấp" và "nhiều", vốn là hai từ quyết định câu này mang nghĩa tiêu cực. Đây là hạn chế cụ thể nhóm nhận ra nhưng chưa kịp sửa trong phạm vi đồ án lần này.

---

## Gợi ý khi tập thử

- Giữ cách nói “trong phạm vi bài tập” hoặc “theo kết quả nhóm thử nghiệm” khi trả lời các câu hỏi rộng. Cách nói này phù hợp với vai trò sinh viên và tránh kết luận quá mức.
- Tập một lần với đồng hồ và đánh dấu mốc 6:10 ở cuối slide 8. Nếu vượt mốc, rút ngắn phần cấu hình TF-IDF ở slide 6.
- Ở slide 9, giải thích vì sao Accuracy chưa đủ trước khi đọc F1 của từng lớp. Đây là phần thể hiện nhóm hiểu cách đánh giá mô hình.
- Không cần đọc toàn bộ con số ở slide 11. Chỉ nêu kết luận 4 trên 5 công ty và ngoại lệ VNG.
- Trước khi lên trình bày, mở sẵn ứng dụng Streamlit và bấm thử "Phân tích cảm xúc" một lần (với mẫu bất kỳ) để model và TF-IDF được nạp vào cache trước. Lần bấm đầu tiên sau khi mở app có thể hiện spinner "Đang nạp Logistic Regression và TF-IDF…" và mất vài giây, nếu để lúc live sẽ chiếm hết 40 giây thao tác.
- Nếu live demo tải chậm, giữ nguyên slide 15 và giải thích ngắn ba bước mà nhóm dự định thao tác; không trình chiếu sẵn kết quả dự đoán trên slide.
- Khi chưa chắc một câu trả lời, có thể nói: “Phần này nhóm chưa kiểm chứng đủ trong phạm vi đồ án. Theo hiểu biết hiện tại của nhóm, chúng em dự đoán rằng...” rồi nêu giả thuyết và cách kiểm tra thêm.

## Một số câu trả lời ngắn phù hợp với sinh viên năm nhất

**Vì sao chọn Logistic Regression thay vì SVM?**  
Hai mô hình có điểm rất gần nhau. Nhóm chọn Logistic Regression vì điểm CV nhỉnh hơn một chút và mô hình trả về xác suất thuận tiện cho web demo. Nhóm không kết luận Logistic Regression luôn tốt hơn SVM.

**Vì sao Accuracy cao nhưng Macro F1 thấp hơn?**  
Vì dữ liệu có nhiều mẫu Positive. Mô hình làm tốt lớp này sẽ có Accuracy cao, nhưng vẫn có thể làm chưa tốt ở Negative và Neutral. Macro F1 cho ba lớp trọng số ngang nhau nên phản ánh rõ hơn vấn đề mất cân bằng.

**Kết quả 0,5714 có tốt không?**  
Theo nhóm, đây là kết quả tham khảo ở mức vừa phải cho pipeline cơ bản. Kết quả giữa Development và Final Test khá ổn định, nhưng F1 của lớp Negative còn thấp nên mô hình vẫn cần cải thiện.

**SMOTE có làm thay đổi dữ liệu thật không?**  
SMOTE chỉ tạo thêm điểm tổng hợp trong phần dữ liệu huấn luyện. Nhóm không thêm mẫu tổng hợp vào validation hoặc Final Test, nên các tập dùng để đánh giá vẫn giữ nguyên.

**Tương quan cao có chứng minh lương hoặc quản lý gây ra rating thấp không?**  
Không. Tương quan chỉ cho thấy hai giá trị thay đổi cùng nhau trong dữ liệu. Muốn kết luận nguyên nhân cần thiết kế phân tích khác và kiểm soát thêm nhiều yếu tố.
