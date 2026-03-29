# core/reasoning/answer_builder.py
"""
v2 Answer Builder — LLM-powered RAG with template fallback.
Receives top-N candidates and asks an LLM to reason about which
article(s) best answer the query.
"""

import re
from core.reasoning.llm_provider import llm_generate


# ---------------------------------------------------------------------------
# RAG Prompt
# ---------------------------------------------------------------------------
_RAG_SYSTEM_PROMPT = """You are VidhiSakhā, an expert on the Constitution of India.
You will be given a user's legal query and a list of candidate constitutional articles.

Your task:
1. Identify which article(s) BEST answer the query.
2. Draft two HIGHLY DETAILED answer styles:
    - HUMAN_ANSWER: A comprehensive, expanded, plain-language explanation for non-lawyers. Break down the core concepts thoroughly and clearly.
    - LEGAL_ANSWER: A highly technical and expanded legal analysis. You must include statutory interpretation, structural analysis of the article, precise legal phrasing, and note any judicial precedent styling if applicable.
3. Note any exceptions, constitutional constraints, or reasonable restrictions mentioned.

Rules:
- DO NOT be brief. Provide an expanded and thoroughly reasoned response.
- ONLY use information from the provided articles. Do NOT hallucinate articles.
- If none of the articles are relevant, say "No directly relevant provision found."
- Always cite article numbers in both answer styles.
- Output in EXACT format:
HUMAN_ANSWER: <highly detailed text>
LEGAL_ANSWER: <highly technical text>
No extra headers, bullets, JSON, or markdown formatting before the keywords."""


def _build_rag_prompt(query: str, articles: list) -> str:
    """Format the candidates into a numbered context block."""
    context_parts = []
    for i, a in enumerate(articles, 1):
        aid = a.get("article-id", a.get("article_id", "?"))
        title = a.get("title", "")
        text = a.get("full_text", "")
        # Truncate very long text to stay within context window
        if len(text) > 1200:
            text = text[:1200] + "..."
        context_parts.append(
            f"[{i}] Article {aid} — {title}\n{text}"
        )

    context_block = "\n\n".join(context_parts)

    return f"""{_RAG_SYSTEM_PROMPT}

--- CANDIDATE ARTICLES ---
{context_block}

--- USER QUERY ---
{query}

--- YOUR ANSWER ---
HUMAN_ANSWER:
LEGAL_ANSWER:"""


# ---------------------------------------------------------------------------
# Template fallback (when LLM is unavailable)
# ---------------------------------------------------------------------------
def _template_answer(articles: list) -> tuple[str, str]:
    """Expanded rule-based dual-format answer when LLM fails or times out."""
    best = articles[0]
    aid = best.get("article-id", best.get("article_id", "?"))
    title = best.get("title", "Relevant constitutional provision")
    rule_h = (
        f"*(Static Fallback)* The backend AI is currently generating a long response, or is unavailable.\n\n"
        f"Based on our database, your query heavily relates to **Article {aid}: {title}**. "
        f"This article establishes the foundational constitutional principles relevant to your concern."
    )
    rule_l = (
        f"*(Static Template Mechanism)* LLM provider timeout or unavailability detected.\n\n"
        f"The constitutional issue at hand is formally governed by **Article {aid} of the Constitution of India** ({title}). "
        f"This forms the statutory and constitutional basis for addressing your fundamental rights and obligations."
    )
    exception = ""
    if "restriction" in best.get("full_text", "").lower():
        exception = (
            "\n\nIt is important to note that this provision is not absolute. "
            "It may be subject to reasonable restrictions imposed by law or the State."
        )
    return rule_h + exception, rule_l + exception


def _parse_dual_answer(raw: str) -> tuple[str, str]:
    text = (raw or "").strip()
    if not text:
        return "", ""

    human_match = re.search(r"[*]*HUMAN_ANSWER[*]*\s*:\s*(.*?)(?:\n\s*[*]*LEGAL_ANSWER[*]*\s*:|\Z)", text, re.IGNORECASE | re.DOTALL)
    legal_match = re.search(r"[*]*LEGAL_ANSWER[*]*\s*:\s*(.*)$", text, re.IGNORECASE | re.DOTALL)

    human = human_match.group(1).strip() if human_match else ""
    legal = legal_match.group(1).strip() if legal_match else ""

    if human and legal:
        return human, legal

    if text:
        return text, text

    return "", ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def build_answer(query: str, articles: list, use_llm: bool = True) -> dict:
    """
    Build an answer using LLM-powered RAG (top-N candidates).
    Falls back to template if LLM is unavailable.
    """
    if not articles:
        return {
            "answer": "No directly relevant legal provision was found.",
            "answer_human": "No directly relevant legal provision was found.",
            "answer_legal": "No directly relevant legal provision was found.",
            "citations": [],
        }

    # Try LLM-powered RAG
    answer_human = ""
    answer_legal = ""
    if use_llm:
        prompt = _build_rag_prompt(query, articles)
        raw = llm_generate(prompt)
        answer_human, answer_legal = _parse_dual_answer(raw)

    # Fallback to template if LLM returned nothing
    if not answer_human or not answer_legal:
        print(f"[ANSWER] fallback_used=template query={query!r} candidates={len(articles)}")
        answer_human, answer_legal = _template_answer(articles)

    citations = [
        {"article_id": a.get("article-id", a.get("article_id", "?")),
         "title": a.get("title", "")}
        for a in articles
    ]

    return {
        "answer": answer_human,
        "answer_human": answer_human,
        "answer_legal": answer_legal,
        "citations": citations,
    }
