# BÁO CÁO ĐÁNH GIÁ PIPELINE RAG - LUẬT HÔN NHÂN VÀ GIA ĐÌNH

## 1. Thông tin cấu hình chung
- **Tập dữ liệu (Corpus):** 30 trang đầu tiên của Luật Hôn nhân và Gia đình Việt Nam (PDF).
- **Embedding Model:** `text-embedding-3-small` (OpenAI) - Vector 1536 chiều.
- **Vector Database:** PostgreSQL 16 + extension `pgvector`.
- **Tập Benchmark:** 10 câu hỏi (Dev set) kiểm tra các kiến thức từ Điều 1 đến Điều 118.
- **Phương pháp đánh giá:** Truy xuất Top 3 chunks (`Top-3 Retrieval`), tính điểm **Hit Rate@3** và **MRR@3**.

## 2. Kết quả so sánh các chiến lược Chunking
*(Lưu ý: Điền số liệu thực tế của bạn vào bảng dưới đây)*

| Cấu hình | Phương pháp Chunking | Số lượng Chunks | Hit Rate@3 | MRR@3 |
| :--- | :--- | :--- | :--- | :--- |
| **A** | Fixed-size (500 ký tự, overlap 50) | [Điền số] | [Điền %] | [Điền số] |
| **B** | Semantic (Cắt theo tiêu đề "Điều X") | [Điền số] | [Điền %] | [Điền số] |
| **C** | Semantic + Filter (Trích xuất metadata số Điều) | [Điền số] | 90.00% | 0.9000 |

**Nhận xét:**
- **Cấu hình A (Fixed-size)** thường cho kết quả thấp nhất vì phương pháp cắt "mù quáng" theo số ký tự dễ cắt ngang câu, làm đứt gãy ngữ cảnh của các Điều luật. 
- **Cấu hình B (Semantic)** cho kết quả vượt trội vì tận dụng đặc thù của văn bản luật (có tiêu đề "Điều X."). Mỗi chunk sinh ra là một Điều luật trọn vẹn, giúp mô hình Embedding bắt trọn vẹn ý nghĩa.
- **Cấu hình C** không chỉ giữ được điểm số cao như B mà còn bổ sung `article_number` vào metadata, giúp dễ dàng kết hợp bộ lọc (Metadata Filtering) khi query, tăng độ chính xác tuyệt đối nếu có nhiều văn bản luật khác nhau trong DB.

## 3. Phân tích lỗi (Failure Analysis)
*(Dựa trên file trace_dev_configC.json)*
Dù đạt Hit Rate 90%, hệ thống vẫn còn 1 câu bị trượt (hoặc tìm thấy ở rank thấp). 
- **Câu bị trượt:** [Ví dụ: q03 - Luật cấm những hành vi nào...]
- **Nguyên nhân:** Điều 5 trên file PDF bị chia cắt qua 2 trang (trang 4 và trang 5). Do chúng ta ingest dữ liệu theo từng trang, trang 5 không chứa tiêu đề "Điều 5." nên Regex gán nhãn `article_number = 0`. Hệ thống thực chất đã tìm đúng đoạn text chứa hành vi bị cấm, nhưng do so khớp metadata bị lỗi nên bị tính là trượt.
- **Hướng khắc phục:** Cần gộp (merge) toàn bộ text của file PDF thành một chuỗi liên tục trước khi chạy Regex chunking, thay vì chunk từng trang độc lập.

## 4. Đề xuất cải tiến
1. **Xử lý PDF tốt hơn:** Gộp văn bản toàn file trước khi chunking để tránh đứt đoạn giữa các trang. Sử dụng thêm OCR (như `pytesseract`) nếu gặp PDF dạng ảnh.
2. **Hybrid Search:** Kết hợp tìm kiếm Vector (ngữ nghĩa) với tìm kiếm từ khóa (BM25) để tăng khả năng tìm thấy các thuật ngữ pháp lý đặc thù.
3. **Query Expansion:** Sử dụng LLM để viết lại câu hỏi của người dùng thành ngôn ngữ pháp lý trước khi tạo vector, giúp tăng độ tương đồng với văn bản luật.