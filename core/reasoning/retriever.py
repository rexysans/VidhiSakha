def retrieve_articles(conn, parsed_query: dict):
    parts = parsed_query["likely_parts"]
    topic = parsed_query["topic"]
    cursor = conn.cursor()

    if not parts:
        return []

    cursor.execute(
        "SELECT article_id,title,full_text FROM articles WHERE part_uid = ANY(%s)",
        (parts,),
    )

    rows = cursor.fetchall()
    cursor.close()

    relevant_articles = []

    keywords = parsed_query["keywords"]
    for article_id, title, text in rows:
        t = text.lower()
        if any(k in t for k in keywords):
            relevant_articles.append(
                {"article_id": article_id, "title": title, "full_text": text}
            )

    return relevant_articles
