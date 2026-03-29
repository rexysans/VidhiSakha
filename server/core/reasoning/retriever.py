# core/reasoning/retriever.py
"""
v2 Hybrid Retriever — Dense (BGE-M3) + Sparse (PostgreSQL BM25)
Fused via Reciprocal Rank Fusion (RRF).
"""

import os
import re
from sentence_transformers import SentenceTransformer
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Retriever running on: {device}")

model = SentenceTransformer("BAAI/bge-m3", device=device)

if device == "cuda":
    model.half()

model.eval()


# ---------------------------------------------------------------------------
# Dense retrieval (vector search)
# ---------------------------------------------------------------------------
def _retrieve_dense(conn, query: str, k: int):
    """Return top-k by cosine distance using pgvector."""
    cur = conn.cursor()
    q_emb = model.encode(query, normalize_embeddings=True,
                         show_progress_bar=False).tolist()
    cur.execute(
        """
        SELECT article_id, title, full_text,
               embedding <=> %s::vector AS distance
        FROM articles
        ORDER BY distance
        LIMIT %s
        """,
        (q_emb, k),
    )
    rows = cur.fetchall()
    return [
        {"article-id": r[0], "title": r[1], "full_text": r[2], "distance": r[3]}
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Sparse retrieval (PostgreSQL full-text search / BM25-style)
# ---------------------------------------------------------------------------
def _retrieve_sparse(conn, query: str, k: int):
    """Return top-k by ts_rank using GIN-indexed tsvector column.
    Uses OR semantics for better recall (AND is too strict for short queries)."""
    cur = conn.cursor()

    # Build OR-based tsquery from individual words
    # plainto_tsquery uses AND which misses docs with only some terms
    import re as _re
    # Strip everything except alphanumeric and spaces to prevent tsquery syntax errors
    sanitized = _re.sub(r"[^a-zA-Z0-9\s]", "", query)
    words = [w.strip() for w in sanitized.split() if len(w.strip()) > 2]
    if not words:
        return []

    # Create OR query: 'word1' | 'word2' | 'word3'
    or_query = " | ".join(f"'{w}'" for w in words)

    cur.execute(
        """
        SELECT article_id, title, full_text,
               ts_rank_cd(tsv, to_tsquery('english', %s)) AS bm25_score
        FROM articles
        WHERE tsv @@ to_tsquery('english', %s)
        ORDER BY bm25_score DESC
        LIMIT %s
        """,
        (or_query, or_query, k),
    )
    rows = cur.fetchall()
    return [
        {"article-id": r[0], "title": r[1], "full_text": r[2], "bm25_score": r[3]}
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion (RRF)
# ---------------------------------------------------------------------------
def _rrf_fuse(dense_results, sparse_results, k_constant=60):
    """
    Merge two ranked lists using RRF.
    score(doc) = sum_over_lists( 1 / (k + rank_in_list) )
    """
    scores = {}   # article_id -> cumulative RRF score
    docs = {}     # article_id -> doc dict

    for rank, doc in enumerate(dense_results, start=1):
        aid = doc["article-id"]
        scores[aid] = scores.get(aid, 0.0) + 1.0 / (k_constant + rank)
        docs[aid] = doc

    for rank, doc in enumerate(sparse_results, start=1):
        aid = doc["article-id"]
        scores[aid] = scores.get(aid, 0.0) + 1.0 / (k_constant + rank)
        if aid not in docs:
            docs[aid] = doc
            docs[aid]["distance"] = 1.0  # no vector distance available
        # Attach bm25_score to the doc for feature extraction
        docs[aid]["bm25_score"] = doc.get("bm25_score", 0.0)

    # Sort by fused score descending
    ranked_ids = sorted(scores, key=scores.get, reverse=True)
    fused = []
    for aid in ranked_ids:
        d = docs[aid]
        d["rrf_score"] = scores[aid]
        fused.append(d)
    return fused


# ---------------------------------------------------------------------------
# Public API — drop-in replacement
# ---------------------------------------------------------------------------
def retrieve_articles(conn, query: str, k=100):
    """
    Hybrid retrieval: dense + sparse, fused with RRF.
    Returns up to ~k unique candidates (may be slightly more due to union).
    """
    q_lower = query.lower().strip()
    dense_k = 40 if " " in q_lower else 80
    sparse_k = 40   # BM25 arm always fetches 40

    dense = _retrieve_dense(conn, query, dense_k)
    sparse = _retrieve_sparse(conn, query, sparse_k)

    fused = _rrf_fuse(dense, sparse)

    # Cap to k candidates for downstream stages
    return fused[:k]
