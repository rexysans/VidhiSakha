# core/ingestion/transform_qa_to_ltr.py

import sys
import os
import json
import pandas as pd
import re
import logging
import time
import numpy as np

sys.path.append(os.getcwd())

from core.reasoning.retriever import retrieve_articles
from core.reasoning.reranker import legal_reranker
from core.api.main import db_pool


# ============================================
# LOGGING (file only, console handled by print)
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    handlers=[
        logging.FileHandler("dataset_generation.log"),
    ],
)

logger = logging.getLogger("LTR")


# ============================================
# TEXT CLEAN
# ============================================

def aggressive_clean(text):
    return re.sub(r"[^a-zA-Z0-9]", "", str(text)).lower()


# ============================================
# FIND GROUND TRUTH
# ============================================

def find_correct_article_id(answer_text, candidates):
    if not candidates:
        return None

    ans_clean = aggressive_clean(answer_text)

    # fast match: check if answer text is substring of article text
    for cand in candidates:
        if ans_clean in aggressive_clean(cand["full_text"]):
            return cand["article-id"]

    # neural fallback
    pairs = [[answer_text, cand["full_text"]] for cand in candidates]
    scores = legal_reranker.model.predict(
        pairs,
        batch_size=64,
        show_progress_bar=False
    )

    best_idx = np.argmax(scores)
    if scores[best_idx] > 0.5:
        return candidates[best_idx]["article-id"]

    return None


# ============================================
# MAIN
# ============================================

def transform():
    conn = db_pool.getconn()
    start_time = time.time()

    success = 0
    failed = 0
    skipped_dup = 0
    total_rows = 0

    try:
        with open("dataset/constitution_qa.json", "r", encoding="utf-8") as f:
            qa_data = json.load(f)

        total = len(qa_data)

        print("\n============================================================")
        print(f"STARTED DATASET GENERATION (v2)")
        print(f"TOTAL QUERIES: {total}")
        print("============================================================\n")

        logger.info(f"Started | Total Queries: {total}")

        rows = []
        seen_queries = set()

        # ============================================
        # MAIN LOOP
        # ============================================

        for i, entry in enumerate(qa_data):
            query = entry["question"].strip()

            # Deduplication
            query_key = aggressive_clean(query)
            if query_key in seen_queries:
                skipped_dup += 1
                continue
            seen_queries.add(query_key)

            answer = entry["answer"]

            try:
                candidates = retrieve_articles(conn, query)
                correct_id = find_correct_article_id(answer, candidates)

                if not correct_id:
                    failed += 1
                else:
                    success += 1
                    ranked = legal_reranker.rerank(query, candidates)

                    for pos, cand in enumerate(ranked, start=1):
                        row = {
                            "query": query,
                            "article_id": cand["article-id"],
                            "article_title": cand["title"],
                            "neural_score": cand["cross_score"],
                            "vector_distance": cand.get("distance", 0.0),
                            "rank": pos,
                            "full_text_length": len(cand.get("full_text", "")),
                            "is_correct": int(cand["article-id"] == correct_id),
                        }
                        rows.append(row)
                        total_rows += 1

            except Exception:
                failed += 1

            # ============================================
            # LIVE PROGRESS DISPLAY
            # ============================================

            processed = i + 1
            elapsed = time.time() - start_time
            speed = processed / elapsed if elapsed > 0 else 0
            remaining = total - processed
            eta = remaining / speed if speed > 0 else 0
            percent = (processed / total) * 100

            print(
                f"\r"
                f"[{processed}/{total}] "
                f"{percent:.2f}% | "
                f"ETA: {eta/60:.1f} min | "
                f"Speed: {speed:.2f} q/s | "
                f"Success: {success} | "
                f"Failed: {failed} | "
                f"Dupes: {skipped_dup} | "
                f"Rows: {total_rows}",
                end="",
                flush=True,
            )

        print("\n")

        # ============================================
        # SAVE DATASET
        # ============================================

        df = pd.DataFrame(rows)
        os.makedirs("dataset", exist_ok=True)
        df.to_csv("dataset/dataset_ltr_v2.csv", index=False)

        total_time = time.time() - start_time

        print("\n============================================================")
        print("DATASET GENERATION COMPLETE")
        print("============================================================")
        print(f"Total Queries  : {total}")
        print(f"Unique         : {len(seen_queries)}")
        print(f"Success        : {success}")
        print(f"Failed         : {failed}")
        print(f"Skipped (dup)  : {skipped_dup}")
        print(f"Total Rows     : {total_rows}")
        print(f"Total Time     : {total_time/60:.2f} min")
        print(f"Speed          : {total/total_time:.2f} q/s")
        print("Saved To       : dataset/dataset_ltr_v2.csv")
        print("============================================================\n")

        logger.info("Dataset generation complete")

    finally:
        db_pool.putconn(conn)


# ============================================

if __name__ == "__main__":
    transform()
