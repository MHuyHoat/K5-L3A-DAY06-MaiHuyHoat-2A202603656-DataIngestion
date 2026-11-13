# src/store.py
import os
import psycopg
from psycopg.types.json import Jsonb
from dotenv import load_dotenv
from typing import List
from src.models import Chunk

load_dotenv()

# Đảm bảo bạn đã có DATABASE_URL trong file .env
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:55433/rag_db")

def init_db():
    """Tạo bảng lưu trữ vector nếu chưa có."""
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            # Bảng này lưu vector 1536 chiều (theo model text-embedding-3-small)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    chunk_id VARCHAR(255) UNIQUE,
                    doc_id VARCHAR(255),
                    text TEXT,
                    metadata JSONB,
                    embedding vector(1536)
                );
            """)
            conn.commit()
    print("✅ Khởi tạo Database thành công.")

def save_chunks_to_db(chunks: List[Chunk]):
    """Lưu danh sách các chunk đã có embedding vào database."""
    if not chunks:
        return
        
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            for c in chunks:
                cur.execute(
                    """
                    INSERT INTO document_chunks (chunk_id, doc_id, text, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (chunk_id) DO NOTHING;
                    """,
                    (c.chunk_id, c.doc_id, c.text, Jsonb(c.metadata), c.embedding)
                )
        conn.commit()
    print(f"✅ Đã lưu {len(chunks)} chunks vào Database.")

def search_similar_chunks(query_embedding: List[float], limit: int = 3):
    """Tìm kiếm các chunk có vector gần nhất."""
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT chunk_id, text, metadata, embedding <=> %s::vector AS distance
                FROM document_chunks
                ORDER BY distance ASC
                LIMIT %s;
                """,
                (query_embedding, limit)
            )
            return cur.fetchall()