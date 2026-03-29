import requests
import json

# Test a few queries to see score distribution
test_queries = [
    "equality before law",  # Should be 14 (PASS)
    "protection against double jeopardy",  # Should be 20 (FAIL - returns None)
    "freedom to form associations",  # Should be 19 (FAIL - returns None)
    "right to life",  # Should be 21 (FAIL - returns 41)
]

for query in test_queries:
    try:
        r = requests.get(f"http://127.0.0.1:8000/v1/ask?q={query}", timeout=30)
        data = r.json()
        answer = data.get("answer", {})
        citations = answer.get("citations", [])

        print(f"\nQuery: {query}")
        if citations:
            print(f"  Predicted: {citations[0].get('article_id')}")
        else:
            print(f"  Predicted: None (rejected)")
        print(f"  Response: {answer.get('answer', '')[:100]}...")
    except Exception as e:
        print(f"Error for '{query}': {e}")
