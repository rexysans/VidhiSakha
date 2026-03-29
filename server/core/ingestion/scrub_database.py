import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def scrub_database():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()

    # 1. Fix the 39A Formatting (Crucial for tokenization)
    print("🧹 Fixing Article 39A formatting...")
    cur.execute("""
        UPDATE articles 
        SET full_text = REPLACE(full_text, '39. A', '39A'),
            title = '39A. Equal justice and free legal aid'
        WHERE article_id = '39A';
    """)

    # 2. Fix 31C/32 Text Bleed
    print("🧹 Cleaning Article 31C text bleed...")
    cur.execute("""
        UPDATE articles 
        SET full_text = REGEXP_REPLACE(full_text, 'Right to Constitutional Remedies$', '')
        WHERE article_id = '31C';
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database scrubbed. Re-run embed_articles.py now to update embeddings.")

if __name__ == "__main__":
    scrub_database()