# core/reasoning/reranker.py
import re
from sentence_transformers import CrossEncoder
import torch


class ScalableLegalReranker:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Reranker running on: {device}")
        self.model = CrossEncoder(
            "BAAI/bge-reranker-v2-m3",
            device=device,
            automodel_args={"torch_dtype": torch.float16},
        )

    def rerank(self, query: str, candidates: list):
        if not candidates:
            return []

        # Free cached GPU memory before inference
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Pure Neural Scoring
        pairs = [[query, cand["full_text"]] for cand in candidates]
        scores = self.model.predict(pairs, batch_size=4, show_progress_bar=False)

        for cand, score in zip(candidates, scores):
            # Pass the raw cross-encoder score to the LTR
            cand["cross_score"] = float(score)

        return candidates


legal_reranker = ScalableLegalReranker()
