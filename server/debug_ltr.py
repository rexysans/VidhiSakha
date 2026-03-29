import psycopg2
import pandas as pd
import joblib
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder
from core.reasoning.ltr.feature_extractor import VidhiSakhaFeatureExtractor
from core.api.main import get_connection, retrieve_articles

# Load models manually for debugging
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")

# 1. Retriever
retriever = SentenceTransformer("BAAI/bge-m3", device=device)
if device == "cuda":
    retriever.half()

# 2. Reranker
reranker = CrossEncoder(
    "BAAI/bge-reranker-v2-m3",
    device=device,
    automodel_args={"torch_dtype": torch.float16},
)

# 3. LTR Model
ltr_model = joblib.load("models/ltr_model.pkl")
extractor = VidhiSakhaFeatureExtractor()


def debug_query(query, expected_id):
    print(f"\n{'='*40}\nQuery: {query} (Expected: {expected_id})")
    conn = get_connection()

    # 1. Retrieve
    # Copy logic from retriever.py manually since we can't easily import the instance with the connection
    # Actually main.py has retrieve_articles, let's use that but we need to patch the global model in retriever.py if we import it...
    # Easier to just rely on the main.py imports if they work, or just replicate the SQL

    candidates = retrieve_articles(conn, query)
    print(f"Retrieved {len(candidates)} candidates")

    # Check if expected is in candidates
    found = False
    for c in candidates:
        if str(c["article_id"]) == str(expected_id):
            found = True
            break
    if not found:
        print(
            f"❌ CRITICAL failure: Expected article {expected_id} NOT in retrieval top 100!"
        )
        conn.close()
        return

    # 2. Rerank
    pairs = [[query, c["full_text"]] for c in candidates]
    scores = reranker.predict(pairs, batch_size=32)
    for c, s in zip(candidates, scores):
        c["cross_score"] = float(s)

    # 3. Feature Extraction & LTR
    feature_data = []
    for i, c in enumerate(candidates):
        feats = extractor.extract(
            query, c["article_id"], c["title"], c["cross_score"], i + 1
        )
        c["features"] = feats
        feature_data.append(feats)

    feature_names = [
        "neural_score",
        "reciprocal_rank",
        "id_match",
        "title_overlap",
        "is_part_iii",
        "directional_boost",
    ]
    X_df = pd.DataFrame(feature_data, columns=feature_names)

    ltr_scores = ltr_model.predict(X_df)

    for i, c in enumerate(candidates):
        c["final_score"] = float(ltr_scores[i])

    # Sort
    sorted_cands = sorted(candidates, key=lambda x: x["final_score"], reverse=True)

    print("\n--- Top 5 Predictions ---")
    for i, c in enumerate(sorted_cands[:5]):
        is_correct = str(c["article_id"]) == str(expected_id)
        marker = "✅" if is_correct else "  "
        print(
            f"{marker} Rank {i+1}: Article {c['article_id']} | Final: {c['final_score']:.4f} | Neural: {c['cross_score']:.4f} | Features: {c['features']}"
        )

    # Find expected if not in top 5
    if str(sorted_cands[0]["article_id"]) != str(expected_id):
        for i, c in enumerate(sorted_cands):
            if str(c["article_id"]) == str(expected_id):
                print(f"\n⚠️ Expected Article {expected_id} is at Rank {i+1}")
                print(
                    f"   Final: {c['final_score']:.4f} | Neural: {c['cross_score']:.4f} | Features: {c['features']}"
                )
                break

    conn.close()


# Inspect queries
debug_query("right to life", "21")
debug_query("protection against double jeopardy", "20")
