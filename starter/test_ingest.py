# test_ingest.py
from src.ingestion import ingest_pdf

# Gọi hàm đọc file
docs = ingest_pdf("data/LuatHonNhan_30p.pdf")

# In thử dữ liệu
if len(docs) > 0:
    print("\n--- NỘI DUNG TRANG 1 ---")
    print(docs[0].text) 
    
    print("\n--- NỘI DUNG TRANG 8 ---")
    if len(docs) > 7:
        print(docs[7].text[:300])
else:
    print("❌ Không đọc được trang nào!")