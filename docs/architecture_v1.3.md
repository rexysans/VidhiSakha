# 📘 VidhiSakhā – Architecture v1.3

## 1. System Pipeline

```mermaid
graph TD
    Q[User Query] --> VR[Vector Retrieval (BGE-M3, k=40)]
    VR --> CR[CrossEncoder Reranking (ms-marco-MiniLM)]
    CR --> HS[Heuristic Structural Adjustments]
    HS --> TP[Top-1 Prediction]
```

---

## 2. Retrieval Layer

| Parameter | Value |
|-----------|-------|
| **Model** | BGE-M3 (1024-dim) |
| **k** | 40 |
| **Recall@40** | 97.78% |
| **Vector DB** | Postgres + pgvector |
| **Status** | Embeddings frozen |

---

## 3. Reranker Layer

| Parameter | Value |
|-----------|-------|
| **Model** | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| **Device** | CPU |
| **Score Baseline** | Neural similarity |
| **Junk Threshold** | -0.5 (tuned) |

### Additional Adjustments

- **Reference penalty**: Penalizes "shadow articles" that merely reference others.
- **Directional logic**: Handles migration-related queries.
- **Structural role tagging**: Identifies article roles.
- **Part III hierarchy bias**: Prioritizes Fundamental Rights.

---

## 4. Evaluation

| Metric | Value |
|--------|-------|
| **Core Accuracy** | ~76–78% |
| **Junk Accuracy** | 100% |
| **Recall@40** | 97.78% |
| **Total Queries** | 52 |

---

## 5. Known Failure Classes

- **Sibling Articles**: Confusion between Article 356 vs 357.
- **Directional Citizenship**: Confusion between Article 6 vs 7.
- **Reservation Ambiguity**: Confusion between Article 16 vs 243T.
- **Procedural Overshadowing**: Confusion between Article 19 vs 358.

---

## 6. Architectural Limitation

**Current Issue:** Reranking relies on manually tuned heuristic boosts/penalties.

**Consequences:**
- Tuning instability
- Overfitting risk
- Non-generalizable rules

---

## 7. Next Phase: Learning-to-Rank (LTR)

**Goal:** Replace manual scoring adjustments with a feature-based logistic reranker.

**Objective:** Stabilize ranking precision without hardcoded biases.

### Planned Features

1. **Neural score**
2. **Exact ID match**
3. **Title token overlap**
4. **Reference density**
5. **Length normalization**
6. **Structural location** (Part III flag)