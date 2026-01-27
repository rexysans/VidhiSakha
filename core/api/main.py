from typing import Union
import psycopg2
from dotenv import load_dotenv
import os
from fastapi import FastAPI

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


app = FastAPI()

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
