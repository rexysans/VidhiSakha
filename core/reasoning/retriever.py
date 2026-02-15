import os 
import re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
model = SentenceTransformer("BAAI/bge-m3", device="cpu")

def retrieve_articles(conn, query: str, k=40): # Increased to 40
    q_lower = query.lower()
    curr = conn.cursor()
    
    # 1. DETERMINISTIC BYPASS (Actually fetching the article now)
    match = re.search(r"(?:article|art)\s+(\d+[a-z]?)", q_lower)
    direct_article = None
    if match:
        article_id = match.group(1).upper()
        curr.execute(
            "SELECT article_id, title, full_text, 0.0 as distance FROM articles WHERE article_id = %s",
            (article_id,)
        )
        row = curr.fetchone()
        if row:
            direct_article = {"article-id": row[0], "title": row[1], "full_text": row[2], "distance": row[3]}

    # 2. VECTOR RETRIEVAL
    q_emb = model.encode(query, normalize_embeddings=True).tolist()
    curr.execute(
        "SELECT article_id, title, full_text, embedding <=> %s::vector AS distance FROM articles ORDER BY distance LIMIT %s",
        (q_emb, k),
    )
    rows = curr.fetchall()
    results = [{"article-id": r[0], "title": r[1], "full_text": r[2], "distance": r[3]} for r in rows]

    # 3. STRUCTURAL NUDGE (Part III)
    if any(word in q_lower for word in ["right", "freedom", "liberty", "equality"]):
        for res in results:
            article_num_str = re.sub(r"\D", "", str(res["article-id"]))
            if article_num_str and 12 <= int(article_num_str) <= 35:
                res["distance"] -= 0.1 
        results.sort(key=lambda x: x["distance"])

    # 4. MERGE
    if direct_article:
        results = [r for r in results if r["article-id"] != direct_article["article-id"]]
        results.insert(0, direct_article)

    curr.close()
    return results[:k]