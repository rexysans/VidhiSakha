from sentence_transformers import SentenceTransformer

# MUST match embed_articles.py
model = SentenceTransformer("BAAI/bge-m3")

def retrieve_articles(conn, query: str, k=20): # Increased K to 20 for better Reranker pool
    # Encode with normalization to match the DB storage
    q_emb = model.encode(query, normalize_embeddings=True).tolist()
    curr = conn.cursor()
    
    # Using <=> for Cosine Distance (Elite Standard)
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
    
    # Note: article-id vs article_id consistency check
    return [{"article-id": r[0], "title": r[1], "full_text": r[2], "distance": r[3]} for r in rows]