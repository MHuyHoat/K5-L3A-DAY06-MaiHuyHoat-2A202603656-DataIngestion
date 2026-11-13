# src/run.py
import sys
from src.ingestion import ingest_pdf
from src.chunking import chunk_fixed_size, chunk_by_article, chunk_by_article_with_filter
from src.embeddings import embed_chunks
from src.store import init_db, save_chunks_to_db

def main():
    pdf_path = "data/LuatHonNhan_30p.pdf"
    
    # Mặc định chạy Cấu hình C, nhưng có thể truyền tham số A, B, C từ terminal
    config = "C"
    if len(sys.argv) > 1:
        config = sys.argv[1].upper()
    
    print(f"🚀 Đang chạy với Cấu hình {config}")
    init_db()
    
    docs = ingest_pdf(pdf_path)
    
    all_chunks = []
    for doc in docs:
        if config == "A":
            chunks = chunk_fixed_size(doc)
        elif config == "B":
            chunks = chunk_by_article(doc)
        else: # Mặc định là C
            chunks = chunk_by_article_with_filter(doc)
        all_chunks.extend(chunks)
        
    print(f"✅ Đã cắt thành {len(all_chunks)} chunks (Cấu hình {config}).")
    
    embedded_chunks = embed_chunks(all_chunks)
    save_chunks_to_db(embedded_chunks)
    print("--- HOÀN TẤT PIPELINE ---")

if __name__ == "__main__":
    main()