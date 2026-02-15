from sentence_transformers import CrossEncoder

class LegalReranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        # Load the model once during initialization to save CPU/GPU cycles
        self.model = CrossEncoder(model_name,device="cpu")

    def rerank(self, query: str, candidates: list):
        """
        Takes a query and a list of candidates from the retriever.
        Returns the candidates sorted by logical relevance score.
        """
        if not candidates:
            return []

        # [ELITE TWEAK]: Using [SEP] or clear labeling helps Cross-Encoders 
        # understand that 'Title' is metadata and 'Full Text' is the content.
        # pairs = [[query, f"ARTICLE TITLE: {c['title']} | CONTENT: {c['full_text']}"] for c in candidates]
        # [ELITE TWEAK]
        pairs = [[query, f"LAW: Article {c['article-id']} - {c['title']} | CONTENT: {c['full_text']}"] for c in candidates]
        # Predict relevance scores (High score = high relevance)
        scores = self.model.predict(pairs)

        # Attach scores to the candidate objects
        for i, candidate in enumerate(candidates):
            candidate["rerank_score"] = float(scores[i])

        # Sort candidates: highest score first
        return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

# Export this instance to be used across main.py or other modules
legal_reranker = LegalReranker()