"""
Central embedding module for VidhiSakhā

This guarantees SAME embedding logic for:

• article embedding
• query embedding
• retrieval
• evaluation
"""

from sentence_transformers import SentenceTransformer

print("🚀 Loading BGE-M3 embedding model...")

model = SentenceTransformer(
    "BAAI/bge-m3",
    device="cpu"   # change to cuda if GPU available
)

print("✅ BGE-M3 ready")


# Query embedding
def embed_query(query: str):

    return model.encode(
        query,
        normalize_embeddings=True
    ).tolist()


# Article embedding
def embed_document(article_id, title, text):

    combined = f"""
    Article {article_id}
    Title: {title}
    Content: {text}
    """

    return model.encode(
        combined,
        normalize_embeddings=True
    ).tolist()


# Batch article embedding (FAST)
def embed_documents_batch(rows):

    texts = [

        f"""
        Article {article_id}
        Title: {title}
        Content: {text}
        """

        for uid, article_id, title, text in rows
    ]

    embeddings = model.encode(

        texts,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=True

    )

    return embeddings.tolist()
