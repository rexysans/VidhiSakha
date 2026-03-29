def parse_query(query: str, parts: list) -> dict:
    q = query.lower()
    matched_parts = []

    for p in parts:
        if any(word in q for word in p["name"].split()):
            matched_parts.append(p["part_uid"])

    return {
        "likely_parts": matched_parts,
        "topic": q,
        "keywords": [w for w in q.split() if len(w) > 3],
    }
