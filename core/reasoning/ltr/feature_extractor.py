import re

class VidhiSakhaFeatureExtractor:

    def extract(self, query, article_id, title, neural_score, rank):

        q_low = query.lower()
        t_low = title.lower()
        art_id = str(article_id)

        features = []

        id_clean = re.sub(r'\D', '', art_id)

        q_tokens = set(re.findall(r'\w+', q_low))
        t_tokens = set(re.findall(r'\w+', t_low))

        overlap = len(q_tokens & t_tokens) / (len(q_tokens | t_tokens) + 1e-6)

        # core features
        features.append(float(neural_score))

        features.append(neural_score ** 2)

        features.append(1.0 / rank)

        features.append(
            1.0 if re.search(rf"\b{id_clean}\b", q_low) else 0.0
        )

        features.append(
            1.0 if f"article {id_clean}" in q_low else 0.0
        )

        features.append(overlap)

        # part III
        try:
            art_num = int(id_clean)
            features.append(1.0 if 12 <= art_num <= 35 else 0.0)
        except:
            features.append(0.0)

        # directional
        features.append(
            1.0 if ("from" in q_low and "from" in t_low)
            or ("to" in q_low and "to" in t_low)
            else 0.0
        )

        # length features
        features.append(len(q_tokens))
        features.append(len(t_tokens))

        # rank bucket
        features.append(1.0 if rank <= 3 else 0.0)

        return features
