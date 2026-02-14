from typing import Union
import psycopg2
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from core.reasoning.query_parser import parse_query
from core.reasoning.retriever import retrieve_articles
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
        articles = retrieve_articles(conn, q)

        if not articles:
            conn.close()
            return {
                "answer": {
                    "answer": "No directly relevant legal provision was found.",
                    "citations": [],
                }
            }

        # Step 1: Compute semantic best separately (for gates)
        semantic_sorted = sorted(articles, key=lambda a: a["distance"])
        semantic_best = semantic_sorted[0]
        semantic_second = semantic_sorted[1] if len(semantic_sorted) > 1 else None

        ABS_LIMIT = 1.15
        REL_GAP = 0.005

        ## Debug
        for article in articles:
            print(article["title"], article["distance"])

        # Step 2: Semantic sanity gates (check if semantic signal is real)
        keywords = q.lower().split()

        def keyword_score(article):
            text = (article["title"] + " " + article["full_text"]).lower()
            return sum(k in text for k in keywords)

        # Absolute junk rejection with keyword override
        # Only reject if semantic weak AND keyword score is zero
        if semantic_best["distance"] > ABS_LIMIT and keyword_score(semantic_best) == 0:
            conn.close()
            return {
                "answer": {
                    "answer": "No directly relevant legal provision was found.",
                    "citations": [],
                }
            }

        # Relative sanity gate (using semantic distances)
        if (
            semantic_second
            and (semantic_second["distance"] - semantic_best["distance"]) < REL_GAP
        ):
            conn.close()
            return {
                "answer": {
                    "answer": "No directly relevant legal provision was found.",
                    "citations": [],
                }
            }

        # Step 3: Keyword reranking for final answer selection
        articles.sort(
            key=lambda a: (
                -keyword_score(a),  # keyword relevance first
                a["distance"],  # semantic tie-breaker
            )
        )

        best = articles[0]
        threshold = 1.1

        filtered = [best]

        filtered += [a for a in articles[1:] if a["distance"] <= threshold]
        answer = build_answer(q, filtered)
        conn.close()
        return {"answer": answer}
    except Exception as e:
        raise e
