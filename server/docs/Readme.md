# VidhiSakhā — Constitutional QA Backend

## Current Status
- Core legal retrieval/ranking pipeline is stable.
- API supports dual response styles:
  - `answer_human`: plain-language explanation
  - `answer_legal`: formal legal phrasing
- Legacy key `answer` remains for backward compatibility (mirrors `answer_human`).

---

## End-to-End Workflow
1. User asks a question in natural language.
2. Query is expanded with intent-aware constitutional cues.
3. Domain gate validates constitutional scope.
4. Hybrid retrieval runs (dense + sparse + fusion).
5. Cross-encoder reranking + LTR fusion ranks final candidates.
6. Top candidates are sent to answer builder.
7. Answer builder returns:
   - Human explanation
   - Legal explanation
   - Citations
8. If local LLM is unavailable, template fallback still returns deterministic answers + citations.

---

## API Response Shape (`/v1/ask`)
```json
{
  "answer": {
    "answer": "Plain language answer",
    "answer_human": "Plain language answer",
    "answer_legal": "Legal format answer",
    "citations": [
      {"article_id": "21", "title": "Protection of life and personal liberty"}
    ]
  }
}
```

---

## Runtime Configuration (`.env`)
### LLM/Ollama
- `LLM_PROVIDER_MODE=ollama_only`
- `OLLAMA_MODEL=llama3.1:8b`
- `OLLAMA_HOST=http://127.0.0.1:11434`
- `LLM_TIMEOUT_SECONDS=20`
- `LLM_MAX_RETRIES=1`
- `LLM_ENABLE_CLOUD_FALLBACK=0`
- `VIDHI_USE_LLM_EXPANSION=1`

### Stability / Circuit Breaker
- `LLM_CB_FAILURE_THRESHOLD=3`
- `LLM_CB_COOLDOWN_MINUTES=5`
- `LLM_MAX_PROMPT_CHARS=12000`
- `LLM_NUM_CTX=2048`
- `LLM_NUM_PREDICT=384`

### Abstain Calibration
- `ASK_ABSTAIN_MIN_SCORE=-2.0`
- `ASK_ABSTAIN_MIN_MARGIN=0.03`
- `ASK_ABSTAIN_MIN_DOMAIN=0.35`

### LTR Hard-Negative Training
- `LTR_HARD_NEG_WEIGHT=2.2`
- `LTR_HARD_POS_WEIGHT=1.6`
- `LTR_HARD_NEG_TOPK=5`

---

## Evaluation Scripts
### Core/Regression Set
```bash
python tests/evaluate.py
```

### Stress/Adversarial Set
```bash
python tests/evaluate_2.py
```

### Blind Generalization Set (new)
```bash
python tests/evaluate_blind.py
```
Dataset file: `dataset/blind_eval_120.json`

### LTR Before/After Compare (new)
```bash
python tests/ltr_compare.py
```
Prints:
- Top1
- Recall@5
- MRR
- Delta before vs after retrain

---

## Benchmark Snapshot
| Suite | Legal | Junk | Overall |
|---|---:|---:|---:|
| `evaluate.py` | 45/45 | 7/7 | 100.00% |
| `evaluate_2.py` | 18/18 | 7/7 | 100.00% |

> Note: Perfect benchmark scores can still overfit curated sets. Keep validating on blind paraphrases and real traffic logs.

---

## Frontend Scope (Recommended MVP)
### Required Screens
1. **Chat screen**
   - Query input
   - Submit button
   - Loading state
2. **Answer card**
   - Human answer block (`answer_human`)
   - Legal answer block (`answer_legal`)
   - Citations list (article id + title)
3. **History panel**
   - Previous queries and top citation

### Required UX Rules
- Show `answer_human` first for readability.
- Show `answer_legal` in expandable section for legal precision.
- If citations empty, show "Not enough confidence" state.
- Keep source citations clickable.

### Suggested API Integration Contract
- Always read `response.answer.answer_human` and `response.answer.answer_legal`.
- Fallback to `response.answer.answer` if `answer_human` missing.

### Frontend API Contract (Compact)
Use this exact mapping in UI rendering:

#### 1) Chat Bubble Payload
```json
{
  "message_human": "response.answer.answer_human",
  "message_legal": "response.answer.answer_legal",
  "fallback_message": "response.answer.answer",
  "citations": "response.answer.citations"
}
```

Render rule:
- Primary bubble text = `answer_human ?? answer`
- Legal expandable block = `answer_legal`

#### 2) Citation Card Payload
```json
{
  "id": "citation.article_id",
  "title": "citation.title",
  "chip_label": "Article {citation.article_id}",
  "subtitle": "citation.title"
}
```

#### 3) Empty/Low-Confidence State
```json
{
  "is_low_confidence": "response.answer.citations.length === 0",
  "ui_text": "I am not sufficiently confident. Please rephrase or mention a specific article/topic."
}
```

---

## Production Hardening Next
1. Stabilize Ollama process/runtime at OS/service level.
2. Monitor circuit-breaker open rate and LLM success ratio.
3. Expand blind eval set to 300+ live-like paraphrases.
4. Add latency SLO dashboard (`p50/p95`).
