import psycopg2
import os
from dotenv import load_dotenv
from core.reasoning.retriever import retrieve_articles
from tests.evaluate import test_cases

load_dotenv()

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
    
    # [FIX]: Header updated to reflect the production net size
    print(f"{'Query':<40} | {'Expected':<10} | {'In Top 40?'}")
    print("-" * 65)

    for q, expected in test_cases.items():
        if expected is None:
            continue
        
        total_valid += 1
        
        # [ALIGNED]: Matches your production k=40 setting
        results = retrieve_articles(conn, q, k=40)
        retrieved_ids = [str(r["article-id"]) for r in results]
        
        found = expected in retrieved_ids
        if found:
            hits += 1
        
        status = "✅ YES" if found else "❌ NO"
        print(f"{q[:40]:<40} | {expected:<10} | {status}")

    conn.close()
    
    recall_score = (hits / total_valid) * 100
    print("\n" + "="*40)
    # [FIX]: Label corrected to RECALL@40
    print(f"FINAL RECALL@40: {recall_score:.2f}%")
    print("="*40)
    
    if recall_score >= 98:
        print("\n🏆 RECALL MASTERED: The answer is almost always in the pool.")
        print("STRATEGY: Stop tuning the retriever. All remaining errors are Reranker logic issues.")
    else:
        print("\n⚠️ RECALL LEAK: Some articles are still missing from the top 40.")
        print("STRATEGY: Check if those missing articles were properly embedded.")

if __name__ == "__main__":
    run_recall_benchmark()