import os 
import re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# MUST match embed_articles.py
model = SentenceTransformer("BAAI/bge-m3", device="cpu")

def retrieve_articles(conn, query: str, k=20):
    curr = conn.cursor()
    
    # 1. DETERMINISTIC BYPASS (The 100% Fix)
    # Checks if user mentioned a specific article (e.g., "Article 21" or "Art 21")
    match = re.search(r"(?:article|art)\s+(\d+[a-z]?)", query.lower())
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

    # 2. PROBABILISTIC RETRIEVAL (The Semantic Phase)
    q_emb = model.encode(query, normalize_embeddings=True).tolist()
    
    curr.execute(
        """
        SELECT article_id, title, full_text, embedding <=> %s::vector AS distance
        FROM articles
        ORDER BY distance
        LIMIT %s
        """,
        (q_emb, k),
    )
    rows = curr.fetchall()
    curr.close()
    
    results = [{"article-id": r[0], "title": r[1], "full_text": r[2], "distance": r[3]} for r in rows]

    # 3. MERGE (Ensure direct match is at index 0)
    if direct_article:
        # Filter out the duplicate if the vector search also found it
        results = [r for r in results if r["article-id"] != direct_article["article-id"]]
        results.insert(0, direct_article)

    return results