# src/evaluation.py
import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from src.store import search_similar_chunks
from src.generation import generate_answer  # Import hàm mới

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_benchmark(benchmark_file: str, top_k: int = 3):
    print(f"\n⏳ Bắt đầu đánh giá file: {benchmark_file}")
    
    if not os.path.exists(benchmark_file):
        print(f"❌ Không tìm thấy file {benchmark_file}")
        return

    with open(benchmark_file, "r", encoding="utf-8") as f:
        questions = [json.loads(line) for line in f if line.strip()]

    hits = 0
    mrr_sum = 0.0
    traces = []

    for q in questions:
        query = q["question"]
        expected_articles = q["evidence"]
        golden_answer = q.get("answer", "(Không có sẵn)")  # <-- Đọc đáp án chuẩn
        
        # 1. Tạo vector cho câu hỏi
        response = client.embeddings.create(
            input=[query],
            model="text-embedding-3-small"
        )
        query_vector = response.data[0].embedding
        
        # 2. Filter
        filter_article = None
        if q.get("requires_filter", False):
            match = re.search(r'[Đđ]iều\s+(\d+)', query)
            if match:
                filter_article = int(match.group(1))
        
        # 3. Tìm kiếm
        results = search_similar_chunks(query_vector, limit=top_k, filter_article=filter_article)
        
        # --- IN RA CÂU HỎI VÀ ĐÁP ÁN CHUẨN ---
        print("\n" + "="*70)
        print(f"❓ Câu hỏi: {query}")
        print(f"🎯 Kỳ vọng: Điều {expected_articles}")
        print(f"📖 Đáp án chuẩn: {golden_answer}")
        if filter_article:
            print(f"🔍 (Filter: Chỉ tìm trong Điều {filter_article})")
        print("-" * 70)
        
        hit = False
        rank_found = -1
        retrieved_info = []
        retrieved_texts = []  # <-- Lưu text để đưa vào LLM
        
        for rank, row in enumerate(results):
            chunk_id, text, metadata, distance = row
            retrieved_article = metadata.get("article_number")
            retrieved_texts.append(text)  # Lưu lại để sinh câu trả lời
            
            retrieved_info.append({
                "rank": rank + 1,
                "chunk_id": chunk_id,
                "article_number": retrieved_article,
                "distance": float(distance)
            })
            
            print(f"  [Top {rank + 1}] Điều {retrieved_article} (Độ lệch: {distance:.4f})")
            preview_text = text[:250].replace('\n', ' ') 
            print(f"  📄 Nội dung: {preview_text}...")

            if retrieved_article in expected_articles and not hit:
                hit = True
                rank_found = rank + 1
        
        # --- SINH CÂU TRẢ LỜI BẰNG LLM ---
        print("-" * 70)
        try:
            generated = generate_answer(query, retrieved_texts)
            print(f"🤖 AI trả lời (dựa trên Top 3): {generated}")
        except Exception as e:
            print(f"⚠️ Lỗi sinh câu trả lời: {e}")
            generated = ""
        
        if hit:
            hits += 1
            mrr_sum += (1.0 / rank_found)
            print(f"\n  ✅ KẾT QUẢ TRUY XUẤT: HIT (Tìm thấy ở vị trí {rank_found})")
        else:
            print(f"\n  ❌ KẾT QUẢ TRUY XUẤT: MISS")

        traces.append({
            "id": q.get("id", ""),
            "question": query,
            "golden_answer": golden_answer,
            "expected_articles": expected_articles,
            "retrieved": retrieved_info,
            "generated_answer": generated,  # Lưu lại để báo cáo
            "hit": hit,
            "rank_found": rank_found if hit else None
        })

    # Tính tổng
    total = len(questions)
    hit_rate = (hits / total) * 100 if total > 0 else 0
    mrr = mrr_sum / total if total > 0 else 0

    print("\n" + "="*70)
    print("📊 TỔNG KẾT ĐÁNH GIÁ TRUY XUẤT (RETRIEVAL)")
    print("="*70)
    print(f"Tổng số câu: {total}")
    print(f"Hit Rate@{top_k}: {hit_rate:.2f}% ({hits}/{total} câu)")
    print(f"MRR@{top_k}: {mrr:.4f}")
    print("="*70)
    
    os.makedirs("results", exist_ok=True)
    trace_file = f"results/trace_{os.path.basename(benchmark_file).replace('.jsonl', '')}.json"
    with open(trace_file, "w", encoding="utf-8") as f:
        json.dump(traces, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã lưu trace: {trace_file}")