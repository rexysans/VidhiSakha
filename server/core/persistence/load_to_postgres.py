import psycopg2
from dotenv import load_dotenv
import os
import json


load_dotenv()


db_credentials = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
db_url = f"postgresql://{db_credentials['user']}:{db_credentials['password']}@{db_credentials['host']}/{db_credentials['database']}"

conn = psycopg2.connect(db_url)
cursor = conn.cursor()

with open("dataset/vidhisakha_kb_v1.json", "r") as f:
    data = json.load(f)


for part in data["parts"]:
    cursor.execute(
        "INSERT INTO parts (part_uid,part_id, part_name, article_start, article_end) VALUES (%s,%s, %s, %s, %s)",
        (
            part["part_uid"],
            part["part_id"],
            part["part_name"],
            part["article_range"]["start"],
            part["article_range"]["end"],
        ),
    )

for article in data["articles"]:
    cursor.execute(
        "INSERT INTO articles (article_uid,article_id, title, full_text, part_uid) VALUES (%s,%s, %s, %s, %s)",
        (
            article["article_uid"],
            article["article_id"],
            article["title"],
            article["full_text"],
            article["part_uid"],
        ),
    )


conn.commit()


cursor.close()
conn.close()

print("Knowledge base loaded into PostgreSQL.")
