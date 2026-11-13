# src/models.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class Document:
    """Đại diện cho một trang tài liệu được trích xuất từ file gốc."""
    doc_id: str
    text: str
    source: str
    page: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Chunk:
    """Đại diện cho một đoạn văn bản sau khi được chia nhỏ (chunking)."""
    chunk_id: str
    doc_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None