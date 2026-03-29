"""
Cross-encoder-only baseline: measures Recall@1 when sorting by cross_score
only (no LTR). Proves whether the LTR is helping or hurting.

Usage:
    python -m tests.baseline_cross_encoder
"""

import json
import sys
import os

sys.path.append(os.getcwd())

from core.reasoning.retriever import retrieve_articles
from core.reasoning.reranker import legal_reranker
from core.api.main import get_connection, db_pool


# evaluate_2.py adversarial test cases (legal queries only)
ADVERSARIAL_CASES = [
    {"query": "can i be forced to join a union?", "article_id": "19"},
    {"query": "right against self-incrimination", "article_id": "20"},
    {"query": "protection from arbitrary arrest", "article_id": "22"},
    {"query": "who pays for minority run schools?", "article_id": "30"},
    {"query": "procedure for the death penalty", "article_id": "21"},
    {"query": "what happens to states when center takes over?", "article_id": "356"},
    {"query": "can the president stop giving tax money to states during war?", "article_id": "354"},
    {"query": "declaring a war-time emergency", "article_id": "352"},
    {"query": "person who went to pakistan and came back in 1948", "article_id": "7"},
    {"query": "rights of indian people living in london", "article_id": "8"},
    {"query": "can parliament change citizenship rules?", "article_id": "11"},
    {"query": "how to move the supreme court for rights?", "article_id": "32"},
    {"query": "can high courts issue writs?", "article_id": "226"},
    {"query": "steps to separate judges from bureaucrats", "article_id": "50"},
    {"query": "steps to stop cow slaughter", "article_id": "48"},
    {"query": "guaranteeing a living wage", "article_id": "43"},
    {"query": "protection of the Taj Mahal and other sites", "article_id": "49"},
    {"query": "improving public health", "article_id": "47"},
]


def measure_baseline(queries, label, max_queries=None):
    """Measure Recall@1 and Recall@5 using cross_score sorting only."""
    correct_at_1 = 0
    correct_at_5 = 0
    total = min(len(queries), max_queries) if max_queries else len(queries)

    conn = get_connection()

    for i, entry in enumerate(queries[:total]):
        query = entry["query"]
        expected_id = str(entry["article_id"])

        try:
            candidates = retrieve_articles(conn, query)
            reranked = legal_reranker.rerank(query, candidates)

            # Sort by cross_score ONLY - no LTR
            sorted_by_cross = sorted(
                reranked, key=lambda x: x["cross_score"], reverse=True
            )

            top_ids = [str(c["article-id"]) for c in sorted_by_cross]

            if top_ids and top_ids[0] == expected_id:
                correct_at_1 += 1
            if expected_id in top_ids[:5]:
                correct_at_5 += 1
        except Exception as e:
            print(f"  Error on '{query[:50]}': {e}")

        if (i + 1) % 100 == 0:
            print(f"  [{i+1}/{total}] Running Recall@1: {correct_at_1/(i+1)*100:.1f}%")

    db_pool.putconn(conn)

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Recall@1 (cross-encoder only): {correct_at_1}/{total} = {correct_at_1/total*100:.2f}%")
    print(f"  Recall@5 (cross-encoder only): {correct_at_5}/{total} = {correct_at_5/total*100:.2f}%")
    print(f"{'='*60}\n")
    return correct_at_1 / total


if __name__ == "__main__":
    # Test 1: Adversarial queries (the hard ones)
    print("\n--- Adversarial Baseline ---")
    measure_baseline(ADVERSARIAL_CASES, "evaluate_2 adversarial (18 legal)")

    # Test 2: Training queries (sample)
    print("\n--- Training Queries Baseline ---")
    with open("dataset/training_queries.json") as f:
        train_queries = json.load(f)
    measure_baseline(train_queries, "training_queries.json (sample 500)", max_queries=500)
