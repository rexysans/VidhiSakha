import joblib
import numpy as np
import os
from core.reasoning.ltr.feature_extractor import VidhiSakhaFeatureExtractor


class VidhiSakhaLTRInference:

    def __init__(self, model_path="models/ltr_model.pkl"):

        if not os.path.exists(model_path):
            raise FileNotFoundError("LTR Model not found. Train first.")

        self.model = joblib.load(model_path)

        self.extractor = VidhiSakhaFeatureExtractor()

    def rank(self, query, candidates):

        if not candidates:
            return []

        feature_matrix = []

        for pos, cand in enumerate(candidates, start=1):

            features = self.extractor.extract(
                query=query,
                article_id=cand.get("article-id") or cand.get("article_id"),
                title=cand.get("title", ""),
                neural_score=cand.get("rerank_score") or cand.get("score", 0.0),
                rank=pos,
            )

            feature_matrix.append(features)

        X = np.array(feature_matrix)

        # IMPORTANT: LambdaMART uses predict(), NOT predict_proba
        scores = self.model.predict(X)

        for i, cand in enumerate(candidates):

            cand["ltr_score"] = float(scores[i])

        return sorted(candidates, key=lambda x: x["ltr_score"], reverse=True)
