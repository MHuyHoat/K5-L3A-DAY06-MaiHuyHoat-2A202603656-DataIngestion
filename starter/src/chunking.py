# src/chunking.py
import re
from typing import List
from src.models import Document, Chunk

def chunk_fixed_size(doc: Document, chunk_size: int = 500, overlap: int = 50) -> List[Chunk]:
    """
    Cấu hình A: Cắt theo kích thước cố định (Fixed-size).
    Cắt văn bản thành các đoạn có độ dài `chunk_size` ký tự, 
    phần đầu của đoạn sau sẽ lặp lại `overlap` ký tự của đoạn trước để giữ ngữ cảnh.
    """
    chunks = []
    text = doc.text
    start = 0
    chunk_idx = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        
        chunks.append(Chunk(
            chunk_id=f"{doc.doc_id}_p{doc.page}_fixed_{chunk_idx}",
            doc_id=doc.doc_id,
            text=chunk_text.strip(),
            metadata={
                **doc.metadata, 
                "page": doc.page, 
                "strategy": "fixed_size"
            }
        ))
        
        # Tiến lên, lùi lại một khoảng overlap
        start += (chunk_size - overlap)
        chunk_idx += 1
        
    return chunks


def chunk_by_article(doc: Document) -> List[Chunk]:
    """
    Cấu hình B: Cắt theo đoạn/cấu trúc (Semantic - Cắt theo Điều luật).
    Tận dụng đặc thù văn bản luật có các tiêu đề "Điều X." để chia nhỏ.
    """
    chunks = []
    text = doc.text
    
    # Regex dùng lookahead (?=...) để tách văn bản ngay trước chữ "Điều X."
    # Giữ nguyên chữ "Điều" ở đầu mỗi chunk
    pattern = r'(?=Điều \d+\.)'
    parts = re.split(pattern, text)
    
    chunk_idx = 0
    for part in parts:
        part = part.strip()
        # Bỏ qua các phần quá ngắn (ví dụ: header, footer, rác)
        if len(part) < 30: 
            continue
            
        chunks.append(Chunk(
            chunk_id=f"{doc.doc_id}_p{doc.page}_semantic_{chunk_idx}",
            doc_id=doc.doc_id,
            text=part,
            metadata={
                **doc.metadata, 
                "page": doc.page, 
                "strategy": "semantic"
            }
        ))
        chunk_idx += 1
        
    return chunks


def chunk_by_article_with_filter(doc: Document) -> List[Chunk]:
    """
    Cấu hình C: Giống cấu hình B nhưng trích xuất thêm số Điều vào metadata.
    Việc này cho phép hệ thống tìm kiếm có thể filter (lọc) chính xác theo số Điều.
    """
    chunks = []
    text = doc.text
    
    pattern = r'(?=Điều \d+\.)'
    parts = re.split(pattern, text)
    
    for part in parts:
        part = part.strip()
        if len(part) < 30: 
            continue
            
        # Trích xuất số điều (VD: từ "Điều 15. ..." lấy ra số 15)
        match = re.match(r'Điều (\d+)\.', part)
        article_num = int(match.group(1)) if match else 0
        
        chunks.append(Chunk(
            chunk_id=f"{doc.doc_id}_p{doc.page}_art{article_num}",
            doc_id=doc.doc_id,
            text=part,
            metadata={
                **doc.metadata, 
                "page": doc.page, 
                "strategy": "semantic_filter",
                "article_number": article_num  # <-- Trường dùng để filter
            }
        ))
        
    return chunks