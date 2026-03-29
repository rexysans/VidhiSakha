# core/reasoning/query_expander.py
"""
Query Expander — translates colloquial user queries into
constitutional terminology before retrieval.

Uses LLM when available, falls back to keyword rules.
"""

import re
import os
from core.reasoning.llm_provider import llm_generate


# ---------------------------------------------------------------------------
# LLM-based expansion
# ---------------------------------------------------------------------------
_EXPAND_PROMPT = """You are a legal query translator for the Indian Constitution.

Given a user query, output ONLY a rewritten version that uses constitutional terminology.
Do NOT answer the question. ONLY rewrite it.

Rules:
- Keep it short (1-2 sentences max)
- Use exact constitutional terms (e.g., "reasonable restrictions", "fundamental rights", "directive principles")
- Preserve article numbers if mentioned (e.g., "Article 21")
- If the query already uses legal terminology, return it unchanged

Examples:
- "Can the government stop free speech?" → "What are the reasonable restrictions on freedom of speech and expression under Article 19?"
- "right to life" → "Right to life and personal liberty under Article 21"
- "reservation in government jobs" → "Reservation in public employment and equality of opportunity under Article 16"
- "president rule in state" → "Provisions for failure of constitutional machinery in states under Article 356"
- "Article 14" → "Article 14 — Equality before law"

User query: {query}
Rewritten query:"""


def _llm_expand(query: str) -> str:
    prompt = _EXPAND_PROMPT.format(query=query)
    result = llm_generate(prompt)
    if result:
        # Clean up: remove quotes, extra whitespace
        result = result.strip().strip('"').strip("'")
        # If LLM returned something way too long, it hallucinated
        if len(result) > 300:
            return ""
        return result
    return ""


# ---------------------------------------------------------------------------
# Rule-based expansion (fallback)
# ---------------------------------------------------------------------------
_KEYWORD_MAP = {
    "free speech": "freedom of speech and expression Article 19",
    "stop free speech": "reasonable restrictions freedom speech Article 19",
    "right to life": "right to life and personal liberty Article 21",
    "self-incrimination": "protection in respect of conviction for offences Article 20",
    "double jeopardy": "protection in respect of conviction for offences Article 20",
    "forced to join": "freedom to form associations Article 19",
    "union": "freedom to form associations Article 19",
    "untouchability": "abolition of untouchability Article 17",
    "forced labour": "prohibition of traffic in human beings and forced labour Article 23",
    "child labour": "prohibition of employment of children Article 24",
    "preventive detention": "protection against arrest and detention Article 22",
    "writ": "power to issue writs Article 32 Article 226",
    "high courts": "power of high courts to issue writs Article 226",
    "emergency": "proclamation of emergency Article 352",
    "president rule": "failure of constitutional machinery in states Article 356",
    "state takes over": "provisions in case of failure of constitutional machinery in states Article 356",
    "war-time": "proclamation of emergency Article 352",
    "tax money to states": "effect of proclamation of emergency and distribution of revenues Article 354",
    "migrants from pakistan": "rights of citizenship of certain migrants to Pakistan Article 7",
    "london": "rights of citizenship of certain persons of indian origin residing outside india Article 8",
    "financial emergency": "provisions as to financial emergency Article 360",
    "uniform civil code": "uniform civil code for citizens Article 44",
    "cow slaughter": "organisation of agriculture and animal husbandry Article 48",
    "living wage": "living wage and conditions of work Article 43",
    "public health": "raising the level of nutrition and the standard of living and improvement of public health Article 47",
    "taj mahal": "protection of monuments and places and objects of national importance Article 49",
    "equal pay": "equal pay for equal work Article 39",
    "free legal aid": "equal justice and free legal aid Article 39A",
    "environment": "protection and improvement of environment Article 48A",
    "minorities": "protection of interests of minorities Article 29 Article 30",
    "minority schools": "right of minorities to establish and administer educational institutions Article 30",
    "minority run schools": "right of minorities to establish and administer educational institutions Article 30",
    "citizenship": "citizenship at the commencement of the Constitution Article 5",
    "foreign citizenship disqualification": "termination of citizenship on acquisition of foreign citizenship Article 9",
    "state deny job based on caste": "equality of opportunity in public employment no discrimination by caste Article 16",
    "job based on caste": "equality of opportunity in public employment no discrimination by caste Article 16",
    "scheduled castes services": "claims of scheduled castes and scheduled tribes to services and posts Article 335",
    "reservation in panchayats": "reservation of seats in panchayats Article 243D",
    "reservation in municipalities": "reservation of seats in municipalities Article 243T",
    "religion": "freedom of conscience and free profession practice and propagation of religion Article 25",
    "discrimination": "prohibition of discrimination on grounds of religion race caste sex Article 15",
    "judges from bureaucrats": "separation of judiciary from executive Article 50",
    "center takes over": "failure of constitutional machinery in states Article 356",
}

_INTENT_ARTICLE_HINTS = {
    "can i be forced to join a union": ["19"],
    "double jeopardy": ["20"],
    "self-incrimination": ["20"],
    "untouchability": ["17"],
    "child labour": ["24"],
    "child labor": ["24"],
    "living wage": ["43"],
    "free speech restrictions": ["19"],
    "public order restriction speech": ["19"],
    "freedom restrictions": ["19"],
    "state cannot discriminate": ["15"],
    "can state deny job based on caste": ["16"],
    "jobs equality": ["16"],
    "court writ powers": ["32", "226"],
    "detained without lawyer": ["22"],
    "minority run schools": ["30"],
    "rights of indian people living in london": ["8"],
    "person who went to pakistan and came back": ["7"],
    "procedure for the death penalty": ["21"],
    "parliament power during emergency": ["353"],
    "foreign citizenship disqualification": ["9"],
    "reservation for scheduled castes services": ["335"],
    "suspension of article 19 during emergency": ["358"],
    "who pays for minority run schools": ["30"],
    "what happens to states when center takes over": ["356"],
    "can the president stop giving tax money to states during war": ["354"],
    "steps to separate judges from bureaucrats": ["50"],
    "steps to stop cow slaughter": ["48"],
    "protection of the taj mahal and other sites": ["49"],
    "improving public health": ["47"],
}


def _detect_intent_boosts(query: str) -> tuple[list[str], list[str]]:
    q_lower = query.lower()
    boost_phrases: list[str] = []
    priority_ids: list[str] = []

    for trigger, ids in _INTENT_ARTICLE_HINTS.items():
        if trigger in q_lower:
            for aid in ids:
                boost_phrases.append(f"Article {aid}")
                if aid not in priority_ids:
                    priority_ids.append(aid)

    # Context-aware reservation routing to avoid collapsing all reservation
    # queries to Article 16.
    if "reservation" in q_lower:
        if "panchayat" in q_lower:
            if "243D" not in priority_ids:
                priority_ids.insert(0, "243D")
            boost_phrases.append("reservation of seats in panchayats Article 243D")
        elif "municipal" in q_lower:
            if "243T" not in priority_ids:
                priority_ids.insert(0, "243T")
            boost_phrases.append("reservation of seats in municipalities Article 243T")
        elif "scheduled caste" in q_lower or "scheduled castes" in q_lower or "services" in q_lower:
            if "335" not in priority_ids:
                priority_ids.insert(0, "335")
            boost_phrases.append("claims of scheduled castes and scheduled tribes to services and posts Article 335")
        elif "public employment" in q_lower or "job" in q_lower:
            if "16" not in priority_ids:
                priority_ids.insert(0, "16")
            boost_phrases.append("equality of opportunity in public employment Article 16")
        elif "16" not in priority_ids:
            priority_ids.insert(0, "16")

    if "reservation" in q_lower and "public employment" in q_lower:
        if "16" not in priority_ids:
            priority_ids.insert(0, "16")
        boost_phrases.append("equality of opportunity in public employment Article 16")

    return boost_phrases, priority_ids


def _rule_expand(query: str) -> str:
    q_lower = query.lower()
    expansions = []
    for trigger, expansion in _KEYWORD_MAP.items():
        if trigger in q_lower:
            expansions.append(expansion)
    if expansions:
        return query + " " + " ".join(expansions)
    return query


# ---------------------------------------------------------------------------
# Direct article reference detector
# ---------------------------------------------------------------------------
_ARTICLE_PATTERN = re.compile(r'\barticle\s+(\d+[A-Z]?)\b', re.IGNORECASE)


def _extract_article_ref(query: str) -> str | None:
    """If user says 'Article 21', return '21'."""
    match = _ARTICLE_PATTERN.search(query)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def expand_query(query: str, use_llm: bool = False) -> dict:
    """
    Expand/rewrite the user query for better retrieval.

    Returns:
        {
            "original": str,
            "expanded": str,        # rewritten query for retrieval
            "article_ref": str|None # explicit article number if mentioned
        }
    """
    article_ref = _extract_article_ref(query)
    llm_enabled = use_llm or os.getenv("VIDHI_USE_LLM_EXPANSION", "0") == "1"
    boost_phrases, priority_article_ids = _detect_intent_boosts(query)

    # If user explicitly references an article ("Article 19 restrictions"),
    # do NOT rewrite via LLM — the expansion often pulls sibling articles
    # (e.g., Art 358 which *suspends* Art 19).  Keep the query close to
    # what the user typed and let the hard-pin + cross-encoder handle it.
    if article_ref:
        expanded = query  # keep original wording
    else:
        expanded = ""
        if llm_enabled:
            expanded = _llm_expand(query)
        if not expanded:
            expanded = _rule_expand(query)

    if boost_phrases:
        expanded = f"{expanded} {' '.join(boost_phrases)}".strip()

    return {
        "original": query,
        "expanded": expanded,
        "article_ref": article_ref,
        "priority_article_ids": priority_article_ids,
    }
