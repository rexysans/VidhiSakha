# VidhiSakhā — Technical Architecture v1

## 1. System Overview

VidhiSakhā is a semantic retrieval system for the Indian Constitution. It uses vector embeddings and pgvector to enable natural language queries against constitutional articles.

**Core Stack:**
- **Backend**: FastAPI
- **Database**: PostgreSQL + pgvector
- **Embeddings**: Sentence Transformers (BGE-M3)
- **Search**: Cosine similarity on normalized embeddings

---

## 2. API Layer

The FastAPI backend exposes 6 REST endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/health` | GET | Health check |
| `/v1/articles/{article_id}` | GET | Retrieve specific article by ID |
| `/v1/parts/{part_uid}` | GET | Retrieve specific part of the constitution |
| `/v1/parts/{part_uid}/articles` | GET | List all articles under a part |
| `/v1/search` | POST | Semantic search returning article IDs and titles |
| `/v1/ask` | POST | Question answering (not fully implemented) |

**Search Flow:**
1. User submits natural language query
2. Query is embedded using the same model as articles
3. Top-K retrieval via cosine distance
4. Results filtered through sanity checks (hard gates)
5. Articles returned ranked by distance

---

## 3. Database Layer

**Schema:**

Two primary tables:

### `parts`
Stores structural metadata about constitutional parts.

### `articles`
Stores individual articles with full text and embeddings.

**Key Column:**
- `embedding` (vector): High-dimensional embedding stored using pgvector

**Vector Operations:**
- Distance metric: Cosine distance (`<=>`)
- Index: pgvector index for fast nearest neighbor search

---

## 4. Embedding Evolution

### Initial Model: `all-MiniLM-L6-v2`

**Performance:**
- Fast and lightweight
- Dimensionality: 384

**Issue:**
Limited semantic discrimination in legally adjacent articles.

### Current Model: `BAAI/bge-m3`

**Rationale:**
- Higher-resolution embeddings (1024-dim)
- Better handling of domain-specific legal terminology
- Improved recall for edge cases

**Implementation Details:**
- Embeddings are normalized (`normalize_embeddings=True`)
- Both indexing (`core/reasoning/embed_articles.py`) and retrieval (`core/reasoning/retriever.py`) use the same model
- Retrieval K increased to 20 to support future reranking

---

## 5. Benchmark Results

Test diagnostics are stored in `/tests`:
- `all-MiniLM-L6-v2-diagonistic.md`
- `BAAI/bge-large-en-v1.5-diagonistic.md`

**Measured Metrics:**

| Metric | MiniLM-L6-v2 | BGE-M3 |
|--------|--------------|--------|
| Recall@20 | 86.67% | 93.33% |
| Top-1 Accuracy | ~59% | ~53% |

**Analysis:**
- BGE-M3 significantly improved recall (+6.66%)
- Top-1 accuracy regression indicates ranking logic needs improvement
- Better embeddings alone do not solve precision issues

---

## 6. Current Limitations

### Ranking Logic
- Uses **hard gates** (e.g., keyword-based sanity checks)
- Gates are brittle and not well-calibrated
- No learned reranking stage

### Top-1 Accuracy
- Currently ~53% with BGE-M3
- Regression from MiniLM despite better recall
- Indicates that semantic embeddings alone are insufficient for final ranking

### Query Understanding
- No preprocessing or query expansion
- No hybrid search (semantic + keyword)

---

## 7. Next Planned Upgrade

### Phase 1: Two-Stage Retrieval

**Objective:**
Improve Top-1 accuracy while preserving high recall.

**Approach:**
1. **Retrieve**: Use BGE-M3 to fetch top-20 candidates (recall-focused)
2. **Rerank**: Apply cross-encoder to reorder candidates (precision-focused)

**Candidate Reranker:**
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (initial)
- Upgrade if necessary

**Target:**
- Maintain Recall@20 ≥ 93%
- Improve Top-1 Accuracy to ≥ 85%

### Phase 2: Score Calibration

Replace hard gates with learned thresholds:
- Log reranker scores
- Build histogram of correct/incorrect/junk scores
- Set rejection threshold scientifically

---

## References

- Embedding script: `core/reasoning/embed_articles.py`
- Retrieval logic: `core/reasoning/retriever.py`
- Benchmarking: `tests/measure_recall.py`
- API: `core/api/main.py`


### Current Phase

VidhiSakhā is currently in Phase 1 (Signal Stabilization).

- Recall has improved significantly.
- Precision is the active bottleneck.
- System remains single-stage retrieval with heuristic ranking.
- Two-stage reranking is the next structural upgrade.

The architecture is intentionally kept minimal to avoid premature complexity.
