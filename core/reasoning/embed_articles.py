import psycopg2
from sentence_transformers import SentenceTransformer
import os 
from dotenv import load_dotenv

load_dotenv()

# The new high-resolution engine
model = SentenceTransformer('BAAI/bge-m3')

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

# Get the articles to embed
cur.execute("SELECT article_uid, full_text FROM articles")
rows = cur.fetchall()

print(f"🚀 Embedding {len(rows)} articles with BGE-M3 (1024-dim)...")

for uid, text in rows:
    # We normalize for better distance math later
    emb = model.encode(text, normalize_embeddings=True).tolist()
    cur.execute(
        "UPDATE articles SET embedding = %s WHERE article_uid = %s",
        (emb, uid),
    )

conn.commit()
cur.close()
conn.close()

print("✅ DB Re-indexed successfully.")