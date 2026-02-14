# def score(article, keywords):
#     text = article["full_text"].lower()
#     return sum(1 for k in keywords if k in text)


# def build_answer(parsed_query: dict, articles: list) -> dict:
#     if not articles:
#         return {
#             "answer": "No directly relevant constitutional provision was found.",
#             "citations": [],
#         }

#     # pick the most informative article (longest text)

#     scored = [(a, score(a, parsed_query["keywords"])) for a in articles]
#     best, best_score = max(articles, key=lambda a: score(a, parsed_query["keywords"]))

#     if best_score == 0 :
#         best = articles[0]


#     rule = f"{best['title']} primarily governs the issue raised."

#     exception = ""
#     if "restriction" in best["full_text"].lower():
#         exception = "However, this right is not absolute and may be subject to reasonable restrictions imposed by law."

#     answer = rule
#     if exception:
#         answer += " " + exception

#     citations = [{"article_id": a["article_id"], "title": a["title"]} for a in articles]

#     return {"answer": answer, "citations": citations}



def score(article, keywords):
    text = article["title"].lower()
    hit = sum(1 for k in keywords if k in text)
    return hit * 3  # increase from 1 to 3



def build_answer(query:str,articles:list)->dict:
    if not articles:
          return {
            "answer": "No directly relevant legal provision was found.",
            "citations": [],
        }
        
    best  = articles[0]
    
    rule = f"{best['title']} governs this situation"
    exception = ""
    if "restriction" in best["full_text"].lower():
        exception = (
            " However, this right is not absolute and may be subject "
            "to reasonable restrictions imposed by law."
        )
    answer = rule + exception
    citations = [
        {"article_id": a["article-id"], "title": a["title"]}
        for a in articles
    ]
    return {"answer": answer , "citations":citations}