# src/evaluation.py
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from src.store import search_similar_chunks

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
        
        # 1. Tạo vector cho câu hỏi
        response = client.embeddings.create(
            input=[query],
            model="text-embedding-3-small"
        )
        query_vector = response.data[0].embedding
        
        # 2. Tìm kiếm trong DB
        results = search_similar_chunks(query_vector, limit=top_k)
        
        # 3. Đánh giá kết quả
        hit = False
        rank_found = -1
        
        retrieved_info = []
        for rank, row in enumerate(results):
            chunk_id, text, metadata, distance = row
            # Lấy số điều từ metadata
            retrieved_article = metadata.get("article_number")
            
            retrieved_info.append({
                "rank": rank + 1,
                "chunk_id": chunk_id,
                "article_number": retrieved_article,
                "distance": float(distance)
            })
            
            # Nếu Điều luật tìm được nằm trong danh sách evidence mong đợi
            if retrieved_article in expected_articles and not hit:
                hit = True
                rank_found = rank + 1
                
        # 4. Cộng điểm
        if hit:
            hits += 1
            mrr_sum += (1.0 / rank_found)
            
        # Lưu trace để nộp bài (theo yêu cầu của lab)
        traces.append({
            "id": q.get("id", ""),
            "question": query,
            "expected_articles": expected_articles,
            "retrieved": retrieved_info,
            "hit": hit,
            "rank_found": rank_found if hit else None
        })

    # 5. Tính toán chỉ số tổng
    total = len(questions)
    hit_rate = (hits / total) * 100 if total > 0 else 0
    mrr = mrr_sum / total if total > 0 else 0

    print("\n" + "="*40)
    print("📊 KẾT QUẢ ĐÁNH GIÁ TRUY XUẤT (RETRIEVAL)")
    print("="*40)
    print(f"Tổng số câu hỏi: {total}")
    print(f"Hit Rate@{top_k}: {hit_rate:.2f}% (Tìm thấy đúng {hits}/{total} câu)")
    print(f"MRR@{top_k}: {mrr:.4f}")
    print("="*40)
    
    # Lưu trace ra file để nộp bài
    os.makedirs("results", exist_ok=True)
    trace_file = "results/trace_dev.json"
    with open(trace_file, "w", encoding="utf-8") as f:
        json.dump(traces, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã lưu chi tiết trace vào {trace_file}")