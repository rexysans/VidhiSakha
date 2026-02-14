import psycopg2
import os

from dotenv import load_dotenv
from core.reasoning.retriever import retrieve_articles

load_dotenv()

# Import the test cases from your evaluate.py
from tests.evaluate import test_cases

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def run_recall_benchmark():
    conn = get_connection()
    hits = 0
    total_valid = 0
    
    print(f"{'Query':<40} | {'Expected':<10} | {'In Top 20?'}")
    print("-" * 65)

    for q, expected in test_cases.items():
        # Skip junk queries for recall measurement (they shouldn't have a hit)
        if expected is None:
            continue
        
        total_valid += 1
        
        # We retrieve 20 articles to see if the target is in the net
        results = retrieve_articles(conn, q, k=20)
        retrieved_ids = [str(r["article-id"]) for r in results]
        
        found = expected in retrieved_ids
        if found:
            hits += 1
        
        status = "✅ YES" if found else "❌ NO"
        print(f"{q[:40]:<40} | {expected:<10} | {status}")

    conn.close()
    
    recall_score = (hits / total_valid) * 100
    print("\n" + "="*30)
    print(f"FINAL RECALL@20: {recall_score:.2f}%")
    print("="*30)
    
    if recall_score >= 95:
        print("\nSTRATEGY: Recall is strong. DO NOT upgrade embeddings. Proceed to Reranker.")
    else:
        print("\nSTRATEGY: Recall is the bottleneck. Upgrade to BGE-M3 before adding Reranker.")

if __name__ == "__main__":
    run_recall_benchmark()