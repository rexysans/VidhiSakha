import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

def load_json_articles():
    with open("dataset/vidhisakha_kb_v1.json", "r") as f:
        data = json.load(f)
    return {a["article_id"]: a for a in data["articles"]}

def load_db_articles():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT article_id, title, full_text FROM articles;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {r[0]: {"title": r[1], "full_text": r[2]} for r in rows}

def test_db_matches_json():
    json_articles = load_json_articles()
    db_articles = load_db_articles()

    print("JSON count:", len(json_articles))
    print("DB count:", len(db_articles))

    # 1. Check missing articles
    missing = set(json_articles.keys()) - set(db_articles.keys())
    if missing:
        print("\n❌ Missing in DB:", missing)

    # 2. Check extra articles
    extra = set(db_articles.keys()) - set(json_articles.keys())
    if extra:
        print("\n❌ Extra in DB:", extra)

    # 3. Check corrupted titles
    for aid in json_articles:
        if aid in db_articles:
            if json_articles[aid]["title"] != db_articles[aid]["title"]:
                print(f"\n⚠ Title mismatch for Article {aid}")
                print("JSON:", json_articles[aid]["title"][:100])
                print("DB  :", db_articles[aid]["title"][:100])

    print("\n✅ Integrity check complete.")

if __name__ == "__main__":
    test_db_matches_json()
