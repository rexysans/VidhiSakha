import psycopg2
import pandas as pd
import joblib
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder
from core.reasoning.ltr.feature_extractor import VidhiSakhaFeatureExtractor
from core.api.main import get_connection, retrieve_articles

# Load LTR Model
try:
    ltr_model = joblib.load("models/ltr_model.pkl")
    print("Loaded LTR model.")
except Exception as e:
    print(f"Error loading LTR model: {e}")
    exit(1)

extractor = VidhiSakhaFeatureExtractor()

# Load Reranker manually to get scores
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
reranker = CrossEncoder(
    "BAAI/bge-reranker-v2-m3",
    device=device,
    automodel_args={"torch_dtype": torch.float16},
)


def debug_query(query, expected_id):
    print(f"\n{'='*40}\nQuery: {query} (Expected: {expected_id})")
    conn = get_connection()

    # 1. Retrieve
    # Main.py logic calls retrieve_articles which returns list of dicts: {"article-id": ...}
    candidates = retrieve_articles(conn, query)
    print(f"Retrieved {len(candidates)} candidates")

    # Check retrieval
    # Note: retriever.py returns keys with hyphens "article-id"
    found_idx = -1
    for i, c in enumerate(candidates):
        # Handle key difference if any (main.py uses article_id, retriever returns article-id)
        # Checking retrieve_articles implementation in retriever.py: returns "article-id"
        aid = c.get("article-id") or c.get("article_id")
        if str(aid) == str(expected_id):
            found_idx = i
            break

    if found_idx == -1:
        print(f"❌ CRITICAL: Article {expected_id} NOT found in top 100 retrieval!")
        conn.close()
        return
    else:
        print(f"✅ Found in retrieval at rank {found_idx+1}")

    # 2. Rerank
    pairs = [[query, c["full_text"]] for c in candidates]
    scores = reranker.predict(pairs, batch_size=32)

    for i, (c, s) in enumerate(zip(candidates, scores)):
        c["cross_score"] = float(s)
        # Use simple rank integer i+1
        c["initial_rank"] = i + 1

    # 3. LTR Features
    feature_data = []

    for i, c in enumerate(candidates):
        aid = str(c.get("article-id") or c.get("article_id"))
        title = c["title"]
        score = c["cross_score"]
        rank = c["initial_rank"]

        feats = extractor.extract(query, aid, title, score, rank)
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

    # Predict
    ltr_scores = ltr_model.predict(X_df)

    for i, c in enumerate(candidates):
        c["final_score"] = float(ltr_scores[i])

    # Sort
    sorted_cands = sorted(candidates, key=lambda x: x["final_score"], reverse=True)

    print("\n--- Top 3 Predictions ---")
    for i, c in enumerate(sorted_cands[:3]):
        aid = str(c.get("article-id") or c.get("article_id"))
        is_cor = aid == str(expected_id)
        marker = "✅" if is_cor else "  "
        print(
            f"{marker} Rank {i+1}: Art {aid} | Final: {c['final_score']:.2f} | Neural: {c['cross_score']:.2f} | Feats: {c['features']}"
        )

    # Show expected
    if str(
        sorted_cands[0].get("article-id") or sorted_cands[0].get("article_id")
    ) != str(expected_id):
        for i, c in enumerate(sorted_cands):
            aid = str(c.get("article-id") or c.get("article_id"))
            if aid == str(expected_id):
                print(f"\n⚠️ Expected Art {expected_id} is at Rank {i+1}")
                print(
                    f"   Final: {c['final_score']:.2f} | Neural: {c['cross_score']:.2f} | Feats: {c['features']}"
                )
                break

    conn.close()


if __name__ == "__main__":
    debug_query("right to life", "21")
    debug_query("protection against double jeopardy", "20")
    debug_query("freedom to form associations", "19")
