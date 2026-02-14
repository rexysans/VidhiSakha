# 🏛 VidhiSakhā — Elite 0.0001% Roadmap

This is a 4-Phase execution plan.

Each phase has:
- Objective
- Metrics
- Exit condition
- What NOT to touch

## 🔵 Phase 0 — Baseline Lock (You are here)

**Objective**

Understand exactly where you stand.

**Current Metrics (from your benchmark)**

- Core Accuracy: ~60% (`tests/diagonistic_1.txt`)
- Recall@20: 86.67% (`tests/diagonistic_1.txt`)

**Diagnosis:**
- Recall is the bottleneck.
- You are losing answers before reranking even starts.

**Tasks**

- Freeze `tests/evaluate.py`
- Freeze `tests/measure_recall.py`
- Do not edit test cases casually.

**Exit Condition**

You have:
- Baseline recall
- Baseline accuracy
- Baseline latency numbers written down

---

## 🔴 Phase 1 — Signal Correction (Embedding Upgrade)

**Objective**

Push Recall@20 ≥ 95%.

Because without recall, nothing downstream matters.

**Step 1 — Upgrade Embeddings**

Current: `all-MiniLM-L6-v2`

Upgrade path:
1. Try **BGE-Base**
2. If recall < 95%, move to **BGE-M3**

Re-index entire DB.

**Step 2 — Re-run Recall Benchmark**

Use your recall script `tests/measure_recall.py`

Target:
- Recall@20 ≥ 95%

**Step 3 — Do NOT Add Reranker Yet**

You don't stack systems on weak recall.

**Exit Condition**

- Recall@20 ≥ 95%
- No major latency explosion
- If recall is fixed → move forward.

---

## 🟠 Phase 2 — Precision Engineering (Two-Stage Retrieval)

Now we fix ranking confusion.

**Objective**

Push Top-1 Accuracy ≥ 85%.

**Step 1 — Add Cross-Encoder Reranker**

Pipeline:
```
Query
  ↓
Retrieve Top 20 (semantic)
  ↓
Rerank with Cross-Encoder
  ↓
Select Top 1–3
```

Start with:
- `cross-encoder/ms-marco-MiniLM-L-6-v2`

Only upgrade reranker if necessary.

**Step 2 — Re-run Full Benchmark**

Using `tests/evaluate.py`

Track:
- Top-1 Accuracy
- Top-3 Accuracy
- Junk Rejection Rate

**Targets:**

| Metric | Target |
|--------|--------|
| Recall@20 | ≥ 95% |
| Top-1 Accuracy | ≥ 85% |
| Top-3 Accuracy | ≥ 92% |
| Junk Rejection | ≥ 90% |

**Step 3 — Score Calibration**

Log reranker scores.

Build histogram:
- Correct
- Incorrect
- Junk

Choose rejection threshold scientifically.

**No vibes.**

**Exit Condition**

Stable ≥85% Top-1 with strong junk rejection.

---

## 🟡 Phase 3 — Stability & Discipline

Now you protect the system.

**Objective**

Make system measurable and regression-safe.

**Step 1 — CI Discipline**

Every code change:
1. Run benchmark
2. Compare accuracy delta
3. Reject regressions > 2%

**Step 2 — Latency Budget**

Target:
- P95 latency < 300ms

If too slow:
- Reduce rerank K
- Quantize model
- Batch scoring

**Step 3 — Logging**

Log per query:
- semantic score
- rerank score
- rejection reason

**Exit Condition**

System stable across multiple test runs.

---

## 🟢 Phase 4 — Intelligence Layer (Lite Graph)

Only after:
- Recall ≥ 95%
- Top-1 ≥ 88%
- Stable latency

**Objective**

Handle multi-article logic.

**Step 1 — JSON Adjacency Map**

Example:
```json
relations = {
  "352": {"suspends": ["19"]},
  "358": {"overrides": ["19"]},
}
```

**Step 2 — Conditional Expansion**

Only trigger graph when:
- Query mentions multiple legal contexts
- Rerank scores close

**Step 3 — Multi-Article Output**

Return:
- Primary article
- Related override article

**What NOT To Do**

❌ Do not add Neo4j  
❌ Do not add agent frameworks  
❌ Do not build LangChain pipelines  
❌ Do not overengineer  

395 articles do not require heavy graph infra.

---

## 🟣 Phase 5 — Product Polish

Only after engine is elite.

- Intent router (lightweight)
- Clause-level citation
- Confidence score
- Explainability

---

## 🧠 The Discipline Rules

1. Never jump phases.
2. Never tune blindly.
3. Always measure before upgrading.
4. Remove complexity if not justified.
5. **Elite = minimal sufficient architecture.**

---

## 🎯 Your Immediate Next Move

**You are in Phase 1.**

So:

1. Upgrade to **BGE-Base**.
2. Re-index.
3. Re-run Recall@20.
4. Paste new recall score.

**Do not touch reranker yet.**
