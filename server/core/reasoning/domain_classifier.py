from sentence_transformers import util
import torch
import re

class DomainClassifier:
    def __init__(self, shared_model):
        self.model = shared_model
        # Positive anchors — what constitutional queries look like
        anchors = [
            "Indian Constitution Articles and legal provisions",
            "Fundamental Rights, State Policy, and legal powers",
            "Constitutional law, amendments, and legislative procedures",
            "Citizenship, elections, and governance under the Constitution of India",
            "Parliament, judiciary, and executive powers under Indian law",
            "Religious freedom, minority rights, and social justice in India",
        ]
        self.anchor_embeddings = self.model.encode(
            anchors, normalize_embeddings=True, convert_to_tensor=True
        )
        self.THRESHOLD = 0.45

        # Explicit article reference pattern — always legal
        self._article_re = re.compile(r'\barticle\s+\d+[a-z]?\b', re.IGNORECASE)

        # Strong constitutional cues — fast-track as legal
        self._legal_cue_re = re.compile(
            r"\b("
            r"constitution|constitutional|fundamental rights?|directive principles?|"
            r"citizenship|parliament|supreme court|high court|writs?|"
            r"president'?s? rule|emergency|article\s*\d+[a-z]?|"
            r"detention|self-incrimination|double jeopardy|"
            r"minority rights?|religious freedom|reservation|"
            r"untouchability|labou?r|forced labour|child labour|"
            r"public employment|equal pay|legal aid|environment|"
            r"living wage|public health|cow slaughter|taj mahal|monuments|"
            r"freedom of speech|associations?|union|discrimination"
            r")\b",
            re.IGNORECASE,
        )

        # Hard non-constitutional cues (reject early)
        self._hard_non_constitutional_re = re.compile(
            r"\b("
            r"ipc|crpc|cpc|evidence act|cheque bounce|divorce|"
            r"software engineer|salary|startup|football|weather|"
            r"prime minister of japan|chief justice of the us|"
            r"unreasonable searches|right to bear arms"
            r")\b",
            re.IGNORECASE,
        )

        # Section references are usually statutory (non-Constitution) in this product
        self._section_ref_re = re.compile(r"\bsection\s+\d+[a-z]?\b", re.IGNORECASE)

    def is_legal(self, query: str):
        if self._hard_non_constitutional_re.search(query):
            return False, 0.0

        if self._section_ref_re.search(query):
            return False, 0.0

        # Fast-track: if the query mentions "Article <N>", it's legal
        if self._article_re.search(query):
            return True, 1.0

        # Fast-track: constitutional cue words
        if self._legal_cue_re.search(query):
            return True, 0.95

        q_emb = self.model.encode(
            query, normalize_embeddings=True, convert_to_tensor=True
        )
        cos_scores = util.cos_sim(q_emb, self.anchor_embeddings)[0]
        max_score = torch.max(cos_scores).item()
        return max_score >= self.THRESHOLD, max_score