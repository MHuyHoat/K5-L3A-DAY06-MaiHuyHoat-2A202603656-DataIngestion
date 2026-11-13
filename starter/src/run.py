# src/run.py
from src.ingestion import ingest_pdf
from src.chunking import chunk_by_article_with_filter
from src.embeddings import embed_chunks
from src.store import init_db, save_chunks_to_db

def main():
    pdf_path = "data/LuatHonNhan_30p.pdf"
    
    # 1. Khởi tạo DB
    init_db()
    
    # 2. Đọc PDF
    print("\n--- BẮT ĐẦU PIPELINE ---")
    docs = ingest_pdf(pdf_path)
    
    # 3. Cắt nhỏ (Chunking) - Chúng ta chọn Cấu hình C (tốt nhất cho văn bản luật)
    all_chunks = []
    for doc in docs:
        chunks = chunk_by_article_with_filter(doc)
        all_chunks.extend(chunks)
        
    print(f"✅ Đã cắt thành {len(all_chunks)} chunks.")
    
    # 4. Tạo Embeddings
    embedded_chunks = embed_chunks(all_chunks)
    
    # 5. Lưu vào DB
    save_chunks_to_db(embedded_chunks)
    
    print("--- HOÀN TẤT PIPELINE ---")

if __name__ == "__main__":
    main()