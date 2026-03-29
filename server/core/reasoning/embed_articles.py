import psycopg2
import os
from dotenv import load_dotenv

from core.embeddings.bge_embedder import embed_documents_batch

load_dotenv()

conn = psycopg2.connect(

    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),

)

cur = conn.cursor()

print("📖 Fetching articles...")

cur.execute(
    "SELECT article_uid, article_id, title, full_text FROM articles"
)

rows = cur.fetchall()

print(f"Total articles: {len(rows)}")

embeddings = embed_documents_batch(rows)

print("💾 Saving embeddings...")

for (uid, _, _, _), emb in zip(rows, embeddings):

    cur.execute(

        "UPDATE articles SET embedding = %s WHERE article_uid = %s",
        (emb, uid),

    )

conn.commit()

cur.close()
conn.close()

print("✅ All embeddings saved")
