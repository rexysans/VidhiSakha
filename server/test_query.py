import requests
import time

try:
    start = time.time()
    print("Sending request...")
    r = requests.get(
        "http://127.0.0.1:8000/v1/ask?q=equality%20before%20law", timeout=120
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}...")
    print(f"Time taken: {time.time() - start:.2f}s")
except Exception as e:
    print(f"Error: {e}")
