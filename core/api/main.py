from typing import Union
import psycopg2
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from core.reasoning.query_parser import parse_query
from core.reasoning.retriever import retrieve_articles
from core.reasoning.reranker import legal_reranker
from core.reasoning.answer_builder import build_answer


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def load_parts_cache():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT part_uid, part_name FROM parts")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"part_uid": r[0], "name": r[1].lower()} for r in rows]


app = FastAPI()

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
        conn.close()
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
        conn.close()

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
        conn.close()
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
        conn.close()
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


@app.get("/v1/ask")
def ask_question(q: str):
    try:
        conn = get_connection()

        # 1. RETRIEVAL (The 'Recall' Phase)
        # Fetch 20 candidates using BGE-M3
        initial_candidates = retrieve_articles(conn, q, k=40)

        if not initial_candidates:
            conn.close()
            return {"answer": {"answer": "No legal provisions found.", "citations": []}}

        # 2. RERANKING (The 'Precision' Phase)
        # Use our new specialized reranker module
        reranked_results = legal_reranker.rerank(q, initial_candidates)

        # 3. JUNK GATE (The 'Safety' Phase)
        # Based on initial benchmarks, 1.0 is a solid starting threshold
        best_doc = reranked_results[0]
        print(f"article: {best_doc['title']},rerank score: {best_doc['rerank_score']}")
        JUNK_THRESHOLD = -5.0

        if best_doc["rerank_score"] < JUNK_THRESHOLD:
            conn.close()
            return {
                "answer": {
                    "answer": "No directly relevant legal provision found.",
                    "citations": [],
                }
            }

        # 4. ANSWER BUILDING
        # Send only the logically-best document for the final answer
        answer = build_answer(q, [best_doc])
        conn.close()

        return {"answer": answer}

    except Exception as e:
        print(f"Server Error: {e}")
        return {"error": "Internal processing error"}
