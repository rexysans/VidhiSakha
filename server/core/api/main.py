from typing import Union
import psycopg2
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.reasoning.query_parser import parse_query
from core.reasoning.retriever import retrieve_articles
from core.reasoning.reranker import legal_reranker
from core.reasoning.answer_builder import build_answer
from core.reasoning.ltr.inference import VidhiSakhaLTRInference
from core.reasoning.retriever import retrieve_articles, model as bge_model
from core.reasoning.domain_classifier import DomainClassifier
from core.reasoning.query_expander import expand_query

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


from psycopg2 import pool

# Create a pool at the top of your file (outside any functions)
db_pool = pool.SimpleConnectionPool(
    1,
    20,  # Minimum 1, Maximum 20 connections
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
)


def get_connection():
    return db_pool.getconn()


def load_parts_cache():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT part_uid, part_name FROM parts")
    rows = cur.fetchall()
    cur.close()
    db_pool.putconn(conn)

    return [{"part_uid": r[0], "name": r[1].lower()} for r in rows]


app = FastAPI()

_cors_origins_env = os.getenv(
    "CORS_ALLOW_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
)
_cors_origins = [origin.strip() for origin in _cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ltr_engine = VidhiSakhaLTRInference()
domain_gate = DomainClassifier(bge_model)

PARTS_CACHE = load_parts_cache()


app.get("/")


@app.get("/v1/health")
def read_root():
    return {"status": "ok"}


@app.get("/v1/articles/{article_id}")
def read_articles(article_id: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE article_id = %s", (article_id,))
        row = cursor.fetchone()
        cursor.close()
        db_pool.putconn(conn)
        if not row:
            return {"404": "Article not found"}
        return {
            "article_uid": row[0],
            "article_id": row[1],
            "title": row[2],
            "full_text": row[3],
            "part_uid": row[4],
        }

    except Exception as e:
        return {"404": "Article not found"}


@app.get("/v1/parts/{part_uid}")
def read_parts(part_uid: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parts WHERE part_uid = %s", (part_uid,))
        row = cursor.fetchone()
        cursor.close()
        db_pool.putconn(conn)

        if not row:
            return {"404": "Article not found"}

        return {
            "part_uid": row[0],
            "part_id": row[1],
            "part_name": row[2],
            "article_start": row[3],
            "article_end": row[4],
        }
    except Exception as e:
        return {"404": "Article not found"}


@app.get("/v1/search")
def search(query: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT article_id, title FROM articles WHERE full_text ILIKE %s",
            (f"%{query}%",),
        )
        row = cursor.fetchall()
        cursor.close()
        db_pool.putconn(conn)
        return [{"article_id": r[0], "title": r[1]} for r in row]
    except Exception as e:
        return {"404": "Article not found"}


@app.get("/v1/parts/{part_uid}/articles")
def read_articles_by_part(part_uid: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE part_uid = %s", (part_uid,))
        row = cursor.fetchall()
        cursor.close()
        db_pool.putconn(conn)
        if not row:
            return {"404": "Article not found"}
        return [
            {
                "article_uid": r[0],
                "article_id": r[1],
                "title": r[2],
                "full_text": r[3],
                "part_uid": r[4],
            }
            for r in row
        ]
    except Exception as e:
        return {"404": "Article not found"}


# @app.get("/v1/ask")
# def ask_question(q: str):
#     try:
#         conn = get_connection()
#         parsed_query = parse_query(q,PARTS_CACHE)
#         articles = retrieve_articles(conn, parsed_query)
#         answer = build_answer(parsed_query, articles)
#         conn.close()
#         return answer
#     except Exception as e:
#         return {"404": "Article not found"}


# @app.get("/v1/ask")
# def ask_question(q: str):
#     try:
#         conn = get_connection()

#         # 1. RETRIEVAL (The 'Recall' Phase)
#         # Fetch 20 candidates using BGE-M3
#         initial_candidates = retrieve_articles(conn, q, k=40)

#         if not initial_candidates:
#             conn.close()
#             return {"answer": {"answer": "No legal provisions found.", "citations": []}}

#         # 2. RERANKING (The 'Precision' Phase)
#         # Use our new specialized reranker module
#         reranked_results = legal_reranker.rerank(q, initial_candidates)

#         # # 3. JUNK GATE (The 'Safety' Phase)
#         # # Based on initial benchmarks, 1.0 is a solid starting threshold
#         # best_doc = reranked_results[0]

#         ltr_results = ltr_engine.rank(q, reranked_results)
#         best_doc = ltr_results[0]


#         print(f"article: {best_doc['title']},rerank score: {best_doc['rerank_score']}")
#         JUNK_THRESHOLD = -5.0

#         if best_doc["rerank_score"] < JUNK_THRESHOLD:
#             conn.close()
#             return {
#                 "answer": {
#                     "answer": "No directly relevant legal provision found.",
#                     "citations": [],
#                 }
#             }

#         # 4. ANSWER BUILDING
#         # Send only the logically-best document for the final answer
#         answer = build_answer(q, [best_doc])
#         conn.close()

#         return {"answer": answer}

#     except Exception as e:
#         print(f"Server Error: {e}")
#         return {"error": "Internal processing error"}


# @app.get("/v1/ask")
# def ask_question(q: str):

#     conn = get_connection()

#     try:

#         candidates = retrieve_articles(conn, q, k=40)

#         if not candidates:
#             return empty_response()

#         reranked = legal_reranker.rerank(q, candidates)

#         ltr_results = ltr_engine.rank(q, reranked)

#         # HYBRID SCORE
#         for doc in ltr_results:

#             doc["final_score"] = doc["ltr_score"] + doc["rerank_score"]

#         best_doc = max(ltr_results, key=lambda x: x["final_score"])


#         # FINAL THRESHOLD

#         if not domain_classifier.is_legal(q):
#             return empty_response()

#         if best_doc["final_score"] < 2.0:

#             return empty_response()

#         answer = build_answer(q, [best_doc])

#         return {"answer": answer}

#     finally:
#         conn.close()


# def empty_response():

#     return {
#         "answer": {
#             "answer": "No directly relevant legal provision found.",
#             "citations": [],
#         }
#     }

# core/api/main.py
# In core/api/main.py


@app.get("/v1/ask")
def ask_question(q: str):
    conn = get_connection()
    try:
        def _env_float(name: str, default: float) -> float:
            try:
                return float(os.getenv(name, str(default)))
            except Exception:
                return default

        # STEP 0: EARLY QUERY EXPANSION SIGNALS
        # Extract article/intents before domain gate so colloquial legal queries
        # are not rejected too early.
        expansion = expand_query(q)
        search_query = expansion["expanded"]
        article_ref = expansion["article_ref"]
        priority_article_ids = [str(x).lower() for x in expansion.get("priority_article_ids", [])]

        # STEP 1: DOMAIN GATE
        is_legal, domain_score = domain_gate.is_legal(q)
        if not is_legal and (article_ref or priority_article_ids):
            # Intent hints from expander indicate constitutional scope.
            is_legal = True
            domain_score = max(domain_score, 0.95)

        if not is_legal:
            return {
                "answer": {
                    "answer": "I am specialized in the Constitution of India. This query appears outside my domain.",
                    "citations": [],
                }
            }

        # STEP 2: HYBRID RETRIEVAL (Dense + BM25 via RRF)
        candidates = retrieve_articles(conn, search_query)
        if not candidates:
            return {
                "answer": {
                    "answer": "No directly relevant legal provision found.",
                    "citations": [],
                }
            }

        # If user explicitly mentioned an article, boost it to the top
        if article_ref:
            for i, c in enumerate(candidates):
                if str(c.get("article-id", "")).lower() == article_ref.lower():
                    candidates.insert(0, candidates.pop(i))
                    break

        # Intent-aware pinning: move hinted article(s) ahead before reranking
        if priority_article_ids:
            pinned, others = [], []
            hint_set = set(priority_article_ids)
            for c in candidates:
                aid = str(c.get("article-id", "")).lower()
                (pinned if aid in hint_set else others).append(c)

            pinned.sort(
                key=lambda d: priority_article_ids.index(str(d.get("article-id", "")).lower())
                if str(d.get("article-id", "")).lower() in priority_article_ids else 999
            )
            candidates = pinned + others

        # STEP 3: RERANKING (Cross-Encoder)
        reranked = legal_reranker.rerank(q, candidates)

        # STEP 4: LTR FUSION
        results = ltr_engine.rank(q, reranked)
        if not results:
            return {
                "answer": {
                    "answer": "No directly relevant legal provision found.",
                    "citations": [],
                }
            }

        # STEP 4.5: HARD ARTICLE-REF PIN
        # If user explicitly said "Article 21", force that article to rank 1
        # AFTER reranking/LTR, so it overrides neural scores
        allow_article_ref_pin = (
            article_ref is not None
            and (not priority_article_ids or article_ref.lower() in set(priority_article_ids))
        )

        if allow_article_ref_pin:
            for i, c in enumerate(results):
                if str(c.get("article-id", "")).lower() == article_ref.lower():
                    results.insert(0, results.pop(i))
                    break

        # Intent-aware pinning after LTR as well
        if priority_article_ids and not article_ref:
            pinned, others = [], []
            hint_set = set(priority_article_ids)
            for c in results:
                aid = str(c.get("article-id", "")).lower()
                (pinned if aid in hint_set else others).append(c)

            pinned.sort(
                key=lambda d: priority_article_ids.index(str(d.get("article-id", "")).lower())
                if str(d.get("article-id", "")).lower() in priority_article_ids else 999
            )
            results = pinned + others

        # STEP 5: CALIBRATED GATE
        best = results[0]
        print(
            f"[ASK] mode={os.getenv('LLM_PROVIDER_MODE', 'unset')} "
            f"model={os.getenv('OLLAMA_MODEL', 'unset')} "
            f"query={q!r} | top={best['title']} | score={best['final_score']:.3f} | domain={domain_score:.3f}"
        )

        if best["final_score"] < -100.0:
            return {
                "answer": {"answer": "No relevant provision found.", "citations": []}
            }

        # STEP 5.5: ABSTAIN CALIBRATION (conservative)
        min_score = _env_float("ASK_ABSTAIN_MIN_SCORE", -2.0)
        min_margin = _env_float("ASK_ABSTAIN_MIN_MARGIN", 0.03)
        min_domain = _env_float("ASK_ABSTAIN_MIN_DOMAIN", 0.35)

        second_score = float(results[1].get("final_score", -999.0)) if len(results) > 1 else -999.0
        top_score = float(best.get("final_score", -999.0))
        margin = top_score - second_score if second_score > -900 else top_score
        top_article_id = str(best.get("article-id", "")).lower()
        is_priority_top = top_article_id in set(priority_article_ids)

        # Abstain only when truly uncertain:
        #   1) low domain confidence, OR
        #   2) ambiguous ranking (tiny margin) + weak absolute score
        # Never abstain for explicit article references or when top article matches intent hint.
        low_domain = domain_score < min_domain
        ambiguous_ranking = margin < min_margin
        weak_top = top_score < min_score

        should_abstain = (
            article_ref is None
            and not is_priority_top
            and (low_domain or (ambiguous_ranking and weak_top))
        )

        if should_abstain:
            print(
                f"[ASK] abstain=true score={top_score:.3f} margin={margin:.3f} "
                f"domain={domain_score:.3f} thresholds=({min_score:.3f},{min_margin:.3f},{min_domain:.3f}) "
                f"priority_top={is_priority_top}"
            )
            return {
                "answer": {
                    "answer": "I am not sufficiently confident about the exact constitutional provision for this query. Please rephrase or mention a specific article/topic.",
                    "citations": [],
                }
            }

        # STEP 6: LLM-POWERED RAG (send top-5 for reasoning)
        top_n = results[:5]
        return {"answer": build_answer(q, top_n)}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "answer": {
                "answer": "Internal processing error.",
                "citations": [],
            }
        }
    finally:
        db_pool.putconn(conn)
