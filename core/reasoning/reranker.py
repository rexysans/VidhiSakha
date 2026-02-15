import re
from sentence_transformers import CrossEncoder

class ScalableLegalReranker:
    def __init__(self):
        # Load the 'Logic Brain'
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cpu")
        
        # 1. Structural Patterns (Scalable: Works for any law, not just these IDs)
        self.PROCEDURAL_PATTERNS = ["power", "exercise", "procedure", "provisions", "conferment", "transitional"]
        
        # 2. Domain Anchors (The core pillars of the Constitution)
        self.PRIMARY_ANCHORS = {"14", "16", "17", "19", "20", "21", "22", "32", "352", "356"}

    def classify_query(self, query: str):
        q = query.lower()
        if re.search(r"(?:article|art)\s+\d+", q): return "ID_LOOKUP"
        if len(q.split()) <= 2: return "VAGUE"
        return "SEMANTIC"

    def rerank(self, query: str, candidates: list):
        if not candidates: return []
        q_low = query.lower()
        q_type = self.classify_query(query)
        
        # Extract ID if present in query (e.g., "Article 21" -> "21")
        id_match = re.search(r"(\d+)", q_low)
        query_id = id_match.group(1) if id_match else None

        # --- PHASE 1: NEURAL ENCODING ---
        pairs = []
        for c in candidates:
            # Determine hierarchy role based on patterns
            is_proc = any(kw in c["title"].lower() for kw in self.PROCEDURAL_PATTERNS)
            role = "REFERENCE/PROCEDURE" if is_proc else "SUBSTANTIVE LAW"
            
            # Injecting Role and ID into the model's 'view'
            doc_text = f"ROLE: {role} | ARTICLE: {c['article-id']} | TITLE: {c['title']} | CONTENT: {c['full_text']}"
            pairs.append([query, doc_text])

        raw_scores = self.model.predict(pairs)

        # --- PHASE 2: STRUCTURAL SCORING (The Scalable Part) ---
        for i, cand in enumerate(candidates):
            score = float(raw_scores[i])
            c_id = str(cand["article-id"])
            c_text = cand["full_text"].lower()

            # RULE 1: Length Normalization (The 'Anti-Bully' Rule)
            # Prevents 500-word articles from beating precise 20-word articles.
            score -= (len(c_text) * 0.0004)

            # RULE 2: Reference Density (The 'Anti-Shadow' Rule)
            # If search is for Art 356, and this is Art 357 mentioning 356, penalize it.
            if query_id and c_id != query_id:
                if f"article {query_id}" in c_text:
                    # Penalize more if it mentions the target article multiple times
                    mentions = c_text.count(f"article {query_id}")
                    score -= (mentions * 1.2)

            # RULE 3: Primary Anchor Boost
            # Substantive rights (14, 21, etc.) get a tie-breaker advantage.
            if c_id in self.PRIMARY_ANCHORS:
                score += 1.0

            # RULE 4: Range-Based Hierarchy (Part III Nudge)
            # If the query is vague/semantic, prefer Fundamental Rights (12-35)
            if q_type != "ID_LOOKUP":
                try:
                    art_num = int(re.sub(r"\D", "", c_id))
                    if 12 <= art_num <= 35: score += 0.5
                except: pass

            cand["rerank_score"] = score

        # 4. FINAL SORT
        return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

legal_reranker = ScalableLegalReranker()