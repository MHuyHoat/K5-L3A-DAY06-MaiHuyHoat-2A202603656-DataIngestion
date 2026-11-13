# src/chunking.py
import re
from typing import List
from src.models import Document, Chunk

def chunk_fixed_size(doc: Document, chunk_size: int = 500, overlap: int = 50) -> List[Chunk]:
    chunks = []
    text = doc.text
    start = 0
    chunk_idx = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        
        # Tìm số Điều trong chunk
        match = re.search(r'Điều (\d+)\.', chunk_text)
        article_num = int(match.group(1)) if match else 0
        
        chunks.append(Chunk(
            chunk_id=f"{doc.doc_id}_p{doc.page}_fixed_{chunk_idx}",
            doc_id=doc.doc_id,
            text=chunk_text.strip(),
            metadata={
                **doc.metadata, 
                "page": doc.page, 
                "strategy": "fixed_size",
                "article_number": article_num
            }
        ))
        start += (chunk_size - overlap)
        chunk_idx += 1
    return chunks

def chunk_by_article(doc: Document) -> List[Chunk]:
    chunks = []
    text = doc.text
    pattern = r'(?=Điều \d+\.)'
    parts = re.split(pattern, text)
    
    chunk_idx = 0
    for part in parts:
        part = part.strip()
        if len(part) < 30: 
            continue
            
        match = re.match(r'Điều (\d+)\.', part)
        article_num = int(match.group(1)) if match else 0
        
        chunks.append(Chunk(
            chunk_id=f"{doc.doc_id}_p{doc.page}_semantic_{chunk_idx}",
            doc_id=doc.doc_id,
            text=part,
            metadata={
                **doc.metadata, 
                "page": doc.page, 
                "strategy": "semantic",
                "article_number": article_num
            }
        ))
        chunk_idx += 1
    return chunks

def chunk_by_article_with_filter(doc: Document) -> List[Chunk]:
    chunks = []
    text = doc.text
    pattern = r'(?=Điều \d+\.)'
    parts = re.split(pattern, text)
    
    for part in parts:
        part = part.strip()
        if len(part) < 30: 
            continue
            
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
                "article_number": article_num
            }
        ))
    return chunks