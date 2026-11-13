# test_eval.py
import sys
from src.evaluation import evaluate_benchmark

# Mặc định chạy file dev, có thể truyền file khác từ terminal
file_path = "data/benchmark_dev.json"
if len(sys.argv) > 1:
    file_path = sys.argv[1]

evaluate_benchmark(file_path)