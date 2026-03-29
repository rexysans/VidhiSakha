# core/reasoning/ltr/inference.py
import joblib
import numpy as np
import pandas as pd
import os
import re
import math

from core.reasoning.ltr.feature_extractor import FEATURE_NAMES


class VidhiSakhaLTRInference:
    def __init__(self, model_path="models/ltr_model_v2.pkl"):
        self.model = None
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f"LTR model loaded: {model_path}")
        else:
            print(f"LTR model not found at {model_path} - will sort by cross_score only")

    def rank(self, query, candidates):
        if not candidates:
            return []

        # If no model loaded, fall back to cross-encoder sorting
        if self.model is None:
            for c in candidates:
                c["final_score"] = float(c.get("cross_score", 0.0))
            return sorted(candidates, key=lambda x: x["final_score"], reverse=True)

        q_low = query.lower()
        q_tokens = set(re.findall(r'\w+', q_low))
        q_len = len(q_tokens)
        q_clean = re.sub(r'[^a-z0-9\s]', '', q_low)

        # Group-level neural score stats for normalization
        neurals = np.array([float(c.get("cross_score", 0.0)) for c in candidates])
        mean_n = neurals.mean()
        min_n = neurals.min()
        max_n = neurals.max()
        range_n = max_n - min_n if max_n != min_n else 1.0

        feature_matrix = []
        for c in candidates:
            neural = float(c.get("cross_score", 0.0))
            art_id = str(c.get("article-id", "")).lower()
            title = str(c.get("title", "")).lower()
            vdist = float(c.get("distance", 0.0))
            text_len = len(c.get("full_text", ""))

            feats = []

            # f0: neural_score
            feats.append(neural)

            # f1: neural_score_norm
            feats.append((neural - min_n) / range_n if range_n > 0 else 0.0)

            # f2: vector_distance
            feats.append(vdist)

            # f3: id_match_exact
            id_clean = re.sub(r'[^a-z0-9]', '', art_id)
            if id_clean:
                pattern = r'\b' + re.escape(id_clean) + r'\b'
                feats.append(1.0 if re.search(pattern, q_clean) else 0.0)
            else:
                feats.append(0.0)

            # f4: title_bm25
            t_tokens = set(re.findall(r'\w+', title))
            if q_tokens and t_tokens:
                overlap = q_tokens & t_tokens
                idf_sum = sum(1.0 / math.log2(2 + len(t_tokens)) for _ in overlap)
                bm25 = idf_sum / (len(q_tokens) + 0.5)
            else:
                bm25 = 0.0
            feats.append(bm25)

            # f5: query_length
            feats.append(math.log2(1 + q_len))

            # f6: score_gap
            feats.append(neural - mean_n)

            # f7: text_length_ratio
            feats.append(min(len(q_low) / max(text_len, 1), 1.0))

            feature_matrix.append(feats)

        X_df = pd.DataFrame(feature_matrix, columns=FEATURE_NAMES)
        raw_scores = self.model.predict(X_df)

        for i, cand in enumerate(candidates):
            cand["final_score"] = float(raw_scores[i])

        return sorted(candidates, key=lambda x: x["final_score"], reverse=True)
