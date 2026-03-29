import psycopg2
import json
import os
from dotenv import load_dotenv

from core.embeddings.bge_embedder import embed_query


load_dotenv()


K_VALUES = [1, 5, 10, 20, 40]


INPUT_FILE = "dataset/training_queries.json"


conn = psycopg2.connect(

    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),

)

cur = conn.cursor()


with open(INPUT_FILE) as f:

    queries = json.load(f)


results = {k: 0 for k in K_VALUES}


total = len(queries)


print(f"\nRunning production recall test on {total} queries\n")


for i, entry in enumerate(queries, 1):

    query = entry["query"]

    correct_id = str(entry["article_id"])


    emb = embed_query(query)

    emb_str = "[" + ",".join(map(str, emb)) + "]"


    cur.execute(

        f"""
        SELECT article_id
        FROM articles
        ORDER BY embedding <=> '{emb_str}'::vector
        LIMIT 40
        """

    )


    retrieved = [row[0] for row in cur.fetchall()]


    for k in K_VALUES:

        if correct_id in retrieved[:k]:

            results[k] += 1


    if i % 100 == 0:

        print(f"Processed {i}/{total}")


print("\nFINAL RESULTS\n")


for k in K_VALUES:

    print(

        f"Recall@{k}: {results[k]}/{total} = {(results[k]/total)*100:.2f}%"

    )


cur.close()
conn.close()
