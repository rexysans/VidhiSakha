import re
import math


FEATURE_NAMES = [
    "neural_score",
    "neural_score_norm",
    "vector_distance",
    "id_match_exact",
    "title_bm25",
    "query_length",
    "score_gap",
    "text_length_ratio",
]


class VidhiSakhaFeatureExtractor:
    """
    v2 Feature Extractor - 8 features.

    Design principle: each feature provides orthogonal signal to neural_score.

    Removed (shortcut features that caused overfitting):
      - reciprocal_rank (1/position): encoded "trust vector search order"
      - is_part_iii (articles 12-35 flag): too coarse
      - directional_boost (articles 6/7): too narrow
    """

    def extract(self, query, article_id, title, cross_score, rank,
                vector_distance=0.0, full_text="", group_stats=None):
        """
        Single-candidate feature extraction.

        group_stats: dict with 'mean_neural', 'min_neural', 'range_neural'
                     (pre-computed across all candidates for this query)
        """
        q_low = query.lower()
        q_tokens = set(re.findall(r'\w+', q_low))
        q_len = len(q_tokens)
        t_low = str(title).lower()
        art_id = str(article_id).lower()

        neural = float(cross_score)
        mean_neural = group_stats.get("mean_neural", 0.0) if group_stats else 0.0
        min_neural = group_stats.get("min_neural", 0.0) if group_stats else 0.0
        range_neural = group_stats.get("range_neural", 1.0) if group_stats else 1.0

        features = []

        # f0: neural_score (raw cross-encoder logit - primary signal)
        features.append(neural)

        # f1: neural_score_norm (min-max normalized within query group)
        features.append((neural - min_neural) / range_neural if range_neural > 0 else 0.0)

        # f2: vector_distance (raw cosine distance from retriever)
        features.append(float(vector_distance))

        # f3: id_match_exact (word-boundary article number match)
        id_clean = re.sub(r'[^a-z0-9]', '', art_id)
        q_clean = re.sub(r'[^a-z0-9\s]', '', q_low)
        if id_clean:
            pattern = r'\b' + re.escape(id_clean) + r'\b'
            features.append(1.0 if re.search(pattern, q_clean) else 0.0)
        else:
            features.append(0.0)

        # f4: title_bm25 (BM25-inspired title relevance)
        t_tokens = set(re.findall(r'\w+', t_low))
        if q_tokens and t_tokens:
            overlap = q_tokens & t_tokens
            idf_sum = sum(1.0 / math.log2(2 + len(t_tokens)) for _ in overlap)
            bm25 = idf_sum / (len(q_tokens) + 0.5)
        else:
            bm25 = 0.0
        features.append(bm25)

        # f5: query_length (log-scaled token count)
        features.append(math.log2(1 + q_len))

        # f6: score_gap (this candidate's neural_score - group mean)
        features.append(neural - mean_neural)

        # f7: text_length_ratio (query length / article text length)
        text_len = len(full_text) if full_text else 500
        features.append(min(len(q_low) / max(text_len, 1), 1.0))

        return features  # Returns exactly 8 items
