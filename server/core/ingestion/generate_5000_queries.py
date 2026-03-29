import json
import random

INPUT_FILE = "dataset/vidhisakha_kb_v1.json"
OUTPUT_FILE = "dataset/training_queries_5000.json"

TARGET = 5000


# Query templates (VERY IMPORTANT)
TEMPLATES = [

    # Direct legal
    "explain article {id}",
    "what is article {id}",
    "article {id} meaning",
    "article {id} explanation",

    # Rights style
    "what right does article {id} give",
    "what protection is given under article {id}",
    "constitutional provision for {title}",
    
    # User style natural language
    "can government do {title}",
    "what happens if {title}",
    "is it legal regarding {title}",
    
    # Conversational
    "tell me about {title}",
    "what does constitution say about {title}",
    "indian constitution rule for {title}",

    # Scenario based
    "legal rights related to {title}",
    "constitutional rights about {title}",
    "which article talks about {title}",

    # Adversarial style
    "who is protected under {title}",
    "how is {title} handled in constitution",

    # Short form
    "{title}",
]


def clean_title(title):

    # Remove article number prefix
    parts = title.split(".", 1)
    if len(parts) > 1:
        return parts[1].strip()

    return title.strip()


def main():

    with open(INPUT_FILE) as f:
        kb = json.load(f)

    articles = kb["articles"]

    queries = []

    print("Generating queries...")

    while len(queries) < TARGET:

        article = random.choice(articles)

        id = article["article_id"]
        title = clean_title(article["title"])

        template = random.choice(TEMPLATES)

        q = template.format(
            id=id,
            title=title.lower()
        )

        queries.append({
            "query": q,
            "article_id": id
        })


    print("Saving...")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(queries, f, indent=2)

    print("Done.")
    print("Generated:", len(queries))


if __name__ == "__main__":
    main()
