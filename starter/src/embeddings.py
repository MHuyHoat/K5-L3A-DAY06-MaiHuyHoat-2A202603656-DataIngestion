# src/embeddings.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from src.models import Chunk

load_dotenv()

# Khởi tạo client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_chunks(chunks: List[Chunk]) -> List[Chunk]:
    """Tạo embedding cho danh sách các chunk bằng OpenAI API."""
    if not chunks:
        return []
        
    print(f"⏳ Đang gọi API OpenAI để tạo vector cho {len(chunks)} chunks...")
    texts = [c.text for c in chunks]
    
    # Gọi API (giới hạn batch size khoảng 2048 của OpenAI)
    # Vì file của chúng ta nhỏ (30 trang) nên có thể gửi 1 lần
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    
    # Gán vector vào từng chunk
    for i, data in enumerate(response.data):
        chunks[i].embedding = data.embedding
        
    print("✅ Tạo vector thành công!")
    return chunks