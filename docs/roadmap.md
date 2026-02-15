# 🏛 VidhiSakhā Roadmap

## Overview

This roadmap outlines the systematic improvement of the VidhiSakhā retrieval system, focusing on precision and recall optimization through measured, incremental changes.

---

## 🔵 Phase 1 — Signal Foundation

**Status:** ✅ **COMPLETE**

**Objective:** Improve recall performance

### Completed Tasks

- ✅ Switched to BGE-M3 embedding model
- ✅ Normalized embeddings
- ✅ Increased K to 20
- ✅ Measured Recall@20

### Results

| Metric | Outcome |
|--------|---------|
| Recall | ✅ Improved |
| Precision | ⚠️ Bottleneck exposed |

### Exit Condition

✅ **Recall ≥ 90%** (achieved)

> **Note:** Do not touch embeddings anymore for now.

---

## 🟠 Phase 2 — Precision Upgrade

**Status:** 🚧 **NEXT STEP**

**Objective:** Replace heuristic ranking with learned ranking

### Step 2.1 — Remove Hard Gates

**Action:** Delete or disable the following:

- Absolute distance threshold
- Relative gap threshold
- Keyword-based rerank hacks

**Goal:** Keep system clean

### Step 2.2 — Implement Two-Stage Retrieval

**New Pipeline:**

```
Query
  ↓
BGE-M3 retrieve top 20
  ↓
Cross-Encoder reranker
  ↓
Sort by rerank score
  ↓
Return top result
```

**Recommended Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Why this model:**

- ✓ Balanced speed
- ✓ Stable
- ✓ Easy to integrate

### Step 2.3 — Basic Junk Gate

Add **one simple rule:**

```python
if rerank_score < threshold:
    return "No relevant provision found."
```

> **Important:** Do NOT over-engineer rejection logic yet.

### Step 2.4 — Measure Again

**Action:** Re-run `evaluate.py`

**Track:**

| Metric | Target |
|--------|--------|
| Top-1 accuracy | ≥ 80–85% |
| Top-3 accuracy | Track |
| Junk rejection rate | Track |

---

## 🟡 Phase 3 — Calibration

**Status:** ⏸️ **PENDING** (Only after reranking works)

### Step 3.1 — Log Reranker Scores

For each query, log:

- Correct score
- Incorrect score
- Junk score

### Step 3.2 — Build Histogram

**Actions:**

1. Find natural separation in score distribution
2. Set rejection threshold scientifically
3. Remove magic numbers

---

## 🟢 Phase 4 — Stability Layer

**Status:** ⏸️ **PENDING** (Once precision is strong)

### Tasks

- [ ] Add CI benchmark run
- [ ] Track regression automatically
- [ ] Log latency (Target: **P95 < 300ms**)

---

## 🔴 Phase 5 — Intelligence

**Status:** ⏸️ **OPTIONAL** (Later)

### Prerequisites

**Only proceed if:**

1. Single-article accuracy **> 88%**
2. Multi-article reasoning becomes bottleneck

### Then:

- Add Lite JSON Graph for override logic
  - **NOT** Neo4j
  - **NOT** Agents

---

## 🧠 Important Guardrails

### ❌ Do NOT:

- Switch embeddings again
- Add graph now
- Add intent router now
- Tune 10 hyperparameters at once

### ✅ Core Principle:

**One variable at a time.**