# 📘 VidhiSakhā – Architecture v1.2

## 1. System Overview

VidhiSakhā is a legal retrieval system for the Constitution of India.

### Goals

- Retrieve the correct constitutional article
- Rank it correctly among semantically similar provisions
- Reject non-legal queries safely
- Maintain high recall while improving precision

The system evolved from a single-stage semantic retrieval model to a **two-stage hybrid retrieval architecture** with calibrated rejection.

---

## 2. Motivation for Architectural Shift

### 2.1 Limitations of v1 (Single-Stage Semantic Retrieval)

Architecture v1 used:

- Dense embedding retrieval (BGE-M3)
- Hard rejection threshold
- No reranking layer

#### Observed Issues

**1. Sibling Article Confusion**

- Article 6 vs 7
- Article 356 vs 357
- Article 21 vs 373

**2. Semantic Overlap Problem**

Many constitutional articles share vocabulary:

- "Emergency"
- "Citizenship"
- "Restriction"
- "Reservation"

Dense vector similarity could retrieve relevant articles but failed to reliably rank the correct one at position 1.

**3. Hard Gate Recall Collapse**

- Static thresholds (e.g., -0.2) rejected valid legal matches
- This reduced recall artificially

---

## 3. Architecture v2 (Hybrid Retrieval + Reranking)

### Pipeline

```
User Query
   ↓
Query Parser
   ↓
Stage 1: Vector Retrieval (BGE-M3, K=40)
   ↓
Deterministic Article-ID Bypass
   ↓
Metadata Boosting (Part-aware)
   ↓
Stage 2: Cross-Encoder Reranker
   ↓
Score Calibration Layer
   ↓
Final Answer or Rejection
```

---

## 4. Stage 1 – High Recall Retrieval

### 4.1 Vector Retrieval

| Parameter | Value |
|-----------|-------|
| Model | BAAI/bge-m3 |
| Top-K | 20 |
| Goal | Maximize recall |
| Current Recall@20 | 95.56% |

**Conclusion:** Stage 1 reliably retrieves the correct article in most cases.

### 4.2 Deterministic Article ID Bypass

**Regex-based detection:**

```regex
(?:article|art)\s+(\d+[a-z]?)
```

**Behavior:**

If the user explicitly asks for "Article 21":

1. Perform direct SQL lookup
2. Place article at top of candidate list
3. Skip semantic ambiguity

**Result:** This guarantees precision for explicit ID queries.

### 4.3 Metadata Boosting (Soft)

**Part-aware boosting:**

- Example: If query relates to Fundamental Rights, slightly boost Articles 12–35
- Boost is minimal (e.g., -0.15 distance adjustment)

**Purpose:** Provide contextual prior without distorting ranking.

---

## 5. Stage 2 – Cross-Encoder Reranker

### Model

`cross-encoder/ms-marco-MiniLM-L-6-v2`

### Function

- Evaluate query + article pair jointly
- Produce relevance score

### Why Needed

| Approach | Capability |
|----------|------------|
| Dense embeddings | Measure similarity |
| Cross-encoders | Measure actual relevance |

This resolves:

- Article 6 vs 7
- Article 356 vs 357
- Article 21 vs 373

---

## 6. Score Calibration Layer

Instead of hard rejection:

- Use calibrated `JUNK_THRESHOLD`
- Current value: `-1.0` (experimenting)

### Observation

- Valid legal answers may score negative
- Junk queries typically score < -8

### Goal

Maximize separation between:

- Valid legal nuance
- True junk queries

---

## 7. Data Hygiene Improvements

### Identified Issues

- Article 39A formatting inconsistency ("39. A")
- 31C text bleed into Article 32

### Actions

1. Scrub database
2. Re-embed corpus
3. Maintain clean tokenization

### Reason

Rerankers are highly sensitive to formatting and textual corruption.

---

## 8. Current Performance

| Metric | Value |
|--------|-------|
| Recall@20 | 95.56% |
| Top-1 Accuracy | 71.15% |
| Junk Detection Accuracy | High |

### Interpretation

The bottleneck is **ranking precision**, not retrieval recall.

---

## 9. Next Optimization Plan

1. Scrub DB (39A + 31C)
2. Re-embed corpus
3. Keep K=40
4. Calibrate threshold using score distribution
5. Add minimal part-based boost if needed

### Target

**80%+ accuracy** without changing models