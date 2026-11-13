# src/generation.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(question: str, contexts: list[str]) -> str:
    """Dùng LLM đọc các context tìm được và sinh ra câu trả lời hoàn chỉnh."""
    context_text = "\n\n---\n\n".join(contexts)
    
    prompt = f"""Bạn là trợ lý pháp luật. Dựa HOÀN TOÀN vào các đoạn luật sau để trả lời câu hỏi.
Nếu không có thông tin trong các đoạn luật, hãy trả lời "Không tìm thấy thông tin".

CÁC ĐOẠN LUẬT LIÊN QUAN:
{context_text}

CÂU HỎI: {question}

TRẢ LỜI (ngắn gọn, trích dẫn số Điều nếu có):"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()