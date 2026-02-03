import psycopg2
from sentence_transformers import SentenceTransformer
import os 
from dotenv import load_dotenv


load_dotenv()


model = SentenceTransformer("all-MiniLM-L6-v2")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()
cur.execute("SELECT article_uid, full_text FROM articles")
rows = cur.fetchall()

print(f"Embedding {len(rows)} articles...")

for uid, text in rows:
    emb = model.encode(text).tolist()
    cur.execute(
        "UPDATE articles SET embedding = %s WHERE article_uid = %s",
        (emb, uid),
    )

conn.commit()
cur.close()
conn.close()

print("✅ All embeddings stored.")