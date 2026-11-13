# src/ingestion.py
import os
from pypdf import PdfReader
from src.models import Document  # <--- THÊM DÒNG NÀY

def ingest_pdf(file_path: str) -> list[Document]:
    """
    Đọc file PDF và trả về danh sách các Document (mỗi trang là 1 Document).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    reader = PdfReader(file_path)
    doc_id = os.path.basename(file_path).replace(".pdf", "")
    documents = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        
        if not text or not text.strip():
            continue
            
        doc = Document(
            doc_id=doc_id,
            text=text.strip(),
            source=file_path,
            page=i + 1, 
            metadata={
                "category": "luat_hon_nhan_gia_dinh",
                "year": 2014
            }
        )
        documents.append(doc)

    print(f"✅ Đã đọc thành công {len(documents)} trang từ {file_path}")
    return documents