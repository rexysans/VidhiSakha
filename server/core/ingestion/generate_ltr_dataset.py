import csv
import json
import os
import sys

# Ensure the root directory is in the path for imports
sys.path.append(os.getcwd())

try:
    # Importing the actual functions/classes from your files
    from core.reasoning.retriever import retrieve_articles
    from core.reasoning.reranker import ScalableLegalReranker
    from core.api.main import get_connection
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you run this from the project root (VidhiSakhā/).")
    sys.exit(1)

# File Paths
INPUT_FILE = "dataset/training_queries.json"
OUTPUT_FILE = "dataset/dataset_ltr.csv"


def generate_dataset():

    conn = get_connection()
    # 1. Initialize Reranker Class
    reranker_tool = ScalableLegalReranker()

    # 2. Load Ground Truth Golden Queries
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found. Please create it first.")
        return

    with open(INPUT_FILE, "r") as f:
        training_queries = json.load(f)

    print(f"🚀 Loaded {len(training_queries)} queries from {INPUT_FILE}")

    # 3. Initialize CSV with LOCKED SCHEMA
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "query",
            "article_id",
            "article_title",
            "neural_score",
            "rank",
            "is_correct",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, entry in enumerate(training_queries):
            query = entry["query"]
            correct_id = str(entry["article_id"])

            print(f"[{i+1}/{len(training_queries)}] Processing: {query}")

            try:
                # FIXED: Call 'retrieve_articles' which returns (results, time)
                candidates = retrieve_articles(conn, query, k=40)

                # FIXED: Call '.rerank()' method from the initialized class
                ranked_candidates = reranker_tool.rerank(query, candidates)

                # 4. Extract features and write rows
                for pos, cand in enumerate(ranked_candidates, start=1):
                    cand_id = str(cand.get("article-id"))

                    writer.writerow(
                        {
                            "query": query,
                            "article_id": cand_id,
                            "article_title": cand.get("title", "Unknown"),
                            "neural_score": cand.get("cross_score", 0.0),
                            "rank": pos,
                            "is_correct": 1 if cand_id == correct_id else 0,
                        }
                    )

            except Exception as e:
                print(f"⚠️ Error processing query '{query}': {e}")
                continue

    conn.close()
    print(f"\n✅ SUCCESS: LTR Dataset generated at {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_dataset()
